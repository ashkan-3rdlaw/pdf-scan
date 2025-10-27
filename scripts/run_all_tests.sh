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

# Show usage if help requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [--cloud|-c] [service-url]"
    echo ""
    echo "Options:"
    echo "  --cloud, -c    Include cloud deployment test"
    echo "  service-url    URL of deployed service (for cloud test)"
    echo "  --help, -h     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run local tests only"
    echo "  $0 --cloud            # Run local + cloud tests (default URL)"
    echo "  $0 --cloud https://my-service.onrender.com  # Run local + cloud tests"
    echo ""
    exit 0
fi

# Check if server is running (skip for cloud-only mode)
if [ "$1" != "--cloud-only" ]; then
    echo -e "${YELLOW}Checking if server is running...${NC}"
    if ! curl -s -f "http://localhost:8000/health" > /dev/null 2>&1; then
        echo -e "${RED}✗ Server is not running on localhost:8000${NC}"
        echo "Please start the server with: uv run pdf-scan"
        echo ""
        echo "Or run cloud tests only with: $0 --cloud-only"
        exit 1
    fi
    echo -e "${GREEN}✓ Server is running${NC}"
fi
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

# Run metrics test as the final test
run_test "test_metrics.sh" "Metrics Endpoint Test"

# Optional: Cloud deployment test
if [ "$1" = "--cloud" ] || [ "$1" = "-c" ]; then
    echo ""
    echo -e "${YELLOW}🌐 Running cloud deployment test...${NC}"
    echo -e "${YELLOW}Note: This requires a deployed service URL${NC}"
    echo ""
    
    # Check if service URL provided
    if [ -n "$2" ]; then
        SERVICE_URL="$2"
    else
        SERVICE_URL="https://pdf-scan-service.onrender.com"
        echo -e "${YELLOW}Using default service URL: $SERVICE_URL${NC}"
        echo -e "${YELLOW}To test a different service, use: $0 --cloud <service-url>${NC}"
    fi
    
    echo ""
    run_test "test_cloud_deployment.sh $SERVICE_URL" "Cloud Deployment Test"
fi

# Print summary
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                    TEST SUMMARY                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ "$1" = "--cloud" ] || [ "$1" = "-c" ]; then
    echo -e "Total Tests: $((PASSED + FAILED)) (9 test scripts including cloud test)"
else
    echo -e "Total Tests: $((PASSED + FAILED)) (8 test scripts)"
fi
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

