from typing import Any, List, Optional

from .basic import BasicResponseBuilder
from .response import MockResponse


class PaginationResponseBuilder:

    @staticmethod
    def create_paginated_response(
        items: List[Any],
        page: int = 1,
        per_page: int = 10,
        total_items: Optional[int] = None,
        total_pages: Optional[int] = None,
        base_url: str = "/api/items",
        include_links: bool = True,
    ) -> MockResponse:
        # Calculate totals if not provided
        _total_items = total_items if total_items is not None else len(items)
        _total_pages = total_pages if total_pages is not None else max(1, (_total_items + per_page - 1) // per_page)

        # Get items for the current page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, _total_items)

        # If we have actual items, paginate them
        page_items = []
        if items and start_idx < len(items):
            page_items = items[start_idx : min(end_idx, len(items))]

        # Create metadata
        metadata = {
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_items": _total_items,
                "total_pages": _total_pages,
            }
        }

        # Create links
        links = None
        if include_links:
            links = {
                "self": f"{base_url}?page={page}&per_page={per_page}",
                "first": f"{base_url}?page=1&per_page={per_page}",
                "last": f"{base_url}?page={_total_pages}&per_page={per_page}",
            }

            if page > 1:
                links["prev"] = f"{base_url}?page={page - 1}&per_page={per_page}"

            if page < _total_pages:
                links["next"] = f"{base_url}?page={page + 1}&per_page={per_page}"

        return BasicResponseBuilder.create_response(status_code=200, data=page_items, metadata=metadata, links=links)
