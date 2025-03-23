from typing import Any, Dict, Literal, Optional

class ClientConfig:
    """
    Generic configuration class for API clients.

    Provides common settings for hostname, versioning, authentication,
    retry behavior, and request timeouts. Designed to be subclassed
    for specific APIs that require token refresh, session handling, or
    additional logic.

    Attributes:
        hostname (Optional[str]): Base hostname of the API (e.g., "https://api.example.com").
        version (Optional[str]): API version to be appended to the base URL (e.g., "v1").
        api_key (Optional[str]): Credential or token used for authentication.
        headers (Dict[str, str]): Optional default headers for every request.
        timeout (float): Timeout for each request in seconds (default: 10.0).
        retries (int): Number of retry attempts for failed requests (default: 3).
        auth_type (Literal["bearer", "basic", "none"]): Authentication scheme.
    """

    hostname: Optional[str]
    version: Optional[str]
    api_key: Optional[str]
    headers: Optional[Dict[str, str]]
    timeout: float
    retries: int
    auth_type: Literal["bearer", "basic", "none"]

    def __init__(
        self,
        hostname: Optional[str] = ...,
        version: Optional[str] = ...,
        api_key: Optional[str] = ...,
        headers: Optional[Dict[str, str]] = ...,
        timeout: Optional[float] = ...,
        retries: Optional[int] = ...,
        auth_type: Optional[Literal["bearer", "basic", "none"]] = ...,
    ) -> None: ...
    @property
    def base_url(self) -> str:
        """
        Returns the full base URL by joining hostname and version.

        Raises:
            ValueError: If hostname is not set.

        Returns:
            str: Complete base URL to use in requests.
        """
        ...

    def get_auth_token(self) -> Optional[str]:
        """
        Returns the raw authentication token or credential.

        Override this in subclasses to implement dynamic or refreshable tokens.

        Returns:
            Optional[str]: Token or credential used for authentication.
        """
        ...

    def get_auth_header_name(self) -> str:
        """
        Returns the name of the HTTP header used for authentication.

        Override if the API uses non-standard auth headers.

        Returns:
            str: Name of the header (default: "Authorization").
        """
        ...

    def auth(self) -> Dict[str, Any]:
        """
        Builds the authentication headers to use in requests.

        Behavior depends on `auth_type`:
            - "bearer": Returns {'Authorization': 'Bearer <token>'}
            - "basic": Returns {'Authorization': 'Basic <token>'}
            - "none": Returns {}
            - other/custom: Returns {'Authorization': <token>}

        Returns:
            Dict[str, Any]: Headers to include in requests.
        """
        ...

    def prepare(self) -> None:
        """
        Hook for pre-request setup logic.

        Override in subclasses to implement setup steps such as refreshing tokens,
        validating credentials, or preparing session context.

        This method is called once at client startup.
        """
        ...

    def should_retry_on_403(self) -> bool:
        """
        Indicates whether the client should retry once after a 403 Forbidden response.

        Override in subclasses to enable fallback retry logic, typically used in APIs
        where sessions or tokens may expire and require refresh.

        Returns:
            bool: True to enable 403 retry, False by default.
        """
        ...

    def handle_403_retry(self, client: Any) -> None:
        """
        Hook to handle 403 response fallback logic (e.g. token/session refresh).

        Called once when a 403 response is received and `should_retry_on_403()` returns True.
        The method may update headers, refresh tokens, or mutate session state.

        Args:
            client: Reference to the API client instance making the request.
        """
        ...
