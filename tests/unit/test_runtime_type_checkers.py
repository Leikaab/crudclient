from logging import getLogger

import pytest

from crudclient.runtime_type_checkers import assert_type


class TestAssertType:
    def setup_method(self):
        # Create a logger for testing
        self.logger = getLogger("test_logger")

    def test_assert_type_optional_none(self):
        # Test when optional=True and Instance is None
        assert_type(varname="test_var", Instance=None, Class=int, logger=self.logger, optional=True)

    def test_assert_type_correct_type(self):
        # Test when Instance is of the correct type
        assert_type(varname="test_var", Instance=5, Class=int, logger=self.logger)

    def test_assert_type_incorrect_type(self):
        # Test when Instance is of the incorrect type and raises TypeError
        with pytest.raises(TypeError) as exc_info:
            assert_type(varname="test_var", Instance="string", Class=int, logger=self.logger)

        # Check the exception message
        assert "Invalid test_var provided: expected int" in str(exc_info.value)

    def test_assert_type_incorrect_type_optional(self):
        # Test when optional=True, but Instance is of the incorrect type and raises TypeError
        with pytest.raises(TypeError) as exc_info:
            assert_type(varname="test_var", Instance="string", Class=int, logger=self.logger, optional=True)

        # Check the exception message (with optional check included)
        assert "Invalid test_var provided: expected int or None" in str(exc_info.value)
