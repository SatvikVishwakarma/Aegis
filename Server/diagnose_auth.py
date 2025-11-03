#!/usr/bin/env python3
"""
Aegis Authentication Diagnostic Tool
Tests all authentication components to identify login issues.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import AsyncSession
    from db import AsyncSessionLocal, engine
    from models import User, Base
    import auth
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\nMake sure you're in the virtual environment:")
    print("  source aegis/bin/activate  # Linux/Mac")
    print("  aegis\\Scripts\\activate     # Windows")
    sys.exit(1)

# Load environment variables
load_dotenv()


def print_header(title):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_success(message):
    """Print success message."""
    print(f"✓ {message}")


def print_error(message):
    """Print error message."""
    print(f"✗ {message}")


def print_info(message):
    """Print info message."""
    print(f"ℹ {message}")


async def test_database_connection():
    """Test 1: Database Connection"""
    print_header("Test 1: Database Connection")
    
    try:
        # Check if database file exists
        db_path = "aegis.db"
        if os.path.exists(db_path):
            print_success(f"Database file exists: {db_path}")
            file_size = os.path.getsize(db_path)
            print_info(f"Database size: {file_size} bytes")
        else:
            print_error(f"Database file not found: {db_path}")
            return False
        
        # Test database connection
        async with engine.begin() as conn:
            print_success("Successfully connected to database")
        
        return True
    except Exception as e:
        print_error(f"Database connection failed: {e}")
        return False


async def test_environment_variables():
    """Test 2: Environment Variables"""
    print_header("Test 2: Environment Variables")
    
    required_vars = {
        'SECRET_KEY': 'JWT secret key',
        'ALGORITHM': 'JWT algorithm',
        'ACCESS_TOKEN_EXPIRE_MINUTES': 'Token expiration time',
        'AGENT_API_KEY': 'Agent API key',
    }
    
    all_present = True
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Don't print full secret values
            if 'KEY' in var:
                masked = value[:10] + "..." if len(value) > 10 else value
                print_success(f"{var} is set ({description}): {masked}")
            else:
                print_success(f"{var} is set ({description}): {value}")
        else:
            print_error(f"{var} is NOT set ({description})")
            all_present = False
    
    # Check .env file
    env_path = ".env"
    if os.path.exists(env_path):
        print_success(f".env file exists")
    else:
        print_error(f".env file not found")
        all_present = False
    
    return all_present


async def test_user_table():
    """Test 3: User Table Schema"""
    print_header("Test 3: User Table Schema")
    
    try:
        async with AsyncSessionLocal() as session:
            # Try to query users table
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            print_success("Users table exists and is accessible")
            print_info(f"Total users in database: {len(users)}")
            
            # Show table structure
            if hasattr(User, '__table__'):
                columns = [col.name for col in User.__table__.columns]
                print_info(f"User table columns: {', '.join(columns)}")
            
            return True, len(users)
    except Exception as e:
        print_error(f"Failed to access users table: {e}")
        return False, 0


async def test_admin_user():
    """Test 4: Admin User Existence"""
    print_header("Test 4: Admin User")
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).filter(User.username == "admin")
            )
            admin = result.scalar_one_or_none()
            
            if admin:
                print_success("Admin user exists")
                print_info(f"  Username: {admin.username}")
                print_info(f"  Email: {admin.email}")
                print_info(f"  Full Name: {admin.full_name}")
                print_info(f"  Disabled: {admin.disabled}")
                print_info(f"  Created: {admin.created_at}")
                print_info(f"  Hashed Password Length: {len(admin.hashed_password)} chars")
                print_info(f"  Password Hash (first 30 chars): {admin.hashed_password[:30]}...")
                
                # Check if account is disabled
                if admin.disabled:
                    print_error("⚠️  Admin account is DISABLED!")
                    return False, admin
                else:
                    print_success("Admin account is ACTIVE")
                
                return True, admin
            else:
                print_error("Admin user does NOT exist")
                print_info("Run: python init_db.py to create admin user")
                return False, None
                
    except Exception as e:
        print_error(f"Failed to query admin user: {e}")
        return False, None


async def test_password_hashing():
    """Test 5: Password Hashing Functions"""
    print_header("Test 5: Password Hashing Functions")
    
    test_password = "TestPassword123"
    
    try:
        # Test hashing
        hashed = auth.hash_password(test_password)
        print_success(f"Password hashing works")
        print_info(f"  Test password: {test_password}")
        print_info(f"  Hashed length: {len(hashed)} chars")
        print_info(f"  Hash preview: {hashed[:50]}...")
        
        # Test verification with correct password
        is_valid = auth.verify_password(test_password, hashed)
        if is_valid:
            print_success("Password verification works (correct password)")
        else:
            print_error("Password verification FAILED (correct password should work)")
            return False
        
        # Test verification with wrong password
        is_valid = auth.verify_password("WrongPassword", hashed)
        if not is_valid:
            print_success("Password verification works (wrong password rejected)")
        else:
            print_error("Password verification FAILED (wrong password should fail)")
            return False
        
        return True
    except Exception as e:
        print_error(f"Password hashing/verification failed: {e}")
        return False


async def test_admin_password(admin_user, test_password):
    """Test 6: Admin Password Verification"""
    print_header("Test 6: Admin Password Verification")
    
    if not admin_user:
        print_error("Cannot test - admin user doesn't exist")
        return False
    
    print_info(f"Testing password: {test_password}")
    
    try:
        is_valid = auth.verify_password(test_password, admin_user.hashed_password)
        
        if is_valid:
            print_success(f"✓✓✓ Password '{test_password}' is CORRECT! ✓✓✓")
            return True
        else:
            print_error(f"Password '{test_password}' is INCORRECT")
            return False
    except Exception as e:
        print_error(f"Password verification error: {e}")
        return False


async def test_jwt_token_creation():
    """Test 7: JWT Token Creation"""
    print_header("Test 7: JWT Token Creation")
    
    try:
        test_data = {
            "sub": "admin",
            "user_id": 1,
            "email": "admin@aegis.local"
        }
        
        token = auth.create_jwt_token(test_data)
        print_success("JWT token creation works")
        print_info(f"  Token length: {len(token)} chars")
        print_info(f"  Token preview: {token[:50]}...")
        
        # Verify token structure (should have 3 parts separated by dots)
        parts = token.split('.')
        if len(parts) == 3:
            print_success("Token has correct structure (header.payload.signature)")
        else:
            print_error(f"Token has incorrect structure (expected 3 parts, got {len(parts)})")
            return False
        
        return True
    except Exception as e:
        print_error(f"JWT token creation failed: {e}")
        return False


async def test_login_endpoint_simulation():
    """Test 8: Login Endpoint Simulation"""
    print_header("Test 8: Login Endpoint Simulation")
    
    print_info("This test simulates what happens when you try to login...")
    
    username = input("\nEnter username to test (default: admin): ").strip() or "admin"
    password = input("Enter password to test: ").strip()
    
    if not password:
        print_error("No password provided, skipping test")
        return False
    
    try:
        async with AsyncSessionLocal() as session:
            # Query user
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print_error(f"❌ LOGIN FAILED: User '{username}' not found")
                return False
            
            print_success(f"User '{username}' found in database")
            
            # Check if disabled
            if user.disabled:
                print_error(f"❌ LOGIN FAILED: User account is disabled")
                return False
            
            print_success("User account is active")
            
            # Verify password
            password_valid = auth.verify_password(password, user.hashed_password)
            
            if not password_valid:
                print_error(f"❌ LOGIN FAILED: Password is incorrect")
                print_info("\nPossible reasons:")
                print_info("  1. You're using the wrong password")
                print_info("  2. Password was not saved correctly during setup")
                print_info("  3. Password hash is corrupted")
                return False
            
            print_success("✓✓✓ Password is correct!")
            
            # Create token
            token = auth.create_jwt_token({
                "sub": user.username,
                "user_id": user.id,
                "email": user.email
            })
            
            print_success("JWT token created successfully")
            
            print("\n" + "=" * 80)
            print("✓✓✓ LOGIN WOULD SUCCEED! ✓✓✓")
            print("=" * 80)
            print(f"\nAccess Token: {token[:50]}...")
            print(f"Token Type: bearer")
            
            return True
            
    except Exception as e:
        print_error(f"Login simulation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_all_users():
    """Test 9: List All Users"""
    print_header("Test 9: All Users in Database")
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            if not users:
                print_error("No users found in database!")
                print_info("Run: python init_db.py")
                return False
            
            print_success(f"Found {len(users)} user(s):")
            print()
            
            for i, user in enumerate(users, 1):
                print(f"  User {i}:")
                print(f"    ID: {user.id}")
                print(f"    Username: {user.username}")
                print(f"    Email: {user.email}")
                print(f"    Full Name: {user.full_name}")
                print(f"    Disabled: {user.disabled}")
                print(f"    Created: {user.created_at}")
                print(f"    Password Hash: {user.hashed_password[:40]}...")
                print()
            
            return True
    except Exception as e:
        print_error(f"Failed to list users: {e}")
        return False


async def check_dashboard_config():
    """Test 10: Dashboard Configuration"""
    print_header("Test 10: Dashboard Configuration")
    
    dashboard_path = "../Dashboard"
    
    # Check if Dashboard exists
    if os.path.exists(dashboard_path):
        print_success("Dashboard directory exists")
    else:
        print_error("Dashboard directory not found")
        return False
    
    # Check .env.local
    env_local_path = os.path.join(dashboard_path, ".env.local")
    if os.path.exists(env_local_path):
        print_success(".env.local file exists")
        
        with open(env_local_path, 'r') as f:
            content = f.read()
            if 'NEXT_PUBLIC_API_URL' in content:
                print_success("NEXT_PUBLIC_API_URL is configured")
            else:
                print_error("NEXT_PUBLIC_API_URL not found in .env.local")
    else:
        print_info(".env.local file not found (using defaults)")
    
    # Check api.ts
    api_path = os.path.join(dashboard_path, "src", "lib", "api.ts")
    if os.path.exists(api_path):
        print_success("API configuration file exists")
        
        with open(api_path, 'r') as f:
            content = f.read()
            if 'localhost:8000' in content:
                print_success("API URL points to localhost:8000")
            if '/api/v1/token' in content or '/token' in content:
                print_success("Login endpoint configured")
    else:
        print_error("API configuration file not found")
        return False
    
    return True


async def main():
    """Run all diagnostic tests."""
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    AEGIS AUTHENTICATION DIAGNOSTIC TOOL                     ║
║                                                                              ║
║  This tool tests all authentication components to identify login issues.    ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # Run tests
    results['env_vars'] = await test_environment_variables()
    results['db_connection'] = await test_database_connection()
    results['user_table'], user_count = await test_user_table()
    results['admin_user'], admin_user = await test_admin_user()
    results['password_hashing'] = await test_password_hashing()
    results['jwt_creation'] = await test_jwt_token_creation()
    results['all_users'] = await test_all_users()
    results['dashboard_config'] = await check_dashboard_config()
    
    # If admin user exists, offer to test their password
    if admin_user:
        print_header("Interactive Password Test")
        print_info("You can now test if a specific password is correct for the admin user.")
        
        while True:
            test_pw = input("\nEnter password to test (or press Enter to skip): ").strip()
            if not test_pw:
                break
            
            await test_admin_password(admin_user, test_pw)
            
            another = input("Test another password? (y/N): ").strip().lower()
            if another != 'y':
                break
    
    # Login simulation
    print()
    simulate = input("Do you want to simulate a complete login attempt? (Y/n): ").strip().lower()
    if simulate != 'n':
        results['login_simulation'] = await test_login_endpoint_simulation()
    
    # Summary
    print_header("DIAGNOSTIC SUMMARY")
    
    passed = sum(1 for v in results.values() if v is True)
    total = len(results)
    
    print()
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} - {test_name.replace('_', ' ').title()}")
    
    print()
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print_success("\n✓✓✓ ALL TESTS PASSED! ✓✓✓")
        print_info("If you still can't login, check:")
        print_info("  1. Dashboard is running (npm run dev)")
        print_info("  2. Server is running (uvicorn app:app)")
        print_info("  3. You're using the correct password from setup")
        print_info("  4. Browser console for JavaScript errors")
    else:
        print_error(f"\n✗ {total - passed} test(s) failed")
        print_info("Review the failed tests above for details")
    
    print()
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
