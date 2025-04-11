import base64
import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import requests

from crudclient.auth.base import AuthStrategy

from .models import TokenSessionResponse

# Set up logging
logger = logging.getLogger(__name__)


class TripletexAuthStrategy(AuthStrategy):
    """
    Custom authentication strategy for Tripletex API.

    This strategy handles session token management, including creation,
    expiration checking, and refreshing.
    """

    def __init__(
        self,
        company_id: str,
        consumer_token: str,
        employee_token: str,
        base_url: str,
        session_token: Optional[str] = None,
        session_expires_at: Optional[datetime] = None,
    ):
        self.company_id = company_id
        self.consumer_token = consumer_token
        self.employee_token = employee_token
        self.base_url = base_url
        self.session_token = session_token
        self.session_expires_at = session_expires_at

        # Initialize session if needed
        if not self.session_token or self.is_token_expired():
            self.refresh_token()

    def prepare_request_headers(self) -> Dict[str, str]:
        """
        Prepare headers with Basic authentication using company_id and session_token.
        """
        if self.is_token_expired():
            logger.info("Token expired, refreshing before authentication")
            self.refresh_token()

        if not self.session_token:
            logger.warning("No session token available for authentication")
            return {}

        raw = f"{self.company_id}:{self.session_token}"
        encoded = base64.b64encode(raw.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}

    def prepare_request_params(self) -> Dict[str, str]:
        """
        Tripletex authentication doesn't use query parameters.
        """
        return {}

    def is_token_expired(self) -> bool:
        """
        Check if the session token has expired.
        """
        if not self.session_token:
            logger.debug("No session token exists")
            return True
        if not isinstance(self.session_expires_at, datetime):
            logger.warning("Invalid expiration date format: %r", self.session_expires_at)
            return True

        # Make sure session_expires_at has timezone info
        expires_at = self.session_expires_at
        if expires_at.tzinfo is None:
            # Convert naive datetime to aware datetime by assuming it's in UTC
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        is_expired = datetime.now(timezone.utc) >= expires_at

        if is_expired:
            logger.info("Session token has expired at %s", self.session_expires_at)
        else:
            logger.debug("Session token valid until %s", self.session_expires_at)
        return is_expired

    def create_date(self) -> str:
        """
        Create an expiration date for the session token (tomorrow in CET).

        The API expects a full datetime in ISO format, not just a date.
        """
        # Create a datetime for tomorrow with time component (end of day)
        tomorrow_cet = (datetime.now(timezone.utc) + timedelta(days=2)).replace(hour=23, minute=59, second=59)
        # Format as ISO 8601 with timezone
        expiration_str = tomorrow_cet.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        logger.debug("Created expiration date: %s", expiration_str)
        return expiration_str

    def refresh_token(self, force=False) -> None:
        """
        Refresh the session token.
        """
        if not force and not self.is_token_expired():
            logger.debug("Skipping token refresh, current token is still valid")
            return

        logger.info("Refreshing Tripletex session token%s", " (forced)" if force else "")

        if not self.consumer_token or not self.employee_token:
            logger.error(
                "Missing required tokens for authentication. "
                "Make sure TRIPLETEX_CONSUMER_TOKEN and TRIPLETEX_EMPLOYEE_TOKEN "
                "environment variables are set"
            )
            raise ValueError("Missing required tokens for authentication")

        url = f"{self.base_url}/token/session/:create"
        params = {"consumerToken": self.consumer_token, "employeeToken": self.employee_token, "expirationDate": self.create_date()}

        logger.debug("Requesting new session token from %s", url)
        try:
            response = requests.put(url, headers={}, params=params, timeout=30)
            if response.status_code == 422:
                # Log more details about the 422 error
                logger.error("422 Unprocessable Entity error: %s", response.text)
                # Try to get more information from the response
                error_data = response.json() if response.text else {"error": "No response body"}
                logger.error("Error details: %s", error_data)

            response.raise_for_status()
            data = response.json()
            session_data = TokenSessionResponse.model_validate(data)
            self.session_token = session_data.value.token
            self.session_expires_at = session_data.value.expirationDate
            if self.session_expires_at.tzinfo is None:
                self.session_expires_at = self.session_expires_at.replace(tzinfo=timezone.utc)
            logger.info("Successfully obtained new session token, valid until %s", self.session_expires_at)
        except requests.RequestException as e:
            logger.error("Failed to refresh session token: %s", str(e), exc_info=True)
            raise
