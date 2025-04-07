from datetime import datetime, timezone

import pytest

from .tripletex_resources.setup import TripletexAPI, TripletexTestConfig


@pytest.fixture
def api():
    """
    Create a Tripletex API client for testing.
    """
    config = TripletexTestConfig()
    return TripletexAPI(client_config=config)


def test_api_configuration(api):
    """
    Test that the API client is configured correctly.
    """
    assert api.client.base_url == "https://api-test.tripletex.tech/v2"

    # Check that we have an auth strategy set up
    assert api.client.config.auth_strategy is not None

    # Check that the auth strategy is a TripletexAuthStrategy
    from .tripletex_resources.setup import TripletexAuthStrategy
    assert isinstance(api.client.config.auth_strategy, TripletexAuthStrategy)

    # Check that the session token is set
    assert api.client.config.auth_strategy.session_token is not None
    assert len(api.client.config.auth_strategy.session_token) > 0

    # Check that the session expiration date is set and in the future
    assert api.client.config.auth_strategy.session_expires_at is not None
    assert isinstance(api.client.config.auth_strategy.session_expires_at, datetime)
    # Use timezone-aware datetime for comparison
    assert api.client.config.auth_strategy.session_expires_at > datetime.now(timezone.utc)


@pytest.mark.no_parallel
def test_token_refresh(api):
    """
    Test that the token can be refreshed.
    """
    # Store the current token
    old_token = api.client.config.auth_strategy.session_token

    # Force a token refresh
    api.client.config.auth_strategy.refresh_token(force=True)

    # Check that we got a new token
    new_token = api.client.config.auth_strategy.session_token
    assert new_token is not None
    assert new_token != old_token


def test_auth_headers(api):
    """
    Test that the authentication headers are correctly generated.
    """
    # Get the authentication headers
    headers = api.client.config.auth_strategy.prepare_request_headers()

    # Check that the Authorization header is present and correctly formatted
    assert "Authorization" in headers
    assert headers["Authorization"].startswith("Basic ")
    assert len(headers["Authorization"]) > 10  # Basic + space + base64 encoded string


def test_list_countries(api):
    """
    Test that we can list countries from the Tripletex API.
    """
    # Get the list of countries
    countries = api.countries.list()

    # Check that we got a list of countries
    assert isinstance(countries, list)
    assert len(countries) > 0

    # Check that each country has the expected structure
    for country in countries:
        # The API returns dictionaries, not model objects
        assert isinstance(country, dict)
        assert 'id' in country
        assert 'isoAlpha2Code' in country
        assert 'isoAlpha3Code' in country
        assert 'isoNumericCode' in country
        # The API might use 'displayName' instead of 'name'
        assert 'displayName' in country


def test_read_country(api):
    """
    Test that we can read a specific country from the Tripletex API.
    """
    # Get the list of countries
    countries = api.countries.list()

    # Get the first country's ID
    first_country_id = countries[0]['id']

    # Read the country by ID
    country = api.countries.read(first_country_id)

    # Check that we got the expected country
    assert isinstance(country, dict)
    assert country['id'] == first_country_id
    assert 'displayName' in country
    assert 'isoAlpha2Code' in country
    assert 'isoAlpha3Code' in country
    assert 'isoNumericCode' in country
