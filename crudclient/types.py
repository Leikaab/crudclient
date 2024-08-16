from typing import Any, Dict, List, Union

JSONDict = Dict[str, Any]
JSONList = List[JSONDict]
RawResponse = Union[JSONDict, JSONList, bytes, str]
RawResponseSimple = Union[JSONDict, bytes, str]
