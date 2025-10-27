"""Abstract interface for document repository."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from pdf_scan.models import Document, DocumentStatus


class DocumentRepository(ABC):
    """Abstract interface for document storage and retrieval."""

    @abstractmethod
    async def store_document(self, document: Document) -> None:
        """
        Store a document record.

        Args:
            document: Document entity to store
        """
        pass

    @abstractmethod
    async def get_document(self, document_id: UUID) -> Optional[Document]:
        """
        Retrieve a document by its ID.

        Args:
            document_id: UUID of the document

        Returns:
            Document if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_document_status(
        self, document_id: UUID, status: DocumentStatus, error_message: Optional[str] = None
    ) -> None:
        """
        Update the status of a document.

        Args:
            document_id: UUID of the document
            status: New status to set
            error_message: Optional error message if status is FAILED
        """
        pass

    @abstractmethod
    async def list_documents(self, limit: int = 100, offset: int = 0) -> list[Document]:
        """
        List documents with pagination.

        Args:
            limit: Maximum number of documents to return
            offset: Number of documents to skip

        Returns:
            List of documents
        """
        pass

