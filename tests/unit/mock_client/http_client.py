"""
Mock HTTP client for testing.
"""

from typing import Any, Dict, Optional, Union

import requests
from requests import Response

from crudclient.http.client import HttpClient
from crudclient.config import ClientConfig
from crudclient.types import RawResponseSimple

from .client import MockClient


class MockHttpClient(HttpClient):
    """
    Mock HTTP client that intercepts requests and returns mock responses.

    This class extends the real HttpClient but overrides the request methods
    to delegate to the MockClient's _request method instead of making real
    HTTP requests.
    """

    def __init__(self, config: ClientConfig, mock_client: MockClient):
        """
        Initialize the mock HTTP client.

        Args:
            config: Client configuration
            mock_client: MockClient instance to delegate requests to
        """
        super().__init__(config)
        self.mock_client = mock_client

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> RawResponseSimple:
        """Override get method to use mock client."""
        response = self.mock_client._request("GET", endpoint=endpoint, params=params, handle_response=True)
        assert isinstance(response, (dict, str, bytes, type(None)))  # Ensure it's RawResponseSimple
        return response

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """Override post method to use mock client."""
        response = self.mock_client._request(
            "POST", endpoint=endpoint, data=data, json=json, files=files, handle_response=True
        )
        assert isinstance(response, (dict, str, bytes, type(None)))  # Ensure it's RawResponseSimple
        return response

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """Override put method to use mock client."""
        response = self.mock_client._request(
            "PUT", endpoint=endpoint, data=data, json=json, files=files, handle_response=True
        )
        assert isinstance(response, (dict, str, bytes, type(None)))  # Ensure it's RawResponseSimple
        return response

    def delete(self, endpoint: str, **kwargs: Any) -> RawResponseSimple:
        """Override delete method to use mock client."""
        response = self.mock_client._request("DELETE", endpoint=endpoint, handle_response=True, **kwargs)
        assert isinstance(response, (dict, str, bytes, type(None)))  # Ensure it's RawResponseSimple
        return response

    def patch(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> RawResponseSimple:
        """Override patch method to use mock client."""
        response = self.mock_client._request(
            "PATCH", endpoint=endpoint, data=data, json=json, files=files, handle_response=True
        )
        assert isinstance(response, (dict, str, bytes, type(None)))  # Ensure it's RawResponseSimple
        return response

    def _request(
        self,
        method: str,
        endpoint: Optional[str] = None,
        url: Optional[str] = None,
        handle_response: bool = True,
        **kwargs: Any
    ) -> Union[RawResponseSimple, Response]:
        """Override _request method to use mock client."""
        return self.mock_client._request(
            method, endpoint=endpoint, url=url, handle_response=handle_response, **kwargs
        )
