#!/usr/bin/env python3
"""
Database initialization script for Aegis.
Creates the database tables.
"""

import asyncio
import sys

# Import from local modules
from db import engine
from models import Base


async def init_database():
    """Initialize the database and create tables."""
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database tables created successfully")


async def main():
    """Main initialization function."""
    print("=" * 50)
    print("Aegis Database Initialization")
    print("=" * 50)
    print()
    
    try:
        await init_database()
        
        print()
        print("=" * 50)
        print("✓ Database initialization complete!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
