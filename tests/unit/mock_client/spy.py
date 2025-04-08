"""
Spy implementations for verification-focused testing.

This module provides spy classes that record method calls and parameters
for verification in tests.
"""

import json
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

import requests
from requests import Response

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.types import RawResponseSimple

logger = logging.getLogger(__name__)


class MethodCall:
    """
    Record of a method call for verification.

    This class stores information about a method call, including the method name,
    arguments, and return value.
    """

    def __init__(
        self,
        method_name: str,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        return_value: Any = None,
        exception: Optional[Exception] = None
    ):
        """
        Initialize a method call record.

        Args:
            method_name: Name of the method called
            args: Positional arguments
            kwargs: Keyword arguments
            return_value: Return value (if any)
            exception: Exception raised (if any)
        """
        self.method_name = method_name
        self.args = args
        self.kwargs = kwargs
        self.return_value = return_value
        self.exception = exception

    def __repr__(self) -> str:
        """String representation of the method call."""
        args_str = ", ".join([repr(arg) for arg in self.args])
        kwargs_str = ", ".join([f"{k}={repr(v)}" for k, v in self.kwargs.items()])
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))

        if self.exception:
            result = f" -> raised {self.exception.__class__.__name__}({self.exception})"
        else:
            result = f" -> returned {repr(self.return_value)}" if self.return_value is not None else ""

        return f"{self.method_name}({all_args}){result}"


class SpyBase:
    """
    Base class for spy implementations.

    This class provides common functionality for recording and verifying method calls.
    """

    def __init__(self):
        """Initialize the spy base."""
        self.calls: List[MethodCall] = []
        self.call_count: Dict[str, int] = {}

    def _record_call(
        self,
        method_name: str,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
        return_value: Any = None,
        exception: Optional[Exception] = None
    ) -> None:
        """
        Record a method call.

        Args:
            method_name: Name of the method called
            args: Positional arguments
            kwargs: Keyword arguments
            return_value: Return value (if any)
            exception: Exception raised (if any)
        """
        call = MethodCall(method_name, args, kwargs, return_value, exception)
        self.calls.append(call)

        # Update call count
        self.call_count[method_name] = self.call_count.get(method_name, 0) + 1

    def assert_called(self, method_name: str) -> None:
        """
        Assert that a method was called.

        Args:
            method_name: Name of the method
        """
        assert method_name in self.call_count, f"Method {method_name} was not called"

    def assert_not_called(self, method_name: str) -> None:
        """
        Assert that a method was not called.

        Args:
            method_name: Name of the method
        """
        assert method_name not in self.call_count or self.call_count[method_name] == 0, \
            f"Method {method_name} was called {self.call_count.get(method_name, 0)} times"

    def assert_called_once(self, method_name: str) -> None:
        """
        Assert that a method was called exactly once.

        Args:
            method_name: Name of the method
        """
        assert method_name in self.call_count and self.call_count[method_name] == 1, \
            f"Method {method_name} was called {self.call_count.get(method_name, 0)} times, expected 1"

    def assert_called_with(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """
        Assert that a method was called with specific arguments.

        Args:
            method_name: Name of the method
            *args: Expected positional arguments
            **kwargs: Expected keyword arguments
        """
        for call in self.calls:
            if call.method_name == method_name:
                # Check if args match
                args_match = len(call.args) == len(args) and all(
                    a == b for a, b in zip(call.args, args)
                )

                # Check if kwargs match
                kwargs_match = all(
                    k in call.kwargs and call.kwargs[k] == v
                    for k, v in kwargs.items()
                )

                if args_match and kwargs_match:
                    return

        args_str = ", ".join([repr(arg) for arg in args])
        kwargs_str = ", ".join([f"{k}={repr(v)}" for k, v in kwargs.items()])
        all_args = ", ".join(filter(None, [args_str, kwargs_str]))

        raise AssertionError(
            f"Method {method_name} was not called with arguments ({all_args})"
        )

    def assert_called_once_with(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """
        Assert that a method was called exactly once with specific arguments.

        Args:
            method_name: Name of the method
            *args: Expected positional arguments
            **kwargs: Expected keyword arguments
        """
        self.assert_called_once(method_name)
        self.assert_called_with(method_name, *args, **kwargs)

    def assert_any_call(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """
        Assert that a method was called at least once with specific arguments.

        Args:
            method_name: Name of the method
            *args: Expected positional arguments
            **kwargs: Expected keyword arguments
        """
        self.assert_called_with(method_name, *args, **kwargs)

    def assert_call_count(self, method_name: str, count: int) -> None:
        """
        Assert that a method was called a specific number of times.

        Args:
            method_name: Name of the method
            count: Expected call count
        """
        actual_count = self.call_count.get(method_name, 0)
        assert actual_count == count, \
            f"Method {method_name} was called {actual_count} times, expected {count}"

    def assert_has_calls(self, expected_calls: List[Tuple[str, Tuple[Any, ...], Dict[str, Any]]]) -> None:
        """
        Assert that a sequence of method calls occurred.

        Args:
            expected_calls: List of (method_name, args, kwargs) tuples
        """
        if not expected_calls:
            return

        actual_calls = [(call.method_name, call.args, call.kwargs) for call in self.calls]

        # Check if the expected calls are a subsequence of the actual calls
        i, j = 0, 0
        while i < len(actual_calls) and j < len(expected_calls):
            actual = actual_calls[i]
            expected = expected_calls[j]

            if (
                actual[0] == expected[0]  # method name
                and len(actual[1]) == len(expected[1])  # args length
                and all(a == b for a, b in zip(actual[1], expected[1]))  # args values
                and all(k in actual[2] and actual[2][k] == v for k, v in expected[2].items())  # kwargs
            ):
                j += 1  # Move to next expected call

            i += 1  # Always move to next actual call

        if j < len(expected_calls):
            raise AssertionError(
                f"Not all expected calls were found. Missing: {expected_calls[j:]}"
            )

    def assert_has_exact_calls(self, expected_calls: List[Tuple[str, Tuple[Any, ...], Dict[str, Any]]]) -> None:
        """
        Assert that exactly the specified sequence of method calls occurred.

        Args:
            expected_calls: List of (method_name, args, kwargs) tuples
        """
        actual_calls = [(call.method_name, call.args, call.kwargs) for call in self.calls]

        if len(actual_calls) != len(expected_calls):
            raise AssertionError(
                f"Expected {len(expected_calls)} calls, but got {len(actual_calls)}"
            )

        for i, (actual, expected) in enumerate(zip(actual_calls, expected_calls)):
            if (
                actual[0] != expected[0]  # method name
                or len(actual[1]) != len(expected[1])  # args length
                or not all(a == b for a, b in zip(actual[1], expected[1]))  # args values
                or not all(k in actual[2] and actual[2][k] == v for k, v in expected[2].items())  # kwargs
            ):
                raise AssertionError(
                    f"Call {i} does not match: expected {expected}, got {actual}"
                )


class ClientSpy(Client, SpyBase):
    """
    Spy implementation of the Client interface.

    This class records all method calls to the Client interface for verification
    in tests, while delegating to a real or mock implementation.
    """

    def __init__(
        self,
        config: Union[ClientConfig, Dict[str, Any]],
        delegate: Optional[Client] = None
    ):
        """
        Initialize the client spy.

        Args:
            config: Client configuration
            delegate: Optional delegate client implementation
        """
        Client.__init__(self, config)
        SpyBase.__init__(self)

        # Create a delegate client if not provided
        self.delegate = delegate or super()

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> RawResponseSimple:
        """
        Record and delegate GET method call.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response from delegate
        """
        try:
            result = self.delegate.get(endpoint, params=params)
            self._record_call('get', (endpoint,), {'params': params}, result)
            return result
        except Exception as e:
            self._record_call('get', (endpoint,), {'params': params}, exception=e)
            raise

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """
        Record and delegate POST method call.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            Response from delegate
        """
        try:
            result = self.delegate.post(endpoint, data=data, json=json, files=files)
            self._record_call('post', (endpoint,), {'data': data, 'json': json, 'files': files}, result)
            return result
        except Exception as e:
            self._record_call('post', (endpoint,), {'data': data, 'json': json, 'files': files}, exception=e)
            raise

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """
        Record and delegate PUT method call.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            Response from delegate
        """
        try:
            result = self.delegate.put(endpoint, data=data, json=json, files=files)
            self._record_call('put', (endpoint,), {'data': data, 'json': json, 'files': files}, result)
            return result
        except Exception as e:
            self._record_call('put', (endpoint,), {'data': data, 'json': json, 'files': files}, exception=e)
            raise

    def delete(self, endpoint: str, **kwargs: Any) -> RawResponseSimple:
        """
        Record and delegate DELETE method call.

        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments

        Returns:
            Response from delegate
        """
        try:
            result = self.delegate.delete(endpoint, **kwargs)
            self._record_call('delete', (endpoint,), kwargs, result)
            return result
        except Exception as e:
            self._record_call('delete', (endpoint,), kwargs, exception=e)
            raise

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """
        Record and delegate PATCH method call.

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            Response from delegate
        """
        try:
            result = self.delegate.patch(endpoint, data=data, json=json, files=files)
            self._record_call('patch', (endpoint,), {'data': data, 'json': json, 'files': files}, result)
            return result
        except Exception as e:
            self._record_call('patch', (endpoint,), {'data': data, 'json': json, 'files': files}, exception=e)
            raise

    def _request(
        self,
        method: str,
        endpoint: Optional[str] = None,
        url: Optional[str] = None,
        handle_response: bool = True,
        **kwargs: Any
    ) -> Union[RawResponseSimple, Response]:
        """
        Record and delegate _request method call.

        Args:
            method: HTTP method
            endpoint: API endpoint
            url: Full URL
            handle_response: Whether to handle the response
            **kwargs: Additional arguments

        Returns:
            Response from delegate
        """
        try:
            result = self.delegate._request(
                method, endpoint=endpoint, url=url, handle_response=handle_response, **kwargs
            )
            self._record_call(
                '_request',
                (method,),
                {'endpoint': endpoint, 'url': url, 'handle_response': handle_response, **kwargs},
                result
            )
            return result
        except Exception as e:
            self._record_call(
                '_request',
                (method,),
                {'endpoint': endpoint, 'url': url, 'handle_response': handle_response, **kwargs},
                exception=e
            )
            raise

    def _setup_auth(self) -> None:
        """
        Record and delegate _setup_auth method call.

        Returns:
            None
        """
        try:
            result = self.delegate._setup_auth()
            self._record_call('_setup_auth', (), {}, result)
            return result
        except Exception as e:
            self._record_call('_setup_auth', (), {}, exception=e)
            raise

    def close(self) -> None:
        """
        Record and delegate close method call.

        Returns:
            None
        """
        try:
            result = self.delegate.close()
            self._record_call('close', (), {}, result)
            return result
        except Exception as e:
            self._record_call('close', (), {}, exception=e)
            raise

    # Helper methods for verification

    def assert_endpoint_called(self, endpoint: str) -> None:
        """
        Assert that an endpoint was called with any HTTP method.

        Args:
            endpoint: API endpoint
        """
        for call in self.calls:
            if call.method_name in ('get', 'post', 'put', 'delete', 'patch'):
                if call.args and call.args[0] == endpoint:
                    return

        raise AssertionError(f"Endpoint {endpoint} was not called")

    def assert_endpoint_called_with_method(self, method: str, endpoint: str) -> None:
        """
        Assert that an endpoint was called with a specific HTTP method.

        Args:
            method: HTTP method (get, post, etc.)
            endpoint: API endpoint
        """
        for call in self.calls:
            if call.method_name == method.lower() and call.args and call.args[0] == endpoint:
                return

        raise AssertionError(f"Endpoint {endpoint} was not called with method {method}")

    def assert_json_payload_sent(self, method: str, endpoint: str, expected_json: Dict[str, Any]) -> None:
        """
        Assert that a JSON payload was sent to an endpoint.

        Args:
            method: HTTP method (get, post, etc.)
            endpoint: API endpoint
            expected_json: Expected JSON payload
        """
        for call in self.calls:
            if (
                call.method_name == method.lower()
                and call.args and call.args[0] == endpoint
                and 'json' in call.kwargs and call.kwargs['json'] is not None
            ):
                actual_json = call.kwargs['json']

                # Check if all expected keys and values are present
                if all(k in actual_json and actual_json[k] == v for k, v in expected_json.items()):
                    return

        raise AssertionError(
            f"JSON payload {expected_json} was not sent to {endpoint} with method {method}"
        )

    def assert_auth_header_sent(self, header_name: str = "Authorization", header_value: Optional[str] = None) -> None:
        """
        Assert that an authentication header was sent.

        Args:
            header_name: Name of the header
            header_value: Optional expected value
        """
        for call in self.calls:
            if call.method_name == '_request' and 'headers' in call.kwargs:
                headers = call.kwargs['headers']
                if headers and header_name in headers:
                    if header_value is None or headers[header_name] == header_value:
                        return

        if header_value:
            raise AssertionError(
                f"Header {header_name} with value {header_value} was not sent"
            )
        else:
            raise AssertionError(f"Header {header_name} was not sent")
