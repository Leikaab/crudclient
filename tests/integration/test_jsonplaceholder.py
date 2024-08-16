import pytest

from crudclient.api import API
from crudclient.client import Client, ClientConfig
from crudclient.crud import Crud
from crudclient.types import JSONDict


class PlaceholderConfig(ClientConfig):
    hostname: str = "https://jsonplaceholder.typicode.com"
    version: str = ""


class PostsCrud(Crud[JSONDict]):
    _resource_path = "posts"


class CommentsCrud(Crud[JSONDict]):
    _resource_path = "comments"


class JsonplaceholderAPI(API):
    client_class = Client

    def _register_endpoints(self):
        self.posts = PostsCrud(self.client)
        self.comments = CommentsCrud(self.client)


@pytest.fixture
def api():
    config = PlaceholderConfig()
    return JsonplaceholderAPI(client_config=config)


def test_list_posts(api):
    posts = api.posts.list()
    assert isinstance(posts, list)
    assert len(posts) > 0
    assert isinstance(posts[0], dict)
    assert "id" in posts[0]
    assert "title" in posts[0]


def test_create_post(api):
    new_post = {"title": "foo", "body": "bar", "userId": 1}
    created_post = api.posts.create(new_post)
    assert isinstance(created_post, dict)
    assert "id" in created_post
    assert created_post["title"] == "foo"
    assert created_post["body"] == "bar"


def test_read_post(api):
    post = api.posts.read("1")
    assert isinstance(post, dict)
    assert post["id"] == 1
    assert "title" in post
    assert "body" in post


def test_update_post(api):
    updated_data = {
        "title": "Updated Title",
        "body": "Updated Body",
    }
    updated_post = api.posts.update("1", updated_data)
    assert isinstance(updated_post, dict)
    assert updated_post["id"] == 1
    assert updated_post["title"] == "Updated Title"
    assert updated_post["body"] == "Updated Body"


def test_partial_update_post(api):
    partial_data = {
        "title": "Partially Updated Title",
    }
    updated_post = api.posts.partial_update("1", partial_data)
    assert isinstance(updated_post, dict)
    assert updated_post["id"] == 1
    assert updated_post["title"] == "Partially Updated Title"


def test_delete_post(api):
    api.posts.destroy("1")
    # Note: JSONPlaceholder doesn't actually delete resources, it just pretends to.
    # So we can't really assert anything meaningful here.


def test_custom_action(api):
    # Test getting comments for a specific post
    post_id = "1"
    result = api.comments.custom_action("", method="get", params={"postId": post_id})

    assert isinstance(result, list)
    assert len(result) > 0
    for comment in result:
        assert isinstance(comment, dict)
        assert "id" in comment
        assert "postId" in comment
        assert comment["postId"] == int(post_id)
        assert "name" in comment
        assert "email" in comment
        assert "body" in comment
