# ClickHouse Backend Implementation

This document describes how to use the ClickHouse backend implementation for the PDF scan service.

## Overview

The service supports two backend implementations:
- **In-Memory**: Default, uses Python dictionaries (data lost on restart)
- **ClickHouse**: Production-ready, persistent storage with high performance

## Quick Start

### 1. Start ClickHouse

```bash
# Start ClickHouse container with docker-compose
docker-compose up -d

# Verify it's running
./scripts/test_clickhouse.sh
```

The ClickHouse container will automatically:
- Create the `pdf_scan` database
- Initialize all tables (documents, findings, metrics)
- Set up authentication (user: `pdf_user`, password: `pdf_password`)

### 2. Install Dependencies

```bash
# Install Python dependencies including clickhouse-connect
uv sync
```

### 3. Use ClickHouse Backend

#### Option A: Update app.py to use ClickHouse

Modify `src/pdf_scan/app.py` to create ClickHouse backends:

```python
from pdf_scan.db.factory import BackendFactory

# Create ClickHouse client
clickhouse_client = BackendFactory.create_clickhouse_client()

# Create backends with ClickHouse
_backends_instance = BackendFactory.create_backends(
    backend="clickhouse",
    client=clickhouse_client
)
```

#### Option B: Use Environment Variable

Create a configuration module to switch backends based on environment:

```python
import os
from pdf_scan.db.factory import BackendFactory

def get_backend_type():
    return os.getenv("PDF_SCAN_BACKEND", "memory")  # "memory" or "clickhouse"

def create_app_backends():
    backend_type = get_backend_type()
    
    if backend_type == "clickhouse":
        client = BackendFactory.create_clickhouse_client()
        return BackendFactory.create_backends(backend="clickhouse", client=client)
    else:
        return BackendFactory.create_backends()  # Default to in-memory
```

Then run:
```bash
# Use in-memory (default)
uv run pdf-scan

# Use ClickHouse
PDF_SCAN_BACKEND=clickhouse uv run pdf-scan
```

## Factory Methods

### Create ClickHouse Client

```python
from pdf_scan.db.factory import BackendFactory

# With default settings (localhost, pdf_scan database)
client = BackendFactory.create_clickhouse_client()

# With custom settings
client = BackendFactory.create_clickhouse_client(
    host="clickhouse.example.com",
    port=8123,
    username="pdf_user",
    password="pdf_password",
    database="pdf_scan",
)
```

### Create Individual Repositories

```python
from pdf_scan.db.factory import BackendFactory

# Create ClickHouse client
client = BackendFactory.create_clickhouse_client()

# Create individual repositories
doc_repo = BackendFactory.create_document_repository("clickhouse", client)
finding_repo = BackendFactory.create_finding_repository("clickhouse", client)
metrics_repo = BackendFactory.create_metrics_repository("clickhouse", client)
```

### Create All Backends

```python
from pdf_scan.db.factory import BackendFactory

# In-memory (default)
backends = BackendFactory.create_backends()

# ClickHouse
client = BackendFactory.create_clickhouse_client()
backends = BackendFactory.create_backends(backend="clickhouse", client=client)
```

## Repository Implementations

### ClickHouseDocumentRepository

Location: `src/pdf_scan/db/core/impl/clickhouse_document_repository.py`

Methods:
- `store_document(document)` - Insert document record
- `get_document(document_id)` - Retrieve by UUID
- `update_document_status(document_id, status, error_message)` - Update status
- `list_documents(limit, offset)` - Paginated list

### ClickHouseFindingRepository

Location: `src/pdf_scan/db/core/impl/clickhouse_finding_repository.py`

Methods:
- `store_finding(finding)` - Insert finding record
- `get_findings(document_id)` - Get findings for document
- `get_all_findings(limit, offset, finding_type)` - Paginated list with filter
- `count_findings(document_id)` - Count findings

### ClickHouseMetricsRepository

Location: `src/pdf_scan/db/analytics/impl/clickhouse_metrics_repository.py`

Methods:
- `store_metric(metric)` - Insert metric record
- `get_metrics(operation, document_id, start_time, end_time, limit, offset)` - Filtered retrieval
- `get_average_duration(operation, start_time, end_time)` - Calculate averages

## Connection Settings

### Default Configuration

From `docker-compose.yml`:
```yaml
Host: localhost
HTTP Port: 8123
Native Port: 9000
Database: pdf_scan
Username: pdf_user
Password: pdf_password
```

### Custom Configuration

Pass custom settings to `create_clickhouse_client()`:

```python
client = BackendFactory.create_clickhouse_client(
    host="your-clickhouse-server.com",
    port=8123,
    username="your_user",
    password="your_password",
    database="your_database",
)
```

### Environment Variables (Recommended for Production)

```python
import os
from pdf_scan.db.factory import BackendFactory

client = BackendFactory.create_clickhouse_client(
    host=os.getenv("CLICKHOUSE_HOST", "localhost"),
    port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
    username=os.getenv("CLICKHOUSE_USER", "pdf_user"),
    password=os.getenv("CLICKHOUSE_PASSWORD", "pdf_password"),
    database=os.getenv("CLICKHOUSE_DB", "pdf_scan"),
)
```

## Testing

### Test ClickHouse Connection

```bash
# Run the ClickHouse health check script
./scripts/test_clickhouse.sh
```

### Test Backend Initialization

```bash
# Run the initialization test script
uv run python scripts/init_clickhouse_backends.py
```

### Manual Testing

```python
from pdf_scan.db.factory import BackendFactory
from pdf_scan.models import Document

# Create client and backends
client = BackendFactory.create_clickhouse_client()
backends = BackendFactory.create_backends(backend="clickhouse", client=client)

# Test document storage
doc = Document.create("test.pdf", 1234)
backends.document.store_document(doc)

# Retrieve it
retrieved = backends.document.get_document(doc.id)
print(f"Retrieved: {retrieved.filename}")
```

## Data Types Mapping

| Python Type | ClickHouse Type | Notes |
|------------|-----------------|-------|
| UUID | UUID | Converted to/from string |
| str | String | Direct mapping |
| int | UInt32, Int64 | Based on size |
| float | Float32, Float64 | Based on precision |
| datetime | DateTime | Timezone-aware recommended |
| dict | String | JSON serialized |
| Enum | Enum8 | Maps to enum values |

## Performance Considerations

### Batch Operations

For bulk inserts, consider batching:

```python
# Instead of multiple single inserts
for doc in documents:
    repo.store_document(doc)

# Consider implementing batch insert (future enhancement)
# repo.store_documents_batch(documents)
```

### Connection Pooling

The `clickhouse-connect` client handles connection pooling automatically.

### Partitioning

Tables are partitioned by month (see `docs/schema.md`):
- Efficient for time-based queries
- Enables easy data retention management
- Optimizes storage and query performance

## Troubleshooting

### Connection Failed

```bash
# Check if ClickHouse is running
docker ps | grep clickhouse

# View ClickHouse logs
docker-compose logs clickhouse

# Restart ClickHouse
docker-compose restart clickhouse
```

### Authentication Errors

Verify credentials in `docker-compose.yml` match your client configuration.

### Table Not Found

```bash
# Check if tables exist
docker exec -it pdf-scan-clickhouse clickhouse-client --database pdf_scan --query "SHOW TABLES"

# Recreate tables (if needed)
docker exec -it pdf-scan-clickhouse clickhouse-client --database pdf_scan < init-db.sql
```

### Import Errors

```bash
# Make sure dependencies are installed
uv sync

# Check if clickhouse-connect is installed
uv pip list | grep clickhouse
```

## Migration from In-Memory to ClickHouse

Since in-memory storage doesn't persist, no data migration is needed. Simply:

1. Start ClickHouse: `docker-compose up -d`
2. Update app to use ClickHouse backend
3. Restart application
4. New data will be stored in ClickHouse

## Production Deployment

### Recommendations

1. **Use environment variables** for configuration
2. **Enable TLS/SSL** for ClickHouse connections
3. **Set up replication** using ReplicatedMergeTree
4. **Configure backups** for ClickHouse data
5. **Monitor performance** with metrics endpoint
6. **Set up alerts** for connection failures

### Managed ClickHouse Services

Consider using managed ClickHouse services:
- ClickHouse Cloud
- Altinity.Cloud
- AWS (self-hosted on EC2/ECS)
- Google Cloud Platform
- Azure

## References

- [ClickHouse Documentation](https://clickhouse.com/docs)
- [clickhouse-connect Python Client](https://clickhouse.com/docs/en/integrations/python)
- [Schema Design](./schema.md)
- [API Documentation](./api.md)

