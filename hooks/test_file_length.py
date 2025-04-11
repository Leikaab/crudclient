#!/usr/bin/env python3
"""
This is a module docstring.
It spans multiple lines.
This should be excluded from the line count.
"""

# This is a comment that should be counted


def function1() -> None:
    """
    This is a function docstring.
    It should be counted since it's not a module docstring.
    """
    # This line should be counted
    pass  # This line should be counted


# Blank line above should be excluded


class TestClass:
    """Class docstring should be counted."""

    def method(self) -> bool:
        # This method should be counted
        return True


# Another comment that should be counted
