import pytest

from crudclient.config import ClientConfig
from crudclient.testing.auth import create_custom_auth_mock
from tests.unit.client.auth_examples.common import create_mock_client


class TestCustomAuthExamples:
    """Examples of using Custom Authentication mocks."""

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
    def test_custom_auth_success_scenario(self):
        """Example of testing a successful Custom Auth scenario."""
        # Define custom auth callbacks
        def header_callback():
            return {
                "X-Custom-Auth": "custom_value",
                "X-Timestamp": "12345678"
            }

        def param_callback():
            return {"tenant": "test_tenant"}

        # Create a mock client with Custom Auth
        client = create_mock_client(
            auth_type="custom",
            auth_config={
                "header_callback": header_callback,
                "param_callback": param_callback
            }
        )

        # Configure a successful response
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/custom",
            response={"data": [{"id": 1, "name": "Custom Data"}]}
        )

        # Make a request
        response = client.get("/api/custom")

        # Verify the response
        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["name"] == "Custom Data"

        # Verify the auth headers and params were sent correctly
        assert len(client.request_history) == 1
        request = client.request_history[0]
        assert "X-Custom-Auth" in request["headers"]
        assert request["headers"]["X-Custom-Auth"] == "custom_value"
        assert "X-Timestamp" in request["headers"]
        assert request["headers"]["X-Timestamp"] == "12345678"
        assert "tenant=test_tenant" in request["path"]

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
    def test_custom_auth_failure_scenario(self):
        """Example of testing a Custom Auth failure scenario."""
        # Define a custom auth callback that will fail
        def failing_header_callback():
            raise ValueError("Failed to generate auth headers")

        # Create a mock client with failing Custom Auth
        client = create_mock_client(
            config=ClientConfig(hostname="https://api.example.com", version="v1")
        )

        # Set up the auth strategy manually
        auth_mock = create_custom_auth_mock(header_callback=failing_header_callback)
        client.config.auth_strategy = auth_mock.get_auth_strategy()

        # Configure a response (though it won't be reached)
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/custom",
            response={"data": [{"id": 1, "name": "Custom Data"}]}
        )

        # Make a request and expect it to fail
        with pytest.raises(ValueError) as excinfo:
            client.get("/api/custom")

        # Verify the error
        assert "Failed to generate auth headers" in str(excinfo.value)
