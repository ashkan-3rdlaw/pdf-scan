# Tests

This directory contains all tests for the PDF scan service, organized to mirror the application structure.

## Structure

```
tests/
├── __init__.py
├── fixtures/                    # Test data files
│   ├── README.md
│   ├── sample_with_pii.pdf
│   └── sample_without_pii.pdf
├── unit/                        # Unit tests
│   ├── __init__.py
│   ├── test_models.py          # Data model tests
│   ├── validation/              # Validation module tests
│   │   ├── __init__.py
│   │   └── test_file_validator.py
│   └── processing/              # Processing module tests
│       └── __init__.py
└── integration/                 # Integration tests
    ├── __init__.py
    └── test_api.py             # API endpoint tests
```

## Test Organization

### Unit Tests (`tests/unit/`)

Tests for individual components in isolation:

- **`test_models.py`**: Tests for data models (Document, Finding, Metric)
- **`validation/test_file_validator.py`**: Tests for file validation logic
- **`processing/`**: Tests for document processing (to be added in Phase 5)

Unit tests should:
- Test a single component or function
- Mock external dependencies
- Be fast and independent
- Not require database or external services

### Integration Tests (`tests/integration/`)

Tests for component interactions and API endpoints:

- **`test_api.py`**: Tests for FastAPI endpoints (/health, /upload, etc.)

Integration tests may:
- Test multiple components working together
- Use test databases or in-memory implementations
- Test HTTP endpoints and workflows
- Verify end-to-end scenarios

### Fixtures (`tests/fixtures/`)

Test data files:

- **`sample_with_pii.pdf`**: PDF containing SSN and email for scanner testing
- **`sample_without_pii.pdf`**: Clean PDF for negative testing

See [fixtures/README.md](fixtures/README.md) for details.

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run only unit tests
uv run pytest tests/unit/

# Run only integration tests
uv run pytest tests/integration/

# Run specific test module
uv run pytest tests/unit/test_models.py

# Run specific test  function
uv run pytest tests/unit/test_models.py::test_document_creation

# Run validation tests only
uv run pytest tests/unit/validation/

# Run with coverage
uv run pytest --cov=pdf_scan --cov-report=html
```

## Writing New Tests

### File Naming

- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Where to Put Tests

Follow the application structure:

```
src/pdf_scan/
  module_name/
    file.py          →  tests/unit/module_name/test_file.py
```

Examples:
- `src/pdf_scan/models.py` → `tests/unit/test_models.py`
- `src/pdf_scan/validation/file_validator.py` → `tests/unit/validation/test_file_validator.py`
- `src/pdf_scan/processing/document_processor.py` → `tests/unit/processing/test_document_processor.py`

### Test Template

```python
"""Tests for [module description]."""

import pytest

from pdf_scan.module import ClassToTest


class TestClassName:
    """Tests for ClassToTest."""

    def test_method_with_valid_input(self):
        """Test that method works with valid input."""
        result = ClassToTest.method(valid_input)
        assert result == expected_output

    def test_method_with_invalid_input(self):
        """Test that method raises error with invalid input."""
        with pytest.raises(ExpectedException):
            ClassToTest.method(invalid_input)
```

## Test Coverage

Target: **80%+** code coverage for production code

View coverage report:
```bash
uv run pytest --cov=pdf_scan --cov-report=html
open htmlcov/index.html
```

## Current Test Count

- **Unit Tests**: 24 tests
  - Models: 4 tests
  - Validation: 20 tests
- **Integration Tests**: 8 tests
  - API endpoints: 8 tests

**Total**: 32 tests

