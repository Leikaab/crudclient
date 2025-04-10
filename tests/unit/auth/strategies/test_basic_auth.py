"""
Tests for the BasicAuth strategy in the crudclient library.
"""

import base64

from crudclient.auth.basic import BasicAuth


class TestBasicAuth:
    def test_prepare_request_headers(self):
        """
        GIVEN a BasicAuth instance with username and password
        WHEN prepare_request_headers is called
        THEN the correct Basic Authorization header is returned and params are empty.
        """
        # GIVEN
        auth = BasicAuth(username="user", password="pass")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        expected_token = base64.b64encode(b"user:pass").decode("ascii")
        assert headers == {"Authorization": f"Basic {expected_token}"}
        assert params == {}

    def test_empty_credentials(self):
        """
        GIVEN a BasicAuth instance with empty username and password
        WHEN prepare_request_headers is called
        THEN the Basic Authorization header for empty credentials is returned.
        """
        # GIVEN
        auth = BasicAuth(username="", password="")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        expected_token = base64.b64encode(b":").decode("ascii")
        assert headers == {"Authorization": f"Basic {expected_token}"}
        assert params == {}

    def test_only_username(self):
        """
        GIVEN a BasicAuth instance with only a username
        WHEN prepare_request_headers is called
        THEN the Basic Authorization header includes the username and colon.
        """
        # GIVEN
        auth = BasicAuth(username="user", password="")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        expected_token = base64.b64encode(b"user:").decode("ascii")
        assert headers == {"Authorization": f"Basic {expected_token}"}
        assert params == {}

    def test_only_password(self):
        """
        GIVEN a BasicAuth instance with only a password
        WHEN prepare_request_headers is called
        THEN the Basic Authorization header includes the colon and password.
        """
        # GIVEN
        auth = BasicAuth(username="", password="pass")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        expected_token = base64.b64encode(b":pass").decode("ascii")
        assert headers == {"Authorization": f"Basic {expected_token}"}
        assert params == {}
