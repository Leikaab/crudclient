"""
Models for Tripletex ledger resources.
"""

from datetime import date as date_type
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .api_response_model import Change, IdUrl, TripletexResponse


class Ledger(BaseModel):
    """
    Represents a ledger in the Tripletex API.
    """

    # Using account as the primary identifier instead of direct id
    account: IdUrl
    # Making id optional and derived from account.id
    id: Optional[int] = None

    # Financial amounts
    sum_amount: Optional[float] = Field(None, alias="sumAmount")
    sum_amount_currency: Optional[float] = Field(None, alias="sumAmountCurrency")
    opening_balance: Optional[float] = Field(None, alias="openingBalance")
    opening_balance_currency: Optional[float] = Field(None, alias="openingBalanceCurrency")
    closing_balance: Optional[float] = Field(None, alias="closingBalance")
    closing_balance_currency: Optional[float] = Field(None, alias="closingBalanceCurrency")
    balance_out_in_account_currency: Optional[float] = Field(None, alias="balanceOutInAccountCurrency")

    # Other fields
    currency: Optional[IdUrl] = None
    postings: Optional[List[dict]] = Field(default_factory=list)

    # Keep original fields as optional for backward compatibility
    version: Optional[int] = None
    url: Optional[str] = None
    name: Optional[str] = None
    number: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = Field(None, alias="isActive")
    is_applicable_for_supplier_invoice: Optional[bool] = Field(None, alias="isApplicableForSupplierInvoice")
    is_applicable_for_customer_invoice: Optional[bool] = Field(None, alias="isApplicableForCustomerInvoice")
    vat_type: Optional[IdUrl] = Field(None, alias="vatType")

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True, extra="ignore")

    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        # Set id from account.id if account is present and id is not provided
        if self.id is None and hasattr(self, "account") and self.account is not None and hasattr(self.account, "id"):
            self.id = self.account.id


class LedgerResponse(TripletexResponse[Ledger]):
    """
    Response model for ledger endpoints.
    """

    # The data field is already defined in the parent class with proper aliases
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True, extra="ignore")


class Voucher(BaseModel):
    """
    Represents a voucher in the Tripletex API.
    """

    id: int
    version: Optional[int] = None
    url: Optional[str] = None
    date: Optional[date_type] = None
    description: Optional[str] = None
    voucher_type: Optional[IdUrl] = Field(None, alias="voucherType")
    number: Optional[int] = None
    year: Optional[int] = None
    reverse_voucher: Optional[IdUrl] = Field(None, alias="reverseVoucher")
    attachment_count: Optional[int] = Field(None, alias="attachmentCount")
    is_historical: Optional[bool] = Field(None, alias="historical")

    # Additional fields that might be in the API response
    postings: Optional[List[dict]] = Field(default_factory=list)
    document: Optional[IdUrl] = None
    edi_document: Optional[IdUrl] = Field(None, alias="ediDocument")

    # Financial fields
    total_amount: Optional[float] = Field(None, alias="totalAmount")
    total_amount_currency: Optional[float] = Field(None, alias="totalAmountCurrency")

    # Metadata fields
    created: Optional[Change] = None
    updated: Optional[Change] = None

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True, extra="ignore")


class VoucherResponse(TripletexResponse[Voucher]):
    """
    Response model for voucher endpoints.
    """

    # The data field is already defined in the parent class with proper aliases
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True, extra="ignore")


class HistoricalVoucher(BaseModel):
    """
    Represents a historical voucher in the Tripletex API.
    """

    id: int
    version: Optional[int] = None
    url: Optional[str] = None
    date: Optional[date_type] = None
    description: Optional[str] = None
    voucher_type: Optional[IdUrl] = Field(None, alias="voucherType")
    number: Optional[int] = None
    year: Optional[int] = None
    postings: Optional[List[dict]] = None

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True, extra="ignore")
