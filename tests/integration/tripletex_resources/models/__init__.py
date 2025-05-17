"""
Models for Tripletex API resources.
"""

# TokenSession models are defined directly in the old __init__,
# keeping them here for now but ideally they should also be in their own file.
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .api_response_model import (
    Change,
    IdUrl,
    TripletexResponse,
)
from .company import Company, CompanyResponse
from .country import Country, CountryResponse
from .supplier import (
    BankAccountPresentation,
    Supplier,
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)


class TokenSession(BaseModel):
    """
    Represents a Tripletex API token session.
    """

    token: str
    expirationDate: datetime
    encryptionKey: Optional[str] = None
    autoRenew: bool = False
    id: Optional[int] = None
    version: Optional[int] = None
    url: Optional[str] = None
    changes: Optional[list] = None


class TokenSessionResponse(BaseModel):
    """
    Represents the response from the Tripletex API token session endpoint.
    """

    value: TokenSession
    from_: Optional[datetime] = Field(None, alias="from")
    to: Optional[datetime] = None
    count: Optional[int] = None
    fullResultSize: Optional[int] = None
    versionDigest: Optional[str] = None
    values: Optional[list] = None


__all__ = [
    "Change",
    "IdUrl",
    "TripletexResponse",
    "Company",
    "CompanyResponse",
    "Country",
    "CountryResponse",
    "BankAccountPresentation",
    "Supplier",
    "SupplierCreate",
    "SupplierResponse",
    "SupplierUpdate",
    "TokenSession",
    "TokenSessionResponse",
]
