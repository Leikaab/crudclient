from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    email: EmailStr


class Address(BaseModel):
    streetAddress: str
    streetAddressLine2: Optional[str] = None
    city: str
    postCode: str
    country: str


class Company(BaseModel):
    name: str
    slug: str
    organizationNumber: str
    vatType: str
    address: Address
    phoneNumber: str | None = None
    email: EmailStr
    creationDate: date
    hasApiAccess: bool
    testCompany: bool
    accountingStartDate: date
