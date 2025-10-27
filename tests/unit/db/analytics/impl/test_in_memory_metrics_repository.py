"""Tests for InMemoryMetricsRepository."""

import pytest
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

from pdf_scan.db.analytics.impl import InMemoryMetricsRepository
from pdf_scan.models import Metric


class TestInMemoryMetricsRepository:
    """Test suite for InMemoryMetricsRepository."""

    @pytest.mark.asyncio
    async def test_store_and_get_metric(self):
        """Test storing and retrieving a metric."""
        repo = InMemoryMetricsRepository()
        metric = Metric.create(operation="upload", duration_ms=123.45)

        await repo.store_metric(metric)
        metrics = await repo.get_metrics()

        assert len(metrics) == 1
        assert metrics[0].operation == "upload"
        assert metrics[0].duration_ms == 123.45

    @pytest.mark.asyncio
    async def test_get_metrics_empty(self):
        """Test getting metrics when repository is empty."""
        repo = InMemoryMetricsRepository()
        metrics = await repo.get_metrics()
        assert metrics == []

    @pytest.mark.asyncio
    async def test_get_metrics_sorted_by_timestamp(self):
        """Test that metrics are sorted by timestamp descending."""
        repo = InMemoryMetricsRepository()

        # Create metrics with specific timestamps
        now = datetime.now(UTC)
        metric1 = Metric(
            id=uuid4(),
            operation="upload",
            duration_ms=100.0,
            timestamp=now - timedelta(hours=2),
        )
        metric2 = Metric(
            id=uuid4(),
            operation="scan",
            duration_ms=200.0,
            timestamp=now - timedelta(hours=1),
        )
        metric3 = Metric(
            id=uuid4(),
            operation="upload",
            duration_ms=150.0,
            timestamp=now,
        )

        await repo.store_metric(metric1)
        await repo.store_metric(metric2)
        await repo.store_metric(metric3)

        metrics = await repo.get_metrics()

        # Should be sorted by timestamp descending (most recent first)
        assert len(metrics) == 3
        assert metrics[0].timestamp == now
        assert metrics[1].timestamp == now - timedelta(hours=1)
        assert metrics[2].timestamp == now - timedelta(hours=2)

    @pytest.mark.asyncio
    async def test_get_metrics_filter_by_operation(self):
        """Test filtering metrics by operation type."""
        repo = InMemoryMetricsRepository()

        metric1 = Metric.create(operation="upload", duration_ms=100.0)
        metric2 = Metric.create(operation="scan", duration_ms=200.0)
        metric3 = Metric.create(operation="upload", duration_ms=150.0)

        await repo.store_metric(metric1)
        await repo.store_metric(metric2)
        await repo.store_metric(metric3)

        upload_metrics = await repo.get_metrics(operation="upload")
        scan_metrics = await repo.get_metrics(operation="scan")

        assert len(upload_metrics) == 2
        assert len(scan_metrics) == 1
        assert all(m.operation == "upload" for m in upload_metrics)
        assert all(m.operation == "scan" for m in scan_metrics)

    @pytest.mark.asyncio
    async def test_get_metrics_filter_by_document_id(self):
        """Test filtering metrics by document ID."""
        repo = InMemoryMetricsRepository()
        doc_id1 = uuid4()
        doc_id2 = uuid4()

        metric1 = Metric.create(
            operation="scan", duration_ms=100.0, document_id=doc_id1
        )
        metric2 = Metric.create(
            operation="scan", duration_ms=200.0, document_id=doc_id2
        )
        metric3 = Metric.create(
            operation="scan", duration_ms=150.0, document_id=doc_id1
        )

        await repo.store_metric(metric1)
        await repo.store_metric(metric2)
        await repo.store_metric(metric3)

        doc1_metrics = await repo.get_metrics(document_id=doc_id1)
        doc2_metrics = await repo.get_metrics(document_id=doc_id2)

        assert len(doc1_metrics) == 2
        assert len(doc2_metrics) == 1

    @pytest.mark.asyncio
    async def test_get_metrics_filter_by_time_range(self):
        """Test filtering metrics by time range."""
        repo = InMemoryMetricsRepository()
        now = datetime.now(UTC)

        # Create metrics with different timestamps
        metric1 = Metric(
            id=uuid4(),
            operation="upload",
            duration_ms=100.0,
            timestamp=now - timedelta(days=3),
        )
        metric2 = Metric(
            id=uuid4(),
            operation="upload",
            duration_ms=200.0,
            timestamp=now - timedelta(days=2),
        )
        metric3 = Metric(
            id=uuid4(),
            operation="upload",
            duration_ms=150.0,
            timestamp=now - timedelta(days=1),
        )

        await repo.store_metric(metric1)
        await repo.store_metric(metric2)
        await repo.store_metric(metric3)

        # Get metrics from last 2.5 days
        start_time = now - timedelta(days=2, hours=12)
        metrics = await repo.get_metrics(start_time=start_time)

        assert len(metrics) == 2
        assert all(m.timestamp >= start_time for m in metrics)

    @pytest.mark.asyncio
    async def test_get_metrics_filter_by_start_and_end_time(self):
        """Test filtering metrics by both start and end time."""
        repo = InMemoryMetricsRepository()
        now = datetime.now(UTC)

        # Create metrics spanning 5 days
        for i in range(5):
            metric = Metric(
                id=uuid4(),
                operation="upload",
                duration_ms=100.0 + i,
                timestamp=now - timedelta(days=i),
            )
            await repo.store_metric(metric)

        # Get metrics from 3 days ago to 1 day ago
        start_time = now - timedelta(days=3)
        end_time = now - timedelta(days=1)
        metrics = await repo.get_metrics(start_time=start_time, end_time=end_time)

        assert len(metrics) == 3
        assert all(start_time <= m.timestamp <= end_time for m in metrics)

    @pytest.mark.asyncio
    async def test_get_metrics_with_pagination(self):
        """Test paginating metrics."""
        repo = InMemoryMetricsRepository()

        # Create 5 metrics
        for i in range(5):
            metric = Metric.create(operation="upload", duration_ms=100.0 + i)
            await repo.store_metric(metric)

        # Get first 2
        page1 = await repo.get_metrics(limit=2, offset=0)
        assert len(page1) == 2

        # Get next 2
        page2 = await repo.get_metrics(limit=2, offset=2)
        assert len(page2) == 2

        # Get last page
        page3 = await repo.get_metrics(limit=2, offset=4)
        assert len(page3) == 1

    @pytest.mark.asyncio
    async def test_get_metrics_combined_filters(self):
        """Test combining multiple filters."""
        repo = InMemoryMetricsRepository()
        now = datetime.now(UTC)
        doc_id = uuid4()

        # Create various metrics
        metric1 = Metric(
            id=uuid4(),
            operation="upload",
            duration_ms=100.0,
            timestamp=now - timedelta(hours=2),
            document_id=doc_id,
        )
        metric2 = Metric(
            id=uuid4(),
            operation="scan",
            duration_ms=200.0,
            timestamp=now - timedelta(hours=1),
            document_id=doc_id,
        )
        metric3 = Metric(
            id=uuid4(),
            operation="upload",
            duration_ms=150.0,
            timestamp=now,
            document_id=doc_id,
        )

        await repo.store_metric(metric1)
        await repo.store_metric(metric2)
        await repo.store_metric(metric3)

        # Filter by operation and document_id
        metrics = await repo.get_metrics(operation="upload", document_id=doc_id)
        assert len(metrics) == 2
        assert all(m.operation == "upload" for m in metrics)
        assert all(m.document_id == doc_id for m in metrics)

    @pytest.mark.asyncio
    async def test_get_average_duration_empty(self):
        """Test average duration when no metrics exist."""
        repo = InMemoryMetricsRepository()
        avg = await repo.get_average_duration(operation="upload")
        assert avg == 0.0

    @pytest.mark.asyncio
    async def test_get_average_duration_single_metric(self):
        """Test average duration with a single metric."""
        repo = InMemoryMetricsRepository()
        metric = Metric.create(operation="upload", duration_ms=123.45)
        await repo.store_metric(metric)

        avg = await repo.get_average_duration(operation="upload")
        assert avg == 123.45

    @pytest.mark.asyncio
    async def test_get_average_duration_multiple_metrics(self):
        """Test average duration with multiple metrics."""
        repo = InMemoryMetricsRepository()

        metric1 = Metric.create(operation="upload", duration_ms=100.0)
        metric2 = Metric.create(operation="upload", duration_ms=200.0)
        metric3 = Metric.create(operation="upload", duration_ms=150.0)

        await repo.store_metric(metric1)
        await repo.store_metric(metric2)
        await repo.store_metric(metric3)

        avg = await repo.get_average_duration(operation="upload")
        assert avg == 150.0  # (100 + 200 + 150) / 3

    @pytest.mark.asyncio
    async def test_get_average_duration_filters_by_operation(self):
        """Test that average duration only includes specified operation."""
        repo = InMemoryMetricsRepository()

        metric1 = Metric.create(operation="upload", duration_ms=100.0)
        metric2 = Metric.create(operation="scan", duration_ms=500.0)
        metric3 = Metric.create(operation="upload", duration_ms=200.0)

        await repo.store_metric(metric1)
        await repo.store_metric(metric2)
        await repo.store_metric(metric3)

        upload_avg = await repo.get_average_duration(operation="upload")
        scan_avg = await repo.get_average_duration(operation="scan")

        assert upload_avg == 150.0  # (100 + 200) / 2
        assert scan_avg == 500.0

    @pytest.mark.asyncio
    async def test_get_average_duration_with_time_range(self):
        """Test average duration filtered by time range."""
        repo = InMemoryMetricsRepository()
        now = datetime.now(UTC)

        metric1 = Metric(
            id=uuid4(),
            operation="upload",
            duration_ms=100.0,
            timestamp=now - timedelta(days=3),
        )
        metric2 = Metric(
            id=uuid4(),
            operation="upload",
            duration_ms=200.0,
            timestamp=now - timedelta(days=2),
        )
        metric3 = Metric(
            id=uuid4(),
            operation="upload",
            duration_ms=300.0,
            timestamp=now - timedelta(days=1),
        )

        await repo.store_metric(metric1)
        await repo.store_metric(metric2)
        await repo.store_metric(metric3)

        # Get average for last 2.5 days
        start_time = now - timedelta(days=2, hours=12)
        avg = await repo.get_average_duration(operation="upload", start_time=start_time)

        # Should only include metric2 and metric3
        assert avg == 250.0  # (200 + 300) / 2

    @pytest.mark.asyncio
    async def test_get_average_duration_no_matching_operation(self):
        """Test average duration when operation doesn't match any metrics."""
        repo = InMemoryMetricsRepository()
        metric = Metric.create(operation="upload", duration_ms=100.0)
        await repo.store_metric(metric)

        avg = await repo.get_average_duration(operation="nonexistent")
        assert avg == 0.0

