"""
Spy components for the crudclient testing framework.

This module provides components focused on recording interactions with mock objects
for later verification. It includes both basic spy implementations and enhanced
spy implementations with more sophisticated features.
"""

from .method_call import MethodCall
from .base import SpyBase
from .api_spy import ApiSpy
from .client_spy import ClientSpy
from .crud_spy import CrudSpy
from .enhanced import (
    CallRecord,
    EnhancedSpyBase,
    MethodSpy,
    ClassSpy,
    FunctionSpy,
    EnhancedSpyFactory,
    verify_call_sequence,
    verify_no_unexpected_calls,
    verify_call_timing,
    verify_call_arguments,
)

__all__ = [
    # Basic spy components
    'MethodCall',
    'SpyBase',
    'ApiSpy',
    'ClientSpy',
    'CrudSpy',

    # Enhanced spy components
    'CallRecord',
    'EnhancedSpyBase',
    'MethodSpy',
    'ClassSpy',
    'FunctionSpy',
    'EnhancedSpyFactory',

    # Verification helpers
    'verify_call_sequence',
    'verify_no_unexpected_calls',
    'verify_call_timing',
    'verify_call_arguments',
]
