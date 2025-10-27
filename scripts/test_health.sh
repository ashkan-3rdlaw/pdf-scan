#!/bin/bash
# Test the health endpoint

echo "Testing /health endpoint..."
echo ""

curl -X GET "http://localhost:8000/health" \
  -H "accept: application/json" \
  -w "\n\nHTTP Status: %{http_code}\n" \
  -s | jq '.'

echo ""

