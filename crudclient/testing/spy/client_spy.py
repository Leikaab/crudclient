"""
Client spy implementation for verification-focused testing.

This module provides a spy implementation of the Client interface that records
all method calls for later verification in tests. It can be used to verify
that specific client methods were called with the expected arguments.
"""

from typing import Any, Dict, Optional, Union

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.types import RawResponseSimple

from .base import SpyBase


class ClientSpy(Client, SpyBase):
    """
    Spy implementation of the Client interface.

    This class records all method calls to the Client interface for verification
    in tests, while delegating to a real or mock implementation. It can be used
    to verify that specific HTTP methods were called with the expected arguments,
    without affecting the actual behavior of the client.

    Example:
        >>> from crudclient.testing.spy import ClientSpy
        >>> from crudclient.config import ClientConfig
        >>> client_spy = ClientSpy(ClientConfig(hostname="https://api.example.com"))
        >>> client_spy.get("/users")
        >>> client_spy.assert_endpoint_called("/users")
        >>> client_spy.assert_endpoint_called_with_method("get", "/users")
    """

    def __init__(
        self,
        config: Union[ClientConfig, Dict[str, Any]],
        delegate: Optional[Client] = None,
        **kwargs: Any
    ):
        """
        Initialize the client spy.

        Args:
            config: Client configuration object or dictionary with configuration parameters.
                This is used to initialize the client.
            delegate: Optional delegate client implementation to forward method calls to.
                If not provided, the parent class implementation will be used.
            **kwargs: Additional arguments to pass to the Client constructor.
        """
        Client.__init__(self, config, **kwargs)
        SpyBase.__init__(self)

        # Create a delegate client if not provided
        self.delegate = delegate or super()

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> RawResponseSimple:
        """
        Record and delegate GET request.

        This method records the call to get with the provided
        arguments and delegates to the delegate implementation.

        Args:
            endpoint: API endpoint path
            params: Optional query parameters

        Returns:
            Response from the API
        """
        try:
            result = self.delegate.get(endpoint, params)
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
        Record and delegate POST request.

        This method records the call to post with the provided
        arguments and delegates to the delegate implementation.

        Args:
            endpoint: API endpoint path
            data: Optional form data
            json: Optional JSON data
            files: Optional files to upload

        Returns:
            Response from the API
        """
        try:
            result = self.delegate.post(endpoint, data, json, files)
            self._record_call(
                'post',
                (endpoint,),
                {'data': data, 'json': json, 'files': files},
                result
            )
            return result
        except Exception as e:
            self._record_call(
                'post',
                (endpoint,),
                {'data': data, 'json': json, 'files': files},
                exception=e
            )
            raise

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """
        Record and delegate PUT request.

        This method records the call to put with the provided
        arguments and delegates to the delegate implementation.

        Args:
            endpoint: API endpoint path
            data: Optional form data
            json: Optional JSON data
            files: Optional files to upload

        Returns:
            Response from the API
        """
        try:
            result = self.delegate.put(endpoint, data, json, files)
            self._record_call(
                'put',
                (endpoint,),
                {'data': data, 'json': json, 'files': files},
                result
            )
            return result
        except Exception as e:
            self._record_call(
                'put',
                (endpoint,),
                {'data': data, 'json': json, 'files': files},
                exception=e
            )
            raise

    def delete(self, endpoint: str, **kwargs: Any) -> RawResponseSimple:
        """
        Record and delegate DELETE request.

        This method records the call to delete with the provided
        arguments and delegates to the delegate implementation.

        Args:
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to the request

        Returns:
            Response from the API
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
        Record and delegate PATCH request.

        This method records the call to patch with the provided
        arguments and delegates to the delegate implementation.

        Args:
            endpoint: API endpoint path
            data: Optional form data
            json: Optional JSON data
            files: Optional files to upload

        Returns:
            Response from the API
        """
        try:
            result = self.delegate.patch(endpoint, data, json, files)
            self._record_call(
                'patch',
                (endpoint,),
                {'data': data, 'json': json, 'files': files},
                result
            )
            return result
        except Exception as e:
            self._record_call(
                'patch',
                (endpoint,),
                {'data': data, 'json': json, 'files': files},
                exception=e
            )
            raise

    # Helper methods for verification

    def assert_endpoint_called(self, endpoint: str) -> None:
        """
        Assert that an endpoint was called.

        This method checks if any HTTP method was called with the specified endpoint.

        Args:
            endpoint: API endpoint path to check

        Raises:
            AssertionError: If the endpoint was not called
        """
        for call in self.calls:
            if call.args and call.args[0] == endpoint:
                return

        raise AssertionError(f"Endpoint {endpoint} was not called")

    def assert_endpoint_called_with_method(self, method: str, endpoint: str) -> None:
        """
        Assert that an endpoint was called with a specific method.

        This method checks if the specified HTTP method was called with the specified endpoint.

        Args:
            method: HTTP method name (get, post, put, delete, patch)
            endpoint: API endpoint path to check

        Raises:
            AssertionError: If the endpoint was not called with the specified method
        """
        for call in self.calls:
            if call.method_name == method and call.args and call.args[0] == endpoint:
                return

        raise AssertionError(f"Endpoint {endpoint} was not called with method {method}")

    def assert_json_payload_sent(
        self,
        method: str,
        endpoint: str,
        expected_json: Any
    ) -> None:
        """
        Assert that a JSON payload was sent to an endpoint.

        This method checks if the specified HTTP method was called with the specified endpoint
        and JSON payload.

        Args:
            method: HTTP method name (post, put, patch)
            endpoint: API endpoint path to check
            expected_json: Expected JSON payload

        Raises:
            AssertionError: If the JSON payload was not sent to the endpoint with the specified method
        """
        for call in self.calls:
            if (
                call.method_name == method
                and call.args and call.args[0] == endpoint
                and 'json' in call.kwargs and call.kwargs['json'] == expected_json
            ):
                return

        raise AssertionError(
            f"JSON payload {expected_json} was not sent to {endpoint} "
            f"with method {method}"
        )
