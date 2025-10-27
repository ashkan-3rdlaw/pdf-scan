"""FastAPI web server for PDF scanning service."""

from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile, status

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


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": VERSION,
    }


@app.post("/upload")
async def upload_pdf(
    file: Annotated[UploadFile, File(description="PDF file to scan")]
):
    """
    Upload a PDF file for scanning.
    
    - Validates file type (must be PDF)
    - Validates file size (max 10MB)
    - Generates unique document ID
    - Saves to temporary storage
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
    
    # Process the uploaded document
    try:
        response = DocumentProcessor.process_upload(
            filename=filename,
            file_size=file_size,
            content=content,
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

