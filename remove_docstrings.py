#!/usr/bin/env python3
"""
Script to remove docstrings from Python files.
"""

import os
import re
import sys


def remove_docstrings(file_path):
    """
    Remove docstrings from a Python file.

    Args:
        file_path: Path to the Python file
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove module docstring
    content = re.sub(r'^"""[\s\S]*?"""', '', content, count=1)

    # Remove class and method docstrings
    content = re.sub(r'    """[\s\S]*?    """', '', content)

    # Write the modified content back to the file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Removed docstrings from {file_path}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python remove_docstrings.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist")
        sys.exit(1)

    remove_docstrings(file_path)
