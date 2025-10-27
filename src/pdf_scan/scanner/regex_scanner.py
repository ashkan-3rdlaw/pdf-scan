"""Regex-based PDF scanner implementation."""

import re
from pathlib import Path
from typing import List, Union
from uuid import uuid4

from pypdf import PdfReader

from pdf_scan.models import Finding, FindingType

from .pdf_scanner_interface import PDFScannerInterface


class RegexPDFScanner(PDFScannerInterface):
    """
    PDF scanner that uses regex patterns to detect sensitive information.
    
    Currently supports:
    - SSN: xxx-xx-xxxx format
    - Email addresses: contains @ and ends with .domain
    """

    # Regex patterns for sensitive data detection
    PATTERNS = {
        FindingType.SSN: re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        FindingType.EMAIL: re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        ),
    }

    def scan_pdf(self, file_path: Union[str, Path]) -> List[Finding]:
        """
        Scan a PDF file for sensitive information using regex patterns.
        
        Args:
            file_path: Path to the PDF file to scan
            
        Returns:
            List of Finding objects representing sensitive data detected
            
        Raises:
            FileNotFoundError: If the PDF file does not exist
            ValueError: If the file is not a valid PDF
            RuntimeError: If PDF processing fails (corrupt, password-protected, etc.)
        """
        # Convert to Path object for easier handling
        pdf_path = Path(file_path)
        
        # Check if file exists
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        # Extract text and scan for patterns
        findings: List[Finding] = []
        
        try:
            reader = PdfReader(pdf_path)
            
            # Check if PDF is encrypted/password-protected
            if reader.is_encrypted:
                raise RuntimeError("PDF is password-protected and cannot be scanned")
            
            # Process each page
            for page_num, page in enumerate(reader.pages, start=1):
                try:
                    # Extract text from the page
                    text = page.extract_text()
                    
                    if not text:
                        continue
                    
                    # Search for each pattern type
                    for finding_type, pattern in self.PATTERNS.items():
                        matches = pattern.finditer(text)
                        
                        for match in matches:
                            # Create a finding for each match
                            # Note: content is intentionally not stored for security
                            finding = Finding.create(
                                document_id=uuid4(),  # Will be updated by caller with actual document ID
                                finding_type=finding_type,
                                location=f"page {page_num}",
                                confidence=1.0,  # Regex matches have 100% confidence
                            )
                            findings.append(finding)
                
                except Exception as e:
                    # If a specific page fails, continue with other pages
                    # but note this in a way that could be logged
                    continue
            
            return findings
        
        except FileNotFoundError:
            # Re-raise as-is
            raise
        
        except RuntimeError:
            # Re-raise password-protected error as-is
            raise
        
        except Exception as e:
            # Catch all other errors (corrupt PDFs, invalid format, etc.)
            error_msg = str(e)
            if "EOF marker not found" in error_msg or "PDF" in error_msg.upper():
                raise ValueError(f"Invalid or corrupt PDF file: {file_path}")
            raise RuntimeError(f"Failed to process PDF: {error_msg}")

    def get_supported_patterns(self) -> List[str]:
        """
        Get list of sensitive data patterns this scanner can detect.
        
        Returns:
            List of pattern names (e.g., ["SSN", "EMAIL"])
        """
        return [pattern_type.value for pattern_type in self.PATTERNS.keys()]

