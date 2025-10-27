"""Document processor for handling uploaded PDFs."""

import tempfile
from pathlib import Path
from typing import Dict

from pdf_scan.db import Backends
from pdf_scan.models import Document, Metric


class DocumentProcessor:
    """Handles document processing workflow."""

    @staticmethod
    def process_upload(
        filename: str,
        file_size: int,
        content: bytes,
        backends: Backends,
    ) -> Dict[str, str]:
        """
        Process an uploaded PDF document.
        
        This implementation:
        1. Creates a document record
        2. Stores document in database
        3. Saves to temporary storage
        4. Records metrics
        5. Cleans up temp file (will be kept for scanning in Phase 5)
        
        In Phase 5, this will be enhanced to:
        - Trigger PDF scanning
        - Store findings
        - Update document status
        
        Args:
            filename: Name of the uploaded file
            file_size: Size of the file in bytes
            content: Binary content of the PDF file
            backends: Database backends container
            
        Returns:
            Dictionary with document metadata for response
            
        Raises:
            Exception: If file saving or database operations fail
        """
        # Create document record
        document = Document.create(
            filename=filename,
            file_size=file_size,
        )
        
        # Store document in database
        backends.document.store_document(document)
        
        # Save to temporary storage
        # Note: In Phase 5, we'll keep this file for scanning
        # For now, we just save to temp and clean up
        with tempfile.NamedTemporaryFile(
            mode="wb",
            suffix=".pdf",
            prefix=f"pdf_scan_{document.id}_",
            delete=False,
        ) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Clean up temp file (will be kept in Phase 5 for scanning)
        Path(temp_path).unlink()
        
        # Record upload metrics
        upload_metric = Metric.create(
            operation="upload",
            duration_ms=0.0,  # TODO: Add timing in Phase 8
            document_id=document.id,
            metadata={"file_size": file_size, "filename": filename},
        )
        backends.metrics.store_metric(upload_metric)
        
        # Return document metadata
        return {
            "document_id": str(document.id),
            "filename": filename,
            "status": document.status.value,
            "upload_time": document.upload_time.isoformat(),
            "file_size": file_size,
        }
