# crudclient/testing/response_builder/pagination.pyi
from typing import Any, List, Optional

from .basic import BasicResponseBuilder
from .response import MockResponse

class PaginationResponseBuilder:
    """
    Builder for creating paginated API responses.

    This class provides utilities for creating mock responses that simulate
    paginated API endpoints, including pagination metadata and navigation links.
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
        Create a mock response with pagination support.

        This method creates a standardized paginated response with the requested
        page of items, pagination metadata, and navigation links following
        common REST API pagination patterns.

        Args:
            items: The complete list of items to paginate
            page: The current page number (1-based)
            per_page: Number of items per page
            total_items: Override for the calculated total number of items
            total_pages: Override for the calculated total number of pages
            base_url: Base URL for generating pagination links
            include_links: Whether to include HATEOAS navigation links

        Returns:
            A MockResponse instance with paginated data, metadata, and links

        Examples:
            ```python
            # Create a paginated response with 100 items, showing page 2 with 10 items per page
            items = [{"id": i, "name": f"Item {i}"} for i in range(1, 101)]
            response = PaginationResponseBuilder.create_paginated_response(
                items=items,
                page=2,
                per_page=10,
                base_url="/api/products"
            )

            # The response will contain:
            # - 10 items (items 11-20)
            # - Pagination metadata (page=2, per_page=10, total_items=100, total_pages=10)
            # - Navigation links (self, first, prev, next, last)
            ```
        """
        ...
