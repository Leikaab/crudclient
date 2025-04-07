#!/usr/bin/env python3
"""
Pre-commit hook to enforce docstring rules:
1. All method, function, and class docstrings must be placed in the corresponding .pyi files.
2. No docstrings should exist in .py source files.
"""

import argparse
import ast
import sys
from typing import List, Tuple


def has_docstrings(file_path: str) -> List[Tuple[int, str, str]]:
    """
    Check if a Python file contains docstrings.

    Args:
        file_path: Path to the Python file to check

    Returns:
        List of tuples containing (line_number, node_type, docstring) for each docstring found
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            tree = ast.parse(file.read(), filename=file_path)
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            return []

    docstrings = []

    # Check module docstring
    if (isinstance(tree, ast.Module)
            and len(tree.body) > 0
            and isinstance(tree.body[0], ast.Expr)
            and isinstance(tree.body[0].value, ast.Constant)
            and isinstance(tree.body[0].value.value, str)):
        docstrings.append((1, "module", tree.body[0].value.value))

    # Check class, function, and method docstrings
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            if (len(node.body) > 0
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                node_type = "class" if isinstance(node, ast.ClassDef) else "function"
                docstrings.append((node.lineno, node_type, node.body[0].value.value))

    return docstrings


def main(files: List[str]) -> int:
    """
    Main function to check docstring rules.

    Args:
        files: List of files to check

    Returns:
        0 if all checks pass, 1 otherwise
    """
    errors = []

    for file_path in files:
        if not (file_path.endswith('.py') or file_path.endswith('.pyi')):
            continue

        # Skip files in the hooks/ and tests/ directories
        if file_path.startswith('hooks/') or file_path.startswith('tests/'):
            continue

        is_stub = file_path.endswith('.pyi')
        docstrings = has_docstrings(file_path)

        if not is_stub and docstrings:
            # .py files should not have docstrings
            for line, node_type, docstring in docstrings:
                print(f"DEBUG: Found docstring in {file_path} at line {line}, type {node_type}, content: {docstring[:50]}...")
                errors.append(f"{file_path}:{line}: {node_type} docstring found in .py file. "
                              f"Docstrings should be in .pyi files only.")

    if errors:
        for error in errors:
            print(error)
        print("\nTo fix these issues:")
        print("1. Move all docstrings from .py files to their corresponding .pyi files")
        print("2. Remove all docstrings from .py files")
        return 1

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check docstring rules')
    parser.add_argument('files', nargs='*', help='Files to check')
    args = parser.parse_args()

    sys.exit(main(args.files))
