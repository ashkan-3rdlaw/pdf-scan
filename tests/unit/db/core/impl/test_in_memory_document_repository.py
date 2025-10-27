"""Tests for InMemoryDocumentRepository."""

import pytest
from uuid import UUID

from pdf_scan.db.core.impl import InMemoryDocumentRepository
from pdf_scan.models import Document, DocumentStatus


class TestInMemoryDocumentRepository:
    """Test suite for InMemoryDocumentRepository."""

    @pytest.mark.asyncio
    async def test_store_and_get_document(self):
        """Test storing and retrieving a document."""
        repo = InMemoryDocumentRepository()
        doc = Document.create(filename="test.pdf", file_size=1024)

        await repo.store_document(doc)
        retrieved = await repo.get_document(doc.id)

        assert retrieved is not None
        assert retrieved.id == doc.id
        assert retrieved.filename == "test.pdf"
        assert retrieved.file_size == 1024
        assert retrieved.status == DocumentStatus.PENDING

    @pytest.mark.asyncio
    async def test_get_nonexistent_document(self):
        """Test retrieving a document that doesn't exist."""
        repo = InMemoryDocumentRepository()
        doc_id = UUID("123e4567-e89b-12d3-a456-426614174000")

        result = await repo.get_document(doc_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_document_status(self):
        """Test updating a document's status."""
        repo = InMemoryDocumentRepository()
        doc = Document.create(filename="test.pdf", file_size=1024)
        await repo.store_document(doc)

        await repo.update_document_status(doc.id, DocumentStatus.PROCESSING)
        updated = await repo.get_document(doc.id)

        assert updated is not None
        assert updated.status == DocumentStatus.PROCESSING
        assert updated.error_message is None

    @pytest.mark.asyncio
    async def test_update_document_status_with_error(self):
        """Test updating a document's status with an error message."""
        repo = InMemoryDocumentRepository()
        doc = Document.create(filename="test.pdf", file_size=1024)
        await repo.store_document(doc)

        error_msg = "Failed to scan PDF"
        await repo.update_document_status(doc.id, DocumentStatus.FAILED, error_msg)
        updated = await repo.get_document(doc.id)

        assert updated is not None
        assert updated.status == DocumentStatus.FAILED
        assert updated.error_message == error_msg

    @pytest.mark.asyncio
    async def test_update_nonexistent_document_raises_error(self):
        """Test that updating a nonexistent document raises KeyError."""
        repo = InMemoryDocumentRepository()
        doc_id = UUID("123e4567-e89b-12d3-a456-426614174000")

        with pytest.raises(KeyError):
            await repo.update_document_status(doc_id, DocumentStatus.COMPLETED)

    @pytest.mark.asyncio
    async def test_list_documents_empty(self):
        """Test listing documents when repository is empty."""
        repo = InMemoryDocumentRepository()
        docs = await repo.list_documents()
        assert docs == []

    @pytest.mark.asyncio
    async def test_list_documents_sorted_by_upload_time(self):
        """Test that documents are sorted by upload time (most recent first)."""
        repo = InMemoryDocumentRepository()

        # Create documents with slightly different timestamps
        doc1 = Document.create(filename="first.pdf", file_size=100)
        doc2 = Document.create(filename="second.pdf", file_size=200)
        doc3 = Document.create(filename="third.pdf", file_size=300)

        # Store in random order
        await repo.store_document(doc2)
        await repo.store_document(doc1)
        await repo.store_document(doc3)

        docs = await repo.list_documents()

        # Should be sorted by upload_time descending (most recent first)
        # Since they're created in quick succession, doc3 should be most recent
        assert len(docs) == 3
        assert docs[0].filename == "third.pdf"
        assert docs[2].filename == "first.pdf"

    @pytest.mark.asyncio
    async def test_list_documents_with_pagination(self):
        """Test listing documents with limit and offset."""
        repo = InMemoryDocumentRepository()

        # Create 5 documents
        for i in range(5):
            doc = Document.create(filename=f"doc{i}.pdf", file_size=100 * i)
            await repo.store_document(doc)

        # Get first 2
        page1 = await repo.list_documents(limit=2, offset=0)
        assert len(page1) == 2

        # Get next 2
        page2 = await repo.list_documents(limit=2, offset=2)
        assert len(page2) == 2

        # Get last page
        page3 = await repo.list_documents(limit=2, offset=4)
        assert len(page3) == 1

    @pytest.mark.asyncio
    async def test_list_documents_offset_beyond_length(self):
        """Test that offset beyond length returns empty list."""
        repo = InMemoryDocumentRepository()
        doc = Document.create(filename="test.pdf", file_size=1024)
        await repo.store_document(doc)

        docs = await repo.list_documents(limit=10, offset=10)
        assert docs == []

    @pytest.mark.asyncio
    async def test_store_duplicate_document_overwrites(self):
        """Test that storing a document with same ID overwrites the previous one."""
        repo = InMemoryDocumentRepository()
        doc = Document.create(filename="test.pdf", file_size=1024)

        await repo.store_document(doc)

        # Create a new document with same ID but different data
        updated_doc = Document(
            id=doc.id,
            filename="updated.pdf",
            upload_time=doc.upload_time,
            status=DocumentStatus.COMPLETED,
            file_size=2048,
        )
        await repo.store_document(updated_doc)

        retrieved = await repo.get_document(doc.id)
        assert retrieved is not None
        assert retrieved.filename == "updated.pdf"
        assert retrieved.file_size == 2048
        assert retrieved.status == DocumentStatus.COMPLETED

