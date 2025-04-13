"""
Module `models.py`
=================

This module defines various models used throughout the crudclient library.
These models provide structured data representations for API responses and other data.

Classes:
    - RoleBasedModel: A model that validates fields based on the current role.
    - Link: A model representing a hyperlink.
    - PaginationLinks: A model representing pagination links.
    - ApiResponse: A generic model for API responses with pagination.
"""

from typing import Any, ClassVar, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, HttpUrl, field_validator, validator

class RoleBasedModel(BaseModel):
    """
    A model that validates fields based on the current role.

    This model allows for role-based field validation, where certain fields may be
    required or disallowed based on the current role. The role is specified using
    the `_role` field in the input data.

    Note: This model is currently not used in the core library but is kept here
    as it's intended to be the foundation for future enhancements to the library's
    validation capabilities. Future plans include expanding this to support more
    complex validation scenarios and integrating it with the CRUD operations.

    Attributes:
        _current_role (Optional[str]): The current role for validation.
    """

    _current_role: Optional[str]

    @classmethod
    def check_fields_based_on_role(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate fields based on the current role.

        Args:
            values (Dict[str, Any]): The input values to validate.

        Returns:
            Dict[str, Any]: The validated values.

        Raises:
            ValueError: If a required field is missing or a disallowed field is present.
        """
        ...

T = TypeVar("T")

class Link(BaseModel):
    """
    A model representing a hyperlink.

    Attributes:
        href (Optional[HttpUrl]): The URL of the link.
    """

    href: Optional[HttpUrl]

    @field_validator("href")
    @classmethod
    def validate_href(cls, v: Optional[HttpUrl]) -> Optional[HttpUrl]:
        """Validate the href URL if present."""
        ...

class PaginationLinks(BaseModel):
    """
    A model representing pagination links.

    Attributes:
        next (Optional[Link]): Link to the next page, if available.
        previous (Optional[Link]): Link to the previous page, if available.
        self (Link): Link to the current page.
    """

    next: Optional[Link]
    previous: Optional[Link]
    self: Link = Field(..., description="Link to the current page")

    @field_validator("self")
    @classmethod
    def validate_self_link(cls, v: Link) -> Link:
        """Validate that the self link is present and properly formatted."""
        ...

class ApiResponse(BaseModel, Generic[T]):
    """
    A generic model for API responses with pagination.

    This model represents a standard API response format with pagination links,
    a count of total items, and the actual data.

    Attributes:
        links (PaginationLinks): Pagination links.
        count (int): Total number of items.
        data (List[T]): The actual data items.
    """

    links: PaginationLinks = Field(..., alias="_links", description="Pagination links")
    count: int = Field(..., ge=0, description="Total number of items")
    data: List[T] = Field(..., description="The actual data items")

    @field_validator("count")
    @classmethod
    def validate_count(cls, v: int) -> int:
        """Validate that count is non-negative."""
        ...
