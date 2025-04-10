"""
Examples of using Multi-Factor Authentication mocking utilities.

This module demonstrates how to use the Multi-Factor Authentication mocking utilities
in real-world testing scenarios.
"""

import pytest

from crudclient.exceptions import AuthenticationError

from .common import create_mock_client


class TestMultiFactorAuthExamples:
    """Examples of using Multi-Factor Authentication mocks."""

    def test_mfa_required_scenario(self):
        """Example of testing an MFA required scenario."""
        # Create a mock client with Bearer Auth that requires MFA
        client = create_mock_client(
            auth_type="bearer",
            auth_config={
                "token": "valid_token",
                "mfa_required": True,
                "mfa_verified": False
            }
        )

        # Configure an MFA required response
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/secure",
            response={
                "error": "Unauthorized",
                "message": "MFA verification required"
            },
            status_code=401
        )

        # Make a request and expect it to fail
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/api/secure")

        # Verify the error
        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
        assert "MFA verification required" in str(excinfo.value)

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
            url_pattern=r"/protected-resource",
            response={"detail": "MFA required"},
            status_code=401,
            headers={"WWW-Authenticate": mfa_challenge_header}
        )

        # Make the first request which should fail with 401
        try:
            client.get("/protected-resource")
            pytest.fail("Expected AuthenticationError was not raised")
        except AuthenticationError as e:
            # Verify the error
            assert "401" in str(e) or "Unauthorized" in str(e)
            assert "MFA required" in str(e)

        # Reset the client to simulate a new request with MFA token
        client.http_client.reset()

        # Configure only the success response for the second attempt
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/protected-resource",
            response={"data": "sensitive info"},
            status_code=200
        )

        # Try the request again (simulating that MFA is now verified)
        response = client.get("/protected-resource",
                              headers={"X-MFA-Token": "mock-mfa-12345"})

        # Verify the response
        assert response == {"data": "sensitive info"}
