import logging
from typing import Any, Dict, Optional

import requests

from ..config import ClientConfig
from ..types import RawResponseSimple
from .errors import ErrorHandler
from .request import RequestFormatter
from .response import ResponseHandler
from .retry import RetryHandler
from .session import SessionManager

# Set up logging
logger = logging.getLogger(__name__)


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
        self.request_formatter = request_formatter or RequestFormatter()
        self.response_handler = response_handler or ResponseHandler()
        self.error_handler = error_handler or ErrorHandler()
        self.retry_handler = retry_handler or RetryHandler(max_retries=config.retries)

    def _validate_request_params(self, method: str, endpoint: Optional[str], url: Optional[str], handle_response: bool) -> None:
        if not isinstance(method, str):
            raise TypeError(f"method must be a string, got {type(method).__name__}")
        if endpoint is not None and not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string or None, got {type(endpoint).__name__}")
        if url is not None and not isinstance(url, str):
            raise TypeError(f"url must be a string or None, got {type(url).__name__}")
        if not isinstance(handle_response, bool):
            raise TypeError(f"handle_response must be a boolean, got {type(handle_response).__name__}")

    def _build_request_url(self, endpoint: Optional[str], url: Optional[str]) -> str:
        if url is not None:
            return url
        if endpoint is None:
            raise ValueError("Either 'endpoint' or 'url' must be provided.")
        # Construct the URL from the base URL and endpoint
        return f"{self.config.base_url}/{endpoint.lstrip('/')}"

    def _prepare_auth_params(self, kwargs: Dict[str, Any]) -> None:
        auth_params: Dict[str, Any] = {}
        if (
            hasattr(self.config, "auth_strategy")
            and self.config.auth_strategy is not None
            and hasattr(self.config.auth_strategy, "prepare_request_params")
        ):
            auth_params = self.config.auth_strategy.prepare_request_params()
            if not isinstance(auth_params, dict):
                raise TypeError(f"Auth strategy's prepare_request_params must return a dictionary, " f"got {type(auth_params).__name__}")

        if not auth_params:
            return  # No auth params to merge

        # Ensure 'params' exists in kwargs and is a dictionary
        if "params" not in kwargs or kwargs["params"] is None:
            kwargs["params"] = {}
        elif not isinstance(kwargs["params"], dict):
            logger.warning(
                f"Request 'params' has unexpected type: {type(kwargs['params']).__name__}. " f"Attempting conversion to dict for auth param merging."
            )
            try:
                kwargs["params"] = dict(kwargs["params"])
            except (TypeError, ValueError) as e:
                logger.error(f"Could not convert 'params' to dict: {e}. Auth params might be lost.")
                kwargs["params"] = {}  # Fallback

        # Merge auth params, prioritizing auth params
        if isinstance(kwargs["params"], dict):
            kwargs["params"].update(auth_params)
        else:
            # This case should ideally not be reached
            logger.error("Failed to merge auth params: 'params' is not a dictionary.")

    def _execute_request_with_retry(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        def make_request() -> requests.Response:
            return self.session_manager.session.request(method, url, timeout=self.session_manager.timeout, **kwargs)

        return self.retry_handler.execute_with_retry(make_request, self.session_manager.session, self.session_manager.refresh_auth)

    def _handle_request_response(self, response: requests.Response, handle_response: bool) -> Any:
        if not handle_response:
            return response
        try:
            return self.response_handler.handle_response(response)
        except requests.HTTPError as e:
            # Handle error that occurred during response processing (e.g., bad JSON)
            # or if handle_response itself raised an HTTPError
            return self._handle_request_error(e, handle_response=True)  # Force handling as error

    def _handle_request_error(self, error: requests.HTTPError, handle_response: bool) -> Any:
        response = error.response
        if response is None:  # Should not happen with HTTPError, but safeguard
            raise error  # Re-raise original error if no response attached

        self.error_handler.handle_error_response(response)
        # If handle_error_response doesn't raise, return processed or raw response
        return self.response_handler.handle_response(response) if handle_response else response

    def _request(self, method: str, endpoint: Optional[str] = None, url: Optional[str] = None, handle_response: bool = True, **kwargs: Any) -> Any:
        self._validate_request_params(method, endpoint, url, handle_response)
        final_url = self._build_request_url(endpoint, url)
        self._prepare_auth_params(kwargs)  # Modifies kwargs in-place

        logger.debug(f"Making {method} request to {final_url} with final params: {kwargs.get('params')}")

        try:
            response = self._execute_request_with_retry(method, final_url, **kwargs)
            return self._handle_request_response(response, handle_response)
        except requests.HTTPError as e:
            return self._handle_request_error(e, handle_response)

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> RawResponseSimple:
        # Runtime type checks
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if params is not None and not isinstance(params, dict):
            raise TypeError(f"params must be a dictionary or None, got {type(params).__name__}")
        return self._request("GET", endpoint=endpoint, params=params)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        # Runtime type checks
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")
        prepared_data = self._prepare_data(data, json, files)
        return self._request("POST", endpoint=endpoint, **prepared_data)

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        # Runtime type checks
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")
        prepared_data = self._prepare_data(data, json, files)
        return self._request("PUT", endpoint=endpoint, **prepared_data)

    def delete(self, endpoint: str, **kwargs: Any) -> RawResponseSimple:
        # Runtime type check
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")
        return self._request("DELETE", endpoint=endpoint, **kwargs)

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        # Runtime type checks
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")
        prepared_data = self._prepare_data(data, json, files)
        return self._request("PATCH", endpoint=endpoint, **prepared_data)

    def _prepare_data(
        self,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        # Runtime type checks
        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")
        prepared_data, headers = self.request_formatter.prepare_data(data, json, files)

        # If headers were returned, update the session headers
        if headers:
            self.session_manager.update_headers(headers)

        return prepared_data

    def request_raw(self, method: str, endpoint: Optional[str] = None, url: Optional[str] = None, **kwargs: Any) -> requests.Response:
        # Runtime type checks
        if not isinstance(method, str):
            raise TypeError(f"method must be a string, got {type(method).__name__}")

        if endpoint is not None and not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string or None, got {type(endpoint).__name__}")

        if url is not None and not isinstance(url, str):
            raise TypeError(f"url must be a string or None, got {type(url).__name__}")
        return self._request(method, endpoint, url, handle_response=False, **kwargs)

    def close(self) -> None:
        self.session_manager.close()
        logger.debug("HttpClient closed.")
