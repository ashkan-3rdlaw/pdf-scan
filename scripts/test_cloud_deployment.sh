#!/bin/bash

# PDF Scan Service - Cloud Deployment Testing Script
# Tests the service deployed on Render.com

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVICE_URL="${1:-https://pdf-scan-service.onrender.com}"
TEST_PDF_WITH_PII="tests/fixtures/sample_with_pii.pdf"
TEST_PDF_WITHOUT_PII="tests/fixtures/sample_without_pii.pdf"

echo -e "${BLUE}🚀 PDF Scan Service - Cloud Deployment Testing${NC}"
echo -e "${BLUE}Service URL: ${SERVICE_URL}${NC}"
echo ""

# Function to test endpoint
test_endpoint() {
    local endpoint="$1"
    local description="$2"
    local expected_status="${3:-200}"
    
    echo -e "${YELLOW}Testing ${description}...${NC}"
    
    response=$(curl -s -w "\n%{http_code}" "${SERVICE_URL}${endpoint}")
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ ${description} - Status: ${status_code}${NC}"
        echo "Response: $body"
    else
        echo -e "${RED}❌ ${description} - Expected: ${expected_status}, Got: ${status_code}${NC}"
        echo "Response: $body"
        return 1
    fi
    echo ""
}

# Function to test file upload
test_upload() {
    local file_path="$1"
    local description="$2"
    
    echo -e "${YELLOW}Testing ${description}...${NC}"
    
    if [ ! -f "$file_path" ]; then
        echo -e "${RED}❌ Test file not found: ${file_path}${NC}"
        return 1
    fi
    
    response=$(curl -s -w "\n%{http_code}" -X POST -F "file=@${file_path}" "${SERVICE_URL}/upload")
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" = "200" ]; then
        echo -e "${GREEN}✅ ${description} - Status: ${status_code}${NC}"
        echo "Response: $body"
        
        # Extract document_id for further testing
        document_id=$(echo "$body" | grep -o '"document_id":"[^"]*"' | cut -d'"' -f4)
        if [ -n "$document_id" ]; then
            echo "Document ID: $document_id"
            export LAST_DOCUMENT_ID="$document_id"
        fi
    else
        echo -e "${RED}❌ ${description} - Expected: 200, Got: ${status_code}${NC}"
        echo "Response: $body"
        return 1
    fi
    echo ""
}

# Function to test findings endpoint
test_findings() {
    local document_id="$1"
    local description="$2"
    
    echo -e "${YELLOW}Testing ${description}...${NC}"
    
    response=$(curl -s -w "\n%{http_code}" "${SERVICE_URL}/findings/${document_id}")
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status_code" = "200" ]; then
        echo -e "${GREEN}✅ ${description} - Status: ${status_code}${NC}"
        echo "Response: $body"
    else
        echo -e "${RED}❌ ${description} - Expected: 200, Got: ${status_code}${NC}"
        echo "Response: $body"
        return 1
    fi
    echo ""
}

# Main testing sequence
echo -e "${BLUE}Starting comprehensive cloud deployment tests...${NC}"
echo ""

# Test 1: Health Check
test_endpoint "/health" "Health Check"

# Test 2: Upload PDF without PII
test_upload "$TEST_PDF_WITHOUT_PII" "Upload PDF without PII"
clean_doc_id="$LAST_DOCUMENT_ID"

# Test 3: Upload PDF with PII
test_upload "$TEST_PDF_WITH_PII" "Upload PDF with PII"
pii_doc_id="$LAST_DOCUMENT_ID"

# Test 4: Get findings for clean document
if [ -n "$clean_doc_id" ]; then
    test_findings "$clean_doc_id" "Get findings for clean document"
fi

# Test 5: Get findings for PII document
if [ -n "$pii_doc_id" ]; then
    test_findings "$pii_doc_id" "Get findings for PII document"
fi

# Test 6: Get all findings
test_endpoint "/findings" "Get all findings"

# Test 7: Get metrics
test_endpoint "/metrics" "Get metrics"

# Test 8: Test pagination
test_endpoint "/findings?limit=5&offset=0" "Test pagination"

# Test 9: Test invalid document ID
test_endpoint "/findings/00000000-0000-0000-0000-000000000000" "Test invalid document ID" "404"

# Test 10: Test invalid file upload
echo -e "${YELLOW}Testing invalid file upload...${NC}"
response=$(curl -s -w "\n%{http_code}" -X POST -F "file=@README.md" "${SERVICE_URL}/upload")
status_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$status_code" = "400" ]; then
    echo -e "${GREEN}✅ Invalid file upload - Status: ${status_code}${NC}"
    echo "Response: $body"
else
    echo -e "${RED}❌ Invalid file upload - Expected: 400, Got: ${status_code}${NC}"
    echo "Response: $body"
fi
echo ""

# Summary
echo -e "${BLUE}🎉 Cloud deployment testing completed!${NC}"
echo ""
echo -e "${GREEN}Service is live at: ${SERVICE_URL}${NC}"
echo -e "${GREEN}API Documentation: ${SERVICE_URL}/docs${NC}"
echo -e "${GREEN}Alternative Docs: ${SERVICE_URL}/redoc${NC}"
echo ""
echo -e "${YELLOW}Note: Free tier services may sleep after 15 minutes of inactivity${NC}"
echo -e "${YELLOW}First request after sleep may take longer to respond${NC}"
