"""
CRUD operation mock factories for testing.

This module provides specialized mock factories for Create, Read, Update, Delete operations
with chainable configuration and support for simulating different CRUD behaviors.
"""

import json
import re
from typing import Any, Callable, Dict, List, Optional, Type, Union

from pydantic import BaseModel, ValidationError

from crudclient.exceptions import (
    AuthenticationError, CrudClientError, InvalidResponseError, ModelConversionError, NotFoundError
)
from crudclient.types import JSONDict, JSONList

from .response import MockResponse
from .request_record import RequestRecord


class BaseCrudMock:
    """Base class for CRUD operation mocks."""

    def __init__(self):
        """Initialize the base CRUD mock."""
        self.response_patterns = []
        self.request_history = []
        self.default_response = MockResponse(
            status_code=404,
            json_data={"error": "No matching mock response configured"}
        )
        self._parent_id_handling = True  # Enable parent_id handling by default

    def with_response(
        self,
        url_pattern: str,
        response: Union[MockResponse, Dict[str, Any], List[Dict[str, Any]], str, Callable[..., MockResponse]],
        **kwargs: Any
    ) -> 'BaseCrudMock':
        """Add a response pattern to the mock."""
        # Convert dict/list/string responses to MockResponse
        if isinstance(response, dict):
            response = MockResponse(json_data=response)
        elif isinstance(response, list):
            # Convert list to JSON string to avoid type errors
            response = MockResponse(text=json.dumps(response))
        elif isinstance(response, str):
            response = MockResponse(text=response)

        self.response_patterns.append({
            'url_pattern': url_pattern,
            'response': response,
            'params': kwargs.get('params'),
            'data': kwargs.get('data'),
            'json': kwargs.get('json'),
            'headers': kwargs.get('headers'),
            'max_calls': kwargs.get('max_calls', float('inf')),
            'call_count': 0,
            'status_code': kwargs.get('status_code', 200),
            'error': kwargs.get('error')
        })
        return self

    def with_default_response(
        self,
        response: Union[MockResponse, Dict[str, Any], List[Dict[str, Any]], str]
    ) -> 'BaseCrudMock':
        """Set the default response for unmatched requests."""
        if isinstance(response, dict):
            self.default_response = MockResponse(json_data=response)
        elif isinstance(response, list):
            # Convert list to JSON string to avoid type errors
            self.default_response = MockResponse(text=json.dumps(response))
        elif isinstance(response, str):
            self.default_response = MockResponse(text=response)
        else:
            self.default_response = response
        return self

    def with_parent_id_handling(self, enabled: bool = True) -> 'BaseCrudMock':
        """Enable or disable parent_id handling."""
        self._parent_id_handling = enabled
        return self

    def with_validation_error(
        self,
        url_pattern: str,
        model_class: Type[BaseModel],
        invalid_data: Dict[str, Any],
        **kwargs: Any
    ) -> 'BaseCrudMock':
        """Configure a validation error response."""
        def validation_error_response(**request_kwargs):
            try:
                model_class(**invalid_data)
                # If validation doesn't fail, return a generic error
                return MockResponse(
                    status_code=422,
                    json_data={"error": "Validation should have failed but didn't"}
                )
            except ValidationError as e:
                # Create a proper ValidationError instance
                validation_error = ValidationError(str(e), None)
                return MockResponse(
                    status_code=422,
                    json_data={"error": "Validation Error", "detail": str(e)},
                    error=validation_error
                )

        self.response_patterns.append({
            'url_pattern': url_pattern,
            'response': validation_error_response,
            'params': kwargs.get('params'),
            'data': kwargs.get('data'),
            'json': kwargs.get('json'),
            'headers': kwargs.get('headers'),
            'max_calls': kwargs.get('max_calls', float('inf')),
            'call_count': 0
        })
        return self

    def _find_matching_pattern(self, method: str, url: str, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """Find a matching response pattern."""
        for pattern in self.response_patterns:
            if re.search(pattern['url_pattern'], url):
                # Check if we've reached the max calls for this pattern
                if pattern['call_count'] >= pattern['max_calls']:
                    continue

                # Check params matcher
                params_match = True
                if pattern['params'] is not None:
                    request_params = kwargs.get('params', {})
                    for key, value in pattern['params'].items():
                        if key not in request_params or request_params[key] != value:
                            params_match = False
                            break

                # Check data matcher
                data_match = True
                if pattern['data'] is not None:
                    request_data = kwargs.get('data', {})
                    for key, value in pattern['data'].items():
                        if key not in request_data or request_data[key] != value:
                            data_match = False
                            break

                # Check json matcher
                json_match = True
                if pattern['json'] is not None:
                    request_json = kwargs.get('json', {})
                    for key, value in pattern['json'].items():
                        if key not in request_json or request_json[key] != value:
                            json_match = False
                            break

                # Check headers matcher
                headers_match = True
                if pattern['headers'] is not None:
                    request_headers = kwargs.get('headers', {})
                    for key, value in pattern['headers'].items():
                        if key not in request_headers or request_headers[key] != value:
                            headers_match = False
                            break

                # If all matchers pass, return the pattern
                if params_match and data_match and json_match and headers_match:
                    pattern['call_count'] += 1
                    return pattern

        return None

    def _process_parent_id(self, url: str, parent_id: Optional[str]) -> str:
        """Process parent_id to build the correct URL."""
        if not self._parent_id_handling or not parent_id:
            return url

        # Extract the resource path from the URL
        parts = url.split('/')
        resource_path = parts[-1] if len(parts) == 1 else '/'.join(parts)

        # Build the URL with parent_id
        return f"parents/{parent_id}/{resource_path}"

    def assert_request_count(self, count: int, url_pattern: Optional[str] = None) -> None:
        """Assert that a specific number of matching requests were made."""
        matching_requests = self.request_history
        if url_pattern:
            pattern = re.compile(url_pattern)
            matching_requests = [r for r in matching_requests if pattern.search(r.url)]

        actual_count = len(matching_requests)
        assert actual_count == count, (
            f"Expected {count} matching requests, but found {actual_count}. "
            f"Filter: url_pattern={url_pattern}"
        )

    def assert_request_sequence(
        self,
        sequence: List[Dict[str, Any]],
        strict: bool = False
    ) -> None:
        """Assert that requests were made in a specific sequence."""
        if not sequence:
            return

        if strict and len(sequence) != len(self.request_history):
            raise AssertionError(
                f"Expected {len(sequence)} requests, but found {len(self.request_history)}"
            )

        # Find subsequence match
        history_idx = 0
        sequence_idx = 0

        while history_idx < len(self.request_history) and sequence_idx < len(sequence):
            request = self.request_history[history_idx]
            matcher = sequence[sequence_idx]

            url_match = True
            if 'url_pattern' in matcher:
                url_match = bool(re.search(matcher['url_pattern'], request.url))

            if url_match:
                sequence_idx += 1

            history_idx += 1

        if sequence_idx < len(sequence):
            raise AssertionError(
                f"Request sequence not found. Matched {sequence_idx} of {len(sequence)} expected requests."
            )

    def assert_request_payload(
        self,
        payload: Dict[str, Any],
        url_pattern: Optional[str] = None,
        match_all: bool = False
    ) -> None:
        """Assert that requests were made with specific payload."""
        matching_requests = self.request_history
        if url_pattern:
            pattern = re.compile(url_pattern)
            matching_requests = [r for r in matching_requests if pattern.search(r.url)]

        if not matching_requests:
            raise AssertionError(
                f"No matching requests found. Filter: url_pattern={url_pattern}"
            )

        if match_all:
            for i, request in enumerate(matching_requests):
                request_json = request.json or {}
                for key, value in payload.items():
                    if key not in request_json:
                        raise AssertionError(
                            f"Request {i} missing payload key '{key}'. "
                            f"URL: {request.url}"
                        )
                    if callable(value):
                        if not value(request_json[key]):
                            raise AssertionError(
                                f"Request {i} payload key '{key}' failed validation. "
                                f"URL: {request.url}"
                            )
                    elif request_json[key] != value:
                        raise AssertionError(
                            f"Request {i} payload key '{key}' has value '{request_json[key]}', "
                            f"expected '{value}'. URL: {request.url}"
                        )
        else:
            # At least one request must match all payload
            for i, request in enumerate(matching_requests):
                all_match = True
                request_json = request.json or {}
                for key, value in payload.items():
                    if key not in request_json:
                        all_match = False
                        break
                    if callable(value):
                        if not value(request_json[key]):
                            all_match = False
                            break
                    elif request_json[key] != value:
                        all_match = False
                        break

                if all_match:
                    return  # Found a match

            raise AssertionError(
                f"No request matched all payload {payload}. "
                f"Filter: url_pattern={url_pattern}"
            )


class CreateMock(BaseCrudMock):
    """Mock for Create operations."""

    def __init__(self):
        """Initialize the Create mock."""
        super().__init__()
        self.default_response = MockResponse(
            status_code=201,
            json_data={"id": 1, "name": "Created Resource"}
        )

    def post(self, url: str, **kwargs: Any) -> Any:
        """Handle POST requests."""
        # Process parent_id if present in kwargs
        parent_id = kwargs.pop('parent_id', None)
        if parent_id and self._parent_id_handling:
            url = self._process_parent_id(url, parent_id)

        # Record the request
        record = RequestRecord(
            method="POST",
            url=url,
            params=kwargs.get('params'),
            data=kwargs.get('data'),
            json=kwargs.get('json'),
            headers=kwargs.get('headers')
        )
        self.request_history.append(record)

        # Find a matching pattern
        pattern = self._find_matching_pattern("POST", url, **kwargs)

        if pattern:
            response_obj = pattern['response']

            # Handle callable responses
            if callable(response_obj):
                response_obj = response_obj(**kwargs)

            # Handle errors
            if 'error' in pattern and pattern['error']:
                raise pattern['error']

            # Ensure response_obj is a MockResponse
            if not isinstance(response_obj, MockResponse):
                if isinstance(response_obj, dict):
                    response_obj = MockResponse(json_data=response_obj)
                elif isinstance(response_obj, list):
                    response_obj = MockResponse(text=json.dumps(response_obj))
                elif isinstance(response_obj, str):
                    response_obj = MockResponse(text=response_obj)
                else:
                    response_obj = MockResponse(text=str(response_obj))

            record.response = response_obj

            # Return the appropriate response format
            if hasattr(response_obj, '_json_data') and response_obj._json_data is not None:
                return response_obj._json_data
            return response_obj.text

        # No pattern matched, use default response
        record.response = self.default_response

        if hasattr(self.default_response, '_json_data') and self.default_response._json_data is not None:
            return self.default_response._json_data
        return self.default_response.text

    def with_success_response(
        self,
        url_pattern: str,
        response_data: Dict[str, Any],
        status_code: int = 201,
        **kwargs: Any
    ) -> 'CreateMock':
        """Configure a successful create response."""
        self.with_response(
            url_pattern=url_pattern,
            response=MockResponse(
                status_code=status_code,
                json_data=response_data
            ),
            **kwargs
        )
        return self

    def with_validation_failure(
        self,
        url_pattern: str,
        validation_errors: Dict[str, List[str]],
        status_code: int = 422,
        **kwargs: Any
    ) -> 'CreateMock':
        """Configure a validation failure response."""
        self.with_response(
            url_pattern=url_pattern,
            response=MockResponse(
                status_code=status_code,
                json_data={"errors": validation_errors}
            ),
            **kwargs
        )
        return self


class ReadMock(BaseCrudMock):
    """Mock for Read operations."""

    def __init__(self):
        """Initialize the Read mock."""
        super().__init__()
        self.default_response = MockResponse(
            status_code=200,
            json_data={"id": 1, "name": "Read Resource"}
        )

    def get(self, url: str, **kwargs: Any) -> Any:
        """Handle GET requests."""
        # Process parent_id if present in kwargs
        parent_id = kwargs.pop('parent_id', None)
        if parent_id and self._parent_id_handling:
            url = self._process_parent_id(url, parent_id)

        # Record the request
        record = RequestRecord(
            method="GET",
            url=url,
            params=kwargs.get('params'),
            data=kwargs.get('data'),
            json=kwargs.get('json'),
            headers=kwargs.get('headers')
        )
        self.request_history.append(record)

        # Find a matching pattern
        pattern = self._find_matching_pattern("GET", url, **kwargs)

        if pattern:
            response_obj = pattern['response']

            # Handle callable responses
            if callable(response_obj):
                response_obj = response_obj(**kwargs)

            # Handle errors
            if 'error' in pattern and pattern['error']:
                raise pattern['error']

            # Ensure response_obj is a MockResponse
            if not isinstance(response_obj, MockResponse):
                if isinstance(response_obj, dict):
                    response_obj = MockResponse(json_data=response_obj)
                elif isinstance(response_obj, list):
                    response_obj = MockResponse(text=json.dumps(response_obj))
                elif isinstance(response_obj, str):
                    response_obj = MockResponse(text=response_obj)
                else:
                    response_obj = MockResponse(text=str(response_obj))

            record.response = response_obj

            # Return the appropriate response format
            if hasattr(response_obj, '_json_data') and response_obj._json_data is not None:
                return response_obj._json_data
            return response_obj.text

        # No pattern matched, use default response
        record.response = self.default_response

        if hasattr(self.default_response, '_json_data') and self.default_response._json_data is not None:
            return self.default_response._json_data
        return self.default_response.text

    def with_single_resource(
        self,
        url_pattern: str,
        resource_data: Dict[str, Any],
        **kwargs: Any
    ) -> 'ReadMock':
        """Configure a single resource response."""
        self.with_response(
            url_pattern=url_pattern,
            response=MockResponse(
                status_code=200,
                json_data=resource_data
            ),
            **kwargs
        )
        return self

    def with_resource_list(
        self,
        url_pattern: str,
        resources: List[Dict[str, Any]],
        **kwargs: Any
    ) -> 'ReadMock':
        """Configure a resource list response."""
        self.with_response(
            url_pattern=url_pattern,
            response=MockResponse(
                status_code=200,
                text=json.dumps(resources)
            ),
            **kwargs
        )
        return self  # Return self for method chaining


class UpdateMock(BaseCrudMock):
    """Mock for Update operations."""

    def __init__(self):
        """Initialize the Update mock."""
        super().__init__()
        self.default_response = MockResponse(
            status_code=200,
            json_data={"id": 1, "name": "Updated Resource"}
        )

    def put(self, url: str, **kwargs: Any) -> Any:
        """Handle PUT requests."""
        # Process parent_id if present in kwargs
        parent_id = kwargs.pop('parent_id', None)
        if parent_id and self._parent_id_handling:
            url = self._process_parent_id(url, parent_id)

        # Record the request
        record = RequestRecord(
            method="PUT",
            url=url,
            params=kwargs.get('params'),
            data=kwargs.get('data'),
            json=kwargs.get('json'),
            headers=kwargs.get('headers')
        )
        self.request_history.append(record)

        # Find a matching pattern
        pattern = self._find_matching_pattern("PUT", url, **kwargs)

        if pattern:
            response_obj = pattern['response']

            # Handle callable responses
            if callable(response_obj):
                response_obj = response_obj(**kwargs)

            # Handle errors
            if 'error' in pattern and pattern['error']:
                raise pattern['error']

            # Ensure response_obj is a MockResponse
            if not isinstance(response_obj, MockResponse):
                if isinstance(response_obj, dict):
                    response_obj = MockResponse(json_data=response_obj)
                elif isinstance(response_obj, list):
                    response_obj = MockResponse(text=json.dumps(response_obj))
                elif isinstance(response_obj, str):
                    response_obj = MockResponse(text=response_obj)
                else:
                    response_obj = MockResponse(text=str(response_obj))

            record.response = response_obj

            # Return the appropriate response format
            if hasattr(response_obj, '_json_data') and response_obj._json_data is not None:
                return response_obj._json_data
            return response_obj.text

        # No pattern matched, use default response
        record.response = self.default_response

        if hasattr(self.default_response, '_json_data') and self.default_response._json_data is not None:
            return self.default_response._json_data
        return self.default_response.text

    def patch(self, url: str, **kwargs: Any) -> Any:
        """Handle PATCH requests."""
        # Process parent_id if present in kwargs
        parent_id = kwargs.pop('parent_id', None)
        if parent_id and self._parent_id_handling:
            url = self._process_parent_id(url, parent_id)

        # Record the request
        record = RequestRecord(
            method="PATCH",
            url=url,
            params=kwargs.get('params'),
            data=kwargs.get('data'),
            json=kwargs.get('json'),
            headers=kwargs.get('headers')
        )
        self.request_history.append(record)

        # Find a matching pattern
        pattern = self._find_matching_pattern("PATCH", url, **kwargs)

        if pattern:
            response_obj = pattern['response']

            # Handle callable responses
            if callable(response_obj):
                response_obj = response_obj(**kwargs)

            # Handle errors
            if 'error' in pattern and pattern['error']:
                raise pattern['error']

            # Ensure response_obj is a MockResponse
            if not isinstance(response_obj, MockResponse):
                if isinstance(response_obj, dict):
                    response_obj = MockResponse(json_data=response_obj)
                elif isinstance(response_obj, list):
                    response_obj = MockResponse(text=json.dumps(response_obj))
                elif isinstance(response_obj, str):
                    response_obj = MockResponse(text=response_obj)
                else:
                    response_obj = MockResponse(text=str(response_obj))

            record.response = response_obj

            # Return the appropriate response format
            if hasattr(response_obj, '_json_data') and response_obj._json_data is not None:
                return response_obj._json_data
            return response_obj.text

        # No pattern matched, use default response
        record.response = self.default_response

        if hasattr(self.default_response, '_json_data') and self.default_response._json_data is not None:
            return self.default_response._json_data
        return self.default_response.text

    def with_update_response(
        self,
        url_pattern: str,
        updated_data: Dict[str, Any],
        **kwargs: Any
    ) -> 'UpdateMock':
        """Configure an update response."""
        self.with_response(
            url_pattern=url_pattern,
            response=MockResponse(
                status_code=200,
                json_data=updated_data
            ),
            **kwargs
        )
        return self

    def with_partial_update_response(
        self,
        url_pattern: str,
        partial_data: Dict[str, Any],
        full_response_data: Dict[str, Any],
        **kwargs: Any
    ) -> 'UpdateMock':
        """Configure a partial update response."""
        # This method allows specifying both the partial data expected in the request
        # and the full data to be returned in the response
        self.with_response(
            url_pattern=url_pattern,
            response=MockResponse(
                status_code=200,
                json_data=full_response_data
            ),
            json=partial_data,
            **kwargs
        )
        return self

    def with_conditional_update(
        self,
        url_pattern: str,
        condition_field: str,
        condition_value: Any,
        success_data: Dict[str, Any],
        error_data: Dict[str, Any],
        **kwargs: Any
    ) -> 'UpdateMock':
        """Configure a conditional update response."""
        def conditional_response(**request_kwargs):
            request_json = request_kwargs.get('json', {})
            if request_json.get(condition_field) == condition_value:
                return MockResponse(
                    status_code=200,
                    json_data=success_data
                )
            else:
                return MockResponse(
                    status_code=422,
                    json_data=error_data
                )

        self.with_response(
            url_pattern=url_pattern,
            response=conditional_response,
            **kwargs
        )
        return self  # Return self for method chaining

    def with_not_found(
        self,
        url_pattern: str,
        **kwargs: Any
    ) -> 'UpdateMock':
        """Configure a not found response."""
        # Create a mock response for not found error
        mock_response = MockResponse(
            status_code=404,
            json_data={"error": "Resource not found"}
        )

        # Create the error instance
        error_instance = NotFoundError(
            f"HTTP error occurred: 404, Resource not found"
        )

        # Add to response patterns
        self.response_patterns.append({
            'url_pattern': url_pattern,
            'response': mock_response,
            'error': error_instance,
            'params': kwargs.get('params'),
            'data': kwargs.get('data'),
            'json': kwargs.get('json'),
            'headers': kwargs.get('headers'),
            'max_calls': kwargs.get('max_calls', float('inf')),
            'call_count': 0
        })
        return self  # Return self for method chaining


class DeleteMock(BaseCrudMock):
    """Mock for Delete operations."""

    def __init__(self):
        """Initialize the Delete mock."""
        super().__init__()
        self.default_response = MockResponse(
            status_code=204,
            json_data=None
        )

    def delete(self, url: str, **kwargs: Any) -> Any:
        """Handle DELETE requests."""
        # Process parent_id if present in kwargs
        parent_id = kwargs.pop('parent_id', None)
        if parent_id and self._parent_id_handling:
            url = self._process_parent_id(url, parent_id)

        # Record the request
        record = RequestRecord(
            method="DELETE",
            url=url,
            params=kwargs.get('params'),
            data=kwargs.get('data'),
            json=kwargs.get('json'),
            headers=kwargs.get('headers')
        )
        self.request_history.append(record)

        # Find a matching pattern
        pattern = self._find_matching_pattern("DELETE", url, **kwargs)

        if pattern:
            response_obj = pattern['response']

            # Handle callable responses
            if callable(response_obj):
                response_obj = response_obj(**kwargs)

            # Handle errors
            if 'error' in pattern and pattern['error']:
                raise pattern['error']

            # Ensure response_obj is a MockResponse
            if not isinstance(response_obj, MockResponse):
                if isinstance(response_obj, dict):
                    response_obj = MockResponse(json_data=response_obj)
                elif isinstance(response_obj, list):
                    response_obj = MockResponse(text=json.dumps(response_obj))
                elif isinstance(response_obj, str):
                    response_obj = MockResponse(text=response_obj)
                else:
                    response_obj = MockResponse(text=str(response_obj))

            record.response = response_obj

            # Return the appropriate response format
            if hasattr(response_obj, '_json_data') and response_obj._json_data is not None:
                return response_obj._json_data
            return response_obj.text

        # No pattern matched, use default response
        record.response = self.default_response

        if hasattr(self.default_response, '_json_data') and self.default_response._json_data is not None:
            return self.default_response._json_data
        return self.default_response.text

    def with_success(
        self,
        url_pattern: str,
        **kwargs: Any
    ) -> 'DeleteMock':
        """Configure a successful delete response."""
        self.with_response(
            url_pattern=url_pattern,
            response=MockResponse(
                status_code=204,
                json_data=None
            ),
            **kwargs
        )
        return self  # Return self for method chaining

    def with_resource_in_use_error(
        self,
        url_pattern: str,
        **kwargs: Any
    ) -> 'DeleteMock':
        """Configure a resource in use error response."""
        # Create a mock response for resource in use error
        mock_response = MockResponse(
            status_code=409,
            json_data={"error": "Resource is in use and cannot be deleted"}
        )

        # Create the error instance
        error_instance = CrudClientError(
            f"HTTP error occurred: 409, Resource is in use and cannot be deleted"
        )

        # Add to response patterns
        self.response_patterns.append({
            'url_pattern': url_pattern,
            'response': mock_response,
            'error': error_instance,
            'params': kwargs.get('params'),
            'data': kwargs.get('data'),
            'json': kwargs.get('json'),
            'headers': kwargs.get('headers'),
            'max_calls': kwargs.get('max_calls', float('inf')),
            'call_count': 0
        })
        return self  # Return self for method chaining


class CrudMockFactory:
    """Factory for creating CRUD operation mocks."""

    @staticmethod
    def create() -> CreateMock:
        """Create a Create operation mock."""
        return CreateMock()

    @staticmethod
    def read() -> ReadMock:
        """Create a Read operation mock."""
        return ReadMock()

    @staticmethod
    def update() -> UpdateMock:
        """Create an Update operation mock."""
        return UpdateMock()

    @staticmethod
    def delete() -> DeleteMock:
        """Create a Delete operation mock."""
        return DeleteMock()

    @staticmethod
    def combined() -> 'CombinedCrudMock':
        """Create a combined CRUD mock."""
        return CombinedCrudMock()


class CombinedCrudMock:
    """Combined mock for all CRUD operations."""

    def __init__(self):
        """Initialize the combined CRUD mock."""
        self.create_mock = CreateMock()
        self.read_mock = ReadMock()
        self.update_mock = UpdateMock()
        self.delete_mock = DeleteMock()
        self.request_history = []
        self._parent_id_handling = True

    def get(self, url: str, **kwargs: Any) -> Any:
        """Handle GET requests."""
        result = self.read_mock.get(url, **kwargs)
        self.request_history.extend(self.read_mock.request_history)
        return result

    def post(self, url: str, **kwargs: Any) -> Any:
        """Handle POST requests."""
        result = self.create_mock.post(url, **kwargs)
        self.request_history.extend(self.create_mock.request_history)
        return result

    def put(self, url: str, **kwargs: Any) -> Any:
        """Handle PUT requests."""
        result = self.update_mock.put(url, **kwargs)
        self.request_history.extend(self.update_mock.request_history)
        return result

    def patch(self, url: str, **kwargs: Any) -> Any:
        """Handle PATCH requests."""
        result = self.update_mock.patch(url, **kwargs)
        self.request_history.extend(self.update_mock.request_history)
        return result

    def delete(self, url: str, **kwargs: Any) -> Any:
        """Handle DELETE requests."""
        result = self.delete_mock.delete(url, **kwargs)
        self.request_history.extend(self.delete_mock.request_history)
        return result

    def with_parent_id_handling(self, enabled: bool = True) -> 'CombinedCrudMock':
        """Enable or disable parent_id handling."""
        self._parent_id_handling = enabled
        self.create_mock.with_parent_id_handling(enabled)
        self.read_mock.with_parent_id_handling(enabled)
        self.update_mock.with_parent_id_handling(enabled)
        self.delete_mock.with_parent_id_handling(enabled)
        return self

    def assert_request_count(self, count: int, url_pattern: Optional[str] = None) -> None:
        """Assert that a specific number of matching requests were made."""
        import re

        matching_requests = self.request_history
        if url_pattern:
            pattern = re.compile(url_pattern)
            matching_requests = [r for r in matching_requests if pattern.search(r.url)]

        actual_count = len(matching_requests)
        assert actual_count == count, (
            f"Expected {count} matching requests, but found {actual_count}. "
            f"Filter: url_pattern={url_pattern}"
        )

    def assert_request_sequence(
        self,
        sequence: List[Dict[str, Any]],
        strict: bool = False
    ) -> None:
        """Assert that requests were made in a specific sequence."""
        import re

        if not sequence:
            return

        if strict and len(sequence) != len(self.request_history):
            raise AssertionError(
                f"Expected {len(sequence)} requests, but found {len(self.request_history)}"
            )

        # Find subsequence match
        history_idx = 0
        sequence_idx = 0

        while history_idx < len(self.request_history) and sequence_idx < len(sequence):
            request = self.request_history[history_idx]
            matcher = sequence[sequence_idx]

            method_match = True
            if 'method' in matcher:
                method_match = request.method == matcher['method'].upper()

            url_match = True
            if 'url_pattern' in matcher:
                url_match = bool(re.search(matcher['url_pattern'], request.url))

            if method_match and url_match:
                sequence_idx += 1

            history_idx += 1

        if sequence_idx < len(sequence):
            raise AssertionError(
                f"Request sequence not found. Matched {sequence_idx} of {len(sequence)} expected requests."
            )

    def assert_crud_operation_sequence(
        self,
        operations: List[str],
        resource_id: Optional[str] = None,
        url_pattern: Optional[str] = None
    ) -> None:
        """Assert that CRUD operations were performed in a specific sequence."""
        # Map operation names to HTTP methods
        method_map = {
            "create": "POST",
            "read": "GET",
            "update": "PUT",
            "partial_update": "PATCH",
            "delete": "DELETE"
        }

        # Build sequence matchers
        sequence = []
        for op in operations:
            matcher = {'method': method_map.get(op, op.upper())}
            if url_pattern:
                matcher['url_pattern'] = url_pattern
            if resource_id and op != "create":
                # For non-create operations, include resource_id in the URL pattern
                if 'url_pattern' in matcher:
                    matcher['url_pattern'] = f"{matcher['url_pattern']}.*{resource_id}"
                else:
                    matcher['url_pattern'] = f".*{resource_id}"
            sequence.append(matcher)

        self.assert_request_sequence(sequence)

        return self
