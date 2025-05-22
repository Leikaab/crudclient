# Testing and Quality Control

This document outlines the strict requirements for handling testing, linting, and quality control in the `sr-code-python` mode.

## Core Principle: Delegation of Testing

The `sr-code-python` mode **MUST NOT** run tests or linting tools directly (with the sole exception of `mypy`). This is a **CRITICAL REQUIREMENT** that ensures proper separation of responsibilities between development and testing.

## Allowed Direct Quality Checks

You may **ONLY** run the following checks directly:

- `mypy .` - For type checking after code changes
- `git add .` - For staging changes before quality checks

## Required Test Delegation Process

### 1. What to Delegate

The following must **ALWAYS** be delegated to the `test-runner-summarizer` mode:

- All `pytest` commands (including specific test files or test cases)
- All `pre-commit` commands and hooks
- All linting tools (`flake8`, `black`, etc.)
- Any other quality checks except `mypy`

### 2. How to Delegate Tests

To properly delegate testing:

1. Create a new task with the `test-runner-summarizer` mode
2. Provide clear instructions on which tests to run
3. Wait for the results before reporting completion

Example delegations:

**For code changes:**
```
<new_task>
<mode>test-runner-summarizer</mode>
<message>Run the following tests for the newly implemented endpoint:
1. pytest tests/integration/test_ledgers/test_account.py -v
2. pre-commit run --all-files
</message>
</new_task>
```

**For routine checks after file modifications:**
```
<new_task>
<mode>test-runner-summarizer</mode>
<message>Run pre-commit checks on the modified files:
pre-commit run
</message>
</new_task>
```

**For comprehensive testing:**
```
<new_task>
<mode>test-runner-summarizer</mode>
<message>Run full test suite and all quality checks:
1. pytest
2. pre-commit run --all-files
</message>
</new_task>
```

### 3. Interpreting Test Results

- After creating a `test-runner-summarizer` subtask, you'll receive the test results in the next message
- Review the test summary provided
- Address any failures before reporting completion
- Include a reference to the test results in your completion message

## Integration with Development Workflow

1. **Implementation Phase:**
   - Write code according to requirements
   - Run `mypy .` to check types
   - Fix any type errors

2. **Testing Phase:**
   - Delegate all tests to `test-runner-summarizer`
   - Wait for results
   - Fix any issues reported

3. **Completion Phase:**
   - Report completion only after all delegated tests pass
   - Include a summary of what tests were run and their results

   ## Processing Test Results

   It is **CRITICAL** that you:

   1. After creating a `test-runner-summarizer` subtask, you'll receive the test results in the next message
   2. Do not proceed with further development or report completion until you have received and analyzed the test results
   3. If tests fail, address the issues before continuing
   4. Reference the test results in your completion message

   Example workflow:
   ```
   1. Implement feature
   2. Run mypy directly
   3. Delegate pre-commit and pytest to test-runner-summarizer
   4. Receive test results in the next message
   5. Fix any issues if tests fail
   6. Only then report completion
   ```

   ## Common Mistakes to Avoid

   - **NEVER** run `pytest` directly
   - **NEVER** run `pre-commit` directly
   - **NEVER** attempt to bypass test delegation
   - **NEVER** report completion before receiving test results from `test-runner-summarizer`
   - **NEVER** assume tests will pass without verification

   Following these guidelines ensures consistent quality control and proper separation of responsibilities between development and testing activities.