"""
Tests for Basic Authentication failure handling in the crudclient library.
"""

import pytest

from crudclient.exceptions import AuthenticationError


def test_basic_auth_failure(basic_auth_client, mock_request):
    """Test handling of Basic Authentication failures."""
    url = f"{basic_auth_client.base_url}/users"
    mock_request.get(url, status_code=401, json={"error": "Unauthorized", "message": "Invalid credentials"})

    with pytest.raises(AuthenticationError) as excinfo:
        basic_auth_client.get("/users")

    assert excinfo.value.response is not None
    assert excinfo.value.response.status_code == 401
    assert excinfo.value.response.json()["message"] == "Invalid credentials"

    request = mock_request.request_history[0]
    assert "Authorization" in request.headers
    assert request.headers["Authorization"].startswith("Basic ")
