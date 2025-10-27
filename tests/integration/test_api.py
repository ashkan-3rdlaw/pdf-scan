"""Tests for FastAPI endpoints."""

import io
import os

import pytest
from httpx import ASGITransport, AsyncClient

from pdf_scan.app import app, get_backends
from pdf_scan.db import BackendFactory

# Set test environment before importing anything else
os.environ["DATABASE_BACKEND"] = "memory"

# Create a single shared backends instance for all tests
# This ensures documents and findings persist across test requests
# Use in-memory backend for tests regardless of environment configuration
shared_backends = BackendFactory.create_backends(backend="memory")

# Override the dependency to use shared backends
async def get_test_backends():
    return shared_backends

app.dependency_overrides[get_backends] = get_test_backends


@pytest.fixture
async def client():
    """Create an async HTTP client for testing."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_upload_valid_pdf(client):
    """Test uploading a valid PDF file."""
    # Create a minimal valid PDF
    pdf_content = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>>>/MediaBox[0 0 612 792]/Contents 4 0 R>>endobj
4 0 obj<</Length 44>>stream
BT /F1 12 Tf 100 700 Td (Test PDF) Tj ET
endstream endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000056 00000 n
0000000115 00000 n
0000000323 00000 n
trailer<</Size 5/Root 1 0 R>>
startxref
414
%%EOF"""
    
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    response = await client.post("/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert data["filename"] == "test.pdf"
    assert data["status"] == "completed"  # Now scanned immediately
    assert "upload_time" in data
    assert data["file_size"] == len(pdf_content)
    assert "findings_count" in data  # New field from scanner integration
    assert data["findings_count"] == 0  # Test PDF has no PII


@pytest.mark.asyncio
async def test_upload_no_file(client):
    """Test upload endpoint with no file."""
    response = await client.post("/upload")
    
    assert response.status_code == 422  # FastAPI validation error


@pytest.mark.asyncio
async def test_upload_empty_file(client):
    """Test uploading an empty file."""
    files = {"file": ("test.pdf", io.BytesIO(b""), "application/pdf")}
    response = await client.post("/upload", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "EMPTY_FILE"


@pytest.mark.asyncio
async def test_upload_invalid_extension(client):
    """Test uploading a non-PDF file."""
    files = {"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
    response = await client.post("/upload", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "INVALID_FILE_TYPE"


@pytest.mark.asyncio
async def test_upload_file_too_large(client):
    """Test uploading a file that exceeds size limit."""
    # Create a file larger than 10MB
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    files = {"file": ("large.pdf", io.BytesIO(large_content), "application/pdf")}
    response = await client.post("/upload", files=files)
    
    assert response.status_code == 413
    data = response.json()
    assert data["detail"]["code"] == "FILE_TOO_LARGE"


@pytest.mark.asyncio
async def test_upload_pdf_with_different_content_type(client):
    """Test that PDF with wrong content type is rejected."""
    pdf_content = b"%PDF-1.4\ntest"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "text/plain")}
    response = await client.post("/upload", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "INVALID_CONTENT_TYPE"


@pytest.mark.asyncio
async def test_openapi_docs_available(client):
    """Test that OpenAPI documentation is available."""
    response = await client.get("/docs")
    assert response.status_code == 200
    
    response = await client.get("/openapi.json")
    assert response.status_code == 200


# Findings endpoint tests
@pytest.mark.asyncio
async def test_get_findings_for_nonexistent_document(client):
    """Test getting findings for a document that doesn't exist."""
    fake_uuid = "12345678-1234-5678-1234-567812345678"
    response = await client.get(f"/findings/{fake_uuid}")
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"]["code"] == "DOCUMENT_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_findings_for_document_with_pii(client):
    """Test getting findings for a document with PII."""
    # First, upload a PDF with PII (using sample_with_pii.pdf)
    with open("tests/fixtures/sample_with_pii.pdf", "rb") as f:
        pdf_content = f.read()
    
    files = {"file": ("sample_with_pii.pdf", io.BytesIO(pdf_content), "application/pdf")}
    upload_response = await client.post("/upload", files=files)
    assert upload_response.status_code == 200
    
    upload_data = upload_response.json()
    document_id = upload_data["document_id"]
    assert upload_data["findings_count"] == 2  # Should have 2 findings
    
    # Now get findings for this document
    findings_response = await client.get(f"/findings/{document_id}")
    assert findings_response.status_code == 200
    
    findings_data = findings_response.json()
    assert findings_data["document_id"] == document_id
    assert findings_data["filename"] == "sample_with_pii.pdf"
    assert findings_data["status"] == "completed"
    assert "upload_time" in findings_data
    assert "file_size" in findings_data
    assert "findings" in findings_data
    assert len(findings_data["findings"]) == 2
    
    # Verify finding structure
    for finding in findings_data["findings"]:
        assert "id" in finding
        assert "type" in finding
        assert finding["type"] in ["ssn", "email"]
        assert "location" in finding
        assert "confidence" in finding
        assert finding["confidence"] == 1.0


@pytest.mark.asyncio
async def test_get_findings_for_document_without_pii(client):
    """Test getting findings for a document without PII."""
    # Upload a PDF without PII
    with open("tests/fixtures/sample_without_pii.pdf", "rb") as f:
        pdf_content = f.read()
    
    files = {"file": ("sample_without_pii.pdf", io.BytesIO(pdf_content), "application/pdf")}
    upload_response = await client.post("/upload", files=files)
    assert upload_response.status_code == 200
    
    upload_data = upload_response.json()
    document_id = upload_data["document_id"]
    assert upload_data["findings_count"] == 0
    
    # Get findings for this document
    findings_response = await client.get(f"/findings/{document_id}")
    assert findings_response.status_code == 200
    
    findings_data = findings_response.json()
    assert findings_data["document_id"] == document_id
    assert findings_data["filename"] == "sample_without_pii.pdf"
    assert findings_data["status"] == "completed"
    assert len(findings_data["findings"]) == 0


@pytest.mark.asyncio
async def test_get_all_findings_empty(client):
    """Test getting all findings when none exist (fresh test client)."""
    # Note: In a real test, we'd need to isolate the database state
    # For now, this tests pagination structure
    response = await client.get("/findings")
    assert response.status_code == 200
    
    data = response.json()
    assert "findings" in data
    assert "pagination" in data
    assert data["pagination"]["limit"] == 20  # Default
    assert data["pagination"]["offset"] == 0
    assert "total" in data["pagination"]
    assert "returned" in data["pagination"]


@pytest.mark.asyncio
async def test_get_all_findings_with_data(client):
    """Test getting all findings when some exist."""
    # Upload a document with PII
    with open("tests/fixtures/sample_with_pii.pdf", "rb") as f:
        pdf_content = f.read()
    
    files = {"file": ("test_pii.pdf", io.BytesIO(pdf_content), "application/pdf")}
    upload_response = await client.post("/upload", files=files)
    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    document_id = upload_data["document_id"]
    
    # Get all findings
    response = await client.get("/findings")
    assert response.status_code == 200
    
    data = response.json()
    assert "findings" in data
    assert len(data["findings"]) >= 2  # At least the 2 we just created
    
    # Verify finding structure
    found_our_findings = False
    for finding in data["findings"]:
        assert "id" in finding
        assert "document_id" in finding
        assert "type" in finding
        assert "location" in finding
        assert "confidence" in finding
        
        if finding["document_id"] == document_id:
            found_our_findings = True
    
    assert found_our_findings, "Should find findings for our uploaded document"


@pytest.mark.asyncio
async def test_get_all_findings_with_pagination(client):
    """Test pagination parameters for get all findings."""
    # Test with custom limit and offset
    response = await client.get("/findings?limit=5&offset=0")
    assert response.status_code == 200
    
    data = response.json()
    assert data["pagination"]["limit"] == 5
    assert data["pagination"]["offset"] == 0
    assert len(data["findings"]) <= 5


@pytest.mark.asyncio
async def test_get_all_findings_with_invalid_pagination(client):
    """Test that invalid pagination parameters are rejected."""
    # Test limit too high
    response = await client.get("/findings?limit=200")
    assert response.status_code == 422  # Validation error
    
    # Test negative offset
    response = await client.get("/findings?offset=-1")
    assert response.status_code == 422
    
    # Test limit too low
    response = await client.get("/findings?limit=0")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_all_findings_with_type_filter(client):
    """Test filtering findings by type."""
    # Upload a document with PII
    with open("tests/fixtures/sample_with_pii.pdf", "rb") as f:
        pdf_content = f.read()
    
    files = {"file": ("filter_test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    await client.post("/upload", files=files)
    
    # Get all SSN findings
    response = await client.get("/findings?finding_type=ssn")
    assert response.status_code == 200
    
    data = response.json()
    # Should have at least one SSN finding
    ssn_findings = [f for f in data["findings"] if f["type"] == "ssn"]
    assert len(ssn_findings) >= 1
    
    # Get all EMAIL findings
    response = await client.get("/findings?finding_type=email")
    assert response.status_code == 200
    
    data = response.json()
    # Should have at least one EMAIL finding
    email_findings = [f for f in data["findings"] if f["type"] == "email"]
    assert len(email_findings) >= 1


@pytest.mark.asyncio
async def test_metrics_endpoint_empty(client):
    """Test metrics endpoint structure."""
    response = await client.get("/metrics")
    
    assert response.status_code == 200
    data = response.json()
    
    # Should have metrics structure
    assert "metrics" in data
    assert "filters" in data
    assert "timestamp" in data
    
    # Should have both operation types
    assert "upload" in data["metrics"]
    assert "scan" in data["metrics"]
    
    # Should have operation field
    assert data["metrics"]["upload"]["operation"] == "upload"
    assert data["metrics"]["scan"]["operation"] == "scan"
    
    # Averages should be non-negative (may be 0.0 if no data or > 0.0 if data exists)
    assert data["metrics"]["upload"]["average_duration_ms"] >= 0.0
    assert data["metrics"]["scan"]["average_duration_ms"] >= 0.0


@pytest.mark.asyncio
async def test_metrics_endpoint_with_data(client):
    """Test metrics endpoint after uploading files."""
    # Upload a file to generate metrics
    with open("tests/fixtures/sample_with_pii.pdf", "rb") as f:
        pdf_content = f.read()
    
    files = {"file": ("metrics_test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    upload_response = await client.post("/upload", files=files)
    assert upload_response.status_code == 200
    
    # Get metrics
    response = await client.get("/metrics")
    assert response.status_code == 200
    
    data = response.json()
    
    # Should have metrics structure
    assert "metrics" in data
    assert "filters" in data
    assert "timestamp" in data
    
    # Should have both operation types
    assert "upload" in data["metrics"]
    assert "scan" in data["metrics"]
    
    # Should have non-zero averages after processing
    assert data["metrics"]["upload"]["average_duration_ms"] > 0.0
    assert data["metrics"]["scan"]["average_duration_ms"] > 0.0
    
    # Should have operation field
    assert data["metrics"]["upload"]["operation"] == "upload"
    assert data["metrics"]["scan"]["operation"] == "scan"


@pytest.mark.asyncio
async def test_metrics_endpoint_filter_by_operation(client):
    """Test metrics endpoint with operation filter."""
    # Upload a file to generate metrics
    with open("tests/fixtures/sample_with_pii.pdf", "rb") as f:
        pdf_content = f.read()
    
    files = {"file": ("filter_test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    await client.post("/upload", files=files)
    
    # Test filtering by upload operation
    response = await client.get("/metrics?operation=upload")
    assert response.status_code == 200
    
    data = response.json()
    assert "upload" in data["metrics"]
    assert "scan" not in data["metrics"]
    assert data["filters"]["operation"] == "upload"
    
    # Test filtering by scan operation
    response = await client.get("/metrics?operation=scan")
    assert response.status_code == 200
    
    data = response.json()
    assert "scan" in data["metrics"]
    assert "upload" not in data["metrics"]
    assert data["filters"]["operation"] == "scan"


@pytest.mark.asyncio
async def test_metrics_endpoint_invalid_time_format(client):
    """Test metrics endpoint with invalid time format."""
    response = await client.get("/metrics?start_time=invalid")
    assert response.status_code == 400
    
    data = response.json()
    assert data["detail"]["code"] == "INVALID_TIME_FORMAT"
    assert "Invalid start_time format" in data["detail"]["error"]
    
    response = await client.get("/metrics?end_time=invalid")
    assert response.status_code == 400
    
    data = response.json()
    assert data["detail"]["code"] == "INVALID_TIME_FORMAT"
    assert "Invalid end_time format" in data["detail"]["error"]

