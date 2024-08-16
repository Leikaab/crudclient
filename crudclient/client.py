import logging
from typing import Any, Dict, Optional, Union

import requests

from .config import ClientConfig
from .runtime_type_checkers import _assert_type

# Set up logging
logger = logging.getLogger(__name__)


class Client:
    def __init__(self, config: ClientConfig | Dict[str, Any]) -> None:
        # Validate and set up the config
        _assert_type("config", config, (ClientConfig, dict), logger)
        if isinstance(config, dict):
            config = ClientConfig(**config)

        assert isinstance(config, ClientConfig)  # for mypy
        self.config: ClientConfig = config

        # Set up the requests session
        self.session = requests.Session()

        # Set up authentication
        self._setup_auth()

        # Set up default headers, if any
        if self.config.headers:
            self.session.headers.update(self.config.headers)

        # Set base URL for the API
        self.base_url = self.config.base_url

        # Set up retries and timeouts
        self._setup_retries_and_timeouts()

    # Temporary function to do auth setup
    def _setup_auth(self) -> None:
        auth = self.config.auth()
        if auth is not None:
            if isinstance(auth, dict):
                self.session.headers.update(auth)
            elif isinstance(auth, tuple) and len(auth) == 2:
                self.session.auth = auth
            elif callable(auth):
                auth(self.session)

    def _setup_retries_and_timeouts(self) -> None:
        """
        This function sets up the retries and timeouts for the requests session. It retrieves the number of retries and timeout duration from the config. If the number of retries is not specified in the config, it defaults to 3. If the timeout duration is not specified in the config, it defaults to 5.
        The function creates an HTTPAdapter with the specified number of retries and mounts it to both 'http://' and 'https://' URLs in the session. It also sets the timeout duration for the session.
        Parameters:
        - None
        Returns:
        - None

        """
        retries = self.config.retries or 3
        timeout = self.config.timeout or 5

        # Create an HTTPAdapter with the specified number of retries
        adapter = requests.adapters.HTTPAdapter(max_retries=retries)

        # Mount the adapter to both 'http://' and 'https://' URLs in the session
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set the timeout duration for the session
        self.timeout = timeout

    def _set_content_type_header(self, content_type: str) -> None:
        self.session.headers["Content-Type"] = content_type

    def _prepare_data(
        self, data: Optional[Dict[str, Any]] = None, json: Optional[Any] = None, files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if json is not None:
            self._set_content_type_header("application/json")
            return {"json": json}
        elif files is not None:
            self._set_content_type_header("multipart/form-data")
            return {"files": files, "data": data}
        elif data is not None:
            self._set_content_type_header("application/x-www-form-urlencoded")
            return {"data": data}
        return {}

    def _handle_response(self, response: requests.Response) -> Union[Dict[str, Any], bytes, str]:
        if not response.ok:
            self._handle_error_response(response)

        content_type = response.headers.get("Content-Type", "")

        if "application/json" in content_type:
            return response.json()
        elif "application/octet-stream" in content_type or "multipart/form-data" in content_type:
            return response.content
        else:
            return response.text

    def _handle_error_response(self, response: requests.Response) -> None:
        try:
            error_data = response.json()
        except ValueError:
            logger.warning("Failed to parse JSON response.")
            error_data = response.text

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            logger.error(f"HTTP error occurred: {response.status_code}, {error_data}")
            raise e

        raise requests.RequestException(f"Request failed with status code {response.status_code}, {error_data}")

    def _request(self, method: str, endpoint: str | None = None, url: str | None = None, **kwargs) -> Any:

        if url is None:
            if endpoint is None:
                raise ValueError("Either 'endpoint' or 'url' must be provided.")
            url = f"{self.config.base_url}/{endpoint.lstrip('/')}"

        logger.debug(f"Making {method} request to {url} with params: {kwargs}")
        response: requests.Response = self.session.request(method, url, **kwargs)
        return self._handle_response(response)

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Union[Dict[str, Any], bytes, str]:
        return self._request("GET", endpoint, params=params)

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], bytes, str]:
        prepared_data = self._prepare_data(data, json, files)
        return self._request("POST", endpoint, **prepared_data)

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], bytes, str]:
        prepared_data = self._prepare_data(data, json, files)
        return self._request("PUT", endpoint, **prepared_data)

    def delete(self, endpoint: str, **kwargs: Any) -> Union[Dict[str, Any], bytes, str]:
        return self._request("DELETE", endpoint, **kwargs)

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], bytes, str]:
        prepared_data = self._prepare_data(data, json, files)
        return self._request("PATCH", endpoint, **prepared_data)

    def close(self) -> None:
        self.session.close()
        logger.debug("Session closed.")
