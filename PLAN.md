# PDF Scan Service - Implementation Plan

## Overview
A web service that accepts PDF uploads, scans them for sensitive information, stores findings in Clickhouse, and provides a query endpoint for results.

## Architecture Decisions

### Core Components
1. **Web Server**: FastAPI/Flask for HTTP endpoints
2. **PDF Scanner**: Pluggable interface with regex-based initial implementation
3. **Database**: Pluggable interface with in-memory prototype and Clickhouse production implementation
4. **File Storage**: Local filesystem (temp storage, cleaned after scan)

### Sensitive Data Patterns (v1)
- Social Security Numbers (SSN)
- Email Addresses
- (Extensible pattern list)

### Key Design Decisions
- **Interface-driven design**: Allows swapping implementations without changing business logic
- **Incremental approach**: Each phase produces a working system
- **Schema-first for Clickhouse**: Design real schema early to avoid interface mismatches
- **Synchronous initially**: Can add async processing later if needed

## Implementation Phases

### Phase 1: Data Models & Schema Design
**Status**: 🟢 Completed (2025-10-27)

**Tasks**:
- [x] Define data models for:
  - Upload metadata (document ID, filename, upload time, status)
  - Findings (document ID, finding type, content snippet, location, confidence)
  - Performance metrics (operation type, duration, timestamp)
- [x] Design Clickhouse schema:
  - `documents` table (document metadata)
  - `findings` table (scan results)
  - `metrics` table (performance data)
  - Define primary keys, sorting keys, partitioning strategy
- [x] Document expected API contracts

**Success Criteria**: ✅ Schema documented and reviewed for Clickhouse compatibility

**Deliverables**:
- `src/pdf_scan/models/entities.py`: Database entity definitions using dataclasses
  - `Document`: Upload metadata with status tracking
  - `Finding`: Sensitive data findings with location and confidence
  - `Metric`: Performance metrics with operation tracking
  - `DocumentStatus`: Enum for document processing states
  - `FindingType`: Enum for sensitive data types
- `src/pdf_scan/models/__init__.py`: Public API exports for models module
- `tests/unit/models/test_models.py`: Unit tests for data models (4 tests passing)
- `docs/schema.md`: Clickhouse schema with tables, indexes, and query patterns
- `docs/api.md`: Complete API contracts for all endpoints

**Implementation Notes**:
- Models organized in dedicated `models/` directory for better structure
- Used `StrEnum` for type-safe string enums (DocumentStatus, FindingType)
- Used timezone-aware datetimes with `datetime.now(UTC)` for consistency
- Factory methods (`create()`) provide clean instantiation with auto-generated IDs
- All entities use UUID for primary keys to enable distributed systems

---

### Phase 2: Web Server with Upload Endpoint
**Status**: 🟢 Completed (2025-10-27)

**Tasks**:
- [x] Choose web framework (FastAPI recommended for async + auto docs)
- [x] Implement `/upload` endpoint:
  - Accept multipart/form-data with PDF file
  - Validate file type (PDF only)
  - Validate file size (set reasonable limit, e.g., 10MB)
  - Generate unique document ID
  - Save to temp storage
  - Return document ID and upload status
- [x] Basic error handling:
  - Invalid file type
  - File too large
  - Malformed requests
- [ ] Add metric collection hooks (timing, counters) - Deferred to Phase 8
- [x] Create basic health check endpoint (`/health`)
- [x] Manual testing with curl/Postman

**Success Criteria**: ✅ Can upload valid PDF, get document ID back; invalid uploads rejected with proper errors

**Deliverables**:
- `src/pdf_scan/app.py`: FastAPI application with /upload and /health endpoints
- `src/pdf_scan/main.py`: Server entry point with uvicorn runner
- `src/pdf_scan/__init__.py`: Package exports for public API
- `src/pdf_scan/validation/file_validator.py`: File validation logic
  - `FileValidator`: Static validation methods (extension, content type, size)
  - `ValidationError`: Custom exception for validation failures
- `src/pdf_scan/validation/__init__.py`: Validation module exports
- `src/pdf_scan/processing/document_processor.py`: Document processing logic
  - `DocumentProcessor`: Handles document creation and temporary storage
- `src/pdf_scan/processing/__init__.py`: Processing module exports
- `tests/integration/test_api.py`: API integration tests (8 tests passing)
- `tests/unit/validation/test_file_validator.py`: Validation unit tests (20 tests passing)
- `tests/fixtures/sample_with_pii.pdf`: Static test PDF containing PII
- `tests/fixtures/sample_without_pii.pdf`: Static test PDF without PII
- `tests/fixtures/README.md`: Test fixture documentation
- `scripts/test_health.sh`: Health check testing script
- `scripts/test_upload.sh`: Upload testing script
- `scripts/test_invalid_file.sh`: Validation testing script
- `scripts/README.md`: Testing documentation

**Implementation Notes**:
- Modular architecture with separate `validation` and `processing` modules for better testability
- `FileValidator` is framework-agnostic; FastAPI-specific error handling in `app.py`
- Static test PDFs replace generated ones for consistent, reliable testing
- Tests organized into `unit/` and `integration/` directories mirroring source structure
- Comprehensive validation: file type (PDF only), size (max 10MB), proper error codes
- Metric collection hooks deferred to Phase 8 (will be added when metric storage is implemented)
- Server runs on port 8000 with auto-reload for development
- OpenAPI docs available at /docs and /redoc
- Run server with: `uv run pdf-scan`

---

### Phase 3: Database Interface with In-Memory Implementation
**Status**: 🔴 Not Started

**Tasks**:
- [ ] Define `DatabaseInterface` abstract class with methods:
  - `store_document(doc_id, filename, upload_time, status)` 
  - `store_finding(doc_id, finding_type, content, location, confidence)`
  - `get_findings(doc_id)` - returns list of findings for a document
  - `get_all_findings(limit, offset)` - paginated findings
  - `store_metric(operation, duration, timestamp)`
- [ ] Implement `InMemoryDatabase` class:
  - Use Python dicts/lists for storage
  - Implement all interface methods
  - Data persists only during runtime (acceptable for testing)
- [ ] Unit tests for in-memory implementation

**Success Criteria**: In-memory database passes all unit tests; data can be written and retrieved

---

### Phase 4: PDF Scanner Interface with Regex Implementation
**Status**: 🔴 Not Started

**Tasks**:
- [ ] Define `PDFScannerInterface` abstract class:
  - `scan_pdf(file_path)` - returns list of findings
- [ ] Implement `RegexPDFScanner` class:
  - Extract text from PDF (use PyPDF2 or pdfplumber)
  - Apply regex patterns for sensitive data:
    - SSN: `\d{3}-\d{2}-\d{4}` or `\d{9}`
    - Credit Card: `\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}`
    - Email: standard email regex
    - Phone: various US phone formats
  - Return findings with:
    - Type (SSN, CC, email, etc.)
    - Content snippet (redacted or masked)
    - Location (page number, approx position if available)
    - Confidence (1.0 for regex matches)
- [ ] Handle errors:
  - Corrupt PDFs
  - Password-protected PDFs
  - Empty PDFs
- [ ] Unit tests with sample PDFs

**Success Criteria**: Scanner correctly identifies test patterns in sample PDFs; handles errors gracefully

**Known Limitations**:
- Cannot detect sensitive data in images/scanned documents (no OCR)
- Regex may have false positives (e.g., random number sequences)
- Pattern list is not exhaustive

---

### Phase 5: Integration & End-to-End Testing
**Status**: 🔴 Not Started

**Tasks**:
- [ ] Wire components together:
  - Upload endpoint saves file and stores document in DB
  - Trigger PDF scan after upload
  - Store findings in DB
  - Store performance metrics
- [ ] Implement upload flow:
  ```
  1. Receive PDF upload
  2. Validate and save to temp storage
  3. Store document record (status: processing)
  4. Scan PDF for sensitive data
  5. Store findings in DB
  6. Update document status (status: completed/failed)
  7. Clean up temp file
  8. Return response
  ```
- [ ] Error handling for each step
- [ ] End-to-end tests:
  - Upload PDF with known sensitive data
  - Verify findings stored correctly
  - Verify metrics captured
- [ ] Performance testing (baseline with in-memory DB)

**Success Criteria**: Complete upload-to-storage flow works; findings are correctly stored and retrievable

---

### Phase 6: Findings Endpoint
**Status**: 🔴 Not Started

**Tasks**:
- [ ] Implement `/findings/<document_id>` endpoint:
  - GET request returns findings for specific document
  - Return JSON with findings list
  - Handle non-existent document IDs (404)
- [ ] Implement `/findings` endpoint (optional):
  - GET request with pagination (limit, offset)
  - Returns findings across all documents
  - Useful for admin/monitoring
- [ ] Response format:
  ```json
  {
    "document_id": "...",
    "filename": "...",
    "upload_time": "...",
    "status": "completed",
    "findings": [
      {
        "type": "SSN",
        "location": "page 2",
        "confidence": 1.0
      }
    ]
  }
  ```
- [ ] Integration tests for findings endpoint

**Success Criteria**: Can query findings via HTTP; response format is correct and complete

---

### Phase 7: Clickhouse Implementation
**Status**: 🔴 Not Started

**Tasks**:
- [ ] Set up Clickhouse:
  - Docker container for development
  - Connection configuration
- [ ] Implement `ClickhouseDatabase` class:
  - Implement all `DatabaseInterface` methods
  - Create tables if not exist
  - Use parameterized queries to prevent injection
  - Connection pooling
- [ ] Data migration (if needed):
  - Not applicable for fresh start
  - Document any migration needs for future
- [ ] Configuration:
  - Environment variables for connection string
  - Fallback to in-memory if Clickhouse unavailable (dev mode)
- [ ] Integration tests with real Clickhouse instance
- [ ] Performance comparison with in-memory implementation

**Success Criteria**: Application works with Clickhouse; data persists across restarts; performance acceptable

**Clickhouse-Specific Considerations**:
- Choose appropriate engine (e.g., MergeTree)
- Define ORDER BY for query optimization
- Consider partitioning by date for metrics table
- Set up retention policies if needed

---

### Phase 8: Performance Metrics Enhancement
**Status**: 🔴 Not Started

**Tasks**:
- [ ] Enhance metric collection (hooks should exist from Phase 2):
  - Upload endpoint: request duration, file size
  - PDF scan: scan duration, number of findings
  - Database operations: query duration
  - Overall request processing time
- [ ] Implement `/metrics` endpoint:
  - Return recent metrics in JSON
  - Optionally support Prometheus format
- [ ] Add metric dashboarding (optional):
  - Grafana + Clickhouse
  - Basic SQL queries for common metrics
- [ ] Performance analysis:
  - Identify bottlenecks
  - Optimize slow operations
  - Document performance characteristics

**Success Criteria**: Metrics are collected and queryable; performance bottlenecks identified

---

## Future Enhancements (Out of Scope for v1)

- [ ] Async processing with job queue (Celery, RQ)
- [ ] OCR for scanned PDFs
- [ ] ML-based sensitive data detection
- [ ] User authentication & authorization
- [ ] Support for other file formats (DOCX, images)
- [ ] Webhook notifications when scan completes
- [ ] Findings export (CSV, PDF reports)
- [ ] Batch upload support
- [ ] Rate limiting
- [ ] API versioning

---

## Development Guidelines

### Technology Stack
- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **PDF Processing**: pdfplumber or PyPDF2
- **Database**: Clickhouse (production), in-memory (dev/test)
- **Testing**: pytest
- **Dependency Management**: uv (already initialized)

### Code Quality
- Type hints for all functions
- Docstrings for public APIs
- Unit tests for each component
- Integration tests for endpoints
- Linting with ruff or flake8
- Formatting with black

### Git Workflow
- Commit at the end of each phase
- Descriptive commit messages
- Feature branches if working with team

---

## Progress Tracking

**Last Updated**: 2025-10-27

| Phase | Status | Completion Date |
|-------|--------|-----------------|
| 0. Repository Initialization | 🟢 Completed | 2025-10-27 |
| 1. Data Models & Schema | 🟢 Completed | 2025-10-27 |
| 2. Web Server & Upload | 🟢 Completed | 2025-10-27 |
| 3. Database Interface (In-Memory) | 🔴 Not Started | - |
| 4. PDF Scanner Interface (Regex) | 🔴 Not Started | - |
| 5. Integration & E2E Testing | 🔴 Not Started | - |
| 6. Findings Endpoint | 🔴 Not Started | - |
| 7. Clickhouse Implementation | 🔴 Not Started | - |
| 8. Performance Metrics | 🔴 Not Started | - |

**Legend**:
- 🔴 Not Started
- 🟡 In Progress
- 🟢 Completed
- ⚠️ Blocked

---

## Questions & Decisions Log

### Open Questions
1. Authentication required? (Assuming no for v1)
2. Max file size limit? (Proposal: 10MB)
3. PDF retention policy? (Proposal: delete after scan)
4. Clickhouse deployment? (Proposal: Docker for dev, managed service for prod)
5. Async processing needed? (Proposal: start synchronous, add if performance issues)

### Decisions Made
- (None yet)


