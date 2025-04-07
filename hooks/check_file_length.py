#!/usr/bin/env python3
"""
Pre-commit hook to enforce file length rules:
1. .py source files must be ≤ 300 lines of actual code and inline comments.
2. Module docstrings and blank lines are excluded from the count.
"""

import argparse
import ast
import os
import sys
from typing import Dict, List, Tuple


def count_file_lines(file_path: str) -> int:
    """
    Count the number of non-blank lines in a file, excluding the module docstring.

    Args:
        file_path: Path to the file to count lines for

    Returns:
        Number of non-blank, non-module-docstring lines in the file
    """
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as file:
        file_content = file.read()

    # Check if the file has a module docstring using AST
    has_module_docstring = False
    module_docstring = None

    try:
        tree = ast.parse(file_content, filename=file_path)
        # Check for module docstring
        if (len(tree.body) > 0
                and isinstance(tree.body[0], ast.Expr)
                and isinstance(tree.body[0].value, ast.Constant)
                and isinstance(tree.body[0].value.value, str)):
            has_module_docstring = True
            module_docstring = tree.body[0].value.value
    except (SyntaxError, AttributeError):
        # If there's a syntax error or attribute error, fall back to counting all non-blank lines
        with open(file_path, 'r', encoding='utf-8') as file:
            return sum(1 for line in file if line.strip())

    # Count non-blank lines, excluding the module docstring
    lines = file_content.splitlines()
    count = 0

    # Get module docstring line numbers using AST
    module_docstring_lines = set()
    if has_module_docstring and tree.body and isinstance(tree.body[0], ast.Expr):
        # Get the line number of the module docstring
        start_line = tree.body[0].lineno

        # Find the end line by counting newlines in the docstring
        docstring_text = module_docstring
        if docstring_text is not None:
            docstring_line_count = docstring_text.count('\n') + 1
        else:
            docstring_line_count = 1  # Default to 1 if docstring is None

        # Add all line numbers of the module docstring to the set
        for i in range(start_line, start_line + docstring_line_count):
            module_docstring_lines.add(i)

    # Count non-blank lines that are not part of the module docstring
    for i, line in enumerate(lines, 1):
        # Skip blank lines and module docstring lines
        if line.strip() and i not in module_docstring_lines:
            count += 1

    return count


def check_file_length(files: List[str], max_lines: int = 300) -> Dict[str, int]:
    """
    Check if any .py files exceed the maximum line count.

    Args:
        files: List of files to check
        max_lines: Maximum number of lines allowed in a file

    Returns:
        Dictionary mapping file paths to line counts for files that exceed the limit
    """
    too_long = {}

    for file_path in files:
        if not file_path.endswith('.py'):
            continue

        line_count = count_file_lines(file_path)
        if line_count > max_lines:
            too_long[file_path] = line_count

    return too_long


def main(files: List[str], max_lines: int = 300, verbose: bool = False) -> int:
    """
    Main function to check file length rules.

    Args:
        files: List of files to check
        max_lines: Maximum number of lines allowed in a file
        verbose: Whether to print line counts for all files

    Returns:
        0 if all checks pass, 1 otherwise
    """
    too_long = check_file_length(files, max_lines)

    # Print line counts for all files if verbose is True
    if verbose:
        for file_path in files:
            if file_path.endswith('.py'):
                line_count = count_file_lines(file_path)
                print(f"{file_path}: {line_count} lines of code (excluding module docstring and blank lines)")

    if too_long:
        print(f"Error: The following .py files exceed the maximum line count of {max_lines}:")
        for file_path, line_count in too_long.items():
            print(f"  {file_path}: {line_count} lines of code (limit: {max_lines})")

        print("\nTo fix this issue:")
        print("1. Refactor the code to reduce file length")
        print("2. Split large files into smaller, more focused modules")
        print("3. Remove unnecessary code and inline comments")
        print("\nNote: Module docstrings and blank lines are already excluded from the count.")
        return 1

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check file length rules')
    parser.add_argument('files', nargs='*', help='Files to check')
    parser.add_argument('--max-lines', type=int, default=300, help='Maximum number of lines allowed in a file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Print line counts for all files')
    args = parser.parse_args()

    sys.exit(main(args.files, args.max_lines, args.verbose))
