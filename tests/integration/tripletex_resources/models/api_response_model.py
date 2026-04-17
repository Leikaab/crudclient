from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from crudclient.models import ApiResponse

T = TypeVar("T")


class TripletexResponse(ApiResponse[T], Generic[T]):
    """
    Represents a standard paginated response structure from the Tripletex API,
    adapted to be compatible with the ApiResponse model.

    Attributes:
        full_result_size: The total number of items available across all pages.
        from_index: The starting index of the items included in this response page.
        count: The number of items included in this response page.
        version_digest: A digest representing the version of the data.
        values: A list containing the actual data objects for this page.
    """

    full_result_size: Optional[int] = Field(None, alias="fullResultSize")
    from_index: Optional[int] = Field(None, alias="from")
    version_digest: Optional[str] = Field(None, alias="versionDigest")

    # The parent ListResponseWrapper already handles data/values aliasing via validation_alias
    # We don't need to override the data field - just let the parent handle it

    # Override count to use the data length when not explicitly provided
    count: int = Field(default=0, ge=0, description="Total number of items")

    @property
    def values(self) -> List[T]:
        """Convenience property to access data as 'values' for Tripletex API compatibility."""
        return self.data

    # Override model_config to handle both Tripletex and ApiResponse field names
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True, extra="ignore")

    def __init__(self, **data: Any) -> None:
        # If count is not provided, use the length of values or data
        if "count" not in data:
            if "values" in data:
                data["count"] = len(data["values"])
            elif "data" in data:
                data["count"] = len(data["data"])
        super().__init__(**data)


class IdUrl(BaseModel):
    """
    A simple model representing an object with an ID and a URL.

    Attributes:
        id: The unique identifier of the object.
        url: The URL pointing to the object resource.
    """

    id: int
    url: str


class Change(BaseModel):
    """
    Represents a change record, often associated with creation or modification history.

    Attributes:
        employee_id: The ID of the employee who made the change.
        timestamp: The timestamp when the change occurred.
        change_type: The type of change made (e.g., 'CREATED', 'UPDATED').
    """

    employee_id: Optional[int] = Field(None, alias="employeeId")
    timestamp: Optional[str] = None
    change_type: Optional[str] = Field(None, alias="changeType")
