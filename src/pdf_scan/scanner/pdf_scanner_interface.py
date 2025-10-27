"""Abstract interface for PDF scanning."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union

from pdf_scan.models import Finding


class PDFScannerInterface(ABC):
    """
    Abstract base class for PDF scanning implementations.
    
    Implementations should scan PDF files for sensitive information
    and return structured findings.
    """

    @abstractmethod
    def scan_pdf(self, file_path: Union[str, Path]) -> List[Finding]:
        """
        Scan a PDF file for sensitive information.
        
        Args:
            file_path: Path to the PDF file to scan
            
        Returns:
            List of Finding objects representing sensitive data detected
            
        Raises:
            FileNotFoundError: If the PDF file does not exist
            ValueError: If the file is not a valid PDF
            RuntimeError: If PDF processing fails (corrupt, password-protected, etc.)
        """
        raise NotImplementedError

    @abstractmethod
    def get_supported_patterns(self) -> List[str]:
        """
        Get list of sensitive data patterns this scanner can detect.
        
        Returns:
            List of pattern names (e.g., ["SSN", "EMAIL", "CREDIT_CARD"])
        """
        raise NotImplementedError

