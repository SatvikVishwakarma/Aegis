"""
Aegis Server Database Reset Script
===================================
This script completely clears all data from the database while preserving the schema.
Use this to reset the server to a clean, brand new state.

WARNING: This will delete ALL data including:
- ALL Users (including admin)
- Nodes
- Events/Logs
- Policies
- Rules
- Groups
- All other records

Usage:
    python reset_database.py
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from getpass import getpass
import bcrypt

# Import models and database setup
from models import Base, User, Node, Event, Policy, Rule, Group
from db import engine, SessionLocal

def confirm_reset():
    """Ask user to confirm the destructive operation."""
    print("\n" + "="*60)
    print("⚠️  WARNING: DATABASE RESET OPERATION")
    print("="*60)
    print("\nThis will DELETE ALL data from the database:")
    print("  - ALL users (including admin)")
    print("  - All registered nodes")
    print("  - All events and logs")
    print("  - All policies and rules")
    print("  - All groups")
    print("  - All other records")
    print("\nThe database schema will be preserved.")
    print("="*60)
    
    response = input("\nAre you sure you want to continue? (type 'YES' to confirm): ")
    return response == 'YES'

def clear_all_tables(session):
    """Delete all records from all tables."""
    print("\n🗑️  Clearing database tables...")
    
    try:
        # Delete in order to respect foreign key constraints
        tables_to_clear = [
            ('Events', Event),
            ('Rules', Rule),
            ('Policies', Policy),
            ('Nodes', Node),
            ('Groups', Group),
            ('Users', User),
        ]
        
        for table_name, model in tables_to_clear:
            count = session.query(model).count()
            if count > 0:
                session.query(model).delete()
                print(f"  ✓ Deleted {count} records from {table_name}")
            else:
                print(f"  - {table_name} was already empty")
        
        session.commit()
        print("\n✅ All tables cleared successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error clearing tables: {e}")
        session.rollback()
        return False

def create_admin_user(session):
    """Create a fresh admin user."""
    print("\n👤 Creating new admin user...")
    
    try:
        # Get admin credentials
        print("\nSet up admin credentials:")
        username = input("Admin username [admin]: ").strip() or "admin"
        
        while True:
            password = getpass("Admin password: ")
            if len(password) < 6:
                print("❌ Password must be at least 6 characters!")
                continue
            confirm = getpass("Confirm password: ")
            if password != confirm:
                print("❌ Passwords don't match!")
                continue
            break
        
        email = input("Admin email [admin@aegis.local]: ").strip() or "admin@aegis.local"
        
        # Hash password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create admin user
        admin = User(
            username=username,
            email=email,
            password_hash=hashed.decode('utf-8'),
            role='admin',
            is_active=True
        )
        
        session.add(admin)
        session.commit()
        
        print(f"\n✅ Admin user '{username}' created successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating admin user: {e}")
        session.rollback()
        return False

def reset_database():
    """Main function to reset the database."""
    print("\n" + "="*60)
    print("🔄 Aegis Database Reset Tool")
    print("="*60)
    
    # Check if database file exists
    db_path = "aegis.db"
    if not os.path.exists(db_path):
        print(f"\n⚠️  Database file '{db_path}' not found!")
        print("Creating a fresh database...")
        Base.metadata.create_all(bind=engine)
        print("✅ Fresh database created!")
    
    # Confirm operation
    if not confirm_reset():
        print("\n❌ Operation cancelled by user.")
        return False
    
    # Create session
    session = SessionLocal()
    
    try:
        # Clear all tables
        if not clear_all_tables(session):
            return False
        
        # Create admin user
        if not create_admin_user(session):
            return False
        
        print("\n" + "="*60)
        print("✅ Database reset completed successfully!")
        print("="*60)
        print("\n📝 Summary:")
        print("  - All old data deleted")
        print("  - Fresh admin user created")
        print("  - Database schema intact")
        print("  - Server is ready to use")
        print("\n🚀 You can now restart the server with: python app.py")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False
        
    finally:
        session.close()

def quick_reset():
    """Quick reset without prompts (for development)."""
    print("\n🚀 Quick Reset Mode (Development)")
    print("="*60)
    
    session = SessionLocal()
    
    try:
        # Clear all tables
        tables = [Event, Rule, Policy, Node, Group, User]
        for model in tables:
            count = session.query(model).delete()
            print(f"  ✓ Cleared {count} records from {model.__tablename__}")
        
        # Create default admin
        hashed = bcrypt.hashpw(b'admin123', bcrypt.gensalt())
        admin = User(
            username='admin',
            email='admin@aegis.local',
            password_hash=hashed.decode('utf-8'),
            role='admin',
            is_active=True
        )
        session.add(admin)
        session.commit()
        
        print("\n✅ Quick reset complete!")
        print("   Username: admin")
        print("   Password: admin123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    # Check for quick reset flag
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        quick_reset()
    else:
        reset_database()
