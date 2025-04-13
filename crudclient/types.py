from typing import Any, Dict, List, Union

JSONDict = Dict[str, Any]
JSONList = List[JSONDict]
RawResponse = Union[JSONDict, JSONList, bytes, str, None]
RawResponseSimple = Union[JSONDict, JSONList, bytes, str, None]
