from typing import Any, Dict, Optional

class MockResponse:
    """
    A mock object simulating an HTTP response, typically from libraries like requests or httpx.

    Used in testing scenarios to provide controlled response data without making actual network calls.
    """

    status_code: int
    text: Optional[str]
    headers: Dict[str, str]
    json_data: Optional[Dict[str, Any]]

    def __init__(
        self,
        status_code: int,
        json_data: Optional[Dict[str, Any]] = None,
        text: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initializes the MockResponse.

        Args:
            status_code: The HTTP status code for the mock response.
            json_data: A dictionary representing the JSON body of the response.
            text: A string representing the raw text body of the response.
            headers: A dictionary representing the response headers.
        """
        ...

    def json(self) -> Optional[Dict[str, Any]]:
        """
        Returns the JSON data provided during initialization.

        Returns:
            The dictionary passed as json_data, or None if none was provided.
        """
        ...
