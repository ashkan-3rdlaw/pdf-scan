# PDF Scan Service

A web service that accepts PDF uploads, scans them for sensitive information, stores findings in Clickhouse, and provides a query endpoint for results.

## Project Structure

```
pdf-scan/
├── src/
│   └── pdf_scan/                   # Main application code
│       ├── __init__.py
│       ├── app.py                  # FastAPI application
│       ├── main.py                 # Server entry point
│       ├── models/                 # Data models
│       │   └── __init__.py
│       ├── processing/             # Document processing
│       │   ├── __init__.py
│       │   └── document_processor.py
│       └── validation/             # File validation
│           ├── __init__.py
│           └── file_validator.py
├── tests/                          # Test suite (mirrors src structure)
│   ├── fixtures/                   # Test data files
│   ├── unit/                       # Unit tests
│   │   ├── models/
│   │   ├── validation/
│   │   └── processing/
│   └── integration/                # Integration tests
│       └── test_api.py
├── scripts/                        # Manual testing scripts
├── docs/                           # Documentation
├── PLAN.md                         # Implementation plan
├── pyproject.toml                  # Project configuration
└── README.md                       # This file
```

## Quick Start

### Installation

```bash
# Install dependencies
uv sync
```

### Running the Server

```bash
# Run the FastAPI server (starts on http://localhost:8000)
uv run pdf-scan
```

The server will start with auto-reload enabled for development.

### API Documentation

Once the server is running:
- **Interactive API Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

### Testing

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
uv run pytest tests/unit/models/test_models.py
```

See [tests/README.md](tests/README.md) for detailed testing documentation.

### Manual Testing

See [scripts/README.md](scripts/README.md) for manual testing with curl:

```bash
# Test health endpoint
./scripts/test_health.sh

# Upload sample PDF (uses default test PDF)
./scripts/test_upload.sh

# Test validation
./scripts/test_invalid_file.sh
```

## Implementation Plan

See [PLAN.md](PLAN.md) for detailed implementation plan and progress tracking.

**Current Status**: Initial Setup

## Technology Stack

- **Language**: Python 3.13
- **Dependency Management**: uv

Dependencies will be added incrementally as features are implemented.
