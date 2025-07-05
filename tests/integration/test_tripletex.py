from datetime import datetime, timezone
from typing import cast

import pytest

from .tripletex_resources import (
    Country,
    TripletexAPI,
    TripletexTestConfig,
)
from .tripletex_resources.models.api_response_model import TripletexResponse


@pytest.fixture
def api() -> TripletexAPI:
    """
    Create a Tripletex API client for testing.
    """
    config = TripletexTestConfig()
    return TripletexAPI(client_config=config)


def test_api_configuration(api: TripletexAPI) -> None:
    """
    Test that the API client is configured correctly.
    """
    assert api.client is not None
    client = api.client
    assert client.base_url == "https://api-test.tripletex.tech/v2"

    # Check that we have an auth strategy set up
    assert client.config.auth_strategy is not None

    # Check that the auth strategy is a TripletexAuthStrategy
    from .tripletex_resources import TripletexAuthStrategy

    assert isinstance(client.config.auth_strategy, TripletexAuthStrategy)

    # Check that the session token is set
    assert client.config.auth_strategy.session_token is not None
    assert len(client.config.auth_strategy.session_token) > 0

    # Check that the session expiration date is set and in the future
    assert client.config.auth_strategy.session_expires_at is not None
    assert isinstance(client.config.auth_strategy.session_expires_at, datetime)
    # Use timezone-aware datetime for comparison
    assert client.config.auth_strategy.session_expires_at > datetime.now(timezone.utc)


@pytest.mark.no_parallel
def test_token_refresh(api: TripletexAPI) -> None:
    """
    Test that the token can be refreshed.
    """
    # Store the current token
    assert api.client is not None
    client = api.client
    assert client.config.auth_strategy is not None
    from .tripletex_resources import TripletexAuthStrategy

    auth_strategy = cast(TripletexAuthStrategy, client.config.auth_strategy)
    old_token = auth_strategy.session_token

    # Force a token refresh
    auth_strategy.refresh_token(force=True)

    # Check that we got a new token
    new_token = auth_strategy.session_token
    assert new_token is not None
    assert new_token != old_token


def test_auth_headers(api: TripletexAPI) -> None:
    """
    Test that the authentication headers are correctly generated.
    """
    # Get the authentication headers
    assert api.client is not None
    client = api.client
    assert client.config.auth_strategy is not None
    from .tripletex_resources import TripletexAuthStrategy

    auth_strategy = cast(TripletexAuthStrategy, client.config.auth_strategy)
    headers = auth_strategy.prepare_request_headers()

    # Check that the Authorization header is present and correctly formatted
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Basic ")
    assert len(headers["Authorization"]) > 10  # Basic + space + base64 encoded string


def test_list_countries(api: TripletexAPI) -> None:
    """
    Test that we can list countries from the Tripletex API.
    """
    # Get the list of countries
    # Limit to just 2 items to reduce output
    assert api.client is not None
    countries = api.countries.list(params={"count": 2})
    assert isinstance(countries, TripletexResponse)
    countries_resp = cast(TripletexResponse[Country], countries)

    # Check that we got a list of countries
    assert len(countries_resp.values) > 0

    # Check that each country has the expected structure
    for country in countries_resp.values:
        # The API returns Country objects, not dictionaries
        assert isinstance(country, Country)
        assert hasattr(country, "id")
        assert hasattr(country, "isoAlpha2Code")
        assert hasattr(country, "isoAlpha3Code")
        assert hasattr(country, "isoNumericCode")
        # The API might use 'displayName' instead of 'name'
        assert hasattr(country, "displayName")


def test_read_country(api: TripletexAPI) -> None:
    """
    Test that we can read a specific country from the Tripletex API.
    """
    # Get the list of countries
    # Limit to just 2 items to reduce output
    assert api.client is not None
    countries = api.countries.list(params={"count": 2})
    assert isinstance(countries, TripletexResponse)
    countries_resp = cast(TripletexResponse[Country], countries)

    # Get the first country's ID
    first_country_id = countries_resp.values[0].id

    # Read the country by ID
    country = api.countries.read(str(first_country_id))

    # Check that we got the expected country
    assert isinstance(country, Country)
    assert country.id == first_country_id
    assert hasattr(country, "displayName")
    assert hasattr(country, "isoAlpha2Code")
    assert hasattr(country, "isoAlpha3Code")
    assert hasattr(country, "isoNumericCode")
