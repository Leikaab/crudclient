"""
Examples of using Custom Authentication mocking utilities.

This module demonstrates how to use the Custom Authentication mocking utilities
in real-world testing scenarios.
"""

from typing import Callable, cast

import pytest

from crudclient.config import ClientConfig
from crudclient.testing.auth.custom_auth_mock import CustomAuthMock

from .common import create_mock_client


class TestCustomAuthExamples:
    """Examples of using Custom Authentication mocks."""

    def test_custom_auth_success_scenario(self) -> None:
        """Example of testing a successful Custom Auth scenario."""

        # Define custom auth callbacks
        def header_callback() -> dict[str, str]:
            return {"X-Custom-Auth": "custom_value", "X-Timestamp": "12345678"}

        def param_callback() -> dict[str, str]:
            return {"tenant": "test_tenant"}

        # Create a mock client with Custom Auth
        client = create_mock_client(auth_type="custom", auth_config={"header_callback": header_callback, "param_callback": param_callback})

        # Configure a successful response
        client.with_response_pattern(method="GET", path_pattern=r"/api/custom", data={"data": [{"id": 1, "name": "Custom Data"}]})

        # Make a request
        response = client.get("/api/custom")

        # Verify the response
        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["name"] == "Custom Data"

        # Verify the auth headers and params were sent correctly
        assert client.get_call_count() == 1
        request = client.get_calls()[0]
        assert "X-Custom-Auth" in request.kwargs["headers"]
        assert request.kwargs["headers"]["X-Custom-Auth"] == "custom_value"
        assert "X-Timestamp" in request.kwargs["headers"]
        assert request.kwargs["headers"]["X-Timestamp"] == "12345678"
        # Assuming 'path' contains the full URL or path with params
        assert request.kwargs["params"].get("tenant") == "test_tenant"

    def test_custom_auth_failure_scenario(self) -> None:
        """Example of testing a Custom Auth failure scenario."""

        # Define a custom auth callback that will fail
        def failing_header_callback() -> None:
            raise ValueError("Failed to generate auth headers")

        # Create a mock client with failing Custom Auth
        client = create_mock_client(config=ClientConfig(hostname="https://api.example.com", version="v1"))

        # Set up the auth strategy manually
        auth_mock = CustomAuthMock(header_callback=cast(Callable[[], dict[str, str]], failing_header_callback))
        client.set_auth_strategy(auth_mock.get_auth_strategy())

        # Configure a response (though it won't be reached)
        client.with_response_pattern(method="GET", path_pattern=r"/api/custom", data={"data": [{"id": 1, "name": "Custom Data"}]})

        # Make a request and expect it to fail
        from apiconfig.exceptions.auth import AuthStrategyError

        with pytest.raises(AuthStrategyError) as excinfo:
            client.get("/api/custom")

        # Verify the error
        assert "Failed to generate auth headers" in str(excinfo.value)
