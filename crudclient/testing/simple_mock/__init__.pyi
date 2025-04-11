"""
Simple mock client for testing.

This module provides a lightweight mock client implementation for testing
API interactions without the complexity of the real HTTP client. It offers
a simple interface for configuring mock responses and asserting on request
patterns.
"""

from crudclient.testing.simple_mock.assertions import SimpleMockClientAssertions

class SimpleMockClient(SimpleMockClientAssertions):
    """
    A simple mock client that doesn't inherit from the real Client class.

    This implementation avoids all the complexities of the real HTTP client
    while providing a simple interface for testing API interactions. It allows:

    1. Configuring mock responses based on request patterns
    2. Recording request history for later verification
    3. Asserting on request patterns, sequences, and parameters

    The SimpleMockClient is particularly useful for unit tests where you want
    to isolate your code from actual HTTP interactions and verify that your
    code makes the expected API calls.
    """

    ...

__all__ = ["SimpleMockClient"]
