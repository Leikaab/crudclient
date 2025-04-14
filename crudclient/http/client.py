import logging
import time
from collections.abc import Callable
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
from .logging import HttpLifecycleLogger  # Import the new logger class
from .request import RequestFormatter
from .response import ResponseHandler
from .retry import RetryHandler
from .session import SessionManager

# from .utils import redact_sensitive_headers # Keep only needed utils - Removed as unused

logger = logging.getLogger(__name__)
# _BODY_LOG_TRUNCATION_LIMIT is now in logging.py


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
        self.http_logger = HttpLifecycleLogger(config=config, logger=logger)  # Instantiate the logger

    def _handle_request_response(self, response: requests.Response, handle_response: bool) -> Any:
        response.raise_for_status()

        if not handle_response:
            return response
        return self.response_handler.handle_response(response)

    def _request(self, method: str, endpoint: Optional[str] = None, url: Optional[str] = None, handle_response: bool = True, **kwargs: Any) -> Any:
        if not isinstance(handle_response, bool):
            raise TypeError(f"handle_response must be a boolean, got {type(handle_response).__name__}")

        final_url, prepared_kwargs = self.request_formatter.format_request(method, endpoint, url, **kwargs)

        logger.debug(f"Preparing {method} request to {final_url} with final params: {prepared_kwargs.get('params')}")

        def make_request() -> requests.Response:
            self.http_logger.log_request_details(method, final_url, prepared_kwargs)  # Use new logger
            return self.session_manager.session.request(method, final_url, timeout=self.session_manager.timeout, **prepared_kwargs)

        start_time = time.monotonic()
        attempt_count: int = 0
        final_outcome: Union[requests.Response, Exception, None] = None

        try:
            final_outcome, attempt_count = self._execute_request_with_retry(method, final_url, make_request, handle_response)  # Pass handle_response
            return final_outcome

        except HTTPError as e:
            final_outcome = e.response if e.response is not None else e
            self.http_logger.log_http_error(e, method=method, url=final_url)  # Log error details first
            self._handle_http_error(e)  # Then raise the appropriate exception

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
            self.http_logger.log_request_completion(start_time, method, final_url, attempt_count, final_outcome)  # Use new logger

    def _execute_request_with_retry(
        self, method: str, url: str, make_request_func: Callable[[], requests.Response], handle_response: bool  # Added handle_response back
    ) -> Tuple[Any, int]:  # Return type is processed/raw response or Exception
        result_tuple = cast(
            Tuple[Union[requests.Response, Exception], int],
            self.retry_handler.execute_with_retry(method, url, make_request_func, self.session_manager.session, self.session_manager.refresh_auth),
        )
        result, attempt_count = result_tuple

        if isinstance(result, requests.Response):
            response = result
            self.http_logger.log_response_details(method, url, response)  # Use new logger

            processed_or_raw_response = self._handle_request_response(response, True)  # Assume True for now, need handle_response here
            processed_or_raw_response = self._handle_request_response(response, handle_response)  # Use passed handle_response
            return processed_or_raw_response, attempt_count

        elif isinstance(result, Exception):
            raise result
        else:
            raise CrudClientError(f"Unexpected result type from retry handler: {type(result).__name__}")

    # Logging methods removed, now handled by HttpLifecycleLogger

    def _handle_http_error(self, e: HTTPError) -> None:
        # Logging is now handled by self.http_logger.log_http_error before this method is called
        response = e.response
        request = e.request

        if response is not None:  # Request might still be None in rare cases
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
                request=request,  # Pass request if available
                response=response,
            ) from e
        else:
            # If response is None, raise a generic APIError
            # Logging of this case is handled by log_http_error
            raise APIError(message=f"HTTP error occurred without a response: {e}", request=request, response=None) from e  # Pass request if available

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
