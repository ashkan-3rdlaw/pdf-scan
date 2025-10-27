#!/bin/bash
# Test upload endpoint with invalid files to verify validation

echo "=== Testing Upload Endpoint Validation ==="
echo ""

# Test 1: Non-PDF file
echo "Test 1: Uploading a non-PDF file (.txt)..."
echo "test content" > /tmp/test.txt
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -F "file=@/tmp/test.txt" \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -s | jq '.'
rm /tmp/test.txt
echo ""
echo "---"
echo ""

# Test 2: Empty file
echo "Test 2: Uploading an empty PDF..."
touch /tmp/empty.pdf
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -F "file=@/tmp/empty.pdf" \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -s | jq '.'
rm /tmp/empty.pdf
echo ""
echo "---"
echo ""

# Test 3: No file
echo "Test 3: No file provided..."
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -s | jq '.'
echo ""
echo "---"
echo ""

# Test 4: Large file (if needed - creates 11MB file)
# Uncomment to test file size validation
# echo "Test 4: Uploading a file that's too large (>10MB)..."
# dd if=/dev/zero of=/tmp/large.pdf bs=1024 count=11264 2>/dev/null
# curl -X POST "http://localhost:8000/upload" \
#   -H "accept: application/json" \
#   -F "file=@/tmp/large.pdf" \
#   -w "\n\nHTTP Status: %{http_code}\n" \
#   -s | jq '.'
# rm /tmp/large.pdf
# echo ""

echo "=== Validation tests complete ==="

