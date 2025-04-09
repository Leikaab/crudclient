"""
Simple test to verify that the MockResponse class is correctly imported and works as expected.
"""

import json

from crudclient.testing.types import MockResponse


def test_mock_response_from_types():
    """Test that MockResponse imported from types works correctly."""
    # Create a mock response
    response = MockResponse(
        status_code=200,
        json_data={"message": "Success"}
    )

    # Verify the response properties
    assert response.status_code == 200
    assert response.json() == {"message": "Success"}
    assert response.text == json.dumps({"message": "Success"})

    print("MockResponse test passed!")


if __name__ == "__main__":
    test_mock_response_from_types()
