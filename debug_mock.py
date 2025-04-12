from unittest.mock import MagicMock

m = MagicMock()
m.some_method(1, 2, key='value')
print("mock_calls:", m.mock_calls)
print("type of first call:", type(m.mock_calls[0]))
print("dir of first call:", dir(m.mock_calls[0]))
print("first call name:", m.mock_calls[0][0])
print("first call args:", m.mock_calls[0][1])
print("first call kwargs:", m.mock_calls[0][2])
