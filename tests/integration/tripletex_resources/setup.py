import base64
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union

import requests
from dotenv import load_dotenv

from crudclient.api import API
from crudclient.auth.base import AuthStrategy
from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.crud import Crud, ModelDumpable
from crudclient.types import JSONDict

from .models import Country, CountryResponse, Supplier, SupplierResponse, TokenSessionResponse

T = TypeVar("T", bound=ModelDumpable)

# Load environment variables from .env file
load_dotenv()

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
        session_expires_at: Optional[datetime] = None
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
        params = {
            "consumerToken": self.consumer_token,
            "employeeToken": self.employee_token,
            "expirationDate": self.create_date()
        }

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


class TripletexConfig(ClientConfig):
    """
    Configuration for Tripletex API client.
    """
    hostname = "https://tripletex.no/"
    version = "v2"
    company_id = "0"

    def __init__(self):
        super().__init__()
        consumer_token = os.getenv("TRIPLETEX_CONSUMER_TOKEN", "")
        employee_token = os.getenv("TRIPLETEX_EMPLOYEE_TOKEN", "")

        self.auth_strategy = TripletexAuthStrategy(
            company_id=self.company_id,
            consumer_token=consumer_token,
            employee_token=employee_token,
            base_url=self.base_url
        )

    def should_retry_on_403(self) -> bool:
        """
        Allow retry on 403 responses.
        """
        logger.debug("403 received, allowing retry with token refresh")
        return True

    def handle_403_retry(self, client) -> None:
        """
        Handle 403 response by forcing token refresh.
        """
        logger.warning("Handling 403 response by forcing token refresh")
        if isinstance(self.auth_strategy, TripletexAuthStrategy):
            self.auth_strategy.refresh_token(force=True)


class TripletexTestConfig(TripletexConfig):
    """
    Configuration for Tripletex test API client.
    """
    hostname = "https://api-test.tripletex.tech/"

    def __init__(self):
        # Call grandparent's __init__ to set up basic config, skipping parent's __init__
        super(ClientConfig, self).__init__()

        # Use test tokens
        consumer_token = os.getenv("TRIPLETEX_TEST_CONSUMER_TOKEN", "")
        employee_token = os.getenv("TRIPLETEX_TEST_EMPLOYEE_TOKEN", "")

        self.auth_strategy = TripletexAuthStrategy(
            company_id=self.company_id,
            consumer_token=consumer_token,
            employee_token=employee_token,
            base_url=self.base_url
        )


class TripletexCrud(Crud[T], Generic[T]):
    """
    Base class for Tripletex CRUD operations.

    This class extends the generic Crud class with Tripletex-specific functionality.
    """

    def _validate_response(self, response_data: Any) -> Dict[str, Any]:
        """
        Override the default _validate_response method to handle the nested response structure.

        Tripletex API returns data in the 'value' field of the response.
        """
        if isinstance(response_data, dict) and "value" in response_data:
            return response_data["value"]
        return response_data

    def _validate_list_return(self, response_data: dict) -> List[T]:
        """
        Validate and extract the list of items from the response data.

        Tripletex API returns items in the 'values' field of the response.
        """
        if not isinstance(response_data, dict):
            raise ValueError(f"Expected dict response, got {type(response_data)}")

        if "values" not in response_data:
            raise ValueError(f"Expected 'values' in response, got keys: {list(response_data.keys())}")

        values = response_data["values"]
        if not isinstance(values, list):
            raise ValueError(f"Expected list in 'values', got {type(values)}")

        # For simplicity in this example, we'll just return the raw values
        # In a real implementation, you would convert these to model objects
        return values

    def listcreate(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create multiple resources in a single request.

        Args:
            data_list: A list of dictionaries containing the data for each resource to create.

        Returns:
            A list of the created resources.
        """
        endpoint = self._get_endpoint()
        payload = {"values": data_list}
        response = self.client.post(endpoint + "/list", json=payload)

        if isinstance(response, dict) and "values" in response:
            return response["values"]

        return []

    def listupdate(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Update multiple resources in a single request.

        Args:
            data_list: A list of dictionaries containing the data for each resource to update.
                       Each dictionary must include an 'id' field.

        Returns:
            A list of the updated resources.
        """
        endpoint = self._get_endpoint()
        payload = {"values": data_list}
        response = self.client.put(endpoint + "/list", json=payload)

        if isinstance(response, dict) and "values" in response:
            return response["values"]

        return []


class TripletexSuppliers(TripletexCrud[Supplier]):
    """
    CRUD operations for Tripletex suppliers.

    Note: We're using None for _datamodel to return dictionaries instead of model objects
    because the Tripletex API has specific requirements for the request format.
    The Supplier model is still used for type hints and documentation.
    """
    _resource_path = "supplier"
    _datamodel = None  # Use None to return dictionaries instead of model objects
    _api_response_model = SupplierResponse
    allowed_actions = ["list", "read", "create", "update", "destroy"]

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a supplier.

        This method overrides the default create method to handle the nested response structure.
        """
        endpoint = self._get_endpoint()
        response = self.client.post(endpoint, json=data)

        if isinstance(response, dict) and "value" in response:
            return response["value"]

        # If response is not a dict or doesn't have 'value', return an empty dict
        if isinstance(response, dict):
            return response

        return {}

    def update(self, resource_id: str | int, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a supplier.

        This method overrides the default update method to handle the nested response structure.
        """
        endpoint = f"{self._get_endpoint()}/{resource_id}"
        response = self.client.put(endpoint, json=data)

        if isinstance(response, dict) and "value" in response:
            return response["value"]

        # If response is not a dict or doesn't have 'value', return an empty dict
        if isinstance(response, dict):
            return response

        return {}

    def listcreate(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create multiple suppliers in a single request.

        For Tripletex API, we need to create resources one by one since the batch endpoint
        is returning errors.

        Args:
            data_list: A list of dictionaries containing the data for each resource to create.

        Returns:
            A list of the created resources.
        """
        created_resources = []
        for data in data_list:
            created = self.create(data)
            created_resources.append(created)

        return created_resources

    def listupdate(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Update multiple suppliers in a single request.

        For Tripletex API, we need to update resources one by one since the batch endpoint
        is returning errors.

        Args:
            data_list: A list of dictionaries containing the data for each resource to update.
                       Each dictionary must include an 'id' field.

        Returns:
            A list of the updated resources.
        """
        updated_resources = []
        for data in data_list:
            if "id" not in data:
                raise ValueError("Each item in data_list must have an 'id' field")

            resource_id = data["id"]
            updated = self.update(resource_id, data)
            updated_resources.append(updated)

        return updated_resources


class TripletexCountries(TripletexCrud[Country]):
    """
    CRUD operations for Tripletex countries.
    """
    _resource_path = "country"
    _datamodel = Country
    _api_response_model = CountryResponse
    allowed_actions = ["list", "read"]

    def read(self, resource_id: str | int) -> Union[Dict[str, Any], JSONDict]:
        """
        Read a country by ID.

        This method overrides the default read method to handle the nested response structure.
        """
        endpoint = f"{self._get_endpoint()}/{resource_id}"
        response = self.client.get(endpoint)

        # The response has a 'value' field that contains the actual country data
        if isinstance(response, dict) and 'value' in response:
            return response['value']

        # If response is not a dict or doesn't have 'value', return it as is
        if isinstance(response, dict):
            return response

        # Last resort: return an empty dict
        return {}


class TripletexClient(Client):
    """
    Custom client for Tripletex API.
    """

    def _handle_response(self, response):
        """
        Handle the response from the API.

        This method overrides the default _handle_response method to handle 204 No Content responses.
        """
        if response.status_code == 204:
            return {}

        return super()._handle_response(response)


class TripletexAPI(API):
    """
    API client for Tripletex.
    """
    client_class = TripletexClient

    def _register_endpoints(self):
        """
        Register API endpoints.
        """
        assert self.client is not None, "Client is required!"
        self.countries = TripletexCountries(self.client)
        self.suppliers = TripletexSuppliers(self.client)
