"""
CRUD resources for Tripletex ledger-related endpoints.

This module defines CRUD classes for interacting with ledger-related endpoints
in the Tripletex API, including ledgers, vouchers, and historical vouchers.
"""

from datetime import datetime, timedelta
from typing import Optional, Union, cast

from crudclient.types import JSONDict

from .crud import TripletexCrud
from .models import (
    HistoricalVoucher,
    HistoricalVoucherResponse,
    Ledger,
    LedgerResponse,
    Voucher,
    VoucherResponse,
)


def ensure_date_params(params: Optional[JSONDict] = None) -> JSONDict:
    """
    Ensure that dateFrom and dateTo parameters are present in the params dictionary.
    If not provided, default to the last 30 days.

    Args:
        params: Optional dictionary of query parameters.

    Returns:
        Dictionary with dateFrom and dateTo parameters included.
    """
    if params is None:
        params = {}

    # If dateFrom or dateTo are not provided, use defaults
    if "dateFrom" not in params.keys() or "dateTo" not in params.keys():
        # Default to last 30 days
        date_to = datetime.now().strftime("%Y-%m-%d")
        date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        if "dateFrom" not in params:
            params["dateFrom"] = date_from
        if "dateTo" not in params:
            params["dateTo"] = date_to

    return params


class TripletexLedgerCrud(TripletexCrud[Ledger]):
    """
    CRUD operations for Tripletex ledgers.
    """

    _resource_path = "ledger"
    _datamodel = Ledger
    _api_response_model = LedgerResponse
    allowed_actions = ["list", "read"]

    def list(self, parent_id: Optional[str] = None, params: Optional[JSONDict] = None, **kwargs) -> LedgerResponse:
        """
        List ledgers.

        Args:
            parent_id: Optional parent ID if this is a nested resource.
            params: Optional query parameters. Must include 'dateFrom' and 'dateTo'.
            **kwargs: Additional keyword arguments.

        Returns:
            LedgerResponse object containing a list of Ledger objects.
        """
        # Ensure required date parameters are present
        params = ensure_date_params(params)

        # Call the parent list method with the updated params
        result = super().list(parent_id=parent_id, params=params, **kwargs)
        return cast(LedgerResponse, result)


class TripletexVoucherCrud(TripletexCrud[Voucher]):
    """
    CRUD operations for Tripletex vouchers.
    """

    _resource_path = "voucher"
    _datamodel = Voucher
    _api_response_model = VoucherResponse
    allowed_actions = ["list", "read"]

    def list(self, parent_id: Optional[str] = None, params: Optional[JSONDict] = None, **kwargs) -> VoucherResponse:
        """
        List vouchers.

        Args:
            parent_id: Optional parent ID if this is a nested resource.
            params: Optional query parameters. Must include 'dateFrom' and 'dateTo'.
            **kwargs: Additional keyword arguments.

        Returns:
            VoucherResponse object containing a list of Voucher objects.
        """
        # Ensure required date parameters are present
        params = ensure_date_params(params)

        # Call the parent list method with the updated params
        result = super().list(parent_id=parent_id, params=params, **kwargs)
        return cast(VoucherResponse, result)


class TripletexHistoricalVoucherCrud(TripletexCrud[HistoricalVoucher]):
    """
    CRUD operations for Tripletex historical vouchers.

    This Crud class is designed to be used with a VoucherGroup parent,
    enabling operations on the /ledger/voucher/historical endpoint.
    """

    _resource_path = "historical"
    _datamodel = HistoricalVoucher
    _api_response_model = HistoricalVoucherResponse
    allowed_actions = ["list", "read", "create"]

    def list(self, parent_id: Optional[str] = None, params: Optional[JSONDict] = None, **kwargs) -> HistoricalVoucherResponse:
        """
        List all historical vouchers.

        Args:
            parent_id: The ID of the parent voucher (if applicable).
            params: Optional query parameters. May include 'dateFrom' and 'dateTo'.
            **kwargs: Additional keyword arguments.

        Returns:
            HistoricalVoucherResponse object containing a list of HistoricalVoucher objects.
        """
        # Ensure required date parameters are present
        params = ensure_date_params(params)

        # Call the parent list method with the updated params
        result = super().list(parent_id=parent_id, params=params, **kwargs)
        return cast(HistoricalVoucherResponse, result)

    def create(self, data: Union[dict, JSONDict], parent_id: Optional[str] = None, **kwargs) -> HistoricalVoucher:
        """
        Create a new historical voucher.

        Args:
            data: The data for the new historical voucher.
            parent_id: Optional parent ID if this is a nested resource.
            **kwargs: Additional parameters.

        Returns:
            The created HistoricalVoucher object.
        """
        result = super().create(data, parent_id=parent_id, **kwargs)
        return cast(HistoricalVoucher, result)
