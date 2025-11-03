#!/usr/bin/env python3
"""
Database initialization script for Aegis.
Creates the database tables and generates a secure admin account.
"""

import asyncio
import sys
import secrets
import string

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


def generate_secure_password(length=10):
    """Generate a secure random password."""
    # Use alphanumeric characters (uppercase, lowercase, digits)
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


async def create_admin_user():
    """Create admin user with secure random password."""
    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == "admin"))
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("✓ Admin user already exists")
            return None
        
        # Generate secure password
        password = generate_secure_password(10)
        hashed_password = auth.hash_password(password)
        
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@aegis.local",
            full_name="System Administrator",
            hashed_password=hashed_password,
            disabled=False
        )
        
        session.add(admin_user)
        await session.commit()
        
        return password


async def main():
    """Main initialization function."""
    print("=" * 60)
    print("Aegis Database Initialization")
    print("=" * 60)
    print()
    
    try:
        await init_database()
        
        print()
        print("Creating admin user with secure password...")
        password = await create_admin_user()
        
        print()
        print("=" * 60)
        print("✓ Database initialization complete!")
        print("=" * 60)
        
        if password:
            print()
            print("=" * 60)
            print("🔐 ADMIN CREDENTIALS - SAVE THESE!")
            print("=" * 60)
            print(f"Username: admin")
            print(f"Password: {password}")
            print("=" * 60)
            print()
            print("⚠️  IMPORTANT:")
            print("  - Save this password securely NOW")
            print("  - This password will NOT be shown again")
            print("  - You'll need it to login and confirm deletions")
            print("=" * 60)
            
            # Return password for setup script to capture
            return password
        
    except Exception as e:
        print(f"\n❌ Error during initialization: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    password = asyncio.run(main())
