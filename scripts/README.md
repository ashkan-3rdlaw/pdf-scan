# Test Scripts

Manual testing scripts for the PDF scan service using curl.

## Prerequisites

- Server must be running on `http://localhost:8000`
- `jq` installed for JSON formatting (optional, but recommended)
- `curl` for making HTTP requests

## Starting the Server

```bash
uv run pdf-scan
```

The server will start on `http://localhost:8000` with auto-reload enabled.

## Scripts

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

---

## Testing Workflow

1. **Start the server** in one terminal:
   ```bash
   uv run pdf-scan
   ```

2. **In another terminal**, run tests:
   ```bash
   # Test health
   ./scripts/test_health.sh
   
   # Upload sample PDF (uses default test PDF)
   ./scripts/test_upload.sh
   
   # Test validation
   ./scripts/test_invalid_file.sh
   ```

3. **Check server logs** in the first terminal to see request processing

---

## Notes

- The server runs with auto-reload enabled for development
- Uploaded files are currently saved to temp storage and immediately deleted
- In Phase 5, files will be kept for scanning and then cleaned up
- Document IDs are UUIDs generated for each upload

