from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, HttpUrl

T = TypeVar("T")


class Link(BaseModel):
    href: Optional[HttpUrl] = None


class PaginationLinks(BaseModel):
    next: Optional[Link] = None
    previous: Optional[Link] = None
    self: Link


class ApiResponse(BaseModel, Generic[T]):
    links: PaginationLinks = Field(..., alias="_links")
    count: int
    data: List[T]
