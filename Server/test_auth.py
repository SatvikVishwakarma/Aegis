#!/usr/bin/env python3
"""
Authentication Test Script
Tests password hashing and verification to ensure login works correctly.
"""

import asyncio
from sqlalchemy import select
from db import AsyncSessionLocal
from models import User
import auth


async def test_authentication():
    """Test the complete authentication flow."""
    print("=" * 70)
    print(" Aegis Authentication System Test")
    print("=" * 70)
    print()
    
    # Test 1: Password Hashing
    print("[Test 1] Password Hashing")
    print("-" * 70)
    test_password = "TestPassword123"
    hashed = auth.hash_password(test_password)
    print(f"✓ Original password: {test_password}")
    print(f"✓ Hashed password: {hashed[:50]}...")
    print(f"✓ Hash length: {len(hashed)} characters")
    print()
    
    # Test 2: Password Verification
    print("[Test 2] Password Verification")
    print("-" * 70)
    is_valid = auth.verify_password(test_password, hashed)
    print(f"✓ Verification result: {'PASS' if is_valid else 'FAIL'}")
    
    is_invalid = auth.verify_password("WrongPassword", hashed)
    print(f"✓ Wrong password test: {'FAIL (as expected)' if not is_invalid else 'ERROR'}")
    print()
    
    # Test 3: Database Users
    print("[Test 3] Database Users")
    print("-" * 70)
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            print(f"Total users in database: {len(users)}")
            print()
            
            if not users:
                print("⚠ WARNING: No users found!")
                print("Please run: python manage_users.py")
                print()
                return
            
            for user in users:
                print(f"User: {user.username}")
                print(f"  ID: {user.id}")
                print(f"  Email: {user.email}")
                print(f"  Full Name: {user.full_name}")
                print(f"  Disabled: {user.disabled}")
                print(f"  Created: {user.created_at}")
                print(f"  Hash (first 50 chars): {user.hashed_password[:50]}...")
                print()
                
                # Test password verification for this user
                print(f"  Testing password verification for '{user.username}':")
                test_pw = input(f"  Enter password for {user.username} (or press Enter to skip): ").strip()
                
                if test_pw:
                    is_correct = auth.verify_password(test_pw, user.hashed_password)
                    if is_correct:
                        print(f"  ✓ Password CORRECT - Login should work!")
                    else:
                        print(f"  ✗ Password INCORRECT - Login will fail!")
                else:
                    print(f"  Skipped password test")
                
                print()
    
    except Exception as e:
        print(f"✗ Database error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("=" * 70)
    print(" Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_authentication())
