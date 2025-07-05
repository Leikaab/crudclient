from typing import Optional, cast

from crudclient.types import JSONDict

from ....crud import TripletexCrud
from ....models import HistoricalVoucher, TripletexResponse
from ....utils import ensure_date_params


class TripletexHistoricalVoucherCrud(TripletexCrud[HistoricalVoucher]):
    """
    CRUD operations for Tripletex historical vouchers.

    This Crud class is designed to be used with a VoucherGroup parent,
    enabling operations on the /ledger/voucher/historical endpoint.
    """

    _resource_path = "historical"
    _datamodel = HistoricalVoucher
    allowed_actions = ["list", "read", "create"]

    def list(self, parent_id: Optional[str] = None, params: Optional[JSONDict] = None, **kwargs) -> TripletexResponse[HistoricalVoucher]:
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
        return cast(TripletexResponse[HistoricalVoucher], result)
