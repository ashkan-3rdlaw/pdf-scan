# Test Scripts

Manual testing scripts for the PDF scan service using curl.

## Prerequisites

- Server must be running on `http://localhost:8000`
- `jq` installed for JSON formatting (optional, but recommended)
- `curl` for making HTTP requests
- ClickHouse instance running (optional, for Phase 7+): `docker-compose up -d`

## Starting the Server

```bash
uv run pdf-scan
```

The server will start on `http://localhost:8000` with auto-reload enabled.

## Quick Start

Run all test scripts at once:

```bash
./scripts/run_all_tests.sh
```

This will automatically:
1. Check if the server is running
2. Run all test scripts in sequence
3. Display a summary of passed/failed tests

**Note:** Requires `jq` to be installed (`brew install jq` on macOS).

## Individual Scripts

### 0. ClickHouse Health Check

Test the ClickHouse database connectivity:

```bash
./scripts/test_clickhouse.sh
```

This comprehensive test script checks:
1. HTTP interface availability (port 8123)
2. Query execution capability
3. Database existence (pdf_scan)
4. Table initialization (documents, findings, metrics)
5. Authenticated connection

**Prerequisites:** ClickHouse must be running (`docker-compose up -d`)

**Expected output:**
```
✓ HTTP interface is up (port 8123)
✓ Query execution works
  ClickHouse version: 24.x.x.x
✓ Database 'pdf_scan' exists
  ✓ Table 'documents' exists
  ✓ Table 'findings' exists
  ✓ Table 'metrics' exists
✓ Authentication successful (user: pdf_user)
✓ ClickHouse instance is fully operational
```

---

### 1. Health Check

Test the health endpoint:

```bash
./scripts/test_health.sh
```

**Expected output:**
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

---

### 2. Upload PDF

Upload a PDF file for scanning:

```bash
./scripts/test_upload.sh [path-to-pdf]
```

**Default:** Uses `tests/fixtures/sample_with_pii.pdf` if no file specified  
**Sample PDF contains:** SSN (123-45-6789) and email patterns for testing

**Examples:**
```bash
# Use the default sample PDF (with PII)
./scripts/test_upload.sh

# Upload the clean sample (without PII)
./scripts/test_upload.sh tests/fixtures/sample_without_pii.pdf

# Upload a specific file
./scripts/test_upload.sh my_document.pdf
```

### 2a. Quick Upload Test

For quick testing with the sample PII PDF:

```bash
./scripts/quick_upload_test.sh
```

This is a simplified version that just uploads the sample PDF and shows the JSON response.

### 2b. Detailed Upload Test

For comprehensive testing with health checks and detailed output:

```bash
./scripts/test_upload_pii.sh
```

This script includes:
- Server health check
- File validation
- Detailed response parsing
- Error handling
- Colored output for better readability

**Expected output:**
```json
{
  "document_id": "123e4567-e89b-12d3-a456-426614174000",
  "filename": "test.pdf",
  "status": "pending",
  "upload_time": "2025-10-27T10:00:00.000000",
  "file_size": 455
}
```

---

### 3. Test Validation

Test upload endpoint with invalid files to verify error handling:

```bash
./scripts/test_invalid_file.sh
```

Tests the following scenarios:
- Non-PDF file (.txt)
- Empty file
- No file provided
- File too large (>10MB) - commented out by default

**Expected:** Various HTTP error codes (400, 413, 422) with appropriate error messages

---

### 4. Test Findings Endpoints

Test the findings query endpoints:

```bash
./scripts/test_findings.sh
```

This comprehensive test script:
1. Uploads a PDF with PII
2. Gets findings for the specific document
3. Gets all findings with pagination
4. Tests filtering by finding type
5. Tests 404 for non-existent documents

**Expected:** All endpoints return appropriate responses with findings data

---

## API Documentation

Once the server is running, visit:

- **Interactive Docs (Swagger UI):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

## Common Issues

### "Connection refused"
- Make sure the server is running: `uv run pdf-scan`

### "jq: command not found"
- Install jq: `brew install jq` (macOS) or remove `| jq '.'` from scripts

### "Permission denied"
- Make scripts executable: `chmod +x scripts/*.sh`

### "ClickHouse connection failed"
- Start ClickHouse: `docker-compose up -d`
- Check ClickHouse status: `docker-compose ps`
- View ClickHouse logs: `docker-compose logs clickhouse`

---

## Testing Workflow

1. **Start ClickHouse** (optional, for Phase 7+):
   ```bash
   docker-compose up -d
   ```

2. **Start the server** in one terminal:
   ```bash
   uv run pdf-scan
   ```

3. **In another terminal**, run tests:
   ```bash
   # Test ClickHouse (if using Phase 7+)
   ./scripts/test_clickhouse.sh
   
   # Run all tests at once (recommended)
   ./scripts/run_all_tests.sh
   
   # Or run individual tests:
   
   # Test health
   ./scripts/test_health.sh
   
   # Quick upload test (simple)
   ./scripts/quick_upload_test.sh
   
   # Detailed upload test (with health checks)
   ./scripts/test_upload_pii.sh
   
   # Upload custom PDF
   ./scripts/test_upload.sh
   
   # Test validation
   ./scripts/test_invalid_file.sh
   
   # Test findings endpoints
   ./scripts/test_findings.sh
   ```

4. **Check server logs** in the first terminal to see request processing

5. **Check ClickHouse logs** (if using Phase 7+):
   ```bash
   docker-compose logs -f clickhouse
   ```

---

## Notes

- The server runs with auto-reload enabled for development
- Uploaded files are currently saved to temp storage and immediately deleted
- In Phase 5, files will be kept for scanning and then cleaned up
- Document IDs are UUIDs generated for each upload

