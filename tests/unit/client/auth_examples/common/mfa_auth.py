from typing import Any, Optional

from requests.auth import AuthBase


class MockMFAAuth(AuthBase):
    """
    Mock Multi-Factor Authentication strategy for testing.

    This class simulates a Multi-Factor Authentication flow where:
    1. Initial request fails with 401 and a WWW-Authenticate challenge
    2. Client code provides an MFA token
    3. Subsequent request with the token succeeds
    """

    def __init__(self) -> None:
        """Initialize the MFA auth strategy."""
        self.mfa_token: Optional[str] = None
        self.last_challenge: Optional[str] = None  # Store the last WWW-Authenticate header

    def __call__(self, r: Any) -> Any:
        """Required by requests.auth.AuthBase but not used in our testing."""
        return r

    def handle_response_sync(self, response: Any, request: Any) -> Optional[Any]:
        """Handles 401 responses to potentially trigger MFA flow."""
        self.last_challenge = response.headers.get("WWW-Authenticate")
        if response.status_code == 401 and self.last_challenge:
            # Simulate "user" providing the token based on the challenge
            if "mfa_token_required" in self.last_challenge:
                self.mfa_token = "mock-mfa-12345"  # Simulate getting the token
                # Re-prepare the original request with the MFA token
                # Add the MFA token header for the retry attempt
                new_headers = request.headers.copy() if request.headers else {}
                new_headers["X-MFA-Token"] = self.mfa_token  # Add the token
                # Create a new request object to retry
                # Use a generic approach to avoid import issues
                new_request = type(request)(
                    method=request.method,
                    url=str(request.url),  # Ensure URL is string
                    params=request.params,
                    json=getattr(request, "json", None),  # Handle potential absence
                    data=getattr(request, "data", None),  # Handle potential absence
                    headers=new_headers,
                    extensions=getattr(request, "extensions", {}) or {},  # Preserve extensions
                )
                return new_request  # Signal to retry with this new request
        return None  # No retry needed

    def enrich_request_sync(self, request: Any) -> Any:
        """Adds MFA token header if available."""
        # This might be called before the *first* request too,
        # but handle_response_sync sets the token *after* the first failure.
        # The retry mechanism should use the request returned by handle_response_sync.
        if self.mfa_token:
            # Ensure headers exist and are mutable (or create new request)
            if hasattr(request, "headers") and isinstance(request.headers, dict):
                request.headers["X-MFA-Token"] = self.mfa_token
            else:
                # This case indicates an incompatible Request object or missing headers attribute
                pass  # Or raise TypeError("Request headers are not a mutable dict")
        return request
