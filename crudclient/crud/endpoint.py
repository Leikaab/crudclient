import logging
from typing import List, Optional, Tuple, Union

# Get a logger for this module
logger = logging.getLogger(__name__)

# Type alias for path arguments
PathArgs = Optional[Union[str, int]]


def _endpoint_prefix(self) -> Union[Tuple[Optional[str], ...], List[Optional[str]]]:
    if self.parent:
        # For nested resources, include the parent resource path and ID
        return (self.parent._resource_path, None)
    return []


def _validate_path_segments(self, *args: PathArgs) -> None:
    for arg in args:
        if arg is not None and not isinstance(arg, (str, int)):
            raise TypeError(f"Path segment must be a string, integer, or None, got {type(arg).__name__}")


def _get_parent_path(self, parent_args: Optional[tuple] = None) -> str:
    if not self.parent:
        return ""

    if parent_args:
        return self.parent._get_endpoint(*parent_args)
    return self.parent._get_endpoint()


def _build_resource_path(self, *args: PathArgs) -> List[str]:
    segments = []
    for arg in args:
        if arg is not None:
            segments.append(str(arg))
    return segments


def _get_prefix_segments(self) -> List[str]:
    prefix = self._endpoint_prefix()
    if isinstance(prefix, tuple):
        return self._build_resource_path(*prefix)
    return self._build_resource_path(*prefix)


def _join_path_segments(self, segments: List[str]) -> str:
    if not segments:
        return ""

    # Join segments with slashes and ensure no double slashes
    path = "/".join(segment.strip("/") for segment in segments if segment)
    return path


def _get_endpoint(self, *args: Optional[Union[str, int]], parent_args: Optional[tuple] = None) -> str:
    # Validate path segments
    self._validate_path_segments(*args)

    # Get parent path for nested resources
    parent_path = self._get_parent_path(parent_args)

    # Get prefix segments
    prefix_segments = self._get_prefix_segments()

    # Build resource path
    resource_segments = [self._resource_path]
    resource_segments.extend(self._build_resource_path(*args))

    # Join all segments
    all_segments = []
    if parent_path:
        all_segments.append(parent_path)

    # Only add prefix segments if there's no parent path being used
    # (Prefix is usually for static parts like /api/v1, not dynamic parent types)
    elif prefix_segments:
        all_segments.append(self._join_path_segments(prefix_segments))

    # Add the main resource segments
    all_segments.append(self._join_path_segments(resource_segments))

    # Join with slashes and ensure no double slashes
    endpoint = "/".join(segment.strip("/") for segment in all_segments if segment)

    logger.debug(f"Built endpoint: {endpoint}")
    return endpoint
