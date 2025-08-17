"""
Unit tests for endpoint_builder path_utils module.
"""

from crudclient.utils.endpoint_builder.path_utils import join_path_segments


class TestJoinPathSegments:
    """Test the join_path_segments function."""

    def test_join_path_segments_basic(self):
        """Test basic path joining."""
        result = join_path_segments("api", "v1", "users")
        assert result == "api/v1/users"

    def test_join_path_segments_single(self):
        """Test joining a single segment."""
        result = join_path_segments("users")
        assert result == "users"

    def test_join_path_segments_empty(self):
        """Test joining with no arguments."""
        result = join_path_segments()
        assert result == ""

    def test_join_path_segments_with_none(self):
        """Test joining with None values."""
        result = join_path_segments("api", None, "users")
        assert result == "api/users"

    def test_join_path_segments_with_integers(self):
        """Test joining with integer values."""
        result = join_path_segments("users", 123, "posts")
        assert result == "users/123/posts"

    def test_join_path_segments_with_empty_strings(self):
        """Test joining with empty strings."""
        result = join_path_segments("api", "", "users")
        assert result == "api/users"

    def test_join_path_segments_with_whitespace(self):
        """Test joining with whitespace strings."""
        result = join_path_segments("api", "  ", "users")
        assert result == "api/users"

    def test_join_path_segments_strips_slashes(self):
        """Test that leading/trailing slashes are stripped."""
        result = join_path_segments("/api/", "/v1/", "/users/")
        assert result == "api/v1/users"

    def test_join_path_segments_mixed_types(self):
        """Test joining with mixed types."""
        result = join_path_segments("api", "v1", "users", 456, "posts", None)
        assert result == "api/v1/users/456/posts"

    def test_join_path_segments_all_none(self):
        """Test joining with all None values."""
        result = join_path_segments(None, None, None)
        assert result == ""

    def test_join_path_segments_all_empty(self):
        """Test joining with all empty/whitespace values."""
        result = join_path_segments("", "  ", None, "   ")
        assert result == ""

    def test_join_path_segments_complex_slashes(self):
        """Test handling of complex slash patterns."""
        result = join_path_segments("//api//", "///v1///", "//users//")
        assert result == "api/v1/users"

    def test_join_path_segments_numeric_zero(self):
        """Test joining with zero as a number."""
        result = join_path_segments("users", 0, "posts")
        assert result == "users/0/posts"

    def test_join_path_segments_string_zero(self):
        """Test joining with zero as a string."""
        result = join_path_segments("users", "0", "posts")
        assert result == "users/0/posts"
