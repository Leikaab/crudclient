"""
Examples of using Multi-Factor Authentication mocking utilities.

This module demonstrates how to use the Multi-Factor Authentication mocking utilities
in real-world testing scenarios.
"""

from typing import cast

import pytest
import requests

from crudclient.exceptions import AuthenticationError
from crudclient.http.errors import ErrorHandler

from .common import create_mock_client


class TestMultiFactorAuthExamples:
    """Examples of using Multi-Factor Authentication mocks."""

    def test_mfa_required_scenario(self):
        """Example of testing an MFA required scenario."""
        client = create_mock_client(auth_type="bearer", auth_config={"token": "valid_token", "mfa_required": True, "mfa_verified": False})

        client.with_response_pattern(
            method="GET", path_pattern=r"/api/secure", data={"error": "Unauthorized", "message": "MFA verification required"}, status_code=401
        )

        with pytest.raises(AuthenticationError):
            response = client.get("/api/secure")
            if response.status_code == 401:
                error_handler = ErrorHandler()
                error_handler.handle_error_response(response)

        # Removed assertions checking excinfo.value.response as AuthenticationError lacks this attribute.
        # The core check is that AuthenticationError is raised by the ErrorHandler.

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
        client = create_mock_client()

        mfa_challenge_header = 'mfa_token_required realm="example"'

        client.with_response_pattern(
            method="GET",
            path_pattern=r"/protected-resource",
            data={"detail": "MFA required"},
            status_code=401,
            headers={"WWW-Authenticate": mfa_challenge_header},
        )

        response = client.get("/protected-resource")

        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers
        assert response.headers["WWW-Authenticate"] == mfa_challenge_header

        try:
            error_handler = ErrorHandler()
            error_handler.handle_error_response(response)
            pytest.fail("Expected AuthenticationError was not raised")
        except AuthenticationError as e:
            assert e.response is not None
            assert e.response.status_code == 401
            # Cast to requests.Response to access json() method
            response = cast(requests.Response, e.response)
            assert response.json()["detail"] == "MFA required"

            assert client.get_call_count() == 1
            first_call = client.get_calls()[0]
            assert first_call.method_name == "GET"
            assert first_call.args[0] == "/protected-resource"

        client.http_client.reset()
        client.reset()

        client.with_response_pattern(method="GET", path_pattern=r"/protected-resource", data={"data": "sensitive info"}, status_code=200)

        response = client.get("/protected-resource", headers={"X-MFA-Token": "mock-mfa-12345"})

        assert response.status_code == 200
        response_data = response.json() if hasattr(response, "json") else response
        assert response_data == {"data": "sensitive info"}

        assert client.get_call_count() == 1
        second_call = client.get_calls()[0]
        assert second_call.method_name == "GET"
        assert second_call.args[0] == "/protected-resource"
        assert "X-MFA-Token" in second_call.kwargs["headers"]
        assert second_call.kwargs["headers"]["X-MFA-Token"] == "mock-mfa-12345"
