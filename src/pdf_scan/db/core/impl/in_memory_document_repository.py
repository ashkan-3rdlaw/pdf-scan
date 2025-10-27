"""In-memory implementation of document repository."""

from typing import Optional
from uuid import UUID

from pdf_scan.models import Document, DocumentStatus

from ..document_repository import DocumentRepository


class InMemoryDocumentRepository(DocumentRepository):
    """In-memory document storage using Python dict."""

    def __init__(self) -> None:
        """Initialize with empty storage."""
        self._documents: dict[UUID, Document] = {}

    def store_document(self, document: Document) -> None:
        """
        Store a document record.

        Args:
            document: Document entity to store
        """
        self._documents[document.id] = document

    def get_document(self, document_id: UUID) -> Optional[Document]:
        """
        Retrieve a document by its ID.

        Args:
            document_id: UUID of the document

        Returns:
            Document if found, None otherwise
        """
        return self._documents.get(document_id)

    def update_document_status(
        self, document_id: UUID, status: DocumentStatus, error_message: Optional[str] = None
    ) -> None:
        """
        Update the status of a document.

        Args:
            document_id: UUID of the document
            status: New status to set
            error_message: Optional error message if status is FAILED

        Raises:
            KeyError: If document not found
        """
        if document_id not in self._documents:
            raise KeyError(f"Document {document_id} not found")

        document = self._documents[document_id]
        # Create updated document (dataclasses are immutable by default in our use)
        self._documents[document_id] = Document(
            id=document.id,
            filename=document.filename,
            upload_time=document.upload_time,
            status=status,
            file_size=document.file_size,
            error_message=error_message,
        )

    def list_documents(self, limit: int = 100, offset: int = 0) -> list[Document]:
        """
        List documents with pagination.

        Args:
            limit: Maximum number of documents to return
            offset: Number of documents to skip

        Returns:
            List of documents, sorted by upload_time descending
        """
        # Sort by upload_time descending (most recent first)
        sorted_docs = sorted(
            self._documents.values(), key=lambda d: d.upload_time, reverse=True
        )
        return sorted_docs[offset : offset + limit]

