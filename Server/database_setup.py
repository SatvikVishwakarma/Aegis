"""
database_setup.py - Fresh Database Initialization
Creates database tables and admin user with generated password.
"""

import asyncio
import sys
from sqlalchemy import select

from db import engine, AsyncSessionLocal
from models import Base, User
from authentication import generate_password, hash_password


async def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Tables created successfully")


async def create_admin_account():
    """
    Create admin account with auto-generated password.
    Returns the generated password.
    """
    async with AsyncSessionLocal() as session:
        # Check if admin already exists
        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("[OK] Admin account already exists")
            return None
        
        # Generate secure password
        password = generate_password(10)
        hashed = hash_password(password)
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@aegis.local",
            full_name="System Administrator",
            hashed_password=hashed,
            disabled=False
        )
        
        session.add(admin)
        await session.commit()
        
        print("[OK] Admin account created successfully")
        return password


async def initialize_database():
    """Main initialization function."""
    print("=" * 70)
    print("AEGIS DATABASE INITIALIZATION")
    print("=" * 70)
    print()
    
    try:
        # Create tables
        await create_tables()
        print()
        
        # Create admin account
        print("Creating admin account...")
        password = await create_admin_account()
        
        print()
        print("=" * 70)
        print("INITIALIZATION COMPLETE")
        print("=" * 70)
        
        if password:
            print()
            print("*" * 70)
            print("ADMIN CREDENTIALS")
            print("*" * 70)
            print(f"Username: admin")
            print(f"Password: {password}")
            print("*" * 70)
            print()
            print("[WARNING] SAVE THIS PASSWORD NOW!")
            print("   This is the only time it will be displayed.")
            print("   You need it to login to the dashboard.")
            print("*" * 70)
            print()
            
        return password
        
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(initialize_database())
