#!/bin/bash

# Quick upload test script for sample_with_pii.pdf
# Usage: ./scripts/quick_upload_test.sh

echo "Uploading sample_with_pii.pdf..."
echo ""

curl -X POST \
  -F "file=@tests/fixtures/sample_with_pii.pdf" \
  http://localhost:8000/upload

echo ""
echo "Done!"
