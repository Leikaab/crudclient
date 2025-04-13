import logging
import time
from collections.abc import Callable  # Import Callable
from typing import Any, Dict, Optional, Tuple, Union, cast

import requests
from requests.exceptions import HTTPError

from ..config import ClientConfig
from ..exceptions import (
    APIError,
    BadRequestError,
    ClientAuthenticationError,
    ConflictError,
    CrudClientError,
    ForbiddenError,
    InternalServerError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    UnprocessableEntityError,
)
from ..types import RawResponseSimple
from .errors import ErrorHandler
from .request import RequestFormatter
from .response import ResponseHandler
from .retry import RetryHandler
from .session import SessionManager
from .utils import redact_sensitive_headers

logger = logging.getLogger(__name__)

_BODY_LOG_TRUNCATION_LIMIT = 1024


class HttpClient:

    def __init__(
        self,
        config: ClientConfig,
        session_manager: Optional[SessionManager] = None,
        request_formatter: Optional[RequestFormatter] = None,
        response_handler: Optional[ResponseHandler] = None,
        error_handler: Optional[ErrorHandler] = None,
        retry_handler: Optional[RetryHandler] = None,
    ) -> None:
        if not isinstance(config, ClientConfig):
            raise TypeError("config must be a ClientConfig object")

        self.config = config
        self.session_manager = session_manager or SessionManager(config)
        self.request_formatter = request_formatter or RequestFormatter(config=self.config)
        self.response_handler = response_handler or ResponseHandler()
        self.error_handler = error_handler or ErrorHandler()
        self.retry_handler = retry_handler or RetryHandler(max_retries=config.retries)

    def _handle_request_response(self, response: requests.Response, handle_response: bool) -> Any:
        response.raise_for_status()

        if not handle_response:
            return response
        return self.response_handler.handle_response(response)

    def _request(self, method: str, endpoint: Optional[str] = None, url: Optional[str] = None, handle_response: bool = True, **kwargs: Any) -> Any:
        if not isinstance(handle_response, bool):
            raise TypeError(f"handle_response must be a boolean, got {type(handle_response).__name__}")

        final_url, prepared_kwargs = self.request_formatter.format_request(
            method, endpoint, url, **kwargs
        )

        logger.debug(f"Preparing {method} request to {final_url} with final params: {prepared_kwargs.get('params')}")

        def make_request() -> requests.Response:
            self._log_request_details(method, final_url, prepared_kwargs)  # Log details before sending
            return self.session_manager.session.request(method, final_url, timeout=self.session_manager.timeout, **prepared_kwargs)

        start_time = time.monotonic()
        attempt_count: int = 0
        final_outcome: Union[requests.Response, Exception, None] = None

        try:
            final_outcome, attempt_count = self._execute_request_with_retry(
                method, final_url, make_request, handle_response  # Pass handle_response
            )
            return final_outcome

        except HTTPError as e:
            final_outcome = e.response if e.response is not None else e
            self._handle_http_error(e)  # This method will raise the appropriate exception

        except NetworkError as e:
            final_outcome = e
            raise e  # Re-raise it to be caught by the caller

        except Exception as e:
            final_outcome = e
            logger.exception("An unexpected error occurred during the request to %s: %s", final_url, e)
            if not isinstance(e, CrudClientError):
                raise CrudClientError(f"An unexpected error occurred: {e}") from e
            else:
                raise e
        finally:
            self._log_request_completion(start_time, method, final_url, attempt_count, final_outcome)

    def _execute_request_with_retry(
        self, method: str, url: str, make_request_func: Callable[[], requests.Response], handle_response: bool  # Added handle_response back
    ) -> Tuple[Any, int]:  # Return type is processed/raw response or Exception
        result_tuple = cast(
            Tuple[Union[requests.Response, Exception], int],
            self.retry_handler.execute_with_retry(
                method,
                url,
                make_request_func,
                self.session_manager.session,
                self.session_manager.refresh_auth
            )
        )
        result, attempt_count = result_tuple

        if isinstance(result, requests.Response):
            response = result
            logger.debug("Received response for %s %s: Status %d", method, url, response.status_code)
            if response.status_code in (401, 403):
                logger.warning("Authentication failed for %s %s: Status %d", method, url, response.status_code)
            elif 400 <= response.status_code < 500:
                logger.warning("Client error for %s %s: Status %d", method, url, response.status_code)
            elif response.status_code >= 500:
                logger.error("Server error for %s %s: Status %d", method, url, response.status_code)

            logger.debug("Response Headers: %s", redact_sensitive_headers(response.headers))
            if logger.isEnabledFor(logging.DEBUG):
                if response.content:
                    if len(response.content) > _BODY_LOG_TRUNCATION_LIMIT:
                        logger.debug("Response Body (Truncated): %s...", response.content[:_BODY_LOG_TRUNCATION_LIMIT])
                    else:
                        logger.debug("Response Body: %s", response.content)
                else:
                    logger.debug("Response Body: (empty)")

            processed_or_raw_response = self._handle_request_response(response, True)  # Assume True for now, need handle_response here
            processed_or_raw_response = self._handle_request_response(response, handle_response)  # Use passed handle_response
            return processed_or_raw_response, attempt_count

        elif isinstance(result, Exception):
            raise result
        else:
            raise CrudClientError(f"Unexpected result type from retry handler: {type(result).__name__}")

    def _log_request_details(self, method: str, url: str, kwargs: Dict[str, Any]) -> None:
        params = kwargs.get('params')
        if params:
            logger.debug("Sending request: %s %s Params: %s", method, url, params)
        else:
            logger.debug("Sending request: %s %s", method, url)
        logger.debug("Request Headers: %s", redact_sensitive_headers(kwargs.get('headers', {})))
        if logger.isEnabledFor(logging.DEBUG):
            if 'data' in kwargs and kwargs['data']:
                data_str = str(kwargs['data'])
                if len(data_str) > _BODY_LOG_TRUNCATION_LIMIT:
                    logger.debug("Request Body (data, Truncated): %s...", data_str[:_BODY_LOG_TRUNCATION_LIMIT])
                else:
                    logger.debug("Request Body (data): %s", data_str)
            if 'json' in kwargs and kwargs['json']:
                json_str = str(kwargs['json'])
                if len(json_str) > _BODY_LOG_TRUNCATION_LIMIT:
                    logger.debug("Request Body (json, Truncated): %s...", json_str[:_BODY_LOG_TRUNCATION_LIMIT])
                else:
                    logger.debug("Request Body (json): %s", json_str)

    def _handle_http_error(self, e: HTTPError) -> None:
        response = e.response
        request = e.request

        if response is not None and request is not None:
            log_level = logging.WARNING if 400 <= response.status_code < 500 else logging.ERROR
            response_snippet = response.text[:_BODY_LOG_TRUNCATION_LIMIT] + ("..." if len(response.text) > _BODY_LOG_TRUNCATION_LIMIT else "")
            logger.log(
                log_level,
                "HTTP error encountered for %s %s: Status %d - Response: %s",
                request.method, request.url, response.status_code, response_snippet
            )

            STATUS_CODE_TO_EXCEPTION = {
                400: BadRequestError,
                401: ClientAuthenticationError,
                403: ForbiddenError,
                404: NotFoundError,
                409: ConflictError,
                422: UnprocessableEntityError,
                429: RateLimitError,
                500: InternalServerError,
                503: ServiceUnavailableError,
            }
            exception_cls = STATUS_CODE_TO_EXCEPTION.get(response.status_code, APIError)

            raise exception_cls(
                message=f"HTTP error occurred: {response.status_code} {response.reason}",
                request=request,
                response=response
            ) from e
        else:
            logger.error("HTTPError occurred without a response or request object: %s", e)
            raise APIError(
                message=f"HTTP error occurred: {e}",
                request=request,  # May be None
                response=response  # May be None
            ) from e

    def _log_request_completion(
        self,
        start_time: float,
        method: str,
        url: str,
        attempt_count: int,
        final_outcome: Union[requests.Response, Exception, None],
    ) -> None:
        end_time = time.monotonic()
        duration_ms = int((end_time - start_time) * 1000)
        if isinstance(final_outcome, requests.Response):
            response = final_outcome
            if response.ok:
                logger.info(
                    "Request %s %s completed successfully: %d %s in %dms.",
                    method, url, response.status_code, response.reason, duration_ms
                )
            else:
                logger.info(
                    "Request %s %s failed after %d attempts: %d %s in %dms.",
                    method, url, attempt_count, response.status_code, response.reason, duration_ms
                )
        elif isinstance(final_outcome, Exception):
            logger.info(
                "Request %s %s failed after %d attempts: %s in %dms.",
                method, url, attempt_count, type(final_outcome).__name__, duration_ms
            )
        elif final_outcome is None:
            logger.warning("Request %s %s completed with no outcome recorded in %dms.", method, url, duration_ms)

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> RawResponseSimple:
        return self._request("GET", endpoint=endpoint, params=params)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        prepared_data = {"data": data, "json": json, "files": files}  # Pass raw data to _request
        return self._request("POST", endpoint=endpoint, **prepared_data)

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        prepared_data = {"data": data, "json": json, "files": files}  # Pass raw data to _request
        return self._request("PUT", endpoint=endpoint, **prepared_data)

    def delete(self, endpoint: str, **kwargs: Any) -> RawResponseSimple:
        return self._request("DELETE", endpoint=endpoint, **kwargs)

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        prepared_data = {"data": data, "json": json, "files": files}  # Pass raw data to _request
        return self._request("PATCH", endpoint=endpoint, **prepared_data)

    def request_raw(self, method: str, endpoint: Optional[str] = None, url: Optional[str] = None, **kwargs: Any) -> requests.Response:
        return self._request(method, endpoint, url, handle_response=False, **kwargs)

    def close(self) -> None:
        self.session_manager.close()
        logger.debug("HttpClient closed.")
