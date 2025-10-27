-- Initialize PDF Scan Service Database
-- This script runs automatically when the ClickHouse container starts for the first time

-- Create database
CREATE DATABASE IF NOT EXISTS pdf_scan;

USE pdf_scan;

-- Documents table
-- Stores metadata about uploaded documents
CREATE TABLE IF NOT EXISTS documents (
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

-- Findings table
-- Stores detected sensitive data findings
CREATE TABLE IF NOT EXISTS findings (
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

-- Metrics table
-- Stores performance metrics for monitoring and analysis
CREATE TABLE IF NOT EXISTS metrics (
    id UUID,
    operation LowCardinality(String),
    duration_ms Float64,
    timestamp DateTime,
    document_id Nullable(UUID),
    metadata String
) ENGINE = MergeTree()
ORDER BY (operation, timestamp)
PARTITION BY toYYYYMM(timestamp)
TTL timestamp + INTERVAL 90 DAY
SETTINGS index_granularity = 8192;

