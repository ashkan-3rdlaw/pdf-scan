# PDF Scan Service

A web service that accepts PDF uploads, scans them for sensitive information, stores findings in Clickhouse, and provides a query endpoint for results.

## Project Structure

```
pdf-scan/
├── src/
│   └── pdf_scan/          # Main application code
│       └── __init__.py
├── tests/                 # Test suite
│   ├── __init__.py
│   └── test_basic.py
├── PLAN.md               # Implementation plan and progress tracking
├── pyproject.toml        # Project dependencies and configuration
└── README.md            # This file
```

## Quick Start

### Installation

```bash
# Install dependencies
uv sync
```

### Running

```bash
# Run the application
uv run pdf-scan
```

## Implementation Plan

See [PLAN.md](PLAN.md) for detailed implementation plan and progress tracking.

**Current Status**: Initial Setup

## Technology Stack

- **Language**: Python 3.13
- **Dependency Management**: uv

Dependencies will be added incrementally as features are implemented.
