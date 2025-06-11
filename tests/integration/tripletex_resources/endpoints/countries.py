from ..crud import TripletexCrud
from ..models import (
    Country,
    CountryResponse,
)


class TripletexCountries(TripletexCrud[Country]):
    """
    CRUD operations for Tripletex countries.
    """

    _resource_path = "country"
    _datamodel = Country
    _api_response_model = CountryResponse
    allowed_actions = ["list", "read"]
