from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field

from crudclient.models import ApiResponse, Link


class User(BaseModel):
    links: Dict[str, Link] = Field(None, alias="_links")
    active: bool
    email: str
    id: int
    is_admin: bool
    name: str
    phone_number: str
    state: str
    title: str


class UsersResponse(ApiResponse[User]):
    pass


class DataField(BaseModel):
    name: str
    custom_id: str
    template_type_id: int | None = None
    _links: Optional[Dict[str, Link]]
    active: bool | None = None
    description: str | None = None
    id: int | None = None
    placeholder: str | None = None
    source: str | None = None
    value: str | None = None


class DataFieldsResponse(ApiResponse[DataField]):
    pass


class TemplateType(BaseModel):
    links: Dict[str, Link] = Field(None, alias="_links")
    created_time: datetime
    description: str
    extension_type: str | None
    id: int
    name: str
    updated_time: datetime


class TemplateTypesResponse(ApiResponse[TemplateType]):
    pass
