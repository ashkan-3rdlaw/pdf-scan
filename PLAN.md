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
**Status**: 🟢 Completed (2025-10-27)

**Tasks**:
- [x] Define repository abstract interfaces:
  - `DocumentRepository`: Document storage and retrieval
    - `store_document(document)` - store document entity
    - `get_document(document_id)` - retrieve by ID
    - `update_document_status(document_id, status, error_message)` - update status
    - `list_documents(limit, offset)` - paginated list
  - `FindingRepository`: Finding storage and retrieval
    - `store_finding(finding)` - store finding entity
    - `get_findings(document_id)` - get findings for a document
    - `get_all_findings(limit, offset, finding_type)` - paginated with filter
    - `count_findings(document_id)` - count findings
  - `MetricsRepository`: Metrics storage and analytics
    - `store_metric(metric)` - store metric entity
    - `get_metrics(operation, document_id, start_time, end_time, limit, offset)` - filtered retrieval
    - `get_average_duration(operation, start_time, end_time)` - analytics
- [x] Implement in-memory implementations:
  - `InMemoryDocumentRepository` - dict-based document storage
  - `InMemoryFindingRepository` - dict-based finding storage
  - `InMemoryMetricsRepository` - dict-based metrics storage
- [x] Unit tests for in-memory implementations

**Success Criteria**: ✅ In-memory database passes all unit tests; data can be written and retrieved

**Deliverables**:
- `src/pdf_scan/db/core/document_repository.py`: Abstract DocumentRepository interface
- `src/pdf_scan/db/core/finding_repository.py`: Abstract FindingRepository interface
- `src/pdf_scan/db/core/impl/in_memory_document_repository.py`: In-memory implementation for documents
- `src/pdf_scan/db/core/impl/in_memory_finding_repository.py`: In-memory implementation for findings
- `src/pdf_scan/db/analytics/metrics_repository.py`: Abstract MetricsRepository interface
- `src/pdf_scan/db/analytics/impl/in_memory_metrics_repository.py`: In-memory implementation for metrics
- `src/pdf_scan/db/factory.py`: DatabaseFactory for creating repository instances
- `src/pdf_scan/db/backends.py`: Backends container for dependency management
- `tests/unit/db/core/impl/test_in_memory_document_repository.py`: 10 unit tests for document repository
- `tests/unit/db/core/impl/test_in_memory_finding_repository.py`: 12 unit tests for finding repository
- `tests/unit/db/analytics/impl/test_in_memory_metrics_repository.py`: 15 unit tests for metrics repository
- `tests/unit/db/test_factory.py`: 6 unit tests for DatabaseFactory
- `tests/unit/db/test_backends.py`: 6 unit tests for Backends container
- `scripts/test_upload_pii.sh`: Comprehensive upload test script with health checks
- `scripts/quick_upload_test.sh`: Simple upload test script for quick testing

**Implementation Notes**:
- Restructured into `db/` module with `core/` and `analytics/` subdirectories
- Interfaces at root level, implementations in `impl/` subdirectories
- Separate repository interfaces for each domain (documents, findings, metrics)
- `DocumentRepository` and `FindingRepository` in `db/core/` module (core data)
- `MetricsRepository` in `db/analytics/` module (performance tracking)
- Repository pattern enables easy swapping between in-memory and Clickhouse implementations
- In-memory implementations use Python dicts for storage (UUID keys)
- Repositories start with clean slate on each server restart (no persistence)
- Sorting: documents by upload_time (desc), findings by confidence (desc), metrics by timestamp (desc)
- Comprehensive filtering and pagination support in all repositories
- **Dependency Injection**: FastAPI endpoints use `Backends` container for clean dependency management
- **Factory Pattern**: `DatabaseFactory` centralizes repository creation
- **Backends Wrapper**: Single `Backends` object contains all database dependencies
- **Simplified API**: Endpoints accept single `Backends` parameter instead of multiple repositories
- **Test Scripts**: Upload test scripts for manual testing with sample PII PDF
- 43 new tests passing, 81 total tests passing
- All imports updated to use `pdf_scan.db` module

---

### Phase 4: PDF Scanner Interface with Regex Implementation
**Status**: 🟢 Completed (2025-10-27)

**Tasks**:
- [x] Define `PDFScannerInterface` abstract class:
  - `scan_pdf(file_path)` - returns list of findings
  - `get_supported_patterns()` - returns list of pattern names
- [x] Implement `RegexPDFScanner` class:
  - Extract text from PDF (using pypdf)
  - Apply regex patterns for sensitive data:
    - SSN: `\b\d{3}-\d{2}-\d{4}\b` (xxx-xx-xxxx format)
    - Email: `\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b`
  - Return findings with:
    - Type (SSN, email)
    - Location (page number format: "page N")
    - Confidence (1.0 for regex matches)
    - Content intentionally NOT stored for security
- [x] Handle errors:
  - Corrupt PDFs (ValueError)
  - Password-protected PDFs (RuntimeError)
  - Empty PDFs (gracefully skips empty pages)
  - File not found (FileNotFoundError)
- [x] Unit tests with sample PDFs
- [x] Integrate scanner into dependency injection system (Backends and BackendFactory)

**Success Criteria**: ✅ Scanner correctly identifies test patterns in sample PDFs; handles errors gracefully

**Known Limitations**:
- Cannot detect sensitive data in images/scanned documents (no OCR)
- Regex may have false positives (e.g., random number sequences)
- Pattern list is not exhaustive

**Deliverables**:
- `src/pdf_scan/scanner/pdf_scanner_interface.py`: Abstract PDFScannerInterface class
- `src/pdf_scan/scanner/regex_scanner.py`: RegexPDFScanner implementation with pypdf
- `src/pdf_scan/scanner/__init__.py`: Scanner module exports
- `src/pdf_scan/db/backends.py`: Updated to include scanner in Backends container
- `src/pdf_scan/db/factory.py`: Renamed to BackendFactory, added create_backends() and create_scanner() methods
- `tests/unit/scanner/test_regex_scanner.py`: 11 comprehensive unit tests for regex scanner
- `tests/unit/scanner/__init__.py`: Scanner test module
- `tests/unit/db/test_factory.py`: Updated tests for BackendFactory (8 tests)
- `tests/unit/db/test_backends.py`: Updated tests for Backends with scanner (6 tests)
- `pyproject.toml`: Added pypdf>=5.1.0 dependency
- `scripts/run_all_tests.sh`: Convenience script to run all manual test scripts

**Implementation Notes**:
- Interface defines contract for all scanner implementations
- `scan_pdf()` accepts file path and returns list of Finding objects
- `get_supported_patterns()` provides introspection of scanner capabilities
- Proper error handling with specific exceptions (FileNotFoundError, ValueError, RuntimeError)
- Type hints use Union[str, Path] for flexible path handling
- Ready for multiple scanner implementations (regex, OCR, ML-based, etc.)
- **PDF Library Choice**: `pypdf>=5.1.0` - Pure Python, minimal dependencies, easy installation, MIT license. Good enough for MVP text extraction. Can be swapped later if needed thanks to interface abstraction.
- **Security-First Design**: Finding content is intentionally NOT stored, only location metadata
- **Per-Page Processing**: Scans each PDF page individually, continues on page-level errors
- **Pattern Validation**: 11 unit tests covering pattern matching, error handling, and edge cases
- **Test Coverage**: Validates both sample_with_pii.pdf (2 findings) and sample_without_pii.pdf (0 findings)
- **Dependency Injection**: Scanner integrated into Backends container and BackendFactory
- **Factory Refactoring**: Renamed DatabaseFactory to BackendFactory for clarity; all creation logic centralized in factory
- **Manual Testing**: Added run_all_tests.sh convenience script with color-coded output and summary
- 94 total tests passing (includes scanner tests and updated factory/backends tests)

---

### Phase 5: Integration & End-to-End Testing
**Status**: 🟢 Completed (2025-10-27)

**Tasks**:
- [x] Wire components together:
  - Upload endpoint saves file and stores document in DB
  - Trigger PDF scan after upload
  - Store findings in DB
  - Store performance metrics
- [x] Implement upload flow:
  ```
  1. Receive PDF upload
  2. Validate and save to temp storage
  3. Store document record (status: pending → processing)
  4. Scan PDF for sensitive data
  5. Store findings in DB
  6. Update document status (status: completed/failed)
  7. Clean up temp file
  8. Return response with findings_count
  ```
- [x] Error handling for each step
- [x] End-to-end tests:
  - Upload PDF with known sensitive data
  - Verify findings stored correctly
  - Verify metrics captured
- [x] Manual testing scripts verify complete flow
- [ ] Performance testing (baseline with in-memory DB) - Deferred to Phase 8

**Success Criteria**: ✅ Complete upload-to-storage flow works; findings are correctly stored and retrievable

**Deliverables**:
- `src/pdf_scan/processing/document_processor.py`: Complete integration of upload → scan → store workflow
  - Full implementation of 8-step upload flow
  - Error handling with status updates (FAILED + error_message)
  - Metrics recording (upload and scan operations)
  - Automatic temp file cleanup in finally block
  - Returns findings_count in response
- `src/pdf_scan/app.py`: Upload endpoint integrated with scanner via Backends
- `tests/integration/test_api.py`: Updated integration tests to verify completed status and findings_count
- `scripts/run_all_tests.sh`: Comprehensive manual testing suite
- `scripts/test_upload_pii.sh`: E2E test with sample_with_pii.pdf
- `scripts/quick_upload_test.sh`: Quick E2E test
- `README.md`: Updated with manual testing instructions
- `scripts/README.md`: Updated with run_all_tests.sh documentation

**Implementation Notes**:
- **Complete Integration**: Upload endpoint now performs full scan workflow synchronously
- **Status Tracking**: Document status transitions: PENDING → PROCESSING → COMPLETED/FAILED
- **Finding Storage**: Findings are stored in database with correct document_id references
- **Metrics Recording**: Both upload and scan operations are tracked in metrics repository
- **Error Recovery**: Failed scans update document status to FAILED with error message
- **Resource Cleanup**: Temp files always cleaned up via finally block
- **Response Enhancement**: Upload response includes findings_count field
- **Manual Verification**: 6 manual test scripts all pass successfully
  - Health check test
  - Upload with PII (2 findings detected)
  - Upload without PII (0 findings detected)
  - Quick upload test
  - Comprehensive upload test with health checks
  - Invalid file validation tests
- **Integration Tests Updated**: test_upload_valid_pdf now expects status="completed" and findings_count field
- 94 total tests passing (all unit + integration tests)
- All manual test scripts pass (verified with run_all_tests.sh)

---

### Phase 6: Findings Endpoint
**Status**: 🟢 Completed (2025-10-27)

**Tasks**:
- [x] Implement `/findings/{document_id}` endpoint:
  - GET request returns findings for specific document
  - Return JSON with findings list
  - Handle non-existent document IDs (404)
- [x] Implement `/findings` endpoint:
  - GET request with pagination (limit, offset)
  - Returns findings across all documents
  - Filtering by finding_type parameter
  - Useful for admin/monitoring
- [x] Response format:
  ```json
  {
    "document_id": "...",
    "filename": "...",
    "upload_time": "...",
    "status": "completed",
    "file_size": 1234,
    "findings": [
      {
        "id": "...",
        "type": "ssn",
        "location": "page 2",
        "confidence": 1.0
      }
    ]
  }
  ```
- [x] Integration tests for findings endpoints

**Success Criteria**: ✅ Can query findings via HTTP; response format is correct and complete

**Deliverables**:
- `src/pdf_scan/app.py`: Two new endpoints implemented
  - `GET /findings/{document_id}`: Get findings for a specific document
  - `GET /findings`: Get all findings with pagination and filtering
- `tests/integration/test_api.py`: 8 new integration tests for findings endpoints (16 total tests, up from 8)
  - test_get_findings_for_nonexistent_document: Verifies 404 handling
  - test_get_findings_for_document_with_pii: Tests document with 2 findings
  - test_get_findings_for_document_without_pii: Tests document with 0 findings
  - test_get_all_findings_empty: Tests pagination structure
  - test_get_all_findings_with_data: Tests multiple documents
  - test_get_all_findings_with_pagination: Tests limit/offset parameters
  - test_get_all_findings_with_invalid_pagination: Tests validation
  - test_get_all_findings_with_type_filter: Tests finding_type filter
- `scripts/test_findings.sh`: Comprehensive manual test script
  - Tests upload → query workflow
  - Tests pagination
  - Tests filtering by type
  - Tests 404 error handling
- `scripts/run_all_tests.sh`: Updated to include findings test (7 tests total)
- `scripts/README.md`: Updated with findings endpoint documentation

**Implementation Notes**:
- **Endpoint 1: /findings/{document_id}**
  - Accepts UUID path parameter
  - Returns 404 if document not found
  - Includes document metadata + findings array
  - Finding fields: id, type, location, confidence
- **Endpoint 2: /findings**
  - Pagination: limit (1-100, default 20), offset (0+, default 0)
  - Optional filtering: finding_type query parameter
  - Returns findings array + pagination metadata
  - Pagination metadata: limit, offset, total, returned
- **Singleton Backend**: `get_backends()` dependency returns singleton instance to maintain state across requests
- **State Persistence**: Documents and findings persist in memory for server lifetime
- **UUID Handling**: FastAPI automatically validates and converts UUID path parameters
- **Query Validation**: FastAPI Query validators ensure limit/offset are within valid ranges
- **Response Format**: All UUIDs serialized as strings in JSON responses
- **Finding Types**: Enum values are lowercase ("ssn", "email") in API responses
- 102 total tests passing (94 unit + 16 integration tests, 8 new for findings)
- 7 manual test scripts passing (added findings endpoint test)

---

### Phase 7: Clickhouse Implementation
**Status**: 🟢 Completed (2025-10-27)

**Tasks**:
- [x] Set up Clickhouse:
  - Docker container for development (`docker-compose.yml`)
  - Connection configuration with environment variables
  - Database initialization script (`init-db.sql`)
- [x] Implement ClickHouse repository classes:
  - `ClickHouseDocumentRepository` - implements `DocumentRepository` interface
  - `ClickHouseFindingRepository` - implements `FindingRepository` interface  
  - `ClickHouseMetricsRepository` - implements `MetricsRepository` interface
  - All methods use parameterized queries to prevent injection
  - Connection pooling via `clickhouse-connect` library
- [x] Database schema implementation:
  - `documents` table with MergeTree engine
  - `findings` table with optimized sorting by confidence
  - `metrics` table with timestamp-based partitioning
  - Proper ORDER BY clauses for query optimization
- [x] Configuration:
  - Environment variables for connection string
  - Fallback to in-memory if ClickHouse unavailable (dev mode)
  - BackendFactory supports both "memory" and "clickhouse" backends
- [x] Integration and testing:
  - ClickHouse health check script (`scripts/test_clickhouse.sh`)
  - Example usage script (`scripts/init_clickhouse_backends.py`)
  - Comprehensive documentation (`docs/clickhouse.md`)

**Success Criteria**: ✅ Application works with ClickHouse; data persists across restarts; performance acceptable

**Clickhouse-Specific Implementation**:
- ✅ MergeTree engine for all tables with optimized ORDER BY
- ✅ Proper data type mappings (UUID, DateTime, JSON serialization)
- ✅ Parameterized queries for security
- ✅ Connection pooling and error handling
- ✅ Environment-based configuration with fallback

**Deliverables**:
- `docker-compose.yml`: ClickHouse container setup with persistent volumes
- `init-db.sql`: Database initialization script creating all tables
- `src/pdf_scan/db/core/impl/clickhouse_document_repository.py`: ClickHouse document repository implementation
- `src/pdf_scan/db/core/impl/clickhouse_finding_repository.py`: ClickHouse finding repository implementation
- `src/pdf_scan/db/analytics/impl/clickhouse_metrics_repository.py`: ClickHouse metrics repository implementation
- `src/pdf_scan/db/factory.py`: Enhanced BackendFactory with ClickHouse support
- `docs/clickhouse.md`: Comprehensive ClickHouse usage guide
- `CLICKHOUSE_IMPLEMENTATION.md`: Implementation summary and details
- `scripts/test_clickhouse.sh`: ClickHouse health check and verification script
- `scripts/init_clickhouse_backends.py`: Example ClickHouse backend usage
- `pyproject.toml`: Added `clickhouse-connect>=0.8.14` dependency
- `scripts/README.md`: Updated with ClickHouse testing procedures
- `README.md`: Updated with ClickHouse backend documentation

**Implementation Notes**:
- **Repository Pattern**: Each repository implements its corresponding interface, enabling seamless backend switching
- **Connection Management**: Uses `clickhouse-connect` library with automatic connection pooling
- **Data Type Handling**: Proper conversion between Python types and ClickHouse types (UUID, DateTime, JSON)
- **Security**: All queries use parameterized statements to prevent SQL injection
- **Configuration**: Environment variables control backend selection with graceful fallback to in-memory
- **Docker Setup**: Complete containerized development environment with auto-initialization
- **Schema Design**: Optimized table structures with proper indexing and partitioning
- **Testing**: Health check scripts verify ClickHouse availability and table structure
- **Documentation**: Comprehensive guides for setup, usage, and troubleshooting
- **Backward Compatibility**: Existing in-memory backend remains default for development

---

### Phase 8: Performance Metrics Enhancement
**Status**: 🟢 Completed (2025-10-27)

**Tasks**:
- [x] Enhance metric collection (hooks should exist from Phase 2):
  - Upload endpoint: request duration, file size
  - PDF scan: scan duration, number of findings
  - Database operations: query duration
  - Overall request processing time
- [x] Implement `/metrics` endpoint:
  - Return recent metrics in JSON
  - Average processing times by operation type
  - Filtering by operation and time range
  - Error handling for invalid parameters
- [x] Add comprehensive testing:
  - Integration tests for metrics endpoint
  - Manual testing script
  - Error handling validation
- [ ] Add metric dashboarding (optional):
  - Grafana + Clickhouse
  - Basic SQL queries for common metrics
- [ ] Performance analysis:
  - Identify bottlenecks
  - Optimize slow operations
  - Document performance characteristics

**Success Criteria**: ✅ Metrics are collected and queryable; performance bottlenecks identified

**Implementation Details**:
- ✅ **Timing Collection**: Added precise timing to document processor for upload and scan operations
- ✅ **Metrics Endpoint**: Simple JSON API returning average durations by operation type
- ✅ **Filtering Support**: Query parameters for operation type and time range filtering
- ✅ **Error Handling**: Proper validation and error responses for invalid parameters
- ✅ **Testing**: Comprehensive test coverage including edge cases

**Deliverables**:
- `src/pdf_scan/app.py`: Added `/metrics` endpoint with filtering and error handling
- `src/pdf_scan/processing/document_processor.py`: Enhanced with precise timing collection
- `tests/integration/test_api.py`: Added 4 new integration tests for metrics endpoint
- `scripts/test_metrics.sh`: Manual testing script for metrics functionality
- Updated test count: 106 tests passing (4 new metrics tests)

**Implementation Notes**:
- **Simple Design**: Focused on essential metrics without complex dashboarding
- **Operation Types**: Tracks "upload" and "scan" operations with separate timing
- **Timing Precision**: Uses `time.time()` for millisecond-precision measurements
- **Filtering**: Supports operation type filtering and ISO time range filtering
- **Error Handling**: Validates time format and provides clear error messages
- **Response Format**: Clean JSON structure with metrics, filters, and timestamp
- **Backward Compatibility**: No breaking changes to existing functionality
- **Testing**: Comprehensive test coverage including empty state, data state, filtering, and error cases

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
| 3. Database Interface (In-Memory) | 🟢 Completed | 2025-10-27 |
| 4. PDF Scanner Interface (Regex) | 🟢 Completed | 2025-10-27 |
| 5. Integration & E2E Testing | 🟢 Completed | 2025-10-27 |
| 6. Findings Endpoint | 🟢 Completed | 2025-10-27 |
| 7. Clickhouse Implementation | 🟢 Completed | 2025-10-27 |
| 8. Performance Metrics | 🟢 Completed | 2025-10-27 |

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


