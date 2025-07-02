from typing import Generic, List, Optional, TypeVar

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

    # Override the data field to use 'values' instead
    values: List[T] = Field(default_factory=list)

    # Override count to use the values length when not explicitly provided
    count: int = Field(default=0, ge=0, description="Total number of items")

    # Make data an alias for values to maintain compatibility with ApiResponse
    @property
    def data(self) -> List[T]:
        """Alias for values to maintain compatibility with ApiResponse."""
        return self.values

    # Override model_config to handle both Tripletex and ApiResponse field names
    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True, extra="ignore")

    def __init__(self, **data):
        # If count is not provided, use the length of values
        if "count" not in data and "values" in data:
            data["count"] = len(data["values"])
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
