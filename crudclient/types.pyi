"""
Module `types.py`
================

This module defines common type aliases used throughout the crudclient library.
These type aliases provide consistent typing for JSON data structures and API responses.

Type Aliases:
    - JSONDict: A dictionary with string keys and any values, representing a JSON object.
    - JSONList: A list of JSONDict objects, representing a JSON array of objects.
    - RawResponse: A union type representing various possible raw API responses.
    - RawResponseSimple: A simplified union type for raw API responses.
"""

from typing import Any, Dict, List, Union

# A dictionary with string keys and any values, representing a JSON object
JSONDict = Dict[str, Any]

# A list of JSONDict objects, representing a JSON array of objects
JSONList = List[JSONDict]

# A union type representing various possible raw API responses
RawResponse = Union[JSONDict, JSONList, bytes, str, None]

# A simplified union type for raw API responses
RawResponseSimple = Union[JSONDict, bytes, str, None]
