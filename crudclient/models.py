from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, HttpUrl, field_validator

T = TypeVar("T")


class Link(BaseModel):
    href: Optional[HttpUrl] = None

    @field_validator("href")
    @classmethod
    def validate_href(cls, v: Optional[HttpUrl]) -> Optional[HttpUrl]:
        if v is None:
            return v
        # Additional validation could be added here if needed
        return v


class PaginationLinks(BaseModel):
    next: Optional[Link] = None
    previous: Optional[Link] = None
    self: Link = Field(..., description="Link to the current page")

    @field_validator("self")
    @classmethod
    def validate_self_link(cls, v: Link) -> Link:
        if v.href is None:
            raise ValueError("Self link must have a valid href")
        return v


class ApiResponse(BaseModel, Generic[T]):
    links: PaginationLinks = Field(..., alias="_links", description="Pagination links")
    count: int = Field(..., ge=0, description="Total number of items")
    data: List[T] = Field(..., description="The actual data items")

    @field_validator("count")
    @classmethod
    def validate_count(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Count cannot be negative")
        return v
