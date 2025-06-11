from datetime import datetime, timedelta
from typing import Optional

from crudclient.types import JSONDict


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
