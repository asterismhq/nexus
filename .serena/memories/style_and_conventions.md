# Style and Conventions
- Follow PEP 484 type hints where practical; modules rely on pydantic models and FastAPI typing.
- Formatting and linting enforced by `black` (py312 target) and `ruff` (E,F,I rules, ignore E501). Run them before commits.
- Tests use `pytest` with asyncio auto mode; fixtures configured via layered `conftest.py` files.
- Keep dependency container registrations explicit; prefer constructor injection patterns used across the codebase.