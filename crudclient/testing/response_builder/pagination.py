"""
Pagination response builder utilities for mock client.

This module provides utilities for building paginated API responses with consistent
formats and navigation links. It supports common pagination patterns including
page-based pagination with metadata and HATEOAS links.
"""

from typing import Any, List, Optional

from .response import MockResponse
from .basic import BasicResponseBuilder


class PaginationResponseBuilder:
    """
    Builder for creating paginated API responses.

    This class provides methods to generate standardized paginated responses
    with metadata about the pagination state and navigation links. It supports
    common pagination patterns and can be configured to match different API styles.
    """

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
        """
        Create a paginated response with items, metadata, and navigation links.

        This method creates a standardized paginated response that includes the
        requested page of items, metadata about the pagination state (current page,
        total pages, etc.), and HATEOAS links for navigation between pages.

        Args:
            items: List of items for the current page or the complete collection
            page: Current page number (1-based)
            per_page: Number of items per page
            total_items: Total number of items across all pages (calculated from items if not provided)
            total_pages: Total number of pages (calculated from total_items and per_page if not provided)
            base_url: Base URL for pagination links
            include_links: Whether to include HATEOAS links for navigation

        Returns:
            A MockResponse instance with paginated data, metadata, and links
        """
        # Calculate totals if not provided
        _total_items = total_items if total_items is not None else len(items)
        _total_pages = total_pages if total_pages is not None else max(1, (_total_items + per_page - 1) // per_page)

        # Get items for the current page
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, _total_items)

        # If we have actual items, paginate them
        page_items = []
        if items and start_idx < len(items):
            page_items = items[start_idx:min(end_idx, len(items))]

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

        return BasicResponseBuilder.create_response(
            status_code=200,
            data=page_items,
            metadata=metadata,
            links=links
        )
