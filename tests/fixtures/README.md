# Test Fixtures

This directory contains test files for the PDF scan service.

## Files

### sample_with_pii.pdf

A minimal valid PDF document containing PII (Personally Identifiable Information) for testing scanner functionality.

**Contents:**
- Text: "Sample PDF for Testing"
- SSN pattern: `123-45-6789`
- Email pattern: `test@example.com`

**Specifications:**
- PDF version: 1.4
- Pages: 1
- Size: ~715 bytes
- Font: Helvetica

**Usage:**
- Used by default in `scripts/test_upload.sh`
- Primary test file for scanner validation (Phase 4)
- Tests detection of sensitive data patterns

---

### sample_without_pii.pdf

A minimal valid PDF document without any PII for testing clean documents.

**Contents:**
- Text: "Sample PDF Without PII"
- Generic content without sensitive information

**Specifications:**
- PDF version: 1.4
- Pages: 1
- Size: ~695 bytes
- Font: Helvetica

**Usage:**
- Testing documents that should have zero findings
- Negative test cases for scanner
- Validation baseline testing

---

## Adding New Test Files

When adding new test PDFs:
1. Keep files small (< 1MB preferred)
2. Document the contents and purpose
3. Use descriptive naming: `*_with_pii.pdf` or `*_without_pii.pdf`
4. Specify what PII patterns are included (SSN, email, phone, etc.)
5. Name files descriptively (e.g., `multi_page_with_pii.pdf`, `scanned_document.pdf`)

