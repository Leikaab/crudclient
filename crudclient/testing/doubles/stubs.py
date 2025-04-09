"""
Configurable stub implementations for Client, API, and CRUD interfaces.

This module provides sophisticated stub implementations that can be used in testing
to simulate the behavior of real components with configurable responses and behaviors.
The stubs support:

- Customizable response mapping based on endpoint patterns
- Simulated network latency and error rates
- In-memory data store for CRUD operations
- Request history tracking
- Pre and post operation hooks
- Realistic default behaviors
"""

import copy
import json
import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Type, Union

from crudclient.api import API
from crudclient.client import Client
from crudclient.config import ClientConfig


class Response:
    """
    Base Response class for testing.

    This abstract base class defines the interface for response objects
    used in testing. It mirrors the essential properties and methods of
    HTTP response objects like those from the requests library.
    """

    def __init__(self):
        """Initialize the response."""

    @property
    def status_code(self) -> int:
        """
        Get the HTTP status code.

        Returns:
            int: The HTTP status code
        """
        raise NotImplementedError

    @property
    def content(self) -> bytes:
        """
        Get the raw content as bytes.

        Returns:
            bytes: The raw content
        """
        raise NotImplementedError

    @property
    def text(self) -> str:
        """
        Get the content as text.

        Returns:
            str: The content as text
        """
        raise NotImplementedError

    @property
    def headers(self) -> Dict[str, str]:
        """
        Get the response headers.

        Returns:
            Dict[str, str]: The response headers
        """
        raise NotImplementedError

    def json(self) -> Any:
        """
        Parse the response content as JSON.

        Returns:
            Any: The parsed JSON data

        Raises:
            ValueError: If the response content is not valid JSON
        """
        raise NotImplementedError

    def raise_for_status(self) -> None:
        """
        Raise an exception if the response status code indicates an error.

        Raises:
            HTTPError: If the response status code is 4XX or 5XX
        """
        raise NotImplementedError


class CrudBase:
    """
    Base CRUD class for testing.

    This abstract base class defines the interface for CRUD operations
    used in testing. It provides a simplified version of the crudclient
    CRUD interface with the essential methods.
    """

    def __init__(
        self,
        client: Optional[Client] = None,
        endpoint: str = '',
        model: Optional[Type[Any]] = None
    ):
        """
        Initialize the CRUD base.

        Args:
            client: Client instance for making API requests
            endpoint: API endpoint path
            model: Model class for converting response data
        """
        self.client = client
        self.endpoint = endpoint
        self.model = model

    def list(self, **kwargs: Any) -> List[Any]:
        """
        List resources.

        Args:
            **kwargs: Query parameters and options

        Returns:
            List[Any]: List of resources
        """
        raise NotImplementedError

    def get(self, id: Any, **kwargs: Any) -> Any:
        """
        Get a resource by ID.

        Args:
            id: Resource ID
            **kwargs: Additional options

        Returns:
            Any: Resource or None if not found
        """
        raise NotImplementedError

    def create(self, data: Any, **kwargs: Any) -> Any:
        """
        Create a resource.

        Args:
            data: Resource data
            **kwargs: Additional options

        Returns:
            Any: Created resource
        """
        raise NotImplementedError

    def update(self, id: Any, data: Any, **kwargs: Any) -> Any:
        """
        Update a resource.

        Args:
            id: Resource ID
            data: Resource data
            **kwargs: Additional options

        Returns:
            Any: Updated resource or None if not found
        """
        raise NotImplementedError

    def delete(self, id: Any, **kwargs: Any) -> bool:
        """
        Delete a resource.

        Args:
            id: Resource ID
            **kwargs: Additional options

        Returns:
            bool: True if deleted, False if not found
        """
        raise NotImplementedError


class StubResponse(Response):
    """
    Configurable stub implementation of the Response class.

    This class provides a flexible response object for testing with support for:
    - Custom status codes
    - Various content types (string, bytes, dict, list)
    - Custom headers
    - Simulated request timing
    - Automatic JSON handling
    """

    def __init__(
        self,
        status_code: int = 200,
        content: Optional[Union[str, bytes, Dict[str, Any], List[Any]]] = None,
        headers: Optional[Dict[str, str]] = None,
        encoding: str = 'utf-8',
        elapsed: Optional[timedelta] = None
    ):
        """
        Initialize the stub response with configurable properties.

        Args:
            status_code: HTTP status code (default: 200)
            content: Response content (string, bytes, dict, or list)
            headers: Response headers
            encoding: Content encoding (default: utf-8)
            elapsed: Simulated request time (default: 50ms)
        """
        super().__init__()
        self._status_code = status_code
        self._headers = headers or {}
        self._encoding = encoding
        self._elapsed = elapsed or timedelta(milliseconds=50)

        # Handle different content types
        if content is None:
            self._content = b''
            self._text = ''
            self._json_data = None
        elif isinstance(content, (dict, list)):
            self._json_data = content
            self._text = json.dumps(content)
            self._content = self._text.encode(encoding)
        elif isinstance(content, str):
            self._text = content
            self._content = content.encode(encoding)
            try:
                self._json_data = json.loads(content)
            except json.JSONDecodeError:
                self._json_data = None
        elif isinstance(content, bytes):
            self._content = content
            self._text = content.decode(encoding, errors='replace')
            try:
                self._json_data = json.loads(self._text)
            except json.JSONDecodeError:
                self._json_data = None
        else:
            raise TypeError(f"Unsupported content type: {type(content)}")

    @property
    def status_code(self) -> int:
        """
        Get the HTTP status code.

        Returns:
            int: The HTTP status code
        """
        return self._status_code

    @property
    def content(self) -> bytes:
        """
        Get the raw content as bytes.

        Returns:
            bytes: The raw content
        """
        return self._content

    @property
    def text(self) -> str:
        """
        Get the content as text.

        Returns:
            str: The content as text
        """
        return self._text

    @property
    def headers(self) -> Dict[str, str]:
        """
        Get the response headers.

        Returns:
            Dict[str, str]: The response headers
        """
        return self._headers

    @property
    def encoding(self) -> str:
        """
        Get the response encoding.

        Returns:
            str: The encoding
        """
        return self._encoding

    @property
    def elapsed(self) -> timedelta:
        """
        Get the time elapsed for the request.

        Returns:
            timedelta: The elapsed time
        """
        return self._elapsed

    def json(self) -> Any:
        """
        Parse the response content as JSON.

        Returns:
            Any: The parsed JSON data

        Raises:
            ValueError: If the response content is not valid JSON
        """
        if self._json_data is None:
            try:
                self._json_data = json.loads(self._text)
                return self._json_data
            except json.JSONDecodeError:
                raise ValueError("Response content is not valid JSON")
        return self._json_data

    def raise_for_status(self) -> None:
        """
        Raise an exception if the response status code indicates an error.

        Raises:
            HTTPError: If the response status code is 4XX or 5XX
        """
        import requests
        if 400 <= self._status_code < 600:
            # Create a simple error message
            error_msg = f"HTTP error {self._status_code}"

            # Raise HTTPError directly without trying to set response attributes
            raise requests.HTTPError(error_msg)


class StubClient(Client):
    """
    Configurable stub implementation of the Client class.

    This class provides a flexible client for testing with support for:
    - Pattern-based response mapping
    - Default responses for unmatched endpoints
    - Simulated network latency
    - Configurable error rates
    - Request history tracking
    - Support for callable response generators
    """

    def configure_get(self, response=None, handler=None):
        """
        Configure the response for GET requests.

        Args:
            response: The response to return for GET requests
            handler: A function that takes the endpoint and params and returns a response
        """
        if handler:
            # Store the handler with a pattern that matches GET requests
            self.add_response("^GET:", handler)
        elif response:
            # Store the response with a pattern that matches GET requests
            self.add_response("^GET:", response)

    def configure_post(self, response=None, handler=None):
        """
        Configure the response for POST requests.

        Args:
            response: The response to return for POST requests
            handler: A function that takes the endpoint, data, and params and returns a response
        """
        if handler:
            # Store the handler with a pattern that matches POST requests
            self.add_response("^POST:", handler)
        elif response:
            # Store the response with a pattern that matches POST requests
            self.add_response("^POST:", response)

    def __init__(
        self,
        config: Union[ClientConfig, Dict[str, Any]],
        default_response: Optional[Union[Dict[str, Any], List[Dict[str, Any]], str]] = None,
        response_map: Optional[Dict[str, Any]] = None,
        error_rate: float = 0.0,
        latency_ms: int = 0
    ):
        """
        Initialize the stub client with configurable behaviors.

        Args:
            config: Client configuration(ClientConfig or dict)
            default_response: Default response for unmatched endpoints
            response_map: Map of endpoint patterns to responses
            error_rate: Probability of simulating network errors(0.0 to 1.0)
            latency_ms: Simulated network latency in milliseconds
        """
        super().__init__(config)

        # Default response
        if default_response is None:
            self._default_response = {"message": "Stub response"}
        else:
            self._default_response = default_response

        # Response map (endpoint pattern -> response)
        self._response_map = response_map or {}

        # Error simulation
        self._error_rate = max(0.0, min(1.0, error_rate))
        self._latency_ms = max(0, latency_ms)

        # Request history
        self._request_history: List[Dict[str, Any]] = []

    def _request(
        self,
        method: str,
        endpoint: Optional[str] = None,
        url: Optional[str] = None,
        handle_response: bool = True,
        **kwargs: Any
    ) -> str:
        """
        Stub implementation of the _request method.

        This method simulates HTTP requests with configurable responses,
        latency, and error rates.

        Args:
            method: HTTP method(GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            url: Full URL(alternative to endpoint)
            handle_response: Whether to handle errors automatically
            **kwargs: Additional request parameters

        Returns:
            str: Response content as a string

        Raises:
            Exception: If error simulation is enabled and triggers
        """
        import random
        import time

        # Determine the full URL
        if url is None and endpoint is not None:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
        elif url is None:
            url = self.base_url

        # Record the request
        request_record = {
            'method': method,
            'url': url,
            'endpoint': endpoint,
            'kwargs': kwargs,
            'timestamp': datetime.now().isoformat()
        }
        self._request_history.append(request_record)

        # Simulate latency
        if self._latency_ms > 0:
            time.sleep(self._latency_ms / 1000.0)

        # Simulate errors
        if self._error_rate > 0 and random.random() < self._error_rate:
            import requests
            error = requests.ConnectionError("Simulated network error")
            if handle_response:
                raise error
            return json.dumps({"error": "Simulated network error"})

        # Find a matching response in the map
        response = None
        method_prefix = f"{method}:"

        # First try to find a method-specific pattern
        for pattern, resp in self._response_map.items():
            if pattern.startswith("^") and pattern[1:].startswith(method_prefix):
                response = resp
                break

        # If no method-specific pattern found, try generic patterns
        if response is None:
            for pattern, resp in self._response_map.items():
                if not pattern.startswith("^") and re.search(pattern, url):
                    response = resp
                    break

        # Use default response if no match found
        if response is None:
            response = self._default_response

        # Handle callable responses
        if callable(response):
            # Extract the endpoint from the URL
            endpoint = endpoint or url.split('/')[-1]

            # For GET requests
            if method == "GET":
                params = kwargs.get("params", {})
                response = response(endpoint, params)
            # For POST requests
            elif method == "POST":
                data = kwargs.get("data", {})
                json_data = kwargs.get("json", {})
                params = kwargs.get("params", {})
                response = response(endpoint, data=data, json=json_data, params=params)
            # For other methods, pass all kwargs
            else:
                response = response(endpoint, **kwargs)

        # Convert response to string
        if isinstance(response, dict) or isinstance(response, list):
            response_str = json.dumps(response)
        elif isinstance(response, StubResponse):
            if response.status_code >= 400 and handle_response:
                response.raise_for_status()

            if hasattr(response, '_json_data') and response._json_data:
                response_str = json.dumps(response._json_data)
            else:
                response_str = response.text
                # Try to parse as JSON if it looks like JSON
                if response_str.strip().startswith('{') or response_str.strip().startswith('['):
                    try:
                        json.loads(response_str)  # Just to validate it's valid JSON
                    except json.JSONDecodeError:
                        pass  # Not valid JSON, leave as text
        else:
            response_str = str(response)

        return response_str

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Perform a GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            Any: Response data(parsed JSON or string)
        """
        import json as json_module
        response_str = self._request('GET', endpoint=endpoint, params=params)
        try:
            return json_module.loads(response_str)
        except json_module.JSONDecodeError:
            return response_str

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Perform a POST request.

        Args:
            endpoint: API endpoint path
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            Any: Response data(parsed JSON or string)
        """
        import json as json_module
        response_str = self._request('POST', endpoint=endpoint, data=data, json=json, files=files)
        try:
            return json_module.loads(response_str)
        except json_module.JSONDecodeError:
            return response_str

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Perform a PUT request.

        Args:
            endpoint: API endpoint path
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            Any: Response data(parsed JSON or string)
        """
        import json as json_module
        response_str = self._request('PUT', endpoint=endpoint, data=data, json=json, files=files)
        try:
            return json_module.loads(response_str)
        except json_module.JSONDecodeError:
            return response_str

    def delete(self, endpoint: str, **kwargs: Any) -> Any:
        """
        Perform a DELETE request.

        Args:
            endpoint: API endpoint path
            **kwargs: Additional request parameters

        Returns:
            Any: Response data(parsed JSON or string)
        """
        import json as json_module
        response_str = self._request('DELETE', endpoint=endpoint, **kwargs)
        try:
            return json_module.loads(response_str)
        except json_module.JSONDecodeError:
            return response_str

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Perform a PATCH request.

        Args:
            endpoint: API endpoint path
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            Any: Response data(parsed JSON or string)
        """
        import json as json_module
        response_str = self._request('PATCH', endpoint=endpoint, data=data, json=json, files=files)
        try:
            return json_module.loads(response_str)
        except json_module.JSONDecodeError:
            return response_str

    def get_request_history(self) -> List[Dict[str, Any]]:
        """
        Get the request history.

        Returns:
            List[Dict[str, Any]]: List of recorded requests
        """
        return self._request_history

    def clear_request_history(self) -> None:
        """
        Clear the request history.

        This is useful for resetting the state between tests.
        """
        self._request_history = []

    def add_response(self, pattern: str, response: Any) -> None:
        """
        Add a response to the response map.

        Args:
            pattern: Regex pattern to match against endpoints
            response: Response to return (dict, list, string, or callable)
        """
        self._response_map[pattern] = response

    def set_default_response(self, response: Any) -> None:
        """
        Set the default response for unmatched endpoints.

        Args:
            response: Default response(dict, list, string, or callable)
        """
        self._default_response = response

    def set_error_rate(self, error_rate: float) -> None:
        """
        Set the error rate for simulating network errors.

        Args:
            error_rate: Probability of errors(0.0 to 1.0)
        """
        self._error_rate = max(0.0, min(1.0, error_rate))

    def set_latency(self, latency_ms: int) -> None:
        """
        Set the simulated network latency.

        Args:
            latency_ms: Latency in milliseconds
        """
        self._latency_ms = max(0, latency_ms)


class StubCrud(CrudBase):
    """
    Configurable stub implementation of the CrudBase class.

    This class provides a flexible CRUD interface for testing with support for:
    - In-memory data store
    - Filtering, sorting, and pagination
    - Pre and post operation hooks
    - Automatic ID generation
    - Model conversion
    """

    def configure_list(self, response=None, handler=None):
        """
        Configure the response for list operations.

        Args:
            response: The response to return for list operations
            handler: A function that takes kwargs and returns a response
        """
        self._list_response = response
        self._list_handler = handler

    def configure_get(self, response=None, handler=None):
        """
        Configure the response for get operations.

        Args:
            response: The response to return for get operations
            handler: A function that takes the id and kwargs and returns a response
        """
        self._get_response = response
        self._get_handler = handler

    def configure_create(self, response=None, handler=None):
        """
        Configure the response for create operations.

        Args:
            response: The response to return for create operations
            handler: A function that takes the data and kwargs and returns a response
        """
        self._create_response = response
        self._create_handler = handler

    def __init__(
        self,
        client_or_name: Union[Client, str, None] = None,
        endpoint: str = '',
        model: Optional[Type[Any]] = None,
        default_data: Optional[Dict[str, Any]] = None,
        data_store: Optional[Dict[str, Dict[str, Any]]] = None
    ):
        """
        Initialize the stub CRUD with configurable behaviors.

        Args:
            client_or_name: Client instance for making API requests, or a name for the CRUD
            endpoint: API endpoint path
            model: Model class for converting response data
            default_data: Default data for new resources
            data_store: In - memory data store for CRUD operations
        """
        # Handle the case where the first argument is a string (name)
        if isinstance(client_or_name, str):
            client = None
            # If the first argument is a string, use it as the endpoint
            if not endpoint:
                endpoint = client_or_name
        else:
            client = client_or_name

        super().__init__(client, endpoint, model)

        # Default data for responses
        self._default_data = default_data or {"id": 1, "name": "Stub Resource"}

        # In-memory data store for CRUD operations
        self._data_store = data_store or {}

        # Next ID for auto-incrementing
        self._next_id = max([int(id) for id in self._data_store.keys()], default=0) + 1

        # Operation hooks
        self._before_list_hook: Optional[Callable] = None
        self._after_list_hook: Optional[Callable] = None
        self._before_get_hook: Optional[Callable] = None
        self._after_get_hook: Optional[Callable] = None
        self._before_create_hook: Optional[Callable] = None
        self._after_create_hook: Optional[Callable] = None
        self._before_update_hook: Optional[Callable] = None
        self._after_update_hook: Optional[Callable] = None
        self._before_delete_hook: Optional[Callable] = None
        self._after_delete_hook: Optional[Callable] = None

        # Configured responses and handlers
        self._list_response = None
        self._list_handler = None
        self._get_response = None
        self._get_handler = None
        self._create_response = None
        self._create_handler = None

    def list(self, **kwargs: Any) -> List[Any]:
        """
        List resources with support for filtering, sorting, and pagination.

        Args:
            **kwargs: Query parameters and options including:
                - filters: Dict of field - value pairs for filtering
                - sort_by: Field to sort by
                - sort_desc: Whether to sort in descending order
                - page: Page number(1 - based)
                - page_size: Number of items per page

        Returns:
            List[Any]: List of resources matching the criteria
        """
        # Call before hook
        if self._before_list_hook:
            self._before_list_hook(kwargs)

        # Use configured handler if available
        if self._list_handler:
            result = self._list_handler(**kwargs)
            # Convert to model instances if model is provided and result is a list of dicts
            if self.model and isinstance(result, list) and result and isinstance(result[0], dict):
                result = [self.model(**item) for item in result]
            return result

        # Use configured response if available
        if self._list_response is not None:
            return self._list_response

        # Apply filters
        filtered_data = list(self._data_store.values())

        for key, value in kwargs.items():
            if key in ('sort_by', 'sort_desc', 'page', 'page_size'):
                continue

            filtered_data = [item for item in filtered_data if item.get(key) == value]

        # Apply sorting
        sort_by = kwargs.get('sort_by')
        sort_desc = kwargs.get('sort_desc', False)

        if sort_by:
            filtered_data.sort(
                key=lambda x: x.get(sort_by, ''),
                reverse=sort_desc
            )

        # Apply pagination
        page = kwargs.get('page', 1)
        page_size = kwargs.get('page_size')

        if page_size:
            start = (page - 1) * page_size
            end = start + page_size
            filtered_data = filtered_data[start:end]

        # Convert to model instances if model is provided
        result = filtered_data
        if self.model:
            result = [self.model(**item) for item in filtered_data]

        # Call after hook
        if self._after_list_hook:
            result = self._after_list_hook(result, kwargs)

        return result

    def get(self, id: Any, **kwargs: Any) -> Any:
        """
        Get a resource by ID.

        Args:
            id: Resource ID
            **kwargs: Additional options

        Returns:
            Any: Resource or None if not found
        """
        # Call before hook
        if self._before_get_hook:
            self._before_get_hook(id, kwargs)

        # Use configured handler if available
        if self._get_handler:
            result = self._get_handler(id, **kwargs)
            # Convert to model instance if model is provided and result is a dict
            if self.model and isinstance(result, dict):
                result = self.model(**result)
            return result

        # Use configured response if available
        if self._get_response is not None:
            return self._get_response

        # Get the resource
        str_id = str(id)
        if str_id not in self._data_store:
            return None

        data = self._data_store[str_id]

        # Convert to model instance if model is provided
        result = data
        if self.model:
            result = self.model(**data)

        # Call after hook
        if self._after_get_hook:
            result = self._after_get_hook(result, id, kwargs)

        return result

    def create(self, data: Any, **kwargs: Any) -> Any:
        """
        Create a resource.

        Args:
            data: Resource data(dict or model instance)
            **kwargs: Additional options

        Returns:
            Any: Created resource
        """
        # Call before hook
        if self._before_create_hook:
            data = self._before_create_hook(data, kwargs)

        # Use configured handler if available
        if self._create_handler:
            result = self._create_handler(data, **kwargs)
            # Convert to model instance if model is provided and result is a dict
            if self.model and isinstance(result, dict):
                result = self.model(**result)
            return result

        # Use configured response if available
        if self._create_response is not None:
            return self._create_response

        # Convert model instance to dict if needed
        if hasattr(data, '__dict__'):
            data_dict = {k: v for k, v in data.__dict__.items() if not k.startswith('_')}
        else:
            data_dict = copy.deepcopy(data)

        # Generate ID if not provided
        if 'id' not in data_dict:
            data_dict['id'] = self._next_id
            self._next_id += 1

        # Store the resource
        str_id = str(data_dict['id'])
        self._data_store[str_id] = data_dict

        # Convert to model instance if model is provided
        result = data_dict
        if self.model:
            result = self.model(**data_dict)

        # Call after hook
        if self._after_create_hook:
            result = self._after_create_hook(result, kwargs)

        return result

    def update(self, id: Any, data: Any, **kwargs: Any) -> Any:
        """
        Update a resource.

        Args:
            id: Resource ID
            data: Resource data(dict or model instance)
            **kwargs: Additional options

        Returns:
            Any: Updated resource or None if not found
        """
        # Call before hook
        if self._before_update_hook:
            data = self._before_update_hook(id, data, kwargs)

        # Check if resource exists
        str_id = str(id)
        if str_id not in self._data_store:
            return None

        # Convert model instance to dict if needed
        if hasattr(data, '__dict__'):
            data_dict = {k: v for k, v in data.__dict__.items() if not k.startswith('_')}
        else:
            data_dict = copy.deepcopy(data)

        # Update the resource
        existing_data = self._data_store[str_id]
        updated_data = copy.deepcopy(existing_data)
        updated_data.update(data_dict)

        # Ensure ID is preserved
        updated_data['id'] = id

        # Store the updated resource
        self._data_store[str_id] = updated_data

        # Convert to model instance if model is provided
        result = updated_data
        if self.model:
            result = self.model(**updated_data)

        # Call after hook
        if self._after_update_hook:
            result = self._after_update_hook(result, id, kwargs)

        return result

    def delete(self, id: Any, **kwargs: Any) -> bool:
        """
        Delete a resource.

        Args:
            id: Resource ID
            **kwargs: Additional options

        Returns:
            bool: True if deleted, False if not found
        """
        # Call before hook
        if self._before_delete_hook:
            self._before_delete_hook(id, kwargs)

        # Check if resource exists
        str_id = str(id)
        if str_id not in self._data_store:
            return False

        # Delete the resource
        del self._data_store[str_id]

        # Call after hook
        if self._after_delete_hook:
            self._after_delete_hook(id, kwargs)

        return True

    def set_before_list_hook(self, hook: Callable) -> None:
        """
        Set the hook to call before list operations.

        Args:
            hook: Function to call before list operations
        """
        self._before_list_hook = hook

    def set_after_list_hook(self, hook: Callable) -> None:
        """
        Set the hook to call after list operations.

        Args:
            hook: Function to call after list operations
        """
        self._after_list_hook = hook

    def set_before_get_hook(self, hook: Callable) -> None:
        """
        Set the hook to call before get operations.

        Args:
            hook: Function to call before get operations
        """
        self._before_get_hook = hook

    def set_after_get_hook(self, hook: Callable) -> None:
        """
        Set the hook to call after get operations.

        Args:
            hook: Function to call after get operations
        """
        self._after_get_hook = hook

    def set_before_create_hook(self, hook: Callable) -> None:
        """
        Set the hook to call before create operations.

        Args:
            hook: Function to call before create operations
        """
        self._before_create_hook = hook

    def set_after_create_hook(self, hook: Callable) -> None:
        """
        Set the hook to call after create operations.

        Args:
            hook: Function to call after create operations
        """
        self._after_create_hook = hook

    def set_before_update_hook(self, hook: Callable) -> None:
        """
        Set the hook to call before update operations.

        Args:
            hook: Function to call before update operations
        """
        self._before_update_hook = hook

    def set_after_update_hook(self, hook: Callable) -> None:
        """
        Set the hook to call after update operations.

        Args:
            hook: Function to call after update operations
        """
        self._after_update_hook = hook

    def set_before_delete_hook(self, hook: Callable) -> None:
        """
        Set the hook to call before delete operations.

        Args:
            hook: Function to call before delete operations
        """
        self._before_delete_hook = hook

    def set_after_delete_hook(self, hook: Callable) -> None:
        """
        Set the hook to call after delete operations.

        Args:
            hook: Function to call after delete operations
        """
        self._after_delete_hook = hook

    def verify_deleted(self, id: Any) -> bool:
        """
        Verify that a resource was deleted.

        Args:
            id: Resource ID

        Returns:
            bool: True if the resource was deleted, False otherwise
        """
        str_id = str(id)
        return str_id not in self._data_store


class StubAPI(API):
    """
    Configurable stub implementation of the API class.

    This class provides a flexible API for testing with support for:
    - Dynamic endpoint registration
    - In-memory data store for each endpoint
    - Automatic CRUD interface creation
    - Data store population and clearing
    """
    client_class = Client

    def __init__(
        self,
        client: Optional[Client] = None,
        client_config: Optional[ClientConfig] = None,
        **kwargs: Any
    ):
        """
        Initialize the stub API with configurable behaviors.

        Args:
            client: Optional client instance
            client_config: Optional client configuration
            **kwargs: Additional configuration options
        """
        if client_config is None:
            client_config = ClientConfig(hostname="https://api.example.com")
        super().__init__(client, client_config, **kwargs)
        self.endpoints: Dict[str, StubCrud] = {}
        self._data_store: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def register_endpoint(
        self,
        name: str,
        endpoint: str,
        model: Optional[Type[Any]] = None,
        **kwargs: Any
    ) -> StubCrud:
        """
        Register an endpoint with the API.

        This creates a new StubCrud instance for the endpoint and makes it
        accessible as an attribute of the API instance.

        Args:
            name: Name of the endpoint(used as attribute name)
            endpoint: API endpoint path
            model: Optional model class
            **kwargs: Additional configuration options

        Returns:
            StubCrud: CRUD interface for the endpoint
        """
        # Initialize data store for this endpoint if it doesn't exist
        if name not in self._data_store:
            self._data_store[name] = {}

        # Create a stub CRUD for this endpoint
        crud = StubCrud(
            client_or_name=self.client,
            endpoint=endpoint,
            model=model,
            data_store=self._data_store[name]
        )

        # Store the CRUD and make it accessible as an attribute
        self.endpoints[name] = crud
        setattr(self, name, crud)

        return crud

    def _register_endpoints(self) -> None:
        """
        Register endpoints.

        This method is required by the API abstract base class but is not used
        in the stub implementation since endpoints are registered dynamically.
        """

    def __getattr__(self, name: str) -> Any:
        """
        Get an endpoint by name.

        Args:
            name: Name of the endpoint

        Returns:
            StubCrud: CRUD interface for the endpoint

        Raises:
            AttributeError: If the endpoint does not exist
        """
        if name in self.endpoints:
            return self.endpoints[name]

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def get_data_store(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Get the data store.

        Returns:
            Dict[str, Dict[str, Dict[str, Any]]]: Data store mapping endpoint names to collections of resources
        """
        return self._data_store

    def clear_data_store(self) -> None:
        """
        Clear the data store.

        This removes all resources from all endpoints.
        """
        for endpoint_store in self._data_store.values():
            endpoint_store.clear()

    def populate_data_store(
        self,
        endpoint_name: str,
        data: List[Dict[str, Any]]
    ) -> None:
        """
        Populate the data store for an endpoint.

        Args:
            endpoint_name: Name of the endpoint
            data: List of resources to add
        """
        if endpoint_name not in self._data_store:
            self._data_store[endpoint_name] = {}

        for item in data:
            if 'id' not in item:
                item['id'] = str(uuid.uuid4())

            str_id = str(item['id'])
            self._data_store[endpoint_name][str_id] = copy.deepcopy(item)
