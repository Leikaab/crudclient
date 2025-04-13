from typing import Optional

from pydantic import BaseModel

from crudclient.models import ApiResponse


class Post(BaseModel):
    """
    Represents a post in the JSONPlaceholder API.

    Using a specific Pydantic model instead of a generic dictionary provides:
    - Type safety with automatic validation
    - Better IDE autocompletion
    - Self-documenting code
    - Consistent data structure
    """

    id: Optional[int] = None
    title: str
    body: str
    userId: int


class PostResponse(ApiResponse[Post]):
    """
    Represents the response from the JSONPlaceholder API posts endpoint.
    """


class Comment(BaseModel):
    """
    Represents a comment in the JSONPlaceholder API.

    Using a specific Pydantic model instead of a generic dictionary provides:
    - Type safety with automatic validation
    - Better IDE autocompletion
    - Self-documenting code
    - Consistent data structure
    """

    id: Optional[int] = None
    postId: int
    name: str
    email: str
    body: str


class CommentResponse(ApiResponse[Comment]):
    """
    Represents the response from the JSONPlaceholder API comments endpoint.
    """
