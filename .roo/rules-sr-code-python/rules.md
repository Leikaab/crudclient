**Core Responsibility:** Write clean, robust, secure, performant, and maintainable Python code that strictly adheres to the project's architecture and conventions.

**Key Instructions & Constraints:**

1.  **NEVER Commit Code:** You **MUST NOT** use `git commit` or attempt any version control commits. This is the responsibility of the `version-control` mode, you can only add code using `git add <file_path>`.
2.  **Mandatory Post-Change Checks:** After **every** `write_to_file` or `apply_diff` operation on a file (`<file_path>`), you **MUST**:
    *   Run these checks directly using `execute_command`:
        *   `mypy .` (Run static type checking for the whole project)
        *   `python hooks/check_file_length.py <file_path>` (Check max file length)
        *   `git add .` (stage ALL changes, so the hooks checks all files)
    *   **Delegate** all other testing to the `test-runner-summarizer` mode:
        *   Create a new task with the `test-runner-summarizer` mode
        *   Request execution of `pre-commit run` and any necessary `pytest` commands
        *   Wait for results before proceeding

    *   **If any check fails:** You MUST fix the code immediately, re-apply the changes, and re-run *all* checks until they pass.
3.  **Architecture & Conventions (`ARCHITECTURE.md`, `CONTRIBUTING.md`):**
    *   **Type Annotations & Comment Handling:** Include type hints and detailed docstrings directly in the `.py` files. **Remove** explanatory comments (single or multi-line) that describe implementation steps (e.g., `# Make the API request`, `# Assuming data validation...`). **Keep** comments essential for tooling, such as `# type: ignore[...]`.
    *   **Single Responsibility Principle (SRP):** Ensure classes and functions have a single, well-defined purpose.
    *   **Pydantic:** Use Pydantic for data modeling, serialization, and validation where appropriate.
    *   **File Structure:** Organize code logically. Generally, limit files to a single class definition.
    *   **File Length:** Keep files concise (enforced by `check_file_length.py`).
    *   **Composition:** Prefer composition over inheritance where suitable.
    *   **Tooling Awareness:** Note that `black`, `isort`, and `flake8` are run by pre-commit hooks (handled by `version-control` mode), but write code that conforms to their standards.
4.  **Temporary Files:** If you need to create temporary files for checks, modifications, or other intermediate steps, place them exclusively within the `/artifacts/` directory. This directory is ignored by version control (`.gitignore`). Do not create temporary files in the project root or other source directories.
5.  **Output:** When using `attempt_completion`, provide a concise summary. State the task is done and checks passed (e.g., 'Task completed: [Brief description]. All checks passed.'). If errors were encountered and fixed, briefly note the final successful state. If blocked by unresolvable errors, clearly state the issue and provide only the essential details needed for debugging (e.g., 'Task blocked: [Specific error] in [file:line]. Unable to proceed until resolved.'). Avoid including full error logs.

6.  **Testing Delegation:** For detailed testing requirements, refer to the `.roo/rules-sr-code-python/testing_and_quality_control.md` file. You **MUST** delegate all testing responsibilities (except `mypy`) to the `test-runner-summarizer` mode as specified in that document. This includes:
    *   All `pytest` commands
    *   All `pre-commit` commands
    *   All linting tools