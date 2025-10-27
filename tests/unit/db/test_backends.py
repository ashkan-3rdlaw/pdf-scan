"""Tests for Backends class."""

from pdf_scan.db import Backends


class TestBackends:
    """Test suite for Backends class."""

    def test_create_in_memory(self):
        """Test creating backends with in-memory implementations."""
        backends = Backends.create_in_memory()
        
        assert backends is not None
        assert backends.document is not None
        assert backends.finding is not None
        assert backends.metrics is not None
        
        # Verify they have the expected methods
        assert hasattr(backends.document, 'store_document')
        assert hasattr(backends.finding, 'store_finding')
        assert hasattr(backends.metrics, 'store_metric')

    def test_create_from_factory(self):
        """Test creating backends from factory."""
        backends = Backends.create_from_factory()
        
        assert backends is not None
        assert backends.document is not None
        assert backends.finding is not None
        assert backends.metrics is not None

    def test_backends_repr(self):
        """Test string representation of backends."""
        backends = Backends.create_in_memory()
        repr_str = repr(backends)
        
        assert "Backends(" in repr_str
        assert "InMemoryDocumentRepository" in repr_str
        assert "InMemoryFindingRepository" in repr_str
        assert "InMemoryMetricsRepository" in repr_str

    def test_backends_are_different_instances(self):
        """Test that different backend instances are created."""
        backends1 = Backends.create_in_memory()
        backends2 = Backends.create_in_memory()
        
        assert backends1 is not backends2
        assert backends1.document is not backends2.document
        assert backends1.finding is not backends2.finding
        assert backends1.metrics is not backends2.metrics

    def test_backends_attributes(self):
        """Test that backends have the expected attributes."""
        backends = Backends.create_in_memory()
        
        # Test attribute access
        assert hasattr(backends, 'document')
        assert hasattr(backends, 'finding')
        assert hasattr(backends, 'metrics')
        
        # Test that attributes are repositories
        assert 'Repository' in type(backends.document).__name__
        assert 'Repository' in type(backends.finding).__name__
        assert 'Repository' in type(backends.metrics).__name__

    def test_backends_are_in_memory_implementations(self):
        """Test that backends use in-memory implementations."""
        backends = Backends.create_in_memory()
        
        assert 'InMemory' in type(backends.document).__name__
        assert 'InMemory' in type(backends.finding).__name__
        assert 'InMemory' in type(backends.metrics).__name__

