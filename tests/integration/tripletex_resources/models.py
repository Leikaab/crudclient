from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from crudclient.models import ApiResponse


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


class CountryResponse(ApiResponse[Country]):
    """
    Represents the response from the Tripletex API country endpoint.
    """


class Supplier(BaseModel):
    """
    Represents a supplier in the Tripletex API.
    """
    id: Optional[int] = None
    version: Optional[int] = None
    changes: Optional[list] = None
    url: Optional[str] = None
    name: str
    organizationNumber: Optional[str] = None
    supplierNumber: Optional[str] = None
    customerNumber: Optional[str] = None
    email: Optional[str] = None
    bankAccountNumber: Optional[str] = None
    bankAccountIBAN: Optional[str] = None
    bankAccountSWIFT: Optional[str] = None
    phone: Optional[str] = None
    phoneInternationalPrefix: Optional[str] = None
    phoneNumber: Optional[str] = None
    description: Optional[str] = None
    isPrivateIndividual: Optional[bool] = None
    showProducts: Optional[bool] = None
    isInactive: Optional[bool] = None
    currency: Optional[dict] = None
    isSupplier: Optional[bool] = True
    isCustomer: Optional[bool] = False
    postalAddress: Optional[dict] = None
    physicalAddress: Optional[dict] = None
    deliveryAddress: Optional[dict] = None
    category1: Optional[dict] = None
    category2: Optional[dict] = None
    category3: Optional[dict] = None
    ledgerAccount: Optional[dict] = None
    supplierAccount: Optional[dict] = None
    discountPercentage: Optional[float] = None
    accountManager: Optional[dict] = None


class SupplierResponse(ApiResponse[Supplier]):
    """
    Represents the response from the Tripletex API supplier endpoint.
    """
