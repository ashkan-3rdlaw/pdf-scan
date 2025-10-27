"""Tests for InMemoryFindingRepository."""

from uuid import UUID, uuid4

from pdf_scan.db.core.impl import InMemoryFindingRepository
from pdf_scan.models import Finding, FindingType


class TestInMemoryFindingRepository:
    """Test suite for InMemoryFindingRepository."""

    def test_store_and_get_findings(self):
        """Test storing and retrieving findings for a document."""
        repo = InMemoryFindingRepository()
        doc_id = uuid4()

        finding1 = Finding.create(
            document_id=doc_id,
            finding_type=FindingType.SSN,
            location="page 1",
            confidence=0.95,
        )
        finding2 = Finding.create(
            document_id=doc_id,
            finding_type=FindingType.EMAIL,
            location="page 2",
            confidence=0.88,
        )

        repo.store_finding(finding1)
        repo.store_finding(finding2)

        findings = repo.get_findings(doc_id)
        assert len(findings) == 2
        # Should be sorted by confidence descending
        assert findings[0].confidence == 0.95
        assert findings[1].confidence == 0.88

    def test_get_findings_for_nonexistent_document(self):
        """Test getting findings for a document with no findings."""
        repo = InMemoryFindingRepository()
        doc_id = UUID("123e4567-e89b-12d3-a456-426614174000")

        findings = repo.get_findings(doc_id)
        assert findings == []

    def test_get_findings_sorted_by_confidence(self):
        """Test that findings are sorted by confidence descending."""
        repo = InMemoryFindingRepository()
        doc_id = uuid4()

        # Store findings with different confidence levels
        finding1 = Finding.create(
            document_id=doc_id,
            finding_type=FindingType.SSN,
            location="page 1",
            confidence=0.75,
        )
        finding2 = Finding.create(
            document_id=doc_id,
            finding_type=FindingType.EMAIL,
            location="page 2",
            confidence=0.99,
        )
        finding3 = Finding.create(
            document_id=doc_id,
            finding_type=FindingType.SSN,
            location="page 3",
            confidence=0.82,
        )

        repo.store_finding(finding1)
        repo.store_finding(finding2)
        repo.store_finding(finding3)

        findings = repo.get_findings(doc_id)
        assert len(findings) == 3
        assert findings[0].confidence == 0.99
        assert findings[1].confidence == 0.82
        assert findings[2].confidence == 0.75

    def test_get_findings_multiple_documents(self):
        """Test that findings are correctly separated by document."""
        repo = InMemoryFindingRepository()
        doc_id1 = uuid4()
        doc_id2 = uuid4()

        finding1 = Finding.create(
            document_id=doc_id1,
            finding_type=FindingType.SSN,
            location="page 1",
        )
        finding2 = Finding.create(
            document_id=doc_id2,
            finding_type=FindingType.EMAIL,
            location="page 1",
        )
        finding3 = Finding.create(
            document_id=doc_id1,
            finding_type=FindingType.EMAIL,
            location="page 2",
        )

        repo.store_finding(finding1)
        repo.store_finding(finding2)
        repo.store_finding(finding3)

        findings_doc1 = repo.get_findings(doc_id1)
        findings_doc2 = repo.get_findings(doc_id2)

        assert len(findings_doc1) == 2
        assert len(findings_doc2) == 1

    def test_get_all_findings_empty(self):
        """Test getting all findings when repository is empty."""
        repo = InMemoryFindingRepository()
        findings = repo.get_all_findings()
        assert findings == []

    def test_get_all_findings(self):
        """Test getting all findings without filters."""
        repo = InMemoryFindingRepository()
        doc_id = uuid4()

        finding1 = Finding.create(
            document_id=doc_id,
            finding_type=FindingType.SSN,
            location="page 1",
            confidence=0.95,
        )
        finding2 = Finding.create(
            document_id=doc_id,
            finding_type=FindingType.EMAIL,
            location="page 2",
            confidence=0.88,
        )

        repo.store_finding(finding1)
        repo.store_finding(finding2)

        findings = repo.get_all_findings()
        assert len(findings) == 2
        # Should be sorted by confidence descending
        assert findings[0].confidence == 0.95

    def test_get_all_findings_with_type_filter(self):
        """Test filtering findings by type."""
        repo = InMemoryFindingRepository()
        doc_id = uuid4()

        finding1 = Finding.create(
            document_id=doc_id,
            finding_type=FindingType.SSN,
            location="page 1",
        )
        finding2 = Finding.create(
            document_id=doc_id,
            finding_type=FindingType.EMAIL,
            location="page 2",
        )
        finding3 = Finding.create(
            document_id=doc_id,
            finding_type=FindingType.SSN,
            location="page 3",
        )

        repo.store_finding(finding1)
        repo.store_finding(finding2)
        repo.store_finding(finding3)

        ssn_findings = repo.get_all_findings(finding_type=FindingType.SSN)
        email_findings = repo.get_all_findings(finding_type=FindingType.EMAIL)

        assert len(ssn_findings) == 2
        assert len(email_findings) == 1
        assert all(f.finding_type == FindingType.SSN for f in ssn_findings)
        assert all(f.finding_type == FindingType.EMAIL for f in email_findings)

    def test_get_all_findings_with_pagination(self):
        """Test paginating findings."""
        repo = InMemoryFindingRepository()
        doc_id = uuid4()

        # Create 5 findings
        for i in range(5):
            finding = Finding.create(
                document_id=doc_id,
                finding_type=FindingType.SSN,
                location=f"page {i}",
                confidence=0.5 + (i * 0.1),
            )
            repo.store_finding(finding)

        # Get first 2
        page1 = repo.get_all_findings(limit=2, offset=0)
        assert len(page1) == 2

        # Get next 2
        page2 = repo.get_all_findings(limit=2, offset=2)
        assert len(page2) == 2

        # Get last page
        page3 = repo.get_all_findings(limit=2, offset=4)
        assert len(page3) == 1

    def test_count_findings_empty(self):
        """Test counting findings when repository is empty."""
        repo = InMemoryFindingRepository()
        count = repo.count_findings()
        assert count == 0

    def test_count_findings_total(self):
        """Test counting all findings."""
        repo = InMemoryFindingRepository()
        doc_id = uuid4()

        for i in range(3):
            finding = Finding.create(
                document_id=doc_id,
                finding_type=FindingType.SSN,
                location=f"page {i}",
            )
            repo.store_finding(finding)

        count = repo.count_findings()
        assert count == 3

    def test_count_findings_by_document(self):
        """Test counting findings for a specific document."""
        repo = InMemoryFindingRepository()
        doc_id1 = uuid4()
        doc_id2 = uuid4()

        # Add 2 findings for doc1
        for i in range(2):
            finding = Finding.create(
                document_id=doc_id1,
                finding_type=FindingType.SSN,
                location=f"page {i}",
            )
            repo.store_finding(finding)

        # Add 3 findings for doc2
        for i in range(3):
            finding = Finding.create(
                document_id=doc_id2,
                finding_type=FindingType.EMAIL,
                location=f"page {i}",
            )
            repo.store_finding(finding)

        count_doc1 = repo.count_findings(document_id=doc_id1)
        count_doc2 = repo.count_findings(document_id=doc_id2)
        count_total = repo.count_findings()

        assert count_doc1 == 2
        assert count_doc2 == 3
        assert count_total == 5

    def test_count_findings_for_nonexistent_document(self):
        """Test counting findings for a document with no findings."""
        repo = InMemoryFindingRepository()
        doc_id = UUID("123e4567-e89b-12d3-a456-426614174000")

        count = repo.count_findings(document_id=doc_id)
        assert count == 0

