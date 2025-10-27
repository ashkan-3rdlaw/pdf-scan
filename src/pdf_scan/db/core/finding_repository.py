"""Abstract interface for finding repository."""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from pdf_scan.models import Finding, FindingType


class FindingRepository(ABC):
    """Abstract interface for finding storage and retrieval."""

    @abstractmethod
    def store_finding(self, finding: Finding) -> None:
        """
        Store a finding record.

        Args:
            finding: Finding entity to store
        """
        pass

    @abstractmethod
    def get_findings(self, document_id: UUID) -> list[Finding]:
        """
        Retrieve all findings for a specific document.

        Args:
            document_id: UUID of the document

        Returns:
            List of findings for the document
        """
        pass

    @abstractmethod
    def get_all_findings(
        self, limit: int = 100, offset: int = 0, finding_type: Optional[FindingType] = None
    ) -> list[Finding]:
        """
        Retrieve findings with pagination and optional filtering.

        Args:
            limit: Maximum number of findings to return
            offset: Number of findings to skip
            finding_type: Optional filter by finding type

        Returns:
            List of findings
        """
        pass

    @abstractmethod
    def count_findings(self, document_id: Optional[UUID] = None) -> int:
        """
        Count findings, optionally filtered by document.

        Args:
            document_id: Optional document UUID to filter by

        Returns:
            Number of findings
        """
        pass

