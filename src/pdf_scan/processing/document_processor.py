"""Document processor for handling uploaded PDFs."""

import tempfile
from pathlib import Path
from typing import Dict

from pdf_scan.db import Backends
from pdf_scan.models import Document, DocumentStatus, Metric


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
        1. Creates a document record (status: processing)
        2. Stores document in database
        3. Saves to temporary storage
        4. Scans PDF for sensitive data
        5. Stores findings in database
        6. Updates document status (completed/failed)
        7. Records metrics
        8. Cleans up temp file
        
        Args:
            filename: Name of the uploaded file
            file_size: Size of the file in bytes
            content: Binary content of the PDF file
            backends: Database backends container (includes scanner)
            
        Returns:
            Dictionary with document metadata for response
            
        Raises:
            Exception: If file saving, scanning, or database operations fail
        """
        # Create document record with processing status
        document = Document.create(
            filename=filename,
            file_size=file_size,
        )
        
        # Update status to processing
        backends.document.store_document(document)
        backends.document.update_document_status(
            document.id,
            DocumentStatus.PROCESSING,
        )
        
        temp_path = None
        try:
            # Save to temporary storage for scanning
            with tempfile.NamedTemporaryFile(
                mode="wb",
                suffix=".pdf",
                prefix=f"pdf_scan_{document.id}_",
                delete=False,
            ) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Scan PDF for sensitive data using scanner from backends
            findings = backends.scanner.scan_pdf(temp_path)
            
            # Update findings with correct document ID
            for finding in findings:
                # Create new finding with correct document_id
                from pdf_scan.models import Finding
                corrected_finding = Finding(
                    id=finding.id,
                    document_id=document.id,
                    finding_type=finding.finding_type,
                    location=finding.location,
                    confidence=finding.confidence,
                )
                backends.finding.store_finding(corrected_finding)
            
            # Update document status to completed
            backends.document.update_document_status(
                document.id,
                DocumentStatus.COMPLETED,
            )
            
            # Record scan metrics
            scan_metric = Metric.create(
                operation="scan",
                duration_ms=0.0,  # TODO: Add timing in Phase 8
                document_id=document.id,
                metadata={
                    "findings_count": len(findings),
                    "scanner_type": backends.scanner.__class__.__name__,
                },
            )
            backends.metrics.store_metric(scan_metric)
            
        except Exception as e:
            # Update document status to failed
            backends.document.update_document_status(
                document.id,
                DocumentStatus.FAILED,
                error_message=str(e),
            )
            raise
        
        finally:
            # Clean up temp file
            if temp_path and Path(temp_path).exists():
                Path(temp_path).unlink()
        
        # Record upload metrics
        upload_metric = Metric.create(
            operation="upload",
            duration_ms=0.0,  # TODO: Add timing in Phase 8
            document_id=document.id,
            metadata={"file_size": file_size, "filename": filename},
        )
        backends.metrics.store_metric(upload_metric)
        
        # Get updated document to return final status
        final_document = backends.document.get_document(document.id)
        
        # Return document metadata
        return {
            "document_id": str(document.id),
            "filename": filename,
            "status": final_document.status.value if final_document else document.status.value,
            "upload_time": document.upload_time.isoformat(),
            "file_size": file_size,
            "findings_count": len(findings) if 'findings' in locals() else 0,
        }
