"""
Tests for the CustomAuth strategy in the crudclient library.
"""

from typing import Dict

import pytest

from crudclient.auth.custom import CustomAuth


class TestCustomAuth:
    def test_header_callback(self):
        """
        GIVEN a CustomAuth instance with only a header callback
        WHEN prepare_request_headers and prepare_request_params are called
        THEN the header callback is used, params are empty, and attributes match.
        """
        # GIVEN
        def get_headers() -> Dict[str, str]:
            return {"X-Custom-Auth": "custom_value"}

        auth = CustomAuth(header_callback=get_headers)

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {"X-Custom-Auth": "custom_value"}
        assert params == {}
        assert auth.header_callback == get_headers
        assert auth.param_callback is None

    def test_param_callback(self):
        """
        GIVEN a CustomAuth instance with both header and param callbacks
        WHEN prepare_request_headers and prepare_request_params are called
        THEN both callbacks are used correctly and attributes match.
        """
        # GIVEN
        def get_headers() -> Dict[str, str]:
            return {"X-Custom-Auth": "custom_value"}

        def get_params() -> Dict[str, str]:
            return {"custom_param": "param_value"}

        auth = CustomAuth(header_callback=get_headers, param_callback=get_params)

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {"X-Custom-Auth": "custom_value"}
        assert params == {"custom_param": "param_value"}
        assert auth.header_callback == get_headers
        assert auth.param_callback == get_params

    def test_only_param_callback(self):
        """
        GIVEN a CustomAuth instance with only a param callback
        WHEN prepare_request_headers and prepare_request_params are called
        THEN headers are empty, the param callback is used, and attributes match.
        """
        # GIVEN
        def get_params() -> Dict[str, str]:
            return {"custom_param": "param_value"}

        auth = CustomAuth(param_callback=get_params)  # type: ignore[call-arg]

        # WHEN
        headers = auth.prepare_request_headers()
        params = auth.prepare_request_params()

        # THEN
        assert headers == {}
        assert params == {"custom_param": "param_value"}
        assert auth.header_callback is None
        assert auth.param_callback == get_params  # type: ignore[unreachable]

    def test_no_callbacks_raises(self):
        """
        GIVEN no callbacks provided to CustomAuth
        WHEN CustomAuth is instantiated
        THEN a ValueError is raised.
        """
        # GIVEN / WHEN / THEN
        with pytest.raises(ValueError, match="At least one callback must be provided"):
            CustomAuth()  # type: ignore[call-arg]

    def test_header_callback_invalid_return_type(self):
        """
        GIVEN a CustomAuth instance with a header callback returning an invalid type
        WHEN prepare_request_headers is called
        THEN a TypeError is raised.
        """
        # GIVEN
        def get_headers_invalid() -> str:
            return "not_a_dict"

        auth = CustomAuth(header_callback=get_headers_invalid)  # type: ignore[arg-type]

        # WHEN / THEN
        with pytest.raises(TypeError, match="Header callback must return a dictionary"):
            auth.prepare_request_headers()

    def test_param_callback_invalid_return_type(self):
        """
        GIVEN a CustomAuth instance with a param callback returning an invalid type
        WHEN prepare_request_params is called
        THEN a TypeError is raised.
        """
        # GIVEN
        def get_params_invalid() -> list:
            return ["not_a_dict"]

        auth = CustomAuth(param_callback=get_params_invalid)  # type: ignore[call-arg, arg-type]

        # WHEN / THEN
        with pytest.raises(TypeError, match="Parameter callback must return a dictionary"):
            auth.prepare_request_params()
