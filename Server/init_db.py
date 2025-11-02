#!/usr/bin/env python3
"""
Database initialization script for Aegis.
Creates the database tables and adds a default admin user.
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Import from local modules
from db import engine, AsyncSessionLocal
from models import Base, User
import auth


async def init_database():
    """Initialize the database and create tables."""
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Database tables created successfully")


async def create_default_admin():
    """Create a default admin user if no users exist."""
    async with AsyncSessionLocal() as session:
        # Check if any users exist
        result = await session.execute(select(User))
        existing_users = result.scalars().all()
        
        if existing_users:
            print(f"✓ Database already has {len(existing_users)} user(s)")
            return
        
        # Create default admin user
        print("Creating default admin user...")
        default_password = "password123"
        hashed_password = auth.hash_password(default_password)
        
        admin_user = User(
            username="admin",
            email="admin@aegis.local",
            full_name="System Administrator",
            hashed_password=hashed_password,
            disabled=False
        )
        
        session.add(admin_user)
        await session.commit()
        
        print("✓ Default admin user created successfully")
        print(f"  Username: admin")
        print(f"  Password: {default_password}")
        print(f"  Email: admin@aegis.local")
        print("\n⚠️  IMPORTANT: Please change the default password after first login!")


async def main():
    """Main initialization function."""
    print("=" * 50)
    print("Aegis Database Initialization")
    print("=" * 50)
    print()
    
    try:
        await init_database()
        await create_default_admin()
        
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
