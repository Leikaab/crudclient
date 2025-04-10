"""
Tests for the base AuthStrategy class in the crudclient library.
"""


from crudclient.auth.base import AuthStrategy


# Test Base Strategy (Optional, but good practice)
class TestBaseAuthStrategy:
    def test_base_methods_not_implemented(self):
        """
        GIVEN the AuthStrategy class
        WHEN we check its methods
        THEN we verify they are abstract methods.
        """
        # We can't instantiate an abstract class, so let's just verify
        # that the methods are marked as abstract

        # Check that prepare_request_headers is an abstract method
        assert AuthStrategy.prepare_request_headers.__isabstractmethod__

        # Check that prepare_request_params is an abstract method
        assert AuthStrategy.prepare_request_params.__isabstractmethod__

        # No need for WHEN/THEN section since we're just checking if methods are abstract
