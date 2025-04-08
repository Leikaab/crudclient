"""
Client spy implementation for verification-focused testing.
"""

from typing import Any, Dict, List, Optional, Type, Union, Callable

from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.types import RawResponseSimple

from .base import SpyBase


class ClientSpy(Client, SpyBase):
    """
    Spy implementation of the Client interface.

    This class records all method calls to the Client interface for verification
    in tests, while delegating to a real or mock implementation.
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
            config: Client configuration
            delegate: Optional delegate client implementation
            **kwargs: Additional arguments
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

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response
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

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            Response
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

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            Response
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

        Args:
            endpoint: API endpoint
            **kwargs: Additional arguments

        Returns:
            Response
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

        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            files: Files to upload

        Returns:
            Response
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

        Args:
            endpoint: API endpoint
        """
        for call in self.calls:
            if call.args and call.args[0] == endpoint:
                return

        raise AssertionError(f"Endpoint {endpoint} was not called")

    def assert_endpoint_called_with_method(self, method: str, endpoint: str) -> None:
        """
        Assert that an endpoint was called with a specific method.

        Args:
            method: HTTP method
            endpoint: API endpoint
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

        Args:
            method: HTTP method
            endpoint: API endpoint
            expected_json: Expected JSON payload
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
