import pytest

from crudclient.exceptions import AuthenticationError
from tests.unit.client.auth_examples.common import create_mock_client


class TestMultiFactorAuthExamples:
    """Examples of using Multi-Factor Authentication mocks."""

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
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

    @pytest.mark.skip(reason="Test needs to be updated to work with the new testing module")
    def test_mfa_verification_success_scenario(self):
        """Example of testing a successful MFA verification scenario."""
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

        # Configure an MFA verification response
        client.with_response_pattern(
            method="POST",
            url_pattern=r"/api/mfa/verify",
            response={
                "status": "success",
                "message": "MFA verified successfully"
            }
        )

        # Configure a successful response after MFA verification
        client.with_response_pattern(
            method="GET",
            url_pattern=r"/api/secure",
            response={"data": [{"id": 1, "name": "Secure Data"}]},
            headers={"X-MFA-Verified": "true"}
        )

        # First attempt will fail with 401
        with pytest.raises(AuthenticationError) as excinfo:
            client.get("/api/secure")

        # Verify the error
        assert "401" in str(excinfo.value) or "Unauthorized" in str(excinfo.value)
        assert "MFA verification required" in str(excinfo.value)

        # Now verify MFA
        mfa_response = client.post("/api/mfa/verify", json={
            "code": "123456"
        })

        # Verify the MFA response
        assert mfa_response["status"] == "success"

        # Update the client's headers to include MFA verification
        client.http_client.session_manager.session.headers["X-MFA-Verified"] = "true"

        # Try the request again with MFA verified
        response = client.get("/api/secure")

        # Verify the response
        assert "data" in response
        assert len(response["data"]) == 1
        assert response["data"][0]["name"] == "Secure Data"
