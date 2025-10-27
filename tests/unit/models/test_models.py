"""Tests for data models."""

from datetime import datetime
from uuid import UUID

from pdf_scan.models import (
    Document,
    DocumentStatus,
    Finding,
    FindingType,
    Metric,
)


def test_document_creation():
    """Test creating a document with the factory method."""
    doc = Document.create(filename="test.pdf", file_size=1024)

    assert isinstance(doc.id, UUID)
    assert doc.filename == "test.pdf"
    assert doc.file_size == 1024
    assert doc.status == DocumentStatus.PENDING
    assert isinstance(doc.upload_time, datetime)
    assert doc.error_message is None


def test_finding_creation():
    """Test creating a finding with the factory method."""
    doc_id = UUID("123e4567-e89b-12d3-a456-426614174000")
    finding = Finding.create(
        document_id=doc_id,
        finding_type=FindingType.SSN,
        location="page 2",
        confidence=0.95,
    )

    assert isinstance(finding.id, UUID)
    assert finding.document_id == doc_id
    assert finding.finding_type == FindingType.SSN
    assert finding.location == "page 2"
    assert finding.confidence == 0.95


def test_metric_creation():
    """Test creating a metric with the factory method."""
    metric = Metric.create(
        operation="upload",
        duration_ms=123.45,
        metadata={"file_size": 1024},
    )

    assert isinstance(metric.id, UUID)
    assert metric.operation == "upload"
    assert metric.duration_ms == 123.45
    assert isinstance(metric.timestamp, datetime)
    assert metric.document_id is None
    assert metric.metadata == {"file_size": 1024}


def test_metric_with_document_id():
    """Test creating a metric associated with a document."""
    doc_id = UUID("123e4567-e89b-12d3-a456-426614174000")
    metric = Metric.create(
        operation="scan",
        duration_ms=2500.0,
        document_id=doc_id,
    )

    assert metric.document_id == doc_id
    assert metric.operation == "scan"

