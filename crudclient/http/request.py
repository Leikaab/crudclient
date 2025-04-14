import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from ..exceptions import CrudClientError  # Import base exception
from .utils import redact_sensitive_headers  # Correct: utils is sibling # noqa: F401

# Set up logging
if TYPE_CHECKING:
    from ..auth.base import AuthStrategy  # Use the correct class name
    from ..config import ClientConfig  # Type hint for config
logger = logging.getLogger(__name__)


class RequestFormatter:
    def __init__(self, config: Optional["ClientConfig"] = None):
        # Store config if provided, needed for base_url and auth_strategy
        self._config = config

    def validate_request_params(self, method: str, endpoint: Optional[str], url: Optional[str]) -> None:
        # Docstring moved to .pyi
        if not isinstance(method, str):
            raise TypeError(f"method must be a string, got {type(method).__name__}")
        if endpoint is not None and not isinstance(endpoint, str):
            raise TypeError(f"endpoint must be a string or None, got {type(endpoint).__name__}")
        if url is not None and not isinstance(url, str):
            raise TypeError(f"url must be a string or None, got {type(url).__name__}")
        if url is None and endpoint is None:
            raise ValueError("Either 'endpoint' or 'url' must be provided.")

    def build_request_url(self, endpoint: Optional[str], url: Optional[str]) -> str:
        # Docstring moved to .pyi
        if url is not None:
            return url
        # Endpoint is guaranteed non-None by validate_request_params if url is None
        if self._config is None or self._config.base_url is None:
            raise CrudClientError("Cannot build URL: RequestFormatter requires ClientConfig with base_url.")
        # Ensure endpoint is treated as str after validation
        endpoint_str = endpoint if endpoint is not None else ""
        return f"{self._config.base_url}/{endpoint_str.lstrip('/')}"

    def prepare_auth_params(self, kwargs: Dict[str, Any]) -> None:
        # Docstring moved to .pyi
        if self._config is None or self._config.auth_strategy is None:
            return  # No auth strategy configured

        auth_strategy: "AuthStrategy" = self._config.auth_strategy
        if not hasattr(auth_strategy, "prepare_request_params"):
            return  # Strategy doesn't support param preparation

        auth_params: Dict[str, Any] = auth_strategy.prepare_request_params()
        if not isinstance(auth_params, dict):
            raise TypeError(f"Auth strategy's prepare_request_params must return a dictionary, " f"got {type(auth_params).__name__}")

        if not auth_params:
            return

        # Ensure kwargs['params'] exists and is a dictionary for merging.
        # Handle cases where 'params' is missing, None, or not a dict.
        params = kwargs.get("params")
        if not isinstance(params, dict):
            if params is not None:
                logger.warning(f"Request 'params' has unexpected type: {type(params).__name__}. Overwriting with auth params.")
            params = {}  # Initialize as empty dict if None or not a dict
            kwargs["params"] = params

        # Merge auth params, logging potential overwrites
        for key, value in auth_params.items():
            if key in params:
                logger.debug(f"Auth param '{key}' overwrites existing request param.")
            params[key] = value
        logger.debug("Merged auth params into request params: %s", params)

    def prepare_data(
        self, data: Optional[Dict[str, Any]] = None, json: Optional[Any] = None, files: Optional[Dict[str, Any]] = None
    ) -> Tuple[Dict[str, Any], Dict[str, str]]:
        # Runtime type checks for critical parameters
        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")

        if files is not None and not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary or None, got {type(files).__name__}")

        if json is not None:
            return self.prepare_json(json)
        elif files is not None:
            return self.prepare_multipart(files, data)
        elif data is not None:
            return self.prepare_form_data(data)
        return {}, {}

    def prepare_json(self, json_data: Any) -> Tuple[Dict[str, Any], Dict[str, str]]:
        headers = self.get_content_type_header("application/json")
        return {"json": json_data}, headers

    def prepare_form_data(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, str]]:
        # Runtime type check
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary, got {type(data).__name__}")
        headers = self.get_content_type_header("application/x-www-form-urlencoded")
        return {"data": data}, headers

    def prepare_multipart(self, files: Dict[str, Any], data: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, str]]:
        # Runtime type checks
        if not isinstance(files, dict):
            raise TypeError(f"files must be a dictionary, got {type(files).__name__}")

        if data is not None and not isinstance(data, dict):
            raise TypeError(f"data must be a dictionary or None, got {type(data).__name__}")
        headers = self.get_content_type_header("multipart/form-data")
        result = {"files": files}
        if data is not None:
            result["data"] = data
        return result, headers

    def get_content_type_header(self, content_type: str) -> Dict[str, str]:
        # Runtime type check
        if not isinstance(content_type, str):
            raise TypeError(f"content_type must be a string, got {type(content_type).__name__}")
        return {"Content-Type": content_type}

    def format_request(self, method: str, endpoint: Optional[str], url: Optional[str], **kwargs: Any) -> Tuple[str, Dict[str, Any]]:
        # Docstring moved to .pyi
        self.validate_request_params(method, endpoint, url)
        final_url = self.build_request_url(endpoint, url)
        self.prepare_auth_params(kwargs)  # Modifies kwargs in-place

        # Prepare data/json/files payload using existing methods
        data_kwargs, headers = self.prepare_data(data=kwargs.pop("data", None), json=kwargs.pop("json", None), files=kwargs.pop("files", None))
        kwargs.update(data_kwargs)  # Add 'json', 'data', or 'files' back to kwargs

        # Merge content-type headers if any were generated
        if headers:
            existing_headers = kwargs.setdefault("headers", {})
            if not isinstance(existing_headers, dict):
                logger.warning("Overwriting non-dict 'headers' with Content-Type header.")
                existing_headers = {}
            existing_headers.update(headers)
            kwargs["headers"] = existing_headers

        return final_url, kwargs
