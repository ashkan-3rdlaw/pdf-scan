#!/usr/bin/env python3
"""
Example script demonstrating how to create and use ClickHouse backends.

Usage:
    python scripts/init_clickhouse_backends.py
"""

from pdf_scan.db.factory import BackendFactory


def main():
    """Initialize and test ClickHouse backends."""
    print("Creating ClickHouse client...")
    
    # Create ClickHouse client
    client = BackendFactory.create_clickhouse_client(
        host="localhost",
        port=8123,
        username="pdf_user",
        password="pdf_password",
        database="pdf_scan",
    )
    
    print("✓ ClickHouse client created")
    
    # Test connection
    try:
        result = client.command("SELECT version()")
        print(f"✓ ClickHouse connection successful")
        print(f"  Version: {result}")
    except Exception as e:
        print(f"✗ ClickHouse connection failed: {e}")
        print("\nMake sure ClickHouse is running:")
        print("  docker-compose up -d")
        return
    
    print("\nCreating ClickHouse backends...")
    
    # Create backends with ClickHouse
    backends = BackendFactory.create_backends(backend="clickhouse", client=client)
    
    print("✓ ClickHouse backends created:")
    print(f"  Document repository: {type(backends.document).__name__}")
    print(f"  Finding repository: {type(backends.finding).__name__}")
    print(f"  Metrics repository: {type(backends.metrics).__name__}")
    print(f"  Scanner: {type(backends.scanner).__name__}")
    
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("✓ All ClickHouse backends initialized successfully!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("\nYou can now use these backends in your application.")
    print("\nExample - Create with in-memory (default):")
    print("  backends = BackendFactory.create_backends()")
    print("\nExample - Create with ClickHouse:")
    print("  client = BackendFactory.create_clickhouse_client()")
    print("  backends = BackendFactory.create_backends(backend='clickhouse', client=client)")


if __name__ == "__main__":
    main()

