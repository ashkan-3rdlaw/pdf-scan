"""Database entities for the PDF scan service."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID, uuid4


class DocumentStatus(StrEnum):
    """Status of a document in the processing pipeline."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FindingType(StrEnum):
    """Types of sensitive data that can be detected."""

    SSN = "ssn"
    EMAIL = "email"
    # Extensible - add more types as needed


@dataclass
class Document:
    """Represents a uploaded document and its metadata."""

    id: UUID
    filename: str
    upload_time: datetime
    status: DocumentStatus
    file_size: int  # in bytes
    error_message: Optional[str] = None

    @classmethod
    def create(cls, filename: str, file_size: int) -> "Document":
        """Create a new document with generated ID and current timestamp."""
        return cls(
            id=uuid4(),
            filename=filename,
            upload_time=datetime.now(UTC),
            status=DocumentStatus.PENDING,
            file_size=file_size,
        )


@dataclass
class Finding:
    """Represents a sensitive data finding in a document."""

    id: UUID
    document_id: UUID
    finding_type: FindingType
    location: str  # e.g., "page 2", "line 45"
    confidence: float  # 0.0 to 1.0
    # Content snippet is intentionally not stored for security
    # Only store metadata about the finding

    @classmethod
    def create(
        cls,
        document_id: UUID,
        finding_type: FindingType,
        location: str,
        confidence: float = 1.0,
    ) -> "Finding":
        """Create a new finding with generated ID."""
        return cls(
            id=uuid4(),
            document_id=document_id,
            finding_type=finding_type,
            location=location,
            confidence=confidence,
        )


@dataclass
class Metric:
    """Represents a performance metric."""

    id: UUID
    operation: str  # e.g., "upload", "scan", "db_query"
    duration_ms: float
    timestamp: datetime
    document_id: Optional[UUID] = None
    metadata: dict = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        operation: str,
        duration_ms: float,
        document_id: Optional[UUID] = None,
        metadata: Optional[dict] = None,
    ) -> "Metric":
        """Create a new metric with generated ID and current timestamp."""
        return cls(
            id=uuid4(),
            operation=operation,
            duration_ms=duration_ms,
            timestamp=datetime.now(UTC),
            document_id=document_id,
            metadata=metadata or {},
        )

