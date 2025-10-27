"""Tests for Backends class."""

from pdf_scan.db import BackendFactory, Backends


class TestBackends:
    """Test suite for Backends class."""

    def test_create_backends(self):
        """Test creating backends via factory."""
        backends = BackendFactory.create_backends(backend="memory")
        
        assert backends is not None
        assert backends.document is not None
        assert backends.finding is not None
        assert backends.metrics is not None
        assert backends.scanner is not None
        
        # Verify they have the expected methods
        assert hasattr(backends.document, 'store_document')
        assert hasattr(backends.finding, 'store_finding')
        assert hasattr(backends.metrics, 'store_metric')
        assert hasattr(backends.scanner, 'scan_pdf')

    def test_backends_contains_all_dependencies(self):
        """Test that backends contains all required dependencies."""
        backends = BackendFactory.create_backends(backend="memory")
        
        assert hasattr(backends, 'document')
        assert hasattr(backends, 'finding')
        assert hasattr(backends, 'metrics')
        assert hasattr(backends, 'scanner')

    def test_backends_repr(self):
        """Test string representation of backends."""
        backends = BackendFactory.create_backends(backend="memory")
        repr_str = repr(backends)
        
        assert "Backends(" in repr_str
        assert "InMemoryDocumentRepository" in repr_str
        assert "InMemoryFindingRepository" in repr_str
        assert "InMemoryMetricsRepository" in repr_str
        assert "RegexPDFScanner" in repr_str

    def test_backends_are_different_instances(self):
        """Test that different backend instances are created."""
        backends1 = BackendFactory.create_backends(backend="memory")
        backends2 = BackendFactory.create_backends(backend="memory")
        
        assert backends1 is not backends2
        assert backends1.document is not backends2.document
        assert backends1.finding is not backends2.finding
        assert backends1.metrics is not backends2.metrics
        assert backends1.scanner is not backends2.scanner

    def test_backends_attributes(self):
        """Test that backends have the expected attributes."""
        backends = BackendFactory.create_backends(backend="memory")
        
        # Test attribute access
        assert hasattr(backends, 'document')
        assert hasattr(backends, 'finding')
        assert hasattr(backends, 'metrics')
        assert hasattr(backends, 'scanner')
        
        # Test that attributes are repositories/scanner
        assert 'Repository' in type(backends.document).__name__
        assert 'Repository' in type(backends.finding).__name__
        assert 'Repository' in type(backends.metrics).__name__
        assert 'Scanner' in type(backends.scanner).__name__

    def test_backends_are_in_memory_implementations(self):
        """Test that backends use in-memory implementations and regex scanner."""
        backends = BackendFactory.create_backends(backend="memory")
        
        assert 'InMemory' in type(backends.document).__name__
        assert 'InMemory' in type(backends.finding).__name__
        assert 'InMemory' in type(backends.metrics).__name__
        assert 'Regex' in type(backends.scanner).__name__

