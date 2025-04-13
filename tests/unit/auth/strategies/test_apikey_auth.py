"""
Tests for the ApiKeyAuth strategy in the crudclient library.
"""

import pytest

from crudclient.auth.custom import ApiKeyAuth


class TestApiKeyAuth:
    def test_header_auth(self):
        """
        GIVEN an ApiKeyAuth instance configured for header authentication
        WHEN prepare_request_headers and prepare_request_params are called
        THEN the correct header is returned, params are empty, and attributes match.
        """
        # GIVEN
        auth = ApiKeyAuth(api_key="test_key", header_name="X-API-Key")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {"X-API-Key": "test_key"}
        assert params == {}
        assert auth.api_key == "test_key"
        assert auth.header_name == "X-API-Key"
        assert auth.param_name is None

    def test_param_auth(self):
        """
        GIVEN an ApiKeyAuth instance configured for parameter authentication
        WHEN prepare_request_headers and prepare_request_params are called
        THEN headers are empty, the correct param is returned, and attributes match.
        """
        # GIVEN
        auth = ApiKeyAuth(api_key="test_key", param_name="api_key")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {}
        assert params == {"api_key": "test_key"}
        assert auth.api_key == "test_key"
        assert auth.header_name is None
        assert auth.param_name == "api_key"  # type: ignore[unreachable]

    def test_both_header_and_param_auth_raises(self):
        """
        GIVEN ApiKeyAuth initialization arguments for both header and param
        WHEN ApiKeyAuth is instantiated
        THEN a ValueError is raised.
        """
        # GIVEN / WHEN / THEN
        with pytest.raises(ValueError, match="Only one of header_name or param_name"):
            ApiKeyAuth(api_key="test_key", header_name="X-API-Key", param_name="api_key")

    def test_neither_header_nor_param_auth_raises(self):
        """
        GIVEN ApiKeyAuth initialization arguments for neither header nor param
        WHEN ApiKeyAuth is instantiated
        THEN a ValueError is raised.
        """
        # GIVEN / WHEN / THEN
        with pytest.raises(ValueError, match="One of header_name or param_name"):
            ApiKeyAuth(api_key="test_key")

    def test_empty_key_header(self):
        """
        GIVEN an ApiKeyAuth instance for header auth with an empty key
        WHEN prepare_request_headers is called
        THEN the header value is an empty string.
        """
        # GIVEN
        auth = ApiKeyAuth(api_key="", header_name="X-API-Key")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {"X-API-Key": ""}
        assert params == {}

    def test_empty_key_param(self):
        """
        GIVEN an ApiKeyAuth instance for param auth with an empty key
        WHEN prepare_request_params is called
        THEN the param value is an empty string.
        """
        # GIVEN
        auth = ApiKeyAuth(api_key="", param_name="api_key")

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {}
        assert params == {"api_key": ""}
