"""ClickHouse implementation of document repository."""

from typing import Optional
from uuid import UUID

from asynch.pool import Pool

from pdf_scan.models import Document, DocumentStatus

from ..document_repository import DocumentRepository


class ClickHouseDocumentRepository(DocumentRepository):
    """ClickHouse document storage implementation."""

    def __init__(self, pool: Pool) -> None:
        """
        Initialize with ClickHouse connection pool.

        Args:
            pool: ClickHouse connection pool
        """
        self._pool = pool

    async def store_document(self, document: Document) -> None:
        """
        Store a document record.

        Args:
            document: Document entity to store
        """
        async with self._pool.connection() as conn:
            cursor = conn.cursor()
            await cursor.execute(
                """
                INSERT INTO documents (id, filename, upload_time, status, file_size, error_message)
                VALUES
                """,
                [(
                    str(document.id),
                    document.filename,
                    document.upload_time,
                    document.status.value,
                    document.file_size,
                    document.error_message,
                )]
            )

    async def get_document(self, document_id: UUID) -> Optional[Document]:
        """
        Retrieve a document by its ID.

        Args:
            document_id: UUID of the document

        Returns:
            Document if found, None otherwise
        """
        async with self._pool.connection() as conn:
            cursor = conn.cursor()
            await cursor.execute(
                """
                SELECT id, filename, upload_time, status, file_size, error_message
                FROM documents
                WHERE id = %(doc_id)s
                """,
                {"doc_id": str(document_id)}
            )
            row = await cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_document(row)

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
        async with self._pool.connection() as conn:
            cursor = conn.cursor()
            await cursor.execute(
                """
                ALTER TABLE documents
                UPDATE status = %(new_status)s, error_message = %(err_msg)s
                WHERE id = %(doc_id)s
                """,
                {
                    "doc_id": str(document_id),
                    "new_status": status.value,
                    "err_msg": error_message or "",
                }
            )

    async def list_documents(self, limit: int = 100, offset: int = 0) -> list[Document]:
        """
        List documents with pagination.

        Args:
            limit: Maximum number of documents to return
            offset: Number of documents to skip

        Returns:
            List of documents, sorted by upload_time descending
        """
        async with self._pool.connection() as conn:
            cursor = conn.cursor()
            await cursor.execute(
                """
                SELECT id, filename, upload_time, status, file_size, error_message
                FROM documents
                ORDER BY upload_time DESC
                LIMIT %(limit)s OFFSET %(offset)s
                """,
                {"limit": limit, "offset": offset}
            )
            rows = await cursor.fetchall()
            return [self._row_to_document(row) for row in rows]

    def _row_to_document(self, row: tuple) -> Document:
        """
        Convert a database row to a Document entity.

        Args:
            row: Tuple containing document data

        Returns:
            Document entity
        """
        return Document(
            id=UUID(row[0]) if isinstance(row[0], str) else row[0],
            filename=row[1],
            upload_time=row[2],
            status=DocumentStatus(row[3]),
            file_size=row[4],
            error_message=row[5] if row[5] else None,
        )

