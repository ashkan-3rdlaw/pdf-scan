#!/bin/bash

# Test script for uploading sample_with_pii.pdf to the PDF scan service
# Assumes the server is running on localhost:8000

set -e

# Configuration
SERVER_URL="http://localhost:8000"
PDF_FILE="tests/fixtures/sample_with_pii.pdf"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}PDF Scan Service - Upload Test${NC}"
echo "=================================="
echo "Server: $SERVER_URL"
echo "File: $PDF_FILE"
echo ""

# Check if PDF file exists
if [ ! -f "$PDF_FILE" ]; then
    echo -e "${RED}Error: PDF file not found at $PDF_FILE${NC}"
    echo "Please ensure the file exists and run this script from the project root."
    exit 1
fi

# Check if server is running
echo -e "${YELLOW}Checking server health...${NC}"
if ! curl -s -f "$SERVER_URL/health" > /dev/null; then
    echo -e "${RED}Error: Server is not running at $SERVER_URL${NC}"
    echo "Please start the server with: uv run pdf-scan"
    exit 1
fi

echo -e "${GREEN}✓ Server is running${NC}"
echo ""

# Upload the PDF
echo -e "${YELLOW}Uploading PDF...${NC}"
echo "File: $(basename "$PDF_FILE")"
echo "Size: $(ls -lh "$PDF_FILE" | awk '{print $5}')"
echo ""

# Perform the upload
response=$(curl -s -w "\n%{http_code}" \
    -X POST \
    -F "file=@$PDF_FILE" \
    "$SERVER_URL/upload")

# Split response and status code
http_code=$(echo "$response" | tail -n1)
response_body=$(echo "$response" | sed '$d')

echo "Response:"
echo "---------"

if [ "$http_code" -eq 200 ]; then
    echo -e "${GREEN}✓ Upload successful (HTTP $http_code)${NC}"
    echo ""
    echo "Response body:"
    echo "$response_body" | jq . 2>/dev/null || echo "$response_body"
    
    # Extract document ID for potential future use
    doc_id=$(echo "$response_body" | jq -r '.document_id' 2>/dev/null || echo "N/A")
    if [ "$doc_id" != "N/A" ] && [ "$doc_id" != "null" ]; then
        echo ""
        echo -e "${GREEN}Document ID: $doc_id${NC}"
        echo "You can use this ID to query findings in future endpoints."
    fi
else
    echo -e "${RED}✗ Upload failed (HTTP $http_code)${NC}"
    echo ""
    echo "Error response:"
    echo "$response_body" | jq . 2>/dev/null || echo "$response_body"
    exit 1
fi

echo ""
echo -e "${GREEN}Test completed successfully!${NC}"
echo ""
echo "Next steps:"
echo "- Check the server logs for any processing details"
echo "- In Phase 5, you'll be able to query findings for this document"
echo "- The document should now be stored in the in-memory database"
