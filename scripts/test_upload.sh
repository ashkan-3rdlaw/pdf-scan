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

response=$(curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -F "file=@$PDF_FILE" \
  -w "\n%{http_code}" \
  -s)

# Split response and status code
http_code=$(echo "$response" | tail -n1)
json_body=$(echo "$response" | sed '$d')

# Pretty print JSON
echo "$json_body" | jq '.'
echo ""
echo "HTTP Status: $http_code"

echo ""

