import pytest

from .jsonplaceholder_resources.models import Album, Comment, Post, Todo, User
from .jsonplaceholder_resources.setup import JsonplaceholderAPI, PlaceholderConfig


@pytest.fixture
def api():
    config = PlaceholderConfig()
    return JsonplaceholderAPI(client_config=config)


def test_list_posts(api) -> None:
    """
    Test listing posts from the JSONPlaceholder API.

    This test verifies that we can retrieve a list of posts and that each post
    is properly converted to a Post model instance.
    """
    posts = api.posts.list()
    assert isinstance(posts, list)
    assert len(posts) > 0
    assert isinstance(posts[0], Post)
    assert posts[0].id is not None
    assert posts[0].title is not None


@pytest.mark.no_parallel
def test_create_post(api) -> None:
    """
    Test creating a post in the JSONPlaceholder API.

    This test verifies that we can create a new post and that the response
    is properly converted to a Post model instance.
    """
    # Create a Post model instance
    new_post = Post(title="foo", body="bar", userId=1)
    created_post = api.posts.create(new_post)

    # Verify the response is a Post model instance
    assert isinstance(created_post, Post)
    assert created_post.id is not None
    assert created_post.title == "foo"
    assert created_post.body == "bar"

    # Test with dictionary data as well
    new_post_dict = {"title": "foo2", "body": "bar2", "userId": 1}
    created_post_dict = api.posts.create(new_post_dict)
    assert isinstance(created_post_dict, Post)
    assert created_post_dict.id is not None
    assert created_post_dict.title == "foo2"
    assert created_post_dict.body == "bar2"


def test_read_post(api) -> None:
    """
    Test reading a post from the JSONPlaceholder API.

    This test verifies that we can retrieve a specific post by ID and that
    the response is properly converted to a Post model instance.
    """
    post = api.posts.read("1")
    assert isinstance(post, Post)
    assert post.id == 1
    assert post.title is not None
    assert post.body is not None


@pytest.mark.no_parallel
def test_update_post(api) -> None:
    """
    Test updating a post in the JSONPlaceholder API.

    This test verifies that we can update an existing post and that the response
    is properly converted to a Post model instance.
    """
    # Create a Post model instance with updated data
    updated_data = Post(title="Updated Title", body="Updated Body", userId=1)
    updated_post = api.posts.update("1", updated_data)

    # Verify the response is a Post model instance
    assert isinstance(updated_post, Post)
    assert updated_post.id == 1
    assert updated_post.title == "Updated Title"
    assert updated_post.body == "Updated Body"


@pytest.mark.no_parallel
def test_partial_update_post(api) -> None:
    """
    Test partially updating a post in the JSONPlaceholder API.

    This test verifies that we can partially update an existing post and that
    the response is properly converted to a Post model instance.
    """
    partial_data = {
        "title": "Partially Updated Title",
    }
    updated_post = api.posts.partial_update("1", partial_data)
    assert isinstance(updated_post, Post)
    assert updated_post.id == 1
    assert updated_post.title == "Partially Updated Title"


@pytest.mark.no_parallel
def test_delete_post(api) -> None:
    """
    Test deleting a post in the JSONPlaceholder API.

    This test verifies that we can delete a post. Note that JSONPlaceholder
    doesn't actually delete resources, it just pretends to.
    """
    api.posts.destroy("1")
    # Note: JSONPlaceholder doesn't actually delete resources, it just pretends to.
    # So we can't really assert anything meaningful here.


def test_custom_action(api) -> None:
    """
    Test a custom action on the JSONPlaceholder API.

    This test verifies that we can perform a custom action to get comments for a
    specific post and that the response is properly converted to Comment model instances.
    """
    # Test getting comments for a specific post using the helper method
    post_id = "1"
    comments = api.comments.get_comments_for_post(post_id)

    assert isinstance(comments, list)
    assert len(comments) > 0
    for comment in comments:
        assert isinstance(comment, Comment)
        assert comment.id is not None
        assert comment.postId == int(post_id)
        assert comment.name is not None
        assert comment.email is not None
        assert comment.body is not None


# ResourceGroup Tests


def test_list_users(api) -> None:
    """
    Test listing users from the JSONPlaceholder API using ResourceGroup.

    This test verifies that we can retrieve a list of users through the UserGroup
    and that each user is properly converted to a User model instance.
    """
    users = api.users.list()
    assert isinstance(users, list)
    assert len(users) > 0
    assert isinstance(users[0], User)
    assert users[0].id is not None
    assert users[0].name is not None
    assert users[0].email is not None


def test_read_user(api) -> None:
    """
    Test reading a user from the JSONPlaceholder API using ResourceGroup.

    This test verifies that we can retrieve a specific user by ID through the UserGroup
    and that the response is properly converted to a User model instance.
    """
    user = api.users.read("1")
    assert isinstance(user, User)
    assert user.id == 1
    assert user.name is not None
    assert user.email is not None


def test_user_posts(api) -> None:
    """
    Test listing posts for a specific user using nested ResourceGroup structure.

    This test verifies that we can retrieve posts for a specific user through
    the nested UserPostsCrud under UserGroup.
    """
    user_id = "1"
    posts = api.users.posts.list(parent_id=user_id)

    assert isinstance(posts, list)
    assert len(posts) > 0
    for post in posts:
        assert isinstance(post, Post)
        assert post.id is not None
        assert post.userId == int(user_id)
        assert post.title is not None
        assert post.body is not None


def test_user_albums(api) -> None:
    """
    Test listing albums for a specific user using nested ResourceGroup structure.

    This test verifies that we can retrieve albums for a specific user through
    the nested UserAlbumsCrud under UserGroup.
    """
    user_id = "1"
    albums = api.users.albums.list(parent_id=user_id)

    assert isinstance(albums, list)
    assert len(albums) > 0
    for album in albums:
        assert isinstance(album, Album)
        assert album.id is not None
        assert album.userId == int(user_id)
        assert album.title is not None


def test_user_todos(api) -> None:
    """
    Test listing todos for a specific user using nested ResourceGroup structure.

    This test verifies that we can retrieve todos for a specific user through
    the nested UserTodosCrud under UserGroup.
    """
    user_id = "1"
    todos = api.users.todos.list(parent_id=user_id)

    assert isinstance(todos, list)
    assert len(todos) > 0
    for todo in todos:
        assert isinstance(todo, Todo)
        assert todo.id is not None
        assert todo.userId == int(user_id)
        assert todo.title is not None
        assert isinstance(todo.completed, bool)
