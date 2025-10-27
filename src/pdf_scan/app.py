"""FastAPI web server for PDF scanning service."""

import asyncio
from typing import Annotated, Optional
from uuid import UUID

from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile, status

from pdf_scan.db import BackendFactory, Backends
from pdf_scan.processing import DocumentProcessor
from pdf_scan.validation import FileValidator
from pdf_scan.validation.file_validator import ValidationError

# Configuration
VERSION = "0.1.0"

app = FastAPI(
    title="PDF Scan Service",
    description="Upload PDFs to scan for sensitive information",
    version=VERSION,
)

# Singleton: Create a single shared backends instance for the lifetime of the application
# This ensures documents and findings persist across requests
_backends_instance: Optional[Backends] = None
_clickhouse_pool = None


async def get_backends() -> Backends:
    """
    Dependency to get database backends (includes scanner).
    
    Uses environment variables to determine the backend type and configuration.
    For ClickHouse backends, creates and manages a connection pool.
    """
    global _backends_instance, _clickhouse_pool
    
    if _backends_instance is None:
        backend_type = BackendFactory.get_backend_type()
        
        if backend_type == "clickhouse":
            # Create ClickHouse pool if not already created
            if _clickhouse_pool is None:
                _clickhouse_pool = await BackendFactory.create_clickhouse_pool()
            _backends_instance = BackendFactory.create_backends(backend="clickhouse", pool=_clickhouse_pool)
        else:
            # Use in-memory backend
            _backends_instance = BackendFactory.create_backends(backend="memory")
    
    return _backends_instance


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": VERSION,
    }


@app.post("/upload")
async def upload_pdf(
    file: Annotated[UploadFile, File(description="PDF file to scan")],
):
    """
    Upload a PDF file for scanning.
    
    - Validates file type (must be PDF)
    - Validates file size (max 10MB)
    - Generates unique document ID
    - Saves to temporary storage
    - Stores document in database
    - Returns document metadata
    """
    # Validate and read uploaded file
    try:
        content, file_size, filename = await FileValidator.validate_and_read_fastapi_upload(file)
    except ValidationError as e:
        # Map validation errors to appropriate HTTP status codes
        status_code = status.HTTP_400_BAD_REQUEST
        if e.code == "FILE_TOO_LARGE":
            status_code = status.HTTP_413_CONTENT_TOO_LARGE
        
        raise HTTPException(
            status_code=status_code,
            detail={
                "error": e.message,
                "code": e.code,
            },
        )
    
    # Get backends and process the uploaded document
    try:
        backends = await get_backends()
        response = await DocumentProcessor.process_upload(
            filename=filename,
            file_size=file_size,
            content=content,
            backends=backends,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": f"Failed to process document: {str(e)}",
                "code": "PROCESSING_ERROR",
            },
        )
    
    return response


@app.get("/findings/{document_id}")
async def get_findings_for_document(
    document_id: UUID,
):
    """
    Get findings for a specific document.
    
    Returns document metadata along with all findings detected during scanning.
    
    Args:
        document_id: UUID of the document to query
        
    Returns:
        JSON with document metadata and list of findings
        
    Raises:
        404: Document not found
    """
    # Get backends and retrieve document
    backends = await get_backends()
    document = await backends.document.get_document(document_id)
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"Document {document_id} not found",
                "code": "DOCUMENT_NOT_FOUND",
            },
        )
    
    # Get findings for this document
    findings = await backends.finding.get_findings(document_id)
    
    # Format response
    return {
        "document_id": str(document.id),
        "filename": document.filename,
        "upload_time": document.upload_time.isoformat(),
        "status": document.status.value,
        "file_size": document.file_size,
        "findings": [
            {
                "id": str(finding.id),
                "type": finding.finding_type.value,
                "location": finding.location,
                "confidence": finding.confidence,
            }
            for finding in findings
        ],
    }


@app.get("/findings")
async def get_all_findings(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    finding_type: Optional[str] = None,
):
    """
    Get findings across all documents with pagination.
    
    Useful for admin/monitoring to see all findings in the system.
    
    Args:
        limit: Maximum number of findings to return (1-100, default 20)
        offset: Number of findings to skip (default 0)
        finding_type: Optional filter by finding type (e.g., "SSN", "EMAIL")
        
    Returns:
        JSON with findings list and metadata
    """
    # Get backends and retrieve findings
    backends = await get_backends()
    findings = await backends.finding.get_all_findings(
        limit=limit,
        offset=offset,
        finding_type=finding_type,
    )
    
    # Get total count for pagination metadata
    total_count = await backends.finding.count_findings(None)  # Count all findings
    
    # Format response
    return {
        "findings": [
            {
                "id": str(finding.id),
                "document_id": str(finding.document_id),
                "type": finding.finding_type.value,
                "location": finding.location,
                "confidence": finding.confidence,
            }
            for finding in findings
        ],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "total": total_count,
            "returned": len(findings),
        },
    }

