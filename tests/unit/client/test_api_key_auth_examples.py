import pytest

from tests.unit.client.auth_examples.common import create_mock_client


class TestApiKeyAuthExamples:
    """Examples of using API Key Authentication mocks."""

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
    def test_api_key_header_auth_success_scenario(self):
        """Example of testing a successful API Key header auth scenario."""
        # Create a mock client with API Key header auth
        client = create_mock_client(
            auth_type="apikey",
            auth_config={
                "api_key": "valid_api_key",
                "header_name": "X-API-Key"
            }
        )

        # Configure a successful response
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/data",
            response={"data": [{"id": 1, "value": "Test Data"}]}
        )

        # Make a request
        response = client.get("/api/data")

        # Verify the response
        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["value"] == "Test Data"

        # Verify the auth header was sent correctly
        assert len(client.request_history) == 1
        request = client.request_history[0]
        assert "X-API-Key" in request["headers"]
        assert request["headers"]["X-API-Key"] == "valid_api_key"

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
    def test_api_key_param_auth_success_scenario(self):
        """Example of testing a successful API Key param auth scenario."""
        # Create a mock client with API Key param auth
        client = create_mock_client(
            auth_type="apikey",
            auth_config={
                "api_key": "valid_api_key",
                "param_name": "api_key"
            }
        )

        # Configure a successful response
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/data",
            response={"data": [{"id": 1, "value": "Test Data"}]}
        )

        # Make a request
        response = client.get("/api/data")

        # Verify the response
        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["value"] == "Test Data"

        # Verify the auth param was sent correctly
        assert len(client.request_history) == 1
        request = client.request_history[0]
        assert "api_key=valid_api_key" in request["path"]
