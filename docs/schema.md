# Database Schema Design

## Overview

This document defines the database schema for the PDF scan service, optimized for Clickhouse.

## Clickhouse Schema

### Table: documents

Stores metadata about uploaded documents.

```sql
CREATE TABLE documents (
    id UUID,
    filename String,
    upload_time DateTime,
    status Enum8('pending' = 1, 'processing' = 2, 'completed' = 3, 'failed' = 4),
    file_size UInt32,
    error_message Nullable(String)
) ENGINE = MergeTree()
ORDER BY (upload_time, id)
PARTITION BY toYYYYMM(upload_time)
SETTINGS index_granularity = 8192;
```

**Design Notes**:
- Primary key is `(upload_time, id)` for time-based queries
- Partitioned by month for efficient data management and cleanup
- `status` stored as Enum8 for efficiency
- `error_message` is nullable (only set on failure)

**Indexes**:
- Consider adding: `INDEX idx_status status TYPE set(0) GRANULARITY 1`

---

### Table: findings

Stores detected sensitive data findings.

```sql
CREATE TABLE findings (
    id UUID,
    document_id UUID,
    finding_type Enum8('ssn' = 1, 'email' = 2),
    location String,
    confidence Float32,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (document_id, finding_type, id)
PARTITION BY toYYYYMM(created_at)
SETTINGS index_granularity = 8192;
```

**Design Notes**:
- Primary key is `(document_id, finding_type, id)` optimized for queries by document
- Partitioned by month
- `finding_type` stored as Enum8, extensible by adding values
- No sensitive content stored, only metadata
- `confidence` as Float32 (sufficient precision for 0.0-1.0 range)

**Indexes**:
- Consider adding: `INDEX idx_type finding_type TYPE set(0) GRANULARITY 1`

---

### Table: metrics

Stores performance metrics for monitoring and analysis.

```sql
CREATE TABLE metrics (
    id UUID,
    operation LowCardinality(String),
    duration_ms Float64,
    timestamp DateTime,
    document_id Nullable(UUID),
    metadata String  -- JSON string for flexible metadata
) ENGINE = MergeTree()
ORDER BY (operation, timestamp)
PARTITION BY toYYYYMM(timestamp)
TTL timestamp + INTERVAL 90 DAY
SETTINGS index_granularity = 8192;
```

**Design Notes**:
- Primary key is `(operation, timestamp)` for time-series analysis
- `operation` uses LowCardinality for efficiency (limited set of values)
- Partitioned by month
- TTL set to 90 days for automatic cleanup (metrics are ephemeral)
- `metadata` stored as JSON string for flexibility
- `document_id` is nullable (some metrics may not be document-specific)

**Indexes**:
- Time-based queries are naturally optimized by ORDER BY

---

## Query Patterns

### Get document by ID
```sql
SELECT * FROM documents WHERE id = {document_id};
```

### Get findings for a document
```sql
SELECT * FROM findings WHERE document_id = {document_id} ORDER BY finding_type;
```

### Get all findings with pagination
```sql
SELECT 
    f.*,
    d.filename,
    d.upload_time,
    d.status
FROM findings f
JOIN documents d ON f.document_id = d.id
ORDER BY f.created_at DESC
LIMIT {limit} OFFSET {offset};
```

### Get metrics for an operation
```sql
SELECT 
    operation,
    avg(duration_ms) as avg_duration,
    max(duration_ms) as max_duration,
    min(duration_ms) as min_duration,
    count() as count
FROM metrics
WHERE operation = {operation}
  AND timestamp >= now() - INTERVAL 1 DAY
GROUP BY operation;
```

### Get documents by status
```sql
SELECT * FROM documents 
WHERE status = {status} 
ORDER BY upload_time DESC 
LIMIT {limit};
```

---

## Migration Strategy

Since this is a new project:
1. Tables will be created on first run if they don't exist
2. No migrations needed initially
3. Future schema changes will be documented here

---

## Data Retention

- **documents**: Keep indefinitely (or implement policy later)
- **findings**: Keep indefinitely (or implement policy later)
- **metrics**: Automatic cleanup after 90 days via TTL

---

## Scaling Considerations

- **Sharding**: Not needed initially; single node sufficient
- **Replication**: Consider ReplicatedMergeTree for production
- **Partitioning**: Monthly partitions allow efficient old data dropping
- **Compression**: Clickhouse default ZSTD compression is adequate

---

## Index Strategy

Clickhouse uses sparse indexes. The ORDER BY clause defines the primary index.
Additional secondary indexes are noted above but should be added only if query
performance requires them (premature optimization avoided).

