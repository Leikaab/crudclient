from typing import Optional

from pydantic import BaseModel

from .api_response_model import TripletexResponse


class Country(BaseModel):
    """
    Represents a country in the Tripletex API.
    """

    id: Optional[int] = None
    version: Optional[int] = None
    changes: Optional[list] = None
    url: Optional[str] = None
    displayName: str
    isoAlpha2Code: str
    isoAlpha3Code: str
    isoNumericCode: str


class CountryResponse(TripletexResponse[Country]):
    """
    Represents the response from the Tripletex API country endpoint.
    """
