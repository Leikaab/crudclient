from ..crud import TripletexCrud
from ..models import Country


class TripletexCountries(TripletexCrud[Country]):
    """
    CRUD operations for Tripletex countries.
    """

    _resource_path = "country"
    _datamodel = Country
    allowed_actions = ["list", "read"]
