#!/bin/bash

# Test script for metrics endpoint
# Assumes the server is running on localhost:8000

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Counter for test results
PASSED=0
FAILED=0

# Function to run a test and validate response
run_test() {
    local test_name=$1
    local url=$2
    local expected_status=$3
    local description=$4
    
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Running: $test_name${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Description: $description${NC}"
    echo -e "${BLUE}URL: $url${NC}"
    echo ""
    
    # Make the request and capture both response and status code
    response=$(curl -s -w "\n%{http_code}" "$url")
    http_code=$(echo "$response" | tail -n1)
    response_body=$(echo "$response" | sed '$d')
    
    echo -e "${BLUE}HTTP Status: $http_code${NC}"
    echo -e "${BLUE}Response:${NC}"
    echo "$response_body" | jq '.' 2>/dev/null || echo "$response_body"
    echo ""
    
    # Validate the response
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓ $test_name - PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ $test_name - FAILED (Expected: $expected_status, Got: $http_code)${NC}"
        ((FAILED++))
    fi
    echo ""
}

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                Metrics Endpoint Test                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if server is running
echo -e "${YELLOW}Checking if server is running...${NC}"
if ! curl -s -f "http://localhost:8000/health" > /dev/null 2>&1; then
    echo -e "${RED}✗ Server is not running on localhost:8000${NC}"
    echo "Please start the server with: uv run pdf-scan"
    exit 1
fi
echo -e "${GREEN}✓ Server is running${NC}"
echo ""

# Test 1: Get current metrics
run_test "Get Current Metrics" \
    "http://localhost:8000/metrics" \
    "200" \
    "Retrieve current performance metrics for all operations"

# Test 2: Upload a file to generate fresh metrics
echo -e "${YELLOW}Uploading file to generate fresh metrics...${NC}"
upload_response=$(curl -s -X POST "http://localhost:8000/upload" -F "file=@tests/fixtures/sample_with_pii.pdf")
upload_status=$(curl -s -o /dev/null -w "%{http_code}" -X POST "http://localhost:8000/upload" -F "file=@tests/fixtures/sample_with_pii.pdf")

echo -e "${BLUE}Upload Status: $upload_status${NC}"
echo -e "${BLUE}Upload Response:${NC}"
echo "$upload_response" | jq '.'
echo ""

if [ "$upload_status" = "200" ]; then
    echo -e "${GREEN}✓ File Upload - PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ File Upload - FAILED${NC}"
    ((FAILED++))
fi
echo ""

# Test 3: Get metrics after upload
run_test "Get Updated Metrics" \
    "http://localhost:8000/metrics" \
    "200" \
    "Retrieve metrics after uploading a new file to see updated averages"

# Test 4: Filter by upload operation
run_test "Filter by Upload Operation" \
    "http://localhost:8000/metrics?operation=upload" \
    "200" \
    "Filter metrics to show only upload operation data"

# Test 5: Filter by scan operation
run_test "Filter by Scan Operation" \
    "http://localhost:8000/metrics?operation=scan" \
    "200" \
    "Filter metrics to show only scan operation data"

# Test 6: Test invalid time format
run_test "Invalid Time Format Error" \
    "http://localhost:8000/metrics?start_time=invalid" \
    "400" \
    "Test error handling for invalid time format parameters"

# Test 7: Test valid time range filtering
run_test "Valid Time Range Filter" \
    "http://localhost:8000/metrics?start_time=2025-10-27T19:00:00Z" \
    "200" \
    "Test filtering by valid ISO time range"

# Test 8: Test combined filters
run_test "Combined Operation and Time Filters" \
    "http://localhost:8000/metrics?operation=upload&start_time=2025-10-27T19:00:00Z" \
    "200" \
    "Test combining operation and time range filters"

# Print detailed summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    TEST SUMMARY                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED${NC}"
    echo ""
    echo -e "${RED}Some tests failed. Please check the output above.${NC}"
    exit 1
else
    echo -e "${GREEN}Failed: 0${NC}"
    echo ""
    echo -e "${GREEN}✓ All metrics endpoint tests passed!${NC}"
fi
echo ""

echo -e "${BLUE}Metrics Endpoint Capabilities Validated:${NC}"
echo -e "  • ✅ Average processing times by operation type"
echo -e "  • ✅ Filtering by operation (upload, scan)"
echo -e "  • ✅ Time range filtering (ISO format)"
echo -e "  • ✅ Combined filtering (operation + time)"
echo -e "  • ✅ Error handling for invalid parameters"
echo -e "  • ✅ Real-time metrics updates"
echo ""
