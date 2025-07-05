from typing import Optional, cast

from crudclient.models import ListResponseWrapper
from crudclient.types import JSONDict

from ...crud import TripletexResourceGroup
from ...models import Ledger
from ...utils import ensure_date_params
from .voucher_group import VoucherGroup


class LedgerGroup(TripletexResourceGroup[Ledger]):
    voucher: VoucherGroup
    """
    ResourceGroup for Tripletex ledger operations.

    This group handles operations directly on /ledger endpoint and also serves
    as a container for nested resources related to ledgers (vouchers, etc.).

    Attributes:
        _resource_path: The base path for the ledger resource group in the API.
        _datamodel: The data model class for the ledger resource group.
        _api_response_model: Custom API response model for ledger responses.
        allowed_actions: List of allowed methods for this resource group.
    """

    _resource_path = "ledger"
    _datamodel = Ledger
    allowed_actions = ["list", "read"]

    def _register_child_groups(self) -> None:
        """
        Register nested ResourceGroup instances.

        This method registers the VoucherGroup as a child of LedgerGroup,
        enabling access to voucher-related endpoints under the ledger path.
        """
        self.voucher = VoucherGroup(self.client, parent=self)

    def list(self, parent_id: Optional[str] = None, params: Optional[JSONDict] = None, **kwargs) -> ListResponseWrapper[Ledger]:
        """
        List ledgers.

        Args:
            parent_id: Optional parent ID if this is a nested resource.
            params: Optional query parameters. Must include 'dateFrom' and 'dateTo'.
            **kwargs: Additional keyword arguments.

        Returns:
            ListResponseWrapper[Ledger] object containing a list of Ledger objects.
        """
        # Ensure required date parameters are present
        params = ensure_date_params(params)

        # Call the parent list method with the updated params
        result = super().list(parent_id=parent_id, params=params, **kwargs)
        return cast(ListResponseWrapper[Ledger], result)

    def open_post(
        self,
        date: str,
        account_id: Optional[int] = None,
        supplier_id: Optional[int] = None,
        customer_id: Optional[int] = None,
        employee_id: Optional[int] = None,
        department_id: Optional[int] = None,
        project_id: Optional[int] = None,
        product_id: Optional[int] = None,
        from_index: int = 0,
        count: int = 1000,
        sorting: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> ListResponseWrapper[Ledger]:
        """
        Find open posts corresponding with sent data.

        Args:
            date: Invoice date. Format is yyyy-MM-dd (to and excl.)
            account_id: Element ID for filtering
            supplier_id: Element ID for filtering
            customer_id: Element ID for filtering
            employee_id: Element ID for filtering
            department_id: Element ID for filtering
            project_id: Element ID for filtering
            product_id: Element ID for filtering
            from_index: From index
            count: Number of elements to return
            sorting: Sorting pattern (note: 'date' is not a valid sorting field)
            fields: Fields filter pattern

        Returns:
            ListResponseWrapper[Ledger] object containing the open posts
        """
        params = {"date": date, "from": from_index, "count": count}

        if account_id:
            params["accountId"] = account_id
        if supplier_id:
            params["supplierId"] = supplier_id
        if customer_id:
            params["customerId"] = customer_id
        if employee_id:
            params["employeeId"] = employee_id
        if department_id:
            params["departmentId"] = department_id
        if project_id:
            params["projectId"] = project_id
        if product_id:
            params["productId"] = product_id
        if sorting:
            params["sorting"] = sorting
        if fields:
            params["fields"] = fields

        result = self.custom_action("openPost", method="get", params=params)

        return cast(ListResponseWrapper[Ledger], result)
