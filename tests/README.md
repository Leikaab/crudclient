# HOW TESTS SHOULD BE CREATED AND DOCUMENTED

## Documenting tests

* GIVEN - what are the initial conditions for the test?
* WHEN - what is occurring that needs to be tested?
* THEN - what is the expected reponse?

## pytest commands

* `poetry run pytest`
* `poetry run pytest tests/unit` run one folder of tests
* `poetry run pytest tests/unit/test_todos.py` run spesific file of tests
* `poetry run pytest tests/unit/test_todos.py::test_new_todo` run spesific test
* `poetry run pytest -v` gives u verbose output of individual tests
* `poetry run pytest --last-failed` lets u rerun only last failed test
* `poetry run pytest --setup-show` shows when fixtures are called relative to the testfunctions

## coverage

[coverage docs](https://coverage.readthedocs.io/)
[pytest-cov docs](https://pytest-cov.readthedocs.io/en/latest/)