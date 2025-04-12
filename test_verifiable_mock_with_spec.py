from crudclient.testing.verification import Verifier
from tests.unit.helpers import VerifiableMock

# Create a class with a method to mock


class SomeClass:
    def some_method(self, arg1, arg2, key=None):
        return f"Called with {arg1}, {arg2}, key={key}"


# Create a VerifiableMock with spec
mock = VerifiableMock(spec=SomeClass)

# Call methods on it
mock.some_method(1, 2, key="value")

# Print the calls
print("Calls:", mock.calls)
print("Number of calls:", len(mock.calls))
print("First call method name:", mock.calls[0].method_name)
print("First call args:", mock.calls[0].args)
print("First call kwargs:", mock.calls[0].kwargs)

# Try using Verifier
try:
    Verifier.verify_called_once_with(mock, "some_method", 1, 2, key="value")
    print("Verification passed for some_method")
except Exception as e:
    print("Verification failed for some_method:", e)
