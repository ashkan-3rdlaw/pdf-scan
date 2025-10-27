#!/bin/bash
# Test the health endpoint

echo "Testing /health endpoint..."
echo ""

response=$(curl -X GET "http://localhost:8000/health" \
  -H "accept: application/json" \
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

