# Rate Limit Header Parsing (EXPERIMENTAL)

This subpackage contains strategies for extracting rate limit information from HTTP response headers.
It is used by the [`RateLimiter`](../facade.py) to coordinate request throttling based on API feedback.

Currently a single parser is implemented:

- **`tripletex.py`** – defines `TripletexParser` for parsing Tripletex API headers
  (`X-Rate-Limit-Remaining` and `X-Rate-Limit-Reset`).
- **`__init__.py`** – package marker with a short module description.

There are no further subpackages.

## Usage Example
```python
from crudclient.ratelimit.parsing.tripletex import TripletexParser

parser = TripletexParser()
headers = {
    "X-Rate-Limit-Remaining": "95",
    "X-Rate-Limit-Reset": "3600",
}
result = parser.parse(headers)
if result:
    remaining, reset_in = result
    print(f"{remaining} calls left, resets in {reset_in} seconds")
else:
    print("No rate limit headers present")
```

## Key Class
- `TripletexParser.parse(headers)` – returns `(remaining_calls, seconds_until_reset)` or `None` if
  the expected headers are missing or malformed. Header lookup is case-insensitive and a small
  amount of logging is performed for debugging.

## Diagram
```mermaid
graph TD
    A[HTTP response headers] --> B[TripletexParser.parse()]
    B --> C{remaining, reset_in}
```

## Testing
Run the full test suite with **pytest**:
```bash
poetry install
pytest
```

## Status
This module is **experimental** and may change without notice together with the rest of the rate
limiting feature.
