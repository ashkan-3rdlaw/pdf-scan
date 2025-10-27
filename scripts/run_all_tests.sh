#!/bin/bash

# Convenience script to run all manual test scripts
# Assumes the server is running on localhost:8000

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     PDF Scan Service - Manual Test Suite Runner           ║${NC}"
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

# Counter for test results
PASSED=0
FAILED=0

# Function to run a test script
run_test() {
    local script_name=$1
    local description=$2
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Running: ${description}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    
    if "$SCRIPT_DIR/$script_name"; then
        echo ""
        echo -e "${GREEN}✓ $description - PASSED${NC}"
        ((PASSED++))
    else
        echo ""
        echo -e "${RED}✗ $description - FAILED${NC}"
        ((FAILED++))
    fi
    echo ""
}

# Run all test scripts
run_test "test_health.sh" "Health Check Test"
run_test "test_upload.sh" "Standard Upload Test (with PII)"
run_test "quick_upload_test.sh" "Quick Upload Test"
run_test "test_upload_pii.sh" "Comprehensive Upload Test (with health checks)"
run_test "test_invalid_file.sh" "Invalid File Validation Tests"
run_test "test_findings.sh" "Findings Endpoints Test"

# Additional test with clean PDF
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Running: Upload Test (without PII)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
if "$SCRIPT_DIR/test_upload.sh" tests/fixtures/sample_without_pii.pdf; then
    echo ""
    echo -e "${GREEN}✓ Upload Test (without PII) - PASSED${NC}"
    ((PASSED++))
else
    echo ""
    echo -e "${RED}✗ Upload Test (without PII) - FAILED${NC}"
    ((FAILED++))
fi
echo ""

# Print summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    TEST SUMMARY                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Total Tests: $((PASSED + FAILED)) (7 test scripts)"
echo -e "${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED${NC}"
    echo ""
    echo -e "${RED}Some tests failed. Please check the output above.${NC}"
    exit 1
else
    echo -e "${GREEN}Failed: 0${NC}"
    echo ""
    echo -e "${GREEN}✓ All tests passed!${NC}"
fi
echo ""

