from typing import List, Optional, TypeVar, Union, cast

from crudclient.crud.base import Crud
from crudclient.models import ListResponseWrapper
from crudclient.response_strategies import ModelDumpable
from crudclient.types import JSONDict, JSONList

from .models import (
    Album,
    AlbumResponse,
    Post,
    PostResponse,
    Todo,
    TodoResponse,
    User,
    UserResponse,
)

T = TypeVar("T", bound=ModelDumpable)


class UserCrud(Crud[User]):
    """
    CRUD operations for JSONPlaceholder users.

    Using a specific model (User) instead of BaseModel provides:
    - Type safety for all CRUD operations
    - Automatic validation of user data
    - Better IDE autocompletion
    - Consistent data structure
    """

    _resource_path = "users"
    _datamodel = User
    _api_response_model = UserResponse
    allowed_actions = ["list", "read"]


class UserPostsCrud(Crud[Post]):
    """
    CRUD operations for posts belonging to a specific user.

    This Crud class is designed to be used with a UserGroup parent,
    enabling operations on the /users/{userId}/posts endpoint.
    """

    _resource_path = "posts"
    _datamodel = Post
    _api_response_model = PostResponse
    allowed_actions = ["list"]

    def list(
        self, parent_id: Optional[str] = None, params: Optional[JSONDict] = None, **kwargs
    ) -> Union[JSONList, List[Post], ListResponseWrapper[Post]]:
        """
        List all posts for a specific user.

        Args:
            parent_id: The ID of the parent user to get posts for.
            **kwargs: Additional query parameters.

        Returns:
            A list of Post objects for the specified user.
        """
        if parent_id is None:
            raise ValueError("parent_id is required for listing user posts")

        # Pass parent_id to the URL construction
        result = super().list(parent_id=parent_id, **kwargs)
        return cast(List[Post], result)


class UserAlbumsCrud(Crud[Album]):
    """
    CRUD operations for albums belonging to a specific user.

    This Crud class is designed to be used with a UserGroup parent,
    enabling operations on the /users/{userId}/albums endpoint.
    """

    _resource_path = "albums"
    _datamodel = Album
    _api_response_model = AlbumResponse
    allowed_actions = ["list"]

    def list(
        self, parent_id: Optional[str] = None, params: Optional[JSONDict] = None, **kwargs
    ) -> Union[JSONList, List[Album], ListResponseWrapper[Album]]:
        """
        List all albums for a specific user.

        Args:
            parent_id: The ID of the parent user to get albums for.
            **kwargs: Additional query parameters.

        Returns:
            A list of Album objects for the specified user.
        """
        if parent_id is None:
            raise ValueError("parent_id is required for listing user albums")

        # Pass parent_id to the URL construction
        result = super().list(parent_id=parent_id, **kwargs)
        return cast(List[Album], result)


class UserTodosCrud(Crud[Todo]):
    """
    CRUD operations for todos belonging to a specific user.

    This Crud class is designed to be used with a UserGroup parent,
    enabling operations on the /users/{userId}/todos endpoint.
    """

    _resource_path = "todos"
    _datamodel = Todo
    _api_response_model = TodoResponse
    allowed_actions = ["list"]

    def list(
        self, parent_id: Optional[str] = None, params: Optional[JSONDict] = None, **kwargs
    ) -> Union[JSONList, List[Todo], ListResponseWrapper[Todo]]:
        """
        List all todos for a specific user.

        Args:
            parent_id: The ID of the parent user to get todos for.
            **kwargs: Additional query parameters.

        Returns:
            A list of Todo objects for the specified user.
        """
        if parent_id is None:
            raise ValueError("parent_id is required for listing user todos")

        # Pass parent_id to the URL construction
        result = super().list(parent_id=parent_id, **kwargs)
        return cast(List[Todo], result)
