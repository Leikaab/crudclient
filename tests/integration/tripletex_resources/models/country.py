from typing import Optional

from pydantic import BaseModel


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
