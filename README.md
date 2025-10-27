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
│       │   ├── __init__.py
│       │   └── entities.py
│       ├── db/                     # Database interfaces and implementations
│       │   ├── __init__.py
│       │   ├── backends.py         # Backends container for dependency management
│       │   ├── factory.py          # Backend factory for dependency injection
│       │   ├── core/               # Core database interfaces
│       │   │   ├── __init__.py
│       │   │   ├── document_repository.py
│       │   │   ├── finding_repository.py
│       │   │   └── impl/           # Core implementations
│       │   │       ├── __init__.py
│       │   │       ├── in_memory_document_repository.py
│       │   │       ├── in_memory_finding_repository.py
│       │   │       ├── clickhouse_document_repository.py
│       │   │       └── clickhouse_finding_repository.py
│       │   └── analytics/          # Analytics interfaces
│       │       ├── __init__.py
│       │       ├── metrics_repository.py
│       │       └── impl/           # Analytics implementations
│       │           ├── __init__.py
│       │           ├── in_memory_metrics_repository.py
│       │           └── clickhouse_metrics_repository.py
│       ├── processing/             # Document processing
│       │   ├── __init__.py
│       │   └── document_processor.py
│       ├── scanner/                # PDF scanning
│       │   ├── __init__.py
│       │   ├── pdf_scanner_interface.py
│       │   └── regex_scanner.py
│       └── validation/             # File validation
│           ├── __init__.py
│           └── file_validator.py
├── tests/                          # Test suite (mirrors src structure)
│   ├── fixtures/                   # Test data files
│   │   ├── sample_with_pii.pdf
│   │   └── sample_without_pii.pdf
│   ├── unit/                       # Unit tests
│   │   ├── models/
│   │   │   └── test_models.py
│   │   ├── db/                     # Database tests
│   │   │   ├── test_backends.py     # Backends container tests
│   │   │   ├── test_factory.py     # Factory tests
│   │   │   ├── core/impl/          # Core implementation tests
│   │   │   └── analytics/impl/     # Analytics implementation tests
│   │   ├── scanner/                # Scanner tests
│   │   │   └── test_regex_scanner.py
│   │   ├── validation/
│   │   │   └── test_file_validator.py
│   │   └── processing/
│   └── integration/                # Integration tests
│       └── test_api.py
├── scripts/                        # Manual testing scripts
├── docs/                           # Documentation
│   ├── schema.md                   # Database schema
│   ├── api.md                      # API documentation
│   └── clickhouse.md               # ClickHouse backend guide
├── docker-compose.yml              # ClickHouse container setup
├── init-db.sql                     # ClickHouse schema initialization
├── PLAN.md                         # Implementation plan
├── pyproject.toml                  # Project configuration
└── README.md                       # This file
```

## Quick Start

### Prerequisites

- macOS (for setup script)
- Homebrew
- Docker Desktop

### Installation

#### Option 1: Automated Setup (macOS)

Run the setup script to install all dependencies and set up the project:

```bash
./setup.sh
```

This will:
- Install `uv`, `jq`, `docker`, and `docker-compose` via Homebrew
- Set up Python 3.13 if needed
- Run `uv sync` to install project dependencies

#### Option 2: Manual Setup

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
# Run all test scripts (health, upload, validation)
./scripts/run_all_tests.sh

# Or run individual tests:

# Test health endpoint
./scripts/test_health.sh

# Upload sample PDF (uses default test PDF)
./scripts/test_upload.sh

# Test validation
./scripts/test_invalid_file.sh
```

**Note:** The manual test scripts require the server to be running (`uv run pdf-scan`).

## Implementation Plan

See [PLAN.md](PLAN.md) for detailed implementation plan and progress tracking.

**Current Status**: Phases 0-5 Complete (Upload → Scan → Store workflow functional)

## Technology Stack

- **Language**: Python 3.13
- **Dependency Management**: uv
- **Web Framework**: FastAPI
- **PDF Processing**: pypdf
- **Database**: In-memory (default) or ClickHouse (production-ready)
- **Database Client**: clickhouse-connect

## Database Backends

The application supports two database backends configured via environment variables:

### Environment Configuration

Create a `.env` file in the project root:

```bash
# Database Backend Configuration
# Options: "memory" or "clickhouse"
DATABASE_BACKEND=clickhouse

# ClickHouse Configuration (only used when DATABASE_BACKEND=clickhouse)
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_USERNAME=pdf_user
CLICKHOUSE_PASSWORD=pdf_password
CLICKHOUSE_DATABASE=pdf_scan

# Connection Pool Configuration
CLICKHOUSE_POOL_MINSIZE=5
CLICKHOUSE_POOL_MAXSIZE=20

# Application Configuration
APP_HOST=0.0.0.0
APP_PORT=8000
APP_RELOAD=true
```

### In-Memory Backend
- **Use case**: Development, testing, demos
- **Persistence**: Data lost on restart
- **Performance**: Very fast, no I/O
- **Setup**: Set `DATABASE_BACKEND=memory` in `.env`

### ClickHouse Backend (Production)
- **Use case**: Production deployments
- **Persistence**: Data persists across restarts
- **Performance**: Optimized for analytics workloads with async connection pooling
- **Setup**: Set `DATABASE_BACKEND=clickhouse` in `.env`

#### Quick Start with ClickHouse

1. **Start ClickHouse container:**
   ```bash
   docker-compose up -d
   ```

2. **Verify ClickHouse is running:**
   ```bash
   ./scripts/test_clickhouse.sh
   ```

3. **Run the application:**
   ```bash
   uv run uvicorn src.pdf_scan.app:app --reload
   ```

The application will automatically use ClickHouse based on your `.env` configuration.

**See [docs/clickhouse.md](docs/clickhouse.md) for detailed ClickHouse setup and usage guide.**

### Testing & Code Quality

- **Testing**: pytest, httpx
- **Code Quality**: ruff (linting and formatting)

## Performance Metrics & Monitoring

The service includes comprehensive performance monitoring capabilities:

### Metrics Endpoint (`/metrics`)

Returns average processing times by operation type with optional filtering:

```bash
# Get all metrics
curl http://localhost:8000/metrics

# Filter by operation type
curl "http://localhost:8000/metrics?operation=upload"
curl "http://localhost:8000/metrics?operation=scan"

# Filter by time range
curl "http://localhost:8000/metrics?start_time=2025-10-27T19:00:00Z"

# Combined filters
curl "http://localhost:8000/metrics?operation=upload&start_time=2025-10-27T19:00:00Z"
```

### Response Format

```json
{
  "metrics": {
    "upload": {
      "average_duration_ms": 1.19,
      "operation": "upload"
    },
    "scan": {
      "average_duration_ms": 0.72,
      "operation": "scan"
    }
  },
  "filters": {
    "operation": null,
    "start_time": null,
    "end_time": null
  },
  "timestamp": "2025-10-27T20:25:28.476760"
}
```

### Testing Metrics

Run the comprehensive metrics test suite:

```bash
# Test all metrics functionality
bash scripts/test_metrics.sh

# Run complete test suite (includes metrics)
bash scripts/run_all_tests.sh
```

## Cloud Deployment

### Quick Start on Render.com

Deploy your PDF scan service to the cloud in minutes:

1. **Push to Git Repository**
   ```bash
   git add requirements.txt render.yaml
   git commit -m "Add Render deployment configuration"
   git push origin main
   ```

2. **Deploy on Render**
   - Sign up at [render.com](https://render.com/)
   - Connect your Git repository
   - Create new Web Service
   - Use these settings:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn src.pdf_scan.app:app --host 0.0.0.0 --port $PORT`
     - **Environment Variables**:
       ```bash
       DATABASE_BACKEND=memory
       APP_HOST=0.0.0.0
       APP_PORT=$PORT
       APP_RELOAD=false
       ```

3. **Test Your Deployment**
   ```bash
   # Test your deployed service
   ./scripts/test_cloud_deployment.sh https://your-service-name.onrender.com
   ```

### Deployment Features

- ✅ **Zero Configuration**: Works out of the box with in-memory backend
- ✅ **HTTPS**: Automatic SSL certificates
- ✅ **Zero Downtime**: Automatic deploys
- ✅ **Free Tier**: Available for testing and demos
- ✅ **Health Checks**: Built-in monitoring
- ✅ **API Docs**: Available at `/docs` and `/redoc`

### Environment Options

| Backend | Use Case | Persistence | External Dependencies |
|---------|----------|-------------|----------------------|
| `memory` | Quick start, demos | No (data lost on restart) | None |
| `clickhouse` | Production | Yes | External ClickHouse service |

See [docs/deployment.md](docs/deployment.md) for detailed deployment guide.

## Project Status

**Phase 8: Performance Metrics Enhancement** ✅ **COMPLETED**

- ✅ Metrics collection with precise timing
- ✅ `/metrics` endpoint with filtering capabilities
- ✅ Operation-specific performance tracking
- ✅ Time range filtering support
- ✅ Comprehensive test coverage
- ✅ Error handling for invalid parameters

**Phase 9: Cloud Deployment on Render.com** 🔴 **IN PROGRESS**

- ✅ Deployment configuration files created
- ✅ Infrastructure as Code setup
- ✅ Cloud testing scripts
- 🔴 Service deployment and testing
