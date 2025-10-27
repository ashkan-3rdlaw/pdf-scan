"""In-memory implementation of finding repository."""

from typing import Optional
from uuid import UUID

from pdf_scan.models import Finding, FindingType

from ..finding_repository import FindingRepository


class InMemoryFindingRepository(FindingRepository):
    """In-memory finding storage using Python dict."""

    def __init__(self) -> None:
        """Initialize with empty storage."""
        self._findings: dict[UUID, Finding] = {}

    def store_finding(self, finding: Finding) -> None:
        """
        Store a finding record.

        Args:
            finding: Finding entity to store
        """
        self._findings[finding.id] = finding

    def get_findings(self, document_id: UUID) -> list[Finding]:
        """
        Retrieve all findings for a specific document.

        Args:
            document_id: UUID of the document

        Returns:
            List of findings for the document, sorted by confidence descending
        """
        document_findings = [
            f for f in self._findings.values() if f.document_id == document_id
        ]
        # Sort by confidence descending (highest confidence first)
        return sorted(document_findings, key=lambda f: f.confidence, reverse=True)

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
            List of findings, sorted by confidence descending
        """
        # Filter by type if specified
        if finding_type is not None:
            findings = [
                f for f in self._findings.values() if f.finding_type == finding_type
            ]
        else:
            findings = list(self._findings.values())

        # Sort by confidence descending
        sorted_findings = sorted(findings, key=lambda f: f.confidence, reverse=True)
        return sorted_findings[offset : offset + limit]

    def count_findings(self, document_id: Optional[UUID] = None) -> int:
        """
        Count findings, optionally filtered by document.

        Args:
            document_id: Optional document UUID to filter by

        Returns:
            Number of findings
        """
        if document_id is not None:
            return sum(
                1 for f in self._findings.values() if f.document_id == document_id
            )
        return len(self._findings)

