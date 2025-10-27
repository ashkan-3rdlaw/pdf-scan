# ClickHouse Implementation Summary

This document summarizes the ClickHouse backend implementation for Phase 7 of the PDF scan service.

## Overview

Added production-ready ClickHouse backend implementations for all three repositories (DocumentRepository, FindingRepository, MetricsRepository), allowing persistent storage with high performance and scalability.

## Files Created

### 1. Infrastructure

- **`docker-compose.yml`** - ClickHouse container setup with:
  - HTTP interface on port 8123
  - Native protocol on port 9000
  - Persistent volumes for data and logs
  - Auto-initialization with schema
  - Health checks
  - Default credentials (pdf_user/pdf_password)

- **`init-db.sql`** - Database initialization script:
  - Creates `pdf_scan` database
  - Creates `documents` table
  - Creates `findings` table
  - Creates `metrics` table
  - Matches schema defined in `docs/schema.md`

### 2. Repository Implementations

- **`src/pdf_scan/db/core/impl/clickhouse_document_repository.py`**
  - Implements `DocumentRepository` interface
  - Methods: `store_document()`, `get_document()`, `update_document_status()`, `list_documents()`
  - Handles UUID and datetime conversions
  - Uses parameterized queries for security

- **`src/pdf_scan/db/core/impl/clickhouse_finding_repository.py`**
  - Implements `FindingRepository` interface
  - Methods: `store_finding()`, `get_findings()`, `get_all_findings()`, `count_findings()`
  - Supports filtering by finding_type
  - Optimized sorting by confidence

- **`src/pdf_scan/db/analytics/impl/clickhouse_metrics_repository.py`**
  - Implements `MetricsRepository` interface
  - Methods: `store_metric()`, `get_metrics()`, `get_average_duration()`
  - Complex filtering with multiple optional parameters
  - JSON serialization for metadata field

### 3. Factory Updates

- **`src/pdf_scan/db/factory.py`** - Enhanced BackendFactory:
  - `create_clickhouse_client()` - Create ClickHouse client with configurable settings
  - Updated `create_document_repository()` - Accepts backend type ("memory" or "clickhouse")
  - Updated `create_finding_repository()` - Accepts backend type
  - Updated `create_metrics_repository()` - Accepts backend type
  - Updated `create_backends()` - Create complete backend with specified type
  - Updated `create_all_repositories()` - Create all repos with specified type

### 4. Module Exports

- **`src/pdf_scan/db/core/impl/__init__.py`**
  - Added exports for `ClickHouseDocumentRepository` and `ClickHouseFindingRepository`

- **`src/pdf_scan/db/analytics/impl/__init__.py`**
  - Added export for `ClickHouseMetricsRepository`

### 5. Documentation

- **`docs/clickhouse.md`** - Comprehensive ClickHouse guide:
  - Quick start instructions
  - Factory method usage examples
  - Connection configuration
  - Testing procedures
  - Data type mappings
  - Performance considerations
  - Troubleshooting guide
  - Production deployment recommendations

- **`CLICKHOUSE_IMPLEMENTATION.md`** - This file

### 6. Testing Scripts

- **`scripts/test_clickhouse.sh`** - ClickHouse health check script:
  - Tests HTTP interface availability
  - Tests query execution
  - Verifies database existence
  - Verifies all tables exist
  - Tests authenticated connection
  - Provides detailed status output

- **`scripts/init_clickhouse_backends.py`** - Example/test script:
  - Demonstrates ClickHouse client creation
  - Shows backend initialization
  - Tests connection
  - Provides usage examples

### 7. Updated Files

- **`pyproject.toml`**
  - Added `clickhouse-connect>=0.8.14` dependency

- **`scripts/README.md`**
  - Added ClickHouse health check section
  - Updated prerequisites
  - Updated testing workflow
  - Added ClickHouse troubleshooting

- **`README.md`**
  - Updated project structure with ClickHouse files
  - Added "Database Backends" section
  - Documented both in-memory and ClickHouse backends
  - Added quick start guide for ClickHouse

## Usage

### Start ClickHouse

```bash
# Start container
docker-compose up -d

# Verify it's running
./scripts/test_clickhouse.sh
```

### Install Dependencies

```bash
uv sync
```

### Use in Code

#### In-Memory (Default)

```python
from pdf_scan.db.factory import BackendFactory

# Creates in-memory backends (no ClickHouse needed)
backends = BackendFactory.create_backends()
```

#### ClickHouse

```python
from pdf_scan.db.factory import BackendFactory

# Create ClickHouse client
client = BackendFactory.create_clickhouse_client()

# Create backends with ClickHouse
backends = BackendFactory.create_backends(backend="clickhouse", client=client)
```

#### Custom ClickHouse Settings

```python
from pdf_scan.db.factory import BackendFactory

# Create client with custom settings
client = BackendFactory.create_clickhouse_client(
    host="clickhouse.example.com",
    port=8123,
    username="my_user",
    password="my_password",
    database="my_database",
)

backends = BackendFactory.create_backends(backend="clickhouse", client=client)
```

## Implementation Details

### Database Client

- Uses `clickhouse-connect` Python library (official ClickHouse client)
- Connection pooling handled automatically
- Supports both HTTP and native protocols (HTTP used by default)

### Data Type Conversions

| Python | ClickHouse | Notes |
|--------|-----------|-------|
| UUID | UUID | Converted to/from string |
| datetime | DateTime | Timezone-aware recommended |
| str | String | Direct mapping |
| int | UInt32/Int64 | Based on size |
| float | Float32/Float64 | Based on precision |
| dict | String | JSON serialized |
| Enum | Enum8 | Maps to enum values |

### Query Strategy

- **Parameterized queries** for security (SQL injection prevention)
- **Batch inserts** where appropriate
- **Conditional WHERE clauses** built dynamically for flexible filtering
- **Optimized sorting** based on table ORDER BY design

### Error Handling

- Connection errors caught and reported clearly
- Missing tables detected early
- Authentication failures handled gracefully
- Provides helpful error messages with troubleshooting hints

## Testing

### Automated Tests

```bash
# Install dependencies first
uv sync

# Start ClickHouse
docker-compose up -d

# Test ClickHouse connection
./scripts/test_clickhouse.sh

# Test backend initialization
uv run python scripts/init_clickhouse_backends.py
```

### Manual Testing

```python
from pdf_scan.db.factory import BackendFactory
from pdf_scan.models import Document

# Setup
client = BackendFactory.create_clickhouse_client()
backends = BackendFactory.create_backends(backend="clickhouse", client=client)

# Test document storage
doc = Document.create("test.pdf", 1234)
backends.document.store_document(doc)

# Retrieve document
retrieved = backends.document.get_document(doc.id)
assert retrieved.filename == "test.pdf"
```

## Migration Path

### From In-Memory to ClickHouse

Since in-memory storage doesn't persist, no data migration needed:

1. Start ClickHouse: `docker-compose up -d`
2. Update application to use ClickHouse backend
3. Restart application
4. All new data goes to ClickHouse

### Configuration-Based Backend Selection

Recommended approach for flexibility:

```python
import os
from pdf_scan.db.factory import BackendFactory

def create_backends():
    backend_type = os.getenv("PDF_SCAN_BACKEND", "memory")
    
    if backend_type == "clickhouse":
        client = BackendFactory.create_clickhouse_client(
            host=os.getenv("CLICKHOUSE_HOST", "localhost"),
            port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
            username=os.getenv("CLICKHOUSE_USER", "pdf_user"),
            password=os.getenv("CLICKHOUSE_PASSWORD", "pdf_password"),
            database=os.getenv("CLICKHOUSE_DB", "pdf_scan"),
        )
        return BackendFactory.create_backends(backend="clickhouse", client=client)
    
    return BackendFactory.create_backends()  # Default: in-memory
```

Then run:
```bash
# Use in-memory
uv run pdf-scan

# Use ClickHouse
PDF_SCAN_BACKEND=clickhouse uv run pdf-scan
```

## Performance Considerations

### Partitioning

Tables partitioned by month (`toYYYYMM`):
- Efficient for time-based queries
- Enables easy data retention management
- Optimizes storage and query performance

### Indexes

Primary indexes defined by ORDER BY:
- `documents`: `(upload_time, id)`
- `findings`: `(document_id, finding_type, id)`
- `metrics`: `(operation, timestamp)`

### TTL Policy

Metrics table has 90-day TTL for automatic cleanup.

### Connection Pooling

`clickhouse-connect` handles connection pooling automatically.

## Production Recommendations

1. **Use environment variables** for configuration
2. **Enable TLS/SSL** for ClickHouse connections
3. **Set up replication** using ReplicatedMergeTree
4. **Configure backups** for ClickHouse data volumes
5. **Monitor performance** with metrics endpoint (Phase 8)
6. **Set up alerts** for connection failures
7. **Use managed ClickHouse** services for easier ops

## Next Steps

### Phase 7 Completion

To fully complete Phase 7:

1. ✅ ClickHouse implementations created
2. ✅ Factory supports backend selection
3. ✅ Docker setup with docker-compose
4. ✅ Schema initialization
5. ✅ Documentation created
6. ⏳ Update `app.py` to use ClickHouse (or environment-based selection)
7. ⏳ Create integration tests with actual ClickHouse instance
8. ⏳ Add environment variable configuration
9. ⏳ Performance comparison between in-memory and ClickHouse

### Future Enhancements

- Batch insert operations for better performance
- Read replicas for high availability
- Sharding for horizontal scaling
- Query optimization based on usage patterns
- Connection retry logic with exponential backoff
- Circuit breaker pattern for resilience

## References

- [ClickHouse Documentation](https://clickhouse.com/docs)
- [clickhouse-connect GitHub](https://github.com/ClickHouse/clickhouse-connect)
- [Schema Design](./docs/schema.md)
- [API Documentation](./docs/api.md)
- [Implementation Plan](./PLAN.md)

