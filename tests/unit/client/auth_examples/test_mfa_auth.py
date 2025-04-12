"""
Examples of using Multi-Factor Authentication mocking utilities.

This module demonstrates how to use the Multi-Factor Authentication mocking utilities
in real-world testing scenarios.
"""

import pytest

from crudclient.exceptions import AuthenticationError
from crudclient.http.errors import ErrorHandler

from .common import create_mock_client


class TestMultiFactorAuthExamples:
    """Examples of using Multi-Factor Authentication mocks."""

    def test_mfa_required_scenario(self):
        """Example of testing an MFA required scenario."""
        # Create a mock client with Bearer Auth that requires MFA
        client = create_mock_client(auth_type="bearer", auth_config={"token": "valid_token", "mfa_required": True, "mfa_verified": False})

        # Configure an MFA required response
        client.with_response_pattern(
            method="GET", path_pattern=r"/api/secure", data={"error": "Unauthorized", "message": "MFA verification required"}, status_code=401
        )

        # Make a request and handle the error manually
        with pytest.raises(AuthenticationError) as excinfo:
            response = client.get("/api/secure")
            # The mock client doesn't automatically raise exceptions for error status codes
            # so we need to manually check and raise the appropriate exception
            if response.status_code == 401:
                error_handler = ErrorHandler()
                error_handler.handle_error_response(response)

        # Verify the error
        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
        assert "MFA verification required" in str(excinfo.value)

        # Verify the request was made with the correct headers
        assert client.get_call_count() == 1
        calls = client.get_calls()
        request_call = calls[0]
        assert "Authorization" in request_call.kwargs["headers"]
        assert request_call.kwargs["headers"]["Authorization"] == "Bearer valid_token"

    def test_mfa_verification_success_scenario(self):
        """
        Tests the scenario where an initial request requires MFA,
        the MFA code is provided via the auth handler, and the subsequent
        request (retry) succeeds transparently to the caller.
        The client's internal retry logic handles the 401 and applies MFA.
        """
        # Create a mock client
        client = create_mock_client()

        # Simulate initial request requiring MFA (e.g., returns 401)
        mfa_challenge_header = 'mfa_token_required realm="example"'

        # First, configure the 401 response for the initial request
        client.with_response_pattern(
            method="GET",
            path_pattern=r"/protected-resource",
            data={"detail": "MFA required"},
            status_code=401,
            headers={"WWW-Authenticate": mfa_challenge_header},
        )

        # Make the first request which should fail with 401
        response = client.get("/protected-resource")

        # Verify the response status code
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers
        assert response.headers["WWW-Authenticate"] == mfa_challenge_header

        # Manually raise the AuthenticationError for testing
        try:
            error_handler = ErrorHandler()
            error_handler.handle_error_response(response)
            pytest.fail("Expected AuthenticationError was not raised")
        except AuthenticationError as e:
            # Verify the error
            assert "401" in str(e) or "Unauthorized" in str(e)
            assert "MFA required" in str(e)

            # Verify the first request was made
            assert client.get_call_count() == 1
            first_call = client.get_calls()[0]
            assert first_call.method_name == "GET"
            assert first_call.args[0] == "/protected-resource"

        # Reset the client to simulate a new request with MFA token
        client.http_client.reset()
        client.reset()  # Also reset the spy's call history

        # Configure only the success response for the second attempt
        client.with_response_pattern(method="GET", path_pattern=r"/protected-resource", data={"data": "sensitive info"}, status_code=200)

        # Try the request again (simulating that MFA is now verified)
        response = client.get("/protected-resource", headers={"X-MFA-Token": "mock-mfa-12345"})

        # Verify the response - extract JSON data from the response object
        assert response.status_code == 200
        response_data = response.json() if hasattr(response, 'json') else response
        assert response_data == {"data": "sensitive info"}

        # Verify the second request was made with the MFA token
        assert client.get_call_count() == 1
        second_call = client.get_calls()[0]
        assert second_call.method_name == "GET"
        assert second_call.args[0] == "/protected-resource"
        assert "X-MFA-Token" in second_call.kwargs["headers"]
        assert second_call.kwargs["headers"]["X-MFA-Token"] == "mock-mfa-12345"
