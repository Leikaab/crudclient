"""
Pagination helper for mock client.
"""

from typing import Any, Dict, List, Optional


class PaginationHelper:
    """Helper for simulating paginated responses."""

    def __init__(
        self,
        items: List[Any],
        page_size: int = 10,
        current_page: int = 1,
        total_pages: Optional[int] = None,
        total_items: Optional[int] = None,
        page_param: str = "page",
        size_param: str = "per_page",
        base_url: str = "",
    ):
        """
        Initialize pagination helper.

        Args:
            items: List of items to paginate
            page_size: Number of items per page
            current_page: Current page number
            total_pages: Total number of pages (calculated if None)
            total_items: Total number of items (calculated if None)
            page_param: Query parameter name for page
            size_param: Query parameter name for page size
            base_url: Base URL for pagination links
        """
        self.items = items
        self.page_size = page_size
        self.current_page = current_page
        self._total_items = total_items or len(items)
        self._total_pages = total_pages or ((self._total_items + page_size - 1) // page_size)
        self.page_param = page_param
        self.size_param = size_param
        self.base_url = base_url

    def get_page(self, page: int, page_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Get a specific page of items.

        Args:
            page: Page number (1-based)
            page_size: Optional override for page size

        Returns:
            Dict with data, metadata, and links
        """
        size = page_size or self.page_size
        start_idx = (page - 1) * size
        end_idx = min(start_idx + size, self._total_items)

        # If we're simulating pagination beyond actual items
        if start_idx >= len(self.items):
            page_items = []
        else:
            page_items = self.items[start_idx:min(end_idx, len(self.items))]

        return {
            "data": page_items,
            "metadata": {
                "pagination": {
                    "currentPage": page,
                    "perPage": size,
                    "totalItems": self._total_items,
                    "totalPages": self._total_pages,
                }
            },
            "links": self._generate_links(page, size)
        }

    def _generate_links(self, page: int, size: int) -> Dict[str, str]:
        """
        Generate pagination links.

        Args:
            page: Current page number
            size: Page size

        Returns:
            Dict with self, first, last, prev, next links
        """
        links = {
            "self": f"{self.base_url}?{self.page_param}={page}&{self.size_param}={size}",
            "first": f"{self.base_url}?{self.page_param}=1&{self.size_param}={size}",
            "last": f"{self.base_url}?{self.page_param}={self._total_pages}&{self.size_param}={size}",
        }

        if page > 1:
            links["prev"] = f"{self.base_url}?{self.page_param}={page - 1}&{self.size_param}={size}"

        if page < self._total_pages:
            links["next"] = f"{self.base_url}?{self.page_param}={page + 1}&{self.size_param}={size}"

        return links
