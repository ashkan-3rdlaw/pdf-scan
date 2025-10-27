#!/bin/bash
# Test ClickHouse instance connectivity and health

echo "Testing ClickHouse instance..."
echo ""

# Test 1: HTTP interface availability
echo "1. Testing HTTP interface (port 8123)..."
response=$(curl -s -w "\n%{http_code}" "http://localhost:8123/")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | sed '$d')

if [ "$http_code" = "200" ]; then
    echo "✓ HTTP interface is up (port 8123)"
else
    echo "✗ HTTP interface is down (port 8123)"
    echo "  Status: $http_code"
    exit 1
fi
echo ""

# Test 2: Basic query execution
echo "2. Testing query execution..."
version=$(curl -s "http://localhost:8123/" --data "SELECT version()")
if [ -n "$version" ]; then
    echo "✓ Query execution works"
    echo "  ClickHouse version: $version"
else
    echo "✗ Query execution failed"
    exit 1
fi
echo ""

# Test 3: Database accessibility
echo "3. Testing pdf_scan database..."
db_check=$(curl -s "http://localhost:8123/" \
  --data "SELECT name FROM system.databases WHERE name = 'pdf_scan'" \
  -u "pdf_user:pdf_password")

if [ "$db_check" = "pdf_scan" ]; then
    echo "✓ Database 'pdf_scan' exists"
else
    echo "✗ Database 'pdf_scan' not found"
    echo "  Run: docker-compose up -d"
    exit 1
fi
echo ""

# Test 4: Tables check
echo "4. Checking tables..."
tables=$(curl -s "http://localhost:8123/" \
  --data "SELECT name FROM system.tables WHERE database = 'pdf_scan' ORDER BY name" \
  -u "pdf_user:pdf_password")

expected_tables=("documents" "findings" "metrics")
for table in "${expected_tables[@]}"; do
    if echo "$tables" | grep -q "^$table$"; then
        echo "  ✓ Table '$table' exists"
    else
        echo "  ✗ Table '$table' missing"
        exit 1
    fi
done
echo ""

# Test 5: Connection with credentials
echo "5. Testing authenticated connection..."
auth_test=$(curl -s "http://localhost:8123/" \
  --data "SELECT currentUser()" \
  -u "pdf_user:pdf_password")

if [ "$auth_test" = "pdf_user" ]; then
    echo "✓ Authentication successful (user: $auth_test)"
else
    echo "✗ Authentication failed"
    exit 1
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ ClickHouse instance is fully operational"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Connection details:"
echo "  Host: localhost"
echo "  HTTP Port: 8123"
echo "  Native Port: 9000"
echo "  Database: pdf_scan"
echo "  User: pdf_user"
echo ""

