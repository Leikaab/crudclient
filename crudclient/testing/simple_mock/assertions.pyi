"""
Simple mock client assertion methods for testing.

This module provides assertion methods for the SimpleMockClient, allowing
verification of request patterns, sequences, and parameters in tests.
"""

import re
from typing import Any, Dict, List, Optional

from crudclient.testing.crud.request_record import RequestRecord
from crudclient.testing.simple_mock.request_handling import (
    SimpleMockClientRequestHandling,
)

class SimpleMockClientAssertions(SimpleMockClientRequestHandling):
    """
    Assertion methods for the simple mock client.

    This class extends SimpleMockClientRequestHandling to provide methods for
    verifying that requests were made with expected patterns, sequences, and
    parameters. These methods are useful for testing that code interacts with
    APIs in the expected way.
    """

    def assert_request_count(self, count: int, method: Optional[str] = None, url_pattern: Optional[str] = None) -> None:
        """
        Assert that a specific number of matching requests were made.

        This method verifies that the number of requests matching the specified
        criteria (method and/or URL pattern) matches the expected count.

        Args:
            count: Expected number of matching requests
            method: Optional HTTP method to filter by (e.g., GET, POST)
            url_pattern: Optional regex pattern to match request URLs

        Raises:
            AssertionError: If the actual count doesn't match the expected count
        """
        ...

    def assert_request_sequence(self, sequence: List[Dict[str, Any]], strict: bool = False) -> None:
        """
        Assert that requests were made in a specific sequence.

        This method verifies that requests matching the specified sequence
        were made in the expected order. In non-strict mode, it checks for
        the sequence as a subsequence of all requests. In strict mode, it
        requires an exact match of the entire request history.

        Args:
            sequence: List of request matchers, each containing 'method' and/or 'url_pattern'
            strict: If True, requires exact match of entire request history

        Raises:
            AssertionError: If the sequence wasn't found in the request history
        """
        ...

    def assert_request_params(
        self, params: Dict[str, Any], method: Optional[str] = None, url_pattern: Optional[str] = None, match_all: bool = False
    ) -> None:
        """
        Assert that requests were made with specific parameters.

        This method verifies that requests matching the specified criteria
        (method and/or URL pattern) were made with the expected parameters.

        Args:
            params: Dictionary of expected parameter names and values
            method: Optional HTTP method to filter by (e.g., GET, POST)
            url_pattern: Optional regex pattern to match request URLs
            match_all: If True, all matching requests must have the parameters;
                      if False, at least one matching request must have them

        Raises:
            AssertionError: If no matching requests are found or if the
                           parameter requirements aren't met
        """
        ...

    def _filter_requests(self, method: Optional[str] = None, url_pattern: Optional[str] = None) -> List[RequestRecord]:
        """
        Filter request history by method and URL pattern.

        This internal method filters the request history based on the
        specified criteria, returning only the matching requests.

        Args:
            method: Optional HTTP method to filter by (e.g., GET, POST)
            url_pattern: Optional regex pattern to match request URLs

        Returns:
            List of RequestRecord objects matching the criteria
        """
        ...
