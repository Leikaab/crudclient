import logging
import os

from crudclient.config import ClientConfig

from .auth import TripletexAuthStrategy

# Set up logging
logger = logging.getLogger(__name__)


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
            company_id=self.company_id, consumer_token=consumer_token, employee_token=employee_token, base_url=self.base_url
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
            company_id=self.company_id, consumer_token=consumer_token, employee_token=employee_token, base_url=self.base_url
        )
