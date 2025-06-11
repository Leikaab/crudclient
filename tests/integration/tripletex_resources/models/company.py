from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .country import Country


class Address(BaseModel):
    """
    Represents an address in the Tripletex API.
    """

    id: Optional[int] = None
    version: Optional[int] = None
    changes: Optional[list] = None
    url: Optional[str] = None
    addressLine1: Optional[str] = None
    addressLine2: Optional[str] = None
    postalCode: Optional[str] = None
    city: Optional[str] = None
    country: Optional[Country] = None
    displayName: Optional[str] = None


class Company(BaseModel):
    """
    Represents a company in the Tripletex API.
    """

    id: Optional[int] = None
    version: Optional[int] = None
    changes: Optional[list] = None
    url: Optional[str] = None
    name: str
    displayName: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    organizationNumber: Optional[str] = None
    email: Optional[str] = None
    phoneNumber: Optional[str] = None
    phoneNumberMobile: Optional[str] = None
    faxNumber: Optional[str] = None
    address: Optional[Address] = None
