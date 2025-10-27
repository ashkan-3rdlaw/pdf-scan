"""Core database interfaces for document and finding storage."""

from .document_repository import DocumentRepository
from .finding_repository import FindingRepository

__all__ = [
    "DocumentRepository",
    "FindingRepository",
]

