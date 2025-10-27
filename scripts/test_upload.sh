#!/bin/bash
# Test the upload endpoint with a sample PDF

# Default to the sample PDF with PII in tests/fixtures
DEFAULT_PDF="tests/fixtures/sample_with_pii.pdf"
PDF_FILE="${1:-$DEFAULT_PDF}"

if [ ! -f "$PDF_FILE" ]; then
    echo "Error: File '$PDF_FILE' not found"
    exit 1
fi

echo "Testing /upload endpoint with file: $PDF_FILE"
echo ""

curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -F "file=@$PDF_FILE" \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -s | jq '.'

echo ""

