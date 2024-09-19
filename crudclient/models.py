from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, HttpUrl, root_validator


class RoleBasedModel(BaseModel):
    _current_role: Optional[str] = None

    @root_validator(pre=True)
    def check_fields_based_on_role(cls, values):
        role = values.pop("_role", None)  # API internally uses this
        if not role:
            return values

        for field_name, field_value in values.items():
            field_config = cls.__fields__[field_name].field_info.extra.get("methods", {})
            if role in field_config:
                if field_config[role] == "required" and field_value is None:
                    raise ValueError(f"Field '{field_name}' is required for '{role}' operation.")
                if field_config[role] == "unallowed" and field_value is not None:
                    raise ValueError(f"Field '{field_name}' is not allowed in '{role}' operation.")
        return values


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
