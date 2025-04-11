from typing import Any, Callable, Dict, List, Optional


class PaginationHelper:

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
    ):
        self.items = items
        self.page_size = page_size
        self.current_page = current_page
        self._total_items = total_items or len(items)
        self._total_pages = total_pages or ((self._total_items + page_size - 1) // page_size)
        self.page_param = page_param
        self.size_param = size_param
        self.base_url = base_url
        self.pagination_style = pagination_style
        self.cursor_param = cursor_param
        self.next_cursor_generator = next_cursor_generator or self._default_next_cursor_generator
        self.prev_cursor_generator = prev_cursor_generator or self._default_prev_cursor_generator
        self.custom_metadata_generator = custom_metadata_generator
        self.custom_links_generator = custom_links_generator

    def get_page(self, page: Optional[int] = None, page_size: Optional[int] = None, cursor: Optional[str] = None) -> Dict[str, Any]:
        size = page_size or self.page_size

        if self.pagination_style == "cursor" and cursor is not None:
            # For cursor-based pagination, decode the cursor to get the page
            # In a real implementation, this would be more sophisticated
            try:
                # Simple cursor implementation - in real code this would be more secure
                import base64

                decoded = base64.b64decode(cursor.encode()).decode()
                parts = decoded.split(":")
                if len(parts) >= 2:
                    page = int(parts[0])
                    size = int(parts[1])
            except Exception:
                # If cursor is invalid, default to first page
                page = 1

        # Default to first page if not specified
        page = page or 1

        start_idx = (page - 1) * size
        end_idx = min(start_idx + size, self._total_items)

        # If we're simulating pagination beyond actual items
        if start_idx >= len(self.items):
            page_items = []
        else:
            page_items = self.items[start_idx : min(end_idx, len(self.items))]

        # Generate metadata based on pagination style
        if self.custom_metadata_generator:
            metadata = self.custom_metadata_generator(page, size, self._total_items, self._total_pages)
        else:
            if self.pagination_style == "offset":
                metadata = {
                    "pagination": {
                        "currentPage": page,
                        "perPage": size,
                        "totalItems": self._total_items,
                        "totalPages": self._total_pages,
                    }
                }
            elif self.pagination_style == "cursor":
                next_cursor = self.next_cursor_generator(page, size) if page < self._total_pages else None
                prev_cursor = self.prev_cursor_generator(page, size) if page > 1 else None
                metadata = {
                    "pagination": {
                        "perPage": size,
                        "totalItems": self._total_items,
                        "nextCursor": next_cursor,
                        "prevCursor": prev_cursor,
                    }
                }
            else:  # link-based or other styles
                metadata = {
                    "pagination": {
                        "perPage": size,
                        "totalItems": self._total_items,
                    }
                }

        # Generate links based on pagination style
        if self.custom_links_generator:
            links = self.custom_links_generator(page, size, self._total_pages, self.base_url)
        else:
            if self.pagination_style == "offset":
                links = self._generate_offset_links(page, size)
            elif self.pagination_style == "cursor":
                links = self._generate_cursor_links(page, size)
            else:  # link-based or other styles
                links = self._generate_link_based_links(page, size)

        return {"data": page_items, "metadata": metadata, "links": links}

    def _generate_offset_links(self, page: int, size: int) -> Dict[str, str]:
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

    def _generate_cursor_links(self, page: int, size: int) -> Dict[str, str]:
        links = {
            "self": f"{self.base_url}?{self.cursor_param}={self.next_cursor_generator(page - 1, size)}",
        }

        if page > 1:
            links["prev"] = f"{self.base_url}?{self.cursor_param}={self.prev_cursor_generator(page, size)}"

        if page < self._total_pages:
            links["next"] = f"{self.base_url}?{self.cursor_param}={self.next_cursor_generator(page, size)}"

        return links

    def _generate_link_based_links(self, page: int, size: int) -> Dict[str, str]:
        base = self.base_url.rstrip("/")
        links = {
            "self": f"{base}?{self.page_param}={page}&{self.size_param}={size}",
        }

        if self._total_pages > 1:
            links["first"] = f"{base}?{self.page_param}=1&{self.size_param}={size}"
            links["last"] = f"{base}?{self.page_param}={self._total_pages}&{self.size_param}={size}"

        if page > 1:
            links["prev"] = f"{base}?{self.page_param}={page - 1}&{self.size_param}={size}"

        if page < self._total_pages:
            links["next"] = f"{base}?{self.page_param}={page + 1}&{self.size_param}={size}"

        return links

    def _default_next_cursor_generator(self, page: int, size: int) -> str:
        import base64

        cursor_data = f"{page + 1}:{size}:next"
        return base64.b64encode(cursor_data.encode()).decode()

    def _default_prev_cursor_generator(self, page: int, size: int) -> str:
        import base64

        cursor_data = f"{page - 1}:{size}:prev"
        return base64.b64encode(cursor_data.encode()).decode()
