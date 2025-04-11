# crudclient/testing/helpers/pagination.pyi
from typing import Any, Callable, Dict, List, Optional

class PaginationHelper:
    """
    Helper class for simulating various pagination styles in API responses.

    Supports offset-based, cursor-based, and link-based pagination with
    customizable metadata and link generation.
    """

    items: List[Any]
    page_size: int
    current_page: int
    _total_items: int
    _total_pages: int
    page_param: str
    size_param: str
    base_url: str
    pagination_style: str
    cursor_param: str
    next_cursor_generator: Callable[[int, int], str]
    prev_cursor_generator: Callable[[int, int], str]
    custom_metadata_generator: Optional[Callable[[int, int, int, int], Dict[str, Any]]]
    custom_links_generator: Optional[Callable[[int, int, int, str], Dict[str, str]]]

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
        pagination_style: str = "offset",  # "offset", "cursor", or "link"
        cursor_param: str = "cursor",
        next_cursor_generator: Optional[Callable[[int, int], str]] = None,
        prev_cursor_generator: Optional[Callable[[int, int], str]] = None,
        custom_metadata_generator: Optional[Callable[[int, int, int, int], Dict[str, Any]]] = None,
        custom_links_generator: Optional[Callable[[int, int, int, str], Dict[str, str]]] = None,
    ) -> None:
        """
        Initialize a PaginationHelper instance.

        Args:
            items: The complete list of items to paginate
            page_size: Number of items per page
            current_page: The current page number (1-based)
            total_pages: Override for the calculated total pages
            total_items: Override for the calculated total items
            page_param: URL parameter name for page number
            size_param: URL parameter name for page size
            base_url: Base URL for generating pagination links
            pagination_style: Style of pagination ("offset", "cursor", or "link")
            cursor_param: URL parameter name for cursor-based pagination
            next_cursor_generator: Custom function to generate next page cursor
            prev_cursor_generator: Custom function to generate previous page cursor
            custom_metadata_generator: Custom function to generate pagination metadata
            custom_links_generator: Custom function to generate pagination links
        """
        ...

    def get_page(self, page: Optional[int] = None, page_size: Optional[int] = None, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a paginated response for the specified page.

        Args:
            page: The page number to retrieve (1-based)
            page_size: Override for the instance's page size
            cursor: Cursor string for cursor-based pagination

        Returns:
            A dictionary containing:
            - 'data': List of items for the requested page
            - 'metadata': Pagination metadata (varies by pagination style)
            - 'links': URLs for navigating between pages
        """
        ...

    def _generate_offset_links(self, page: int, size: int) -> Dict[str, str]:
        """
        Generate pagination links for offset-based pagination.

        Args:
            page: Current page number
            size: Page size

        Returns:
            Dictionary of link relations to URLs
        """
        ...

    def _generate_cursor_links(self, page: int, size: int) -> Dict[str, str]:
        """
        Generate pagination links for cursor-based pagination.

        Args:
            page: Current page number
            size: Page size

        Returns:
            Dictionary of link relations to URLs
        """
        ...

    def _generate_link_based_links(self, page: int, size: int) -> Dict[str, str]:
        """
        Generate pagination links for link-based pagination.

        Args:
            page: Current page number
            size: Page size

        Returns:
            Dictionary of link relations to URLs
        """
        ...

    def _default_next_cursor_generator(self, page: int, size: int) -> str:
        """
        Default generator for next page cursor.

        Creates a base64-encoded string containing page and size information.

        Args:
            page: Current page number
            size: Page size

        Returns:
            Base64-encoded cursor string
        """
        ...

    def _default_prev_cursor_generator(self, page: int, size: int) -> str:
        """
        Default generator for previous page cursor.

        Creates a base64-encoded string containing page and size information.

        Args:
            page: Current page number
            size: Page size

        Returns:
            Base64-encoded cursor string
        """
        ...
