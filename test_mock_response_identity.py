"""
Test to verify that the MockResponse class is the same when imported from different places.
"""

from crudclient.testing import MockResponse as TestingMockResponse
from crudclient.testing.response_builder.response import MockResponse as ResponseBuilderMockResponse
from crudclient.testing.types import MockResponse as TypesMockResponse


def test_mock_response_identity():
    """Test that all MockResponse imports refer to the same class."""
    print("MockResponse from types is the same as from response_builder:",
          TypesMockResponse is ResponseBuilderMockResponse)

    print("MockResponse from testing is the same as from response_builder:",
          TestingMockResponse is ResponseBuilderMockResponse)

    print("All three imports refer to the same class:",
          TypesMockResponse is ResponseBuilderMockResponse is TestingMockResponse)

    # Create instances to verify they behave the same
    response1 = TypesMockResponse(status_code=200, json_data={"source": "types"})
    response2 = ResponseBuilderMockResponse(status_code=200, json_data={"source": "response_builder"})
    response3 = TestingMockResponse(status_code=200, json_data={"source": "testing"})

    print("\nAll instances have the same class:",
          response1.__class__ is response2.__class__ is response3.__class__)

    print("Identity test passed!")


if __name__ == "__main__":
    test_mock_response_identity()
