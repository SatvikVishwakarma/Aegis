#!/usr/bin/env python3
"""
User management CLI tool for Aegis.
Allows creating, listing, and managing user accounts.
"""

import asyncio
import sys
import getpass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db import AsyncSessionLocal
from models import User
import auth


async def create_user():
    """Interactive user creation."""
    print("\n=== Create New User ===\n")
    
    username = input("Username: ").strip()
    if not username:
        print("❌ Username cannot be empty")
        return
    
    email = input("Email: ").strip()
    if not email:
        print("❌ Email cannot be empty")
        return
    
    full_name = input("Full Name (optional): ").strip() or None
    
    password = getpass.getpass("Password: ")
    password_confirm = getpass.getpass("Confirm Password: ")
    
    if password != password_confirm:
        print("❌ Passwords do not match")
        return
    
    if len(password) < 6:
        print("❌ Password must be at least 6 characters")
        return
    
    try:
        async with AsyncSessionLocal() as session:
            # Check if username exists
            result = await session.execute(
                select(User).where(User.username == username)
            )
            if result.scalar_one_or_none():
                print(f"❌ Username '{username}' already exists")
                return
            
            # Check if email exists
            result = await session.execute(
                select(User).where(User.email == email)
            )
            if result.scalar_one_or_none():
                print(f"❌ Email '{email}' already registered")
                return
            
            # Create user
            hashed_password = auth.hash_password(password)
            new_user = User(
                username=username,
                email=email,
                full_name=full_name,
                hashed_password=hashed_password,
                disabled=False
            )
            
            session.add(new_user)
            await session.commit()
            
            print(f"\n✓ User '{username}' created successfully!")
    
    except Exception as e:
        print(f"\n❌ Error creating user: {e}")


async def list_users():
    """List all users."""
    print("\n=== User List ===\n")
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            if not users:
                print("No users found")
                return
            
            print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Full Name':<25} {'Status':<10}")
            print("-" * 95)
            
            for user in users:
                status = "Disabled" if user.disabled else "Active"
                full_name = user.full_name or "-"
                print(f"{user.id:<5} {user.username:<20} {user.email:<30} {full_name:<25} {status:<10}")
    
    except Exception as e:
        print(f"\n❌ Error listing users: {e}")


async def change_password():
    """Change user password."""
    print("\n=== Change Password ===\n")
    
    username = input("Username: ").strip()
    if not username:
        print("❌ Username cannot be empty")
        return
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"❌ User '{username}' not found")
                return
            
            new_password = getpass.getpass("New Password: ")
            password_confirm = getpass.getpass("Confirm Password: ")
            
            if new_password != password_confirm:
                print("❌ Passwords do not match")
                return
            
            if len(new_password) < 6:
                print("❌ Password must be at least 6 characters")
                return
            
            user.hashed_password = auth.hash_password(new_password)
            await session.commit()
            
            print(f"\n✓ Password changed successfully for user '{username}'!")
    
    except Exception as e:
        print(f"\n❌ Error changing password: {e}")


async def toggle_user_status():
    """Enable or disable a user account."""
    print("\n=== Enable/Disable User ===\n")
    
    username = input("Username: ").strip()
    if not username:
        print("❌ Username cannot be empty")
        return
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"❌ User '{username}' not found")
                return
            
            current_status = "Disabled" if user.disabled else "Active"
            new_status = "Active" if user.disabled else "Disabled"
            
            print(f"Current status: {current_status}")
            confirm = input(f"Change status to {new_status}? (y/n): ").strip().lower()
            
            if confirm != 'y':
                print("Cancelled")
                return
            
            user.disabled = not user.disabled
            await session.commit()
            
            print(f"\n✓ User '{username}' is now {new_status}!")
    
    except Exception as e:
        print(f"\n❌ Error changing user status: {e}")


async def delete_user():
    """Delete a user account."""
    print("\n=== Delete User ===\n")
    
    username = input("Username: ").strip()
    if not username:
        print("❌ Username cannot be empty")
        return
    
    if username == "admin":
        print("❌ Cannot delete the admin user")
        return
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"❌ User '{username}' not found")
                return
            
            print(f"⚠️  WARNING: This will permanently delete user '{username}'")
            confirm = input("Are you sure? Type 'DELETE' to confirm: ").strip()
            
            if confirm != 'DELETE':
                print("Cancelled")
                return
            
            await session.delete(user)
            await session.commit()
            
            print(f"\n✓ User '{username}' deleted successfully!")
    
    except Exception as e:
        print(f"\n❌ Error deleting user: {e}")


def print_menu():
    """Print the main menu."""
    print("\n" + "=" * 50)
    print("Aegis User Management")
    print("=" * 50)
    print("1. Create User")
    print("2. List Users")
    print("3. Change Password")
    print("4. Enable/Disable User")
    print("5. Delete User")
    print("0. Exit")
    print("=" * 50)


async def main():
    """Main menu loop."""
    while True:
        print_menu()
        choice = input("\nSelect an option: ").strip()
        
        if choice == "1":
            await create_user()
        elif choice == "2":
            await list_users()
        elif choice == "3":
            await change_password()
        elif choice == "4":
            await toggle_user_status()
        elif choice == "5":
            await delete_user()
        elif choice == "0":
            print("\nGoodbye!")
            break
        else:
            print("❌ Invalid option")
        
        if choice != "0":
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
