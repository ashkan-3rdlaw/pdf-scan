# API Contracts

## Overview

This document defines the API contracts for the PDF scan service.

---

## Upload Endpoint

### POST /upload

Uploads a PDF file for scanning.

**Request**:
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: 
  - `file`: PDF file (required)

**Response** (Success - 200 OK):
```json
{
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "document.pdf",
  "status": "pending",
  "upload_time": "2025-10-27T10:00:00Z",
  "file_size": 1048576
}
```

**Response** (Error - 400 Bad Request):
```json
{
  "error": "Invalid file type. Only PDF files are allowed.",
  "code": "INVALID_FILE_TYPE"
}
```

**Response** (Error - 413 Payload Too Large):
```json
{
  "error": "File size exceeds maximum allowed size of 10MB.",
  "code": "FILE_TOO_LARGE"
}
```

**Possible Error Codes**:
- `INVALID_FILE_TYPE`: File is not a PDF
- `FILE_TOO_LARGE`: File exceeds size limit
- `MISSING_FILE`: No file provided in request
- `MALFORMED_REQUEST`: Request format is invalid

---

## Findings Endpoint

### GET /findings/{document_id}

Retrieves findings for a specific document.

**Request**:
- Method: `GET`
- Path Parameters:
  - `document_id`: UUID of the document

**Response** (Success - 200 OK):
```json
{
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "document.pdf",
  "upload_time": "2025-10-27T10:00:00Z",
  "status": "completed",
  "findings": [
    {
      "id": "223e4567-e89b-12d3-a456-426614174001",
      "finding_type": "ssn",
      "location": "page 2",
      "confidence": 1.0
    },
    {
      "id": "323e4567-e89b-12d3-a456-426614174002",
      "finding_type": "email",
      "location": "page 1",
      "confidence": 1.0
    }
  ]
}
```

**Response** (Processing - 200 OK):
```json
{
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "document.pdf",
  "upload_time": "2025-10-27T10:00:00Z",
  "status": "processing",
  "findings": []
}
```

**Response** (Failed - 200 OK):
```json
{
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "document.pdf",
  "upload_time": "2025-10-27T10:00:00Z",
  "status": "failed",
  "error_message": "Failed to parse PDF: file is corrupted",
  "findings": []
}
```

**Response** (Not Found - 404):
```json
{
  "error": "Document not found",
  "code": "DOCUMENT_NOT_FOUND"
}
```

---

### GET /findings

Retrieves all findings with pagination (optional, for admin/monitoring).

**Request**:
- Method: `GET`
- Query Parameters:
  - `limit`: Number of results (default: 50, max: 100)
  - `offset`: Offset for pagination (default: 0)

**Response** (Success - 200 OK):
```json
{
  "findings": [
    {
      "id": "223e4567-e89b-12d3-a456-426614174001",
      "document_id": "123e4567-e89b-12d3-a456-426614174000",
      "filename": "document.pdf",
      "finding_type": "ssn",
      "location": "page 2",
      "confidence": 1.0,
      "created_at": "2025-10-27T10:00:05Z"
    }
  ],
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 150
  }
}
```

---

## Health Check Endpoint

### GET /health

Health check endpoint for monitoring.

**Request**:
- Method: `GET`

**Response** (Success - 200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-10-27T10:00:00Z",
  "version": "0.1.0"
}
```

---

## Metrics Endpoint (Phase 8)

### GET /metrics

Returns performance metrics.

**Request**:
- Method: `GET`
- Query Parameters (optional):
  - `operation`: Filter by operation type
  - `since`: ISO timestamp for time range

**Response** (Success - 200 OK):
```json
{
  "metrics": [
    {
      "operation": "upload",
      "avg_duration_ms": 150.5,
      "max_duration_ms": 500.0,
      "min_duration_ms": 50.0,
      "count": 1000
    },
    {
      "operation": "scan",
      "avg_duration_ms": 2500.0,
      "max_duration_ms": 5000.0,
      "min_duration_ms": 1000.0,
      "count": 1000
    }
  ]
}
```

---

## Data Models

### Document Status Values
- `pending`: Document uploaded, waiting to be processed
- `processing`: Document is currently being scanned
- `completed`: Document scan completed successfully
- `failed`: Document scan failed

### Finding Types
- `ssn`: Social Security Number
- `email`: Email address
- (Extensible - more types can be added)

---

## Common Error Response Format

All error responses follow this format:

```json
{
  "error": "Human-readable error message",
  "code": "MACHINE_READABLE_ERROR_CODE",
  "details": {}  // Optional additional context
}
```

---

## Notes

1. All timestamps are in UTC and ISO 8601 format
2. All IDs are UUIDs (RFC 4122)
3. File size is in bytes
4. Confidence is a float between 0.0 and 1.0
5. Sensitive data content is never returned in API responses (security by design)

