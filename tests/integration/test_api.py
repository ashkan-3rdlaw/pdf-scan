"""Tests for FastAPI endpoints."""

import io

import pytest
from fastapi.testclient import TestClient

from pdf_scan.app import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"


def test_upload_valid_pdf():
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
    response = client.post("/upload", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    assert data["filename"] == "test.pdf"
    assert data["status"] == "pending"
    assert "upload_time" in data
    assert data["file_size"] == len(pdf_content)


def test_upload_no_file():
    """Test upload endpoint with no file."""
    response = client.post("/upload")
    
    assert response.status_code == 422  # FastAPI validation error


def test_upload_empty_file():
    """Test uploading an empty file."""
    files = {"file": ("test.pdf", io.BytesIO(b""), "application/pdf")}
    response = client.post("/upload", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "EMPTY_FILE"


def test_upload_invalid_extension():
    """Test uploading a non-PDF file."""
    files = {"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")}
    response = client.post("/upload", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "INVALID_FILE_TYPE"


def test_upload_file_too_large():
    """Test uploading a file that exceeds size limit."""
    # Create a file larger than 10MB
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    files = {"file": ("large.pdf", io.BytesIO(large_content), "application/pdf")}
    response = client.post("/upload", files=files)
    
    assert response.status_code == 413
    data = response.json()
    assert data["detail"]["code"] == "FILE_TOO_LARGE"


def test_upload_pdf_with_different_content_type():
    """Test that PDF with wrong content type is rejected."""
    pdf_content = b"%PDF-1.4\ntest"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "text/plain")}
    response = client.post("/upload", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "INVALID_CONTENT_TYPE"


def test_openapi_docs_available():
    """Test that OpenAPI documentation is available."""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/openapi.json")
    assert response.status_code == 200

