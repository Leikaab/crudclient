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


class User(BaseModel):
    """
    Represents a user in the JSONPlaceholder API.

    Using a specific Pydantic model instead of a generic dictionary provides:
    - Type safety with automatic validation
    - Better IDE autocompletion
    - Self-documenting code
    - Consistent data structure
    """

    id: Optional[int] = None
    name: str
    username: str
    email: str
    address: Optional[dict] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    company: Optional[dict] = None


class UserResponse(ApiResponse[User]):
    """
    Represents the response from the JSONPlaceholder API users endpoint.
    """


class Album(BaseModel):
    """
    Represents an album in the JSONPlaceholder API.

    Using a specific Pydantic model instead of a generic dictionary provides:
    - Type safety with automatic validation
    - Better IDE autocompletion
    - Self-documenting code
    - Consistent data structure
    """

    id: Optional[int] = None
    userId: int
    title: str


class AlbumResponse(ApiResponse[Album]):
    """
    Represents the response from the JSONPlaceholder API albums endpoint.
    """


class Todo(BaseModel):
    """
    Represents a todo item in the JSONPlaceholder API.

    Using a specific Pydantic model instead of a generic dictionary provides:
    - Type safety with automatic validation
    - Better IDE autocompletion
    - Self-documenting code
    - Consistent data structure
    """

    id: Optional[int] = None
    userId: int
    title: str
    completed: bool


class TodoResponse(ApiResponse[Todo]):
    """
    Represents the response from the JSONPlaceholder API todos endpoint.
    """
