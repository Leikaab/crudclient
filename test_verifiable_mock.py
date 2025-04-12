from crudclient.testing.verification import Verifier
from tests.unit.helpers import VerifiableMock, translate_mock_calls_for_verifier

# Create a VerifiableMock
mock = VerifiableMock()

# Call methods on it
mock.some_method(1, 2, key="value")
mock.another_method()
mock()  # Direct call to the mock

# Print the calls
print("Calls:", mock.calls)
print("Number of calls:", len(mock.calls))
print("mock_calls:", mock.mock_calls)

# Try using translate_mock_calls_for_verifier
translate_mock_calls_for_verifier(mock)
print("\nAfter translate_mock_calls_for_verifier:")
print("Calls:", mock.calls)
print("Number of calls:", len(mock.calls))

# Try using Verifier
try:
    Verifier.verify_called_once_with(mock, "some_method", 1, 2, key="value")
    print("Verification passed for some_method")
except Exception as e:
    print("Verification failed for some_method:", e)

try:
    Verifier.verify_called_once_with(mock, "another_method")
    print("Verification passed for another_method")
except Exception as e:
    print("Verification failed for another_method:", e)

try:
    Verifier.verify_called_once_with(mock, "")
    print("Verification passed for direct call")
except Exception as e:
    print("Verification failed for direct call:", e)
