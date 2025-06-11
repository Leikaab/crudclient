from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from .api_response_model import IdUrl


class BankAccountPresentation(BaseModel):
    iban: Optional[str] = None
    bban: Optional[str] = None
    provider: Optional[str] = None


class Supplier(BaseModel):
    name: str
    id: int
    version: int
    changes: Optional[list[str]] = None
    url: str
    organization_number: Optional[str] = Field(None, alias="organizationNumber")
    supplier_number: int = Field(..., alias="supplierNumber")
    customer_number: int = Field(..., alias="customerNumber")
    is_supplier: bool = Field(..., alias="isSupplier")
    is_customer: bool = Field(..., alias="isCustomer")
    is_inactive: bool = Field(..., alias="isInactive")
    email: Optional[str] = None
    bank_accounts: Optional[list[str]] = None
    invoice_email: Optional[str] = Field(None, alias="invoiceEmail")
    overdue_notice_email: Optional[str] = Field(None, alias="overdueNoticeEmail")
    phone_number: Optional[str] = Field(None, alias="phoneNumber")
    phone_number_mobile: Optional[str] = Field(None, alias="phoneNumberMobile")
    description: Optional[str] = None
    is_private_individual: bool = Field(..., alias="isPrivateIndividual")
    show_products: bool = Field(..., alias="showProducts")
    account_manager: Optional[IdUrl] = Field(None, alias="accountManager")
    postal_address: Optional[IdUrl] = Field(None, alias="postalAddress")
    physical_address: Optional[IdUrl] = Field(None, alias="physicalAddress")
    delivery_address: Optional[IdUrl] = Field(None, alias="deliveryAddress")
    category1: Optional[Any] = None
    category2: Optional[Any] = None
    category3: Optional[Any] = None
    bank_account_presentation: Optional[list[BankAccountPresentation]] = Field(None, alias="bankAccountPresentation")
    currency: IdUrl
    ledger_account: Optional[IdUrl] = Field(None, alias="ledgerAccount")
    language: str
    is_wholesaler: bool = Field(..., alias="isWholesaler")
    display_name: str = Field(..., alias="displayName")
    locale: str
    website: str

    model_config = ConfigDict(populate_by_name=True)


# Input models for create/update operations


class SupplierCreate(BaseModel):
    name: str
    email: Optional[str] = None


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
