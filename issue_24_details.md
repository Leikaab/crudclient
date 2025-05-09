title:	`custom_action` limitations: forced JSON payloads and response model validation block real-world API usage
state:	OPEN
author:	SophusMaxiumus
labels:
comments:	1
assignees:
projects:
milestone:
number:	24
--
The current implementation of `custom_action` in `crudclient` has two major limitations that make it difficult or impossible to use for many real-world API endpoints:

---

### 1. Forced JSON Payloads

**Problem:**
`custom_action` always sends the request body as JSON, regardless of the HTTP method or the requirements of the target endpoint. This is problematic for endpoints that require other content types, such as `multipart/form-data` or `application/x-www-form-urlencoded`.

**Example:**
In Tripletex, the endpoint for creating a relative VAT type (`PUT /ledger/vatType/createRelativeVatType`) expects parameters as form data (query parameters or form-encoded), not as a JSON body. The only way to make this request work is to bypass `custom_action` and use the underlying client's `_request` method directly, as seen in our implementation:

```python
# tripletex/endpoints/ledger/crud/vat_type.py
def create_relative_vat_type(self, name: str, vat_type_id: int, percentage: float) -> VatType:
    params = {
        "name": name,
        "vatTypeId": vat_type_id,
        "percentage": percentage
    }
    endpoint = self._get_endpoint("createRelativeVatType")
    response = self.client._request(
        method="PUT",
        endpoint=endpoint,
        params=params
    )
    # ... process response ...
```

**Impact:**
This breaks the abstraction and makes endpoint code less maintainable and less consistent.

---

### 2. Forced Response Model Validation

**Problem:**
`custom_action` always deserializes the response using the endpoint's `_datamodel`, even for subresources or special actions that return a different structure. There is no way to override or bypass this behavior.

**Example:**
The Tripletex endpoint `/ledger/voucher/{id}/options` returns a meta-info object like:

```json
{
  "value": {
    "delete": {
      "available": true,
      "reasons": []
    }
  }
}
```

But the `TripletexVoucher` endpoint's `_datamodel` is `Voucher`, so `custom_action` tries to parse this response as a `Voucher`, resulting in either an error or a meaningless object. The only workaround is to bypass `custom_action` and use the underlying client directly to get the raw response.

---

### Suggested Fixes

1. **Payload Flexibility:**
   - Allow `custom_action` to accept a `content_type` argument and support sending data as form data, multipart, or query parameters, not just JSON.
   - If `data` is provided and `content_type` is set, use the appropriate encoding and headers.

2. **Response Model Flexibility:**
   - Allow `custom_action` to accept a `response_model` argument (or a flag to disable model validation).
   - If `response_model` is `None`, return the raw response (dict or bytes).
   - If a custom model is provided, use it for deserialization instead of the endpoint's default `_datamodel`.

3. **Backward Compatibility:**
   - Default to the current behavior if these arguments are not provided, to avoid breaking existing code.

---

**Summary:**
These changes would make `custom_action` much more flexible and suitable for real-world APIs, allowing endpoint code to remain clean, maintainable, and consistent. Without these changes, developers are forced to break abstraction and use low-level client methods, defeating the purpose of the CRUD abstraction.

---

**References:**
- [Tripletex API: /ledger/voucher/{id}/options](https://tripletex.no/v2-docs/ledger/voucher/)
- [Tripletex API: /ledger/vatType/createRelativeVatType](https://tripletex.no/v2-docs/ledger/vatType/)
author:	SophusMaxiumus
association:	none
edited:	false
status:	none
--
**UPDATE TO ISSUE**
Neither the standard CRUD methods nor `custom_action` in crudclient support multipart/form-data or file uploads. All payloads are sent as JSON, and there is no way to pass `files=...` to requests. This makes it impossible to use the intended API for endpoints requiring file uploads (e.g., POST /ledger/voucher/{voucherId}/attachment in Tripletex).

**Details:**
- The `custom_action_operation` implementation only supports JSON payloads (`kwargs["json"] = ...`) and never passes `files=...`.
- The underlying client methods (`post`, `put`, `patch`) also only support JSON and do not expose a way to pass files.
- Attempts to upload files using these methods result in 400 Bad Request from the API, as the request is not properly encoded as multipart/form-data.
- The only workaround is to use the requests session directly, bypassing the client abstraction.

**Minimal Repro:**
```python
# This fails (400 Bad Request)
api_client.ledger.voucher.custom_action(
    action="attachment",
    method="post",
    resource_id="443370851",
    data=None,
    files={"file": ("test.pdf", open("test.pdf", "rb"), "application/pdf")}
)

# This works (using requests directly)
session = api_client.client.session
url = "https://api-test.tripletex.tech/v2/ledger/voucher/443370851/attachment"
files = {"file": ("test.pdf", open("test.pdf", "rb"), "application/pdf")}
response = session.post(url, files=files)
response.raise_for_status()
```

**Expected:**
There should be a way to pass files/multipart data through the CRUD or custom_action interface, so file uploads can be performed without bypassing the client.

**Suggested Fix:**
- Add support for a `files` parameter in `custom_action_operation` and underlying client methods, and ensure it is passed through to requests without interference.
- Document how to use this for multipart/form-data endpoints.
--
