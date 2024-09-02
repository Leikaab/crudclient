from datetime import date
from typing import List

from pydantic import BaseModel


class User(BaseModel):
    name: str
    email: str


class Address(BaseModel):
    streetAddress: str | None = None
    streetAddressLine2: str | None = None
    city: str | None = None
    postCode: str | None = None
    country: str | None = None


class ContactPerson(BaseModel):
    contactPersonId: int
    name: str
    email: str
    phoneNumber: str
    address: Address


class Company(BaseModel):
    name: str
    slug: str
    organizationNumber: str
    vatType: str
    address: Address
    phoneNumber: str | None = None
    email: str
    creationDate: date
    hasApiAccess: bool
    testCompany: bool
    accountingStartDate: date


class Contact(BaseModel):
    contactId: int
    createdDate: date
    lastModifiedDate: date
    name: str
    customerNumber: int
    customerAccountCode: str
    customer: bool
    supplier: bool
    contactPerson: List[ContactPerson]
    notes: List[str]
    currency: str
    language: str
    inactive: bool
    address: Address
