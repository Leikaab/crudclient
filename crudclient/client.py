import logging
from typing import Any, Dict, Optional, Tuple, Union

import requests

from .config import ClientConfig
from .exceptions import ConfigurationError, ForbiddenError
from .http.client import HttpClient
from .types import RawResponseSimple

log = logging.getLogger(__name__)


class Client:

    def __init__(self, config: Union[ClientConfig, Dict[str, Any]]) -> None:
        log.info("Initializing Client and processing configuration...")
        if not isinstance(config, (ClientConfig, dict)):
            message = f"Invalid config type provided: expected ClientConfig or dict, got {type(config).__name__}."
            log.error(message)
            raise ConfigurationError(message)
        if isinstance(config, dict):
            try:
                config = ClientConfig(**config)
            except (TypeError, ValueError) as e:  # Catch ValueError too for Pydantic validation
                log.error("Configuration validation failed when creating ClientConfig from dict: %s", e, exc_info=True)
                raise ConfigurationError(f"Invalid configuration dictionary provided: {e}") from e

        assert isinstance(config, ClientConfig)
        self.config = config

        try:
            self.base_url = str(self.config.base_url)  # Ensure it's a string after validation
        except ValueError as e:
            log.error("Configuration validation failed for base_url: %s", e, exc_info=True)
            raise ConfigurationError(f"Invalid base_url configuration: {e}") from e

        self.http_client = HttpClient(self.config)
        log.info(
            "Client configuration processed successfully. Base URL: %s, Log Request Body: %s, Log Response Body: %s",
            self.base_url,
            self.config.log_request_body,
            self.config.log_response_body,
        )

        self._session = self.http_client.session_manager.session

    def _setup_auth(self) -> None:
        self.http_client.session_manager.refresh_auth()

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> RawResponseSimple:
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if params is not None and not isinstance(params, dict):
            raise TypeError(f"params must be a dictionary or None, got {type(params).__name__}")

        try:
            raw_response = self.http_client.request_raw("GET", endpoint, params=params)
        except ForbiddenError as e:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            kwargs = {"params": params} if params else {}
            assert e.response is not None  # Ensure response exists for retry logic
            # Attempt retry. If it doesn't happen or fails, _maybe_retry_after_403 returns the original response.
            raw_response = self._maybe_retry_after_403("GET", url, kwargs, e.response)
            # If the status code is still 403 after attempting retry, re-raise the original error.
            if raw_response.status_code == 403:
                raise e
            # Otherwise, the retry was successful (or wasn't needed), proceed with the response

        return self._handle_response(raw_response)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")

        try:
            raw_response = self.http_client.request_raw("POST", endpoint, data=data, json=json, files=files)
        except ForbiddenError as e:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            kwargs = {}
            if data:
                kwargs["data"] = data
            if json:
                kwargs["json"] = json
            if files:
                kwargs["files"] = files
            assert e.response is not None  # Ensure response exists for retry logic
            raw_response = self._maybe_retry_after_403("POST", url, kwargs, e.response)
            if raw_response.status_code == 403:
                raise e

        return self._handle_response(raw_response)

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")

        try:
            raw_response = self.http_client.request_raw("PUT", endpoint, data=data, json=json, files=files)
        except ForbiddenError as e:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            kwargs = {}
            if data:
                kwargs["data"] = data
            if json:
                kwargs["json"] = json
            if files:
                kwargs["files"] = files
            assert e.response is not None  # Ensure response exists for retry logic
            raw_response = self._maybe_retry_after_403("PUT", url, kwargs, e.response)
            if raw_response.status_code == 403:
                raise e

        return self._handle_response(raw_response)

    def delete(self, endpoint: str, **kwargs: Any) -> RawResponseSimple:
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        try:
            # Capture original kwargs for potential retry
            request_kwargs = kwargs.copy()
            raw_response = self.http_client.request_raw("DELETE", endpoint, **request_kwargs)
        except ForbiddenError as e:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            # Use the captured kwargs for the retry call
            assert e.response is not None  # Ensure response exists for retry logic
            raw_response = self._maybe_retry_after_403("DELETE", url, request_kwargs, e.response)
            if raw_response.status_code == 403:
                raise e

        return self._handle_response(raw_response)

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        if not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string, got {type(endpoint).__name__}")

        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")

        try:
            raw_response = self.http_client.request_raw("PATCH", endpoint, data=data, json=json, files=files)
        except ForbiddenError as e:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            kwargs = {}
            if data:
                kwargs["data"] = data
            if json:
                kwargs["json"] = json
            if files:
                kwargs["files"] = files
            assert e.response is not None  # Ensure response exists for retry logic
            raw_response = self._maybe_retry_after_403("PATCH", url, kwargs, e.response)
            if raw_response.status_code == 403:
                raise e

        return self._handle_response(raw_response)

    def _request(
        self, method: str, endpoint: Optional[str] = None, url: Optional[str] = None, handle_response: bool = True, **kwargs: Any
    ) -> Union[RawResponseSimple, requests.Response]:
        if not isinstance(method, str):
            raise TypeError(f"method must be a string, got {type(method).__name__}")

        if endpoint is not None and not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string or None, got {type(endpoint).__name__}")

        if url is not None and not isinstance(url, str):
            raise TypeError(f"url must be a string or None, got {type(url).__name__}")

        if not isinstance(handle_response, bool):
            raise TypeError(f"handle_response must be a boolean, got {type(handle_response).__name__}")
        return self.http_client._request(method, endpoint, url, handle_response, **kwargs)

    def close(self) -> None:
        self.http_client.close()
        log.debug("Client closed.")

    @property
    def session(self) -> requests.Session:
        if not hasattr(self._session, "is_closed"):
            setattr(self._session.__class__, "is_closed", property(lambda s: getattr(self.http_client.session_manager, "is_closed", False)))
        return self._session

    def _prepare_data(
        self, data: Optional[Dict[str, Any]] = None, json: Optional[Any] = None, files: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, str], Dict[str, Any]]:
        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")
        headers = {}
        request_kwargs = {}

        if json is not None:
            headers["Content-Type"] = "application/json"
            request_kwargs["json"] = json
        elif files is not None:
            headers["Content-Type"] = "multipart/form-data"
            request_kwargs["files"] = files
            if data is not None:
                request_kwargs["data"] = data
        elif data is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            request_kwargs["data"] = data

        return headers, request_kwargs

    def _maybe_retry_after_403(self, method: str, url: str, kwargs: Dict[str, Any], response: requests.Response) -> requests.Response:
        if not isinstance(method, str):
            raise TypeError(f"method must be a string, got {type(method).__name__}")

        if not isinstance(url, str):
            raise TypeError(f"url must be a string, got {type(url).__name__}")

        if not isinstance(kwargs, dict):
            raise TypeError(f"kwargs must be a dictionary, got {type(kwargs).__name__}")

        if (
            not isinstance(response, requests.Response)
            and not hasattr(response, "_mock_spec")
            and requests.Response not in getattr(response, "_mock_spec", [])
        ):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        if response.status_code != 403:
            return response

        if not self.config.should_retry_on_403():
            return response

        log.debug("403 Forbidden received. Attempting retry via config handler.")
        self.config.handle_403_retry(self)
        self._setup_auth()
        retry_response = self._session.request(method, url, **kwargs)
        return retry_response

    def _handle_response(self, response: requests.Response) -> RawResponseSimple:
        if (
            not isinstance(response, requests.Response)
            and not hasattr(response, "_mock_spec")
            and requests.Response not in getattr(response, "_mock_spec", [])
        ):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")

        try:
            return self.http_client.response_handler.handle_response(response)
        except requests.HTTPError:
            self._handle_error_response(response)
            return None  # Should not be reached, but satisfies type checker

    def _handle_error_response(self, response: requests.Response) -> None:
        if (
            not isinstance(response, requests.Response)
            and not hasattr(response, "_mock_spec")
            and requests.Response not in getattr(response, "_mock_spec", [])
        ):
            raise TypeError(f"response must be a requests.Response object, got {type(response).__name__}")
        self.http_client.error_handler.handle_error_response(response)
