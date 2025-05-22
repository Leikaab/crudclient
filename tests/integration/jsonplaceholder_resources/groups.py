from crudclient.groups import ResourceGroup

from .models import User, UserResponse
from .resources import UserAlbumsCrud, UserPostsCrud, UserTodosCrud


class UserGroup(ResourceGroup):
    """
    ResourceGroup for JSONPlaceholder users.

    This group handles operations directly on /users endpoint (listing all users,
    getting a specific user by ID) and also serves as a container for nested
    resources related to users (posts, albums, todos).

    Attributes:
        _resource_path: The base path for the user resource group in the API.
        _datamodel: The data model class for the user resource group.
        allowed_actions: List of allowed methods for this resource group.
    """

    _resource_path = "users"
    _datamodel = User
    _api_response_model = UserResponse
    allowed_actions = ["list", "read"]

    def _register_child_endpoints(self) -> None:
        """
        Register child Crud resources for user-related endpoints.

        These resources will become direct attributes of the UserGroup instance,
        enabling access to user-specific posts, albums, and todos.
        """
        self.posts = UserPostsCrud(self.client, parent=self)
        self.albums = UserAlbumsCrud(self.client, parent=self)
        self.todos = UserTodosCrud(self.client, parent=self)
