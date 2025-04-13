#!/usr/bin/env python3
"""
Pre-commit hook to enforce stub file rules:
1. Every .py file inside crudclient/ must have a matching .pyi stub file.
2. If no .pyi exists, the commit should fail.
"""

import argparse
import os
import sys
from typing import List


def check_stub_files(files: List[str]) -> List[str]:
    """
    Check if all .py files in crudclient/ have matching .pyi files.

    Args:
        files: List of files to check

    Returns:
        List of .py files that don't have matching .pyi files
    """
    # Get all .py files in the commit that are in the crudclient/ directory
    # Note: Files in hooks/ directory are already excluded since we only check crudclient/
    py_files = [f for f in files if f.endswith(".py") and f.startswith("crudclient/") and not f.startswith("hooks/")]

    # For each .py file, check if a corresponding .pyi file exists
    missing_stubs = []
    for py_file in py_files:
        pyi_file = py_file + "i"  # Convert .py to .pyi
        if pyi_file not in files and not os.path.exists(pyi_file):
            missing_stubs.append(py_file)

    return missing_stubs


def main(files: List[str]) -> int:
    """
    Main function to check stub file rules.

    Args:
        files: List of files to check

    Returns:
        0 if all checks pass, 1 otherwise
    """
    missing_stubs = check_stub_files(files)

    if missing_stubs:
        print("Error: The following .py files don't have matching .pyi stub files:")
        for py_file in missing_stubs:
            print(f"  {py_file} (missing {py_file}i)")

        print("\nTo fix this issue:")
        print("1. Create a .pyi stub file for each .py file")
        print("2. Move all docstrings from the .py file to the .pyi file")
        print("3. Add proper type annotations in the .pyi file")
        return 1

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check stub file rules")
    parser.add_argument("files", nargs="*", help="Files to check")
    args = parser.parse_args()

    # If no files are provided, check all files in the crudclient/ directory
    if not args.files:
        for root, _, files in os.walk("crudclient"):
            for file in files:
                if file.endswith(".py"):
                    args.files.append(os.path.join(root, file))

    sys.exit(main(args.files))
