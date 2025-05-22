from typing import List, TypeVar

from crudclient.api import API
from crudclient.client import Client
from crudclient.config import ClientConfig
from crudclient.crud import Crud
from crudclient.response_strategies import ModelDumpable

from .groups import UserGroup
from .models import Comment, CommentResponse, Post, PostResponse

T = TypeVar("T", bound=ModelDumpable)


class PlaceholderConfig(ClientConfig):
    """
    Configuration for JSONPlaceholder API client.
    """

    hostname: str = "https://jsonplaceholder.typicode.com"
    version: str = ""


class PostsCrud(Crud[Post]):
    """
    CRUD operations for JSONPlaceholder posts.

    Using a specific model (Post) instead of BaseModel provides:
    - Type safety for all CRUD operations
    - Automatic validation of post data
    - Better IDE autocompletion
    - Consistent data structure
    """

    _resource_path = "posts"
    _datamodel = Post
    _api_response_model = PostResponse
    allowed_actions = ["list", "read", "create", "update", "partial_update", "destroy"]


class CommentsCrud(Crud[Comment]):
    """
    CRUD operations for JSONPlaceholder comments.

    Using a specific model (Comment) instead of BaseModel provides:
    - Type safety for all CRUD operations
    - Automatic validation of comment data
    - Better IDE autocompletion
    - Consistent data structure
    """

    _resource_path = "comments"
    _datamodel = Comment
    _api_response_model = CommentResponse
    allowed_actions = ["list", "read", "create", "update", "partial_update", "destroy"]

    def get_comments_for_post(self, post_id: str) -> List[Comment]:
        """
        Get all comments for a specific post.

        Args:
            post_id: The ID of the post to get comments for.

        Returns:
            A list of Comment objects for the specified post.
        """
        result = self.custom_action("", method="get", params={"postId": post_id})
        if isinstance(result, list):
            return [Comment.model_validate(comment) if isinstance(comment, dict) else comment for comment in result]
        return []


class JsonplaceholderAPI(API):
    """
    API client for JSONPlaceholder.

    This implementation demonstrates the use of ResourceGroups for organizing
    related endpoints under a common path segment.
    """

    client_class = Client

    def _register_endpoints(self) -> None:
        """
        Register top-level API endpoints that are not part of any resource group.
        """
        assert self.client is not None, "Client is required!"
        self.posts = PostsCrud(self.client)
        self.comments = CommentsCrud(self.client)

    def _register_groups(self) -> None:
        """
        Register top-level ResourceGroup instances.

        This method instantiates the UserGroup which handles operations on /users
        and contains nested resources for user-specific posts, albums, and todos.
        """
        assert self.client is not None, "Client is required!"
        self.users = UserGroup(self.client, parent=None)
