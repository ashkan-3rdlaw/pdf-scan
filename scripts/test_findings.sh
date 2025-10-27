#!/bin/bash

# Test script for findings endpoints
# Assumes server is running on localhost:8000

set -e

echo "=== Testing Findings Endpoints ==="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "Step 1: Upload a PDF with PII..."
upload_response=$(curl -s -X POST \
  -F "file=@tests/fixtures/sample_with_pii.pdf" \
  -w "\n%{http_code}" \
  http://localhost:8000/upload)

http_code=$(echo "$upload_response" | tail -n1)
response_body=$(echo "$upload_response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Upload successful${NC}"
    echo "$response_body" | jq '.'
    
    # Extract document ID
    document_id=$(echo "$response_body" | jq -r '.document_id')
    echo ""
    echo -e "${YELLOW}Document ID: $document_id${NC}"
    echo ""
else
    echo "✗ Upload failed with HTTP $http_code"
    echo "$response_body" | jq '.'
    exit 1
fi

echo "---"
echo ""

echo "Step 2: Get findings for the uploaded document..."
findings_response=$(curl -s -X GET \
  -H "accept: application/json" \
  -w "\n%{http_code}" \
  "http://localhost:8000/findings/$document_id")

http_code=$(echo "$findings_response" | tail -n1)
response_body=$(echo "$findings_response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Get findings successful${NC}"
    echo "$response_body" | jq '.'
    
    # Count findings
    findings_count=$(echo "$response_body" | jq '.findings | length')
    echo ""
    echo -e "${YELLOW}Found $findings_count findings${NC}"
else
    echo "✗ Get findings failed with HTTP $http_code"
    echo "$response_body" | jq '.'
    exit 1
fi

echo ""
echo "---"
echo ""

echo "Step 3: Get all findings (paginated)..."
all_findings_response=$(curl -s -X GET \
  -H "accept: application/json" \
  -w "\n%{http_code}" \
  "http://localhost:8000/findings?limit=10&offset=0")

http_code=$(echo "$all_findings_response" | tail -n1)
response_body=$(echo "$all_findings_response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Get all findings successful${NC}"
    echo "$response_body" | jq '.'
    
    # Show pagination info
    total=$(echo "$response_body" | jq '.pagination.total')
    returned=$(echo "$response_body" | jq '.pagination.returned')
    echo ""
    echo -e "${YELLOW}Total findings in system: $total${NC}"
    echo -e "${YELLOW}Returned in this page: $returned${NC}"
else
    echo "✗ Get all findings failed with HTTP $http_code"
    echo "$response_body" | jq '.'
    exit 1
fi

echo ""
echo "---"
echo ""

echo "Step 4: Get findings filtered by type (SSN)..."
filtered_response=$(curl -s -X GET \
  -H "accept: application/json" \
  -w "\n%{http_code}" \
  "http://localhost:8000/findings?finding_type=ssn&limit=5")

http_code=$(echo "$filtered_response" | tail -n1)
response_body=$(echo "$filtered_response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo -e "${GREEN}✓ Filtered findings successful${NC}"
    echo "$response_body" | jq '.'
    
    ssn_count=$(echo "$response_body" | jq '.pagination.returned')
    echo ""
    echo -e "${YELLOW}Found $ssn_count SSN findings${NC}"
else
    echo "✗ Filtered findings failed with HTTP $http_code"
    echo "$response_body" | jq '.'
    exit 1
fi

echo ""
echo "---"
echo ""

echo "Step 5: Test 404 for non-existent document..."
fake_uuid="12345678-1234-5678-1234-567812345678"
not_found_response=$(curl -s -X GET \
  -H "accept: application/json" \
  -w "\n%{http_code}" \
  "http://localhost:8000/findings/$fake_uuid")

http_code=$(echo "$not_found_response" | tail -n1)
response_body=$(echo "$not_found_response" | sed '$d')

if [ "$http_code" = "404" ]; then
    echo -e "${GREEN}✓ 404 error correctly returned${NC}"
    echo "$response_body" | jq '.'
else
    echo "✗ Expected HTTP 404 but got $http_code"
    echo "$response_body" | jq '.'
    exit 1
fi

echo ""
echo "=== All findings endpoint tests passed! ==="

