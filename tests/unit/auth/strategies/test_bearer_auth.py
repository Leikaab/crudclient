"""
Tests for the BearerAuth strategy in the crudclient library.
"""

from crudclient.auth.bearer import BearerAuth


class TestBearerAuth:
    def test_prepare_request_headers(self):
        """
        GIVEN a BearerAuth instance with a token
        WHEN prepare_request_headers is called
        THEN the correct Authorization header is returned and params are empty.
        """
        # GIVEN
        auth = BearerAuth(token="test_token")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {"Authorization": "Bearer test_token"}
        assert params == {}

    def test_empty_token(self):
        """
        GIVEN a BearerAuth instance with an empty token
        WHEN prepare_request_headers is called
        THEN the Authorization header includes 'Bearer ' and params are empty.
        """
        # GIVEN
        auth = BearerAuth(token="")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {"Authorization": "Bearer "}
        assert params == {}

    def test_header_case_insensitivity_provided(self):
        """
        GIVEN a BearerAuth instance
        WHEN prepare_request_headers is called
        THEN the 'Authorization' header key uses standard capitalization.
        """
        # GIVEN
        # Although HTTP headers are case-insensitive, we should store/send exactly as provided
        auth = BearerAuth(token="test_token")

        # WHEN
        headers = auth.prepare_request_headers()

        # THEN
        # We expect the standard "Authorization" capitalization
        assert "Authorization" in headers
        assert "authorization" not in headers  # Check it wasn't lowercased
        assert headers["Authorization"] == "Bearer test_token"
