"""
Migration script to add 'group' column to nodes table
Run this script to update existing databases with the new group feature.
"""

import asyncio
import sqlite3
from pathlib import Path


async def migrate_database():
    """Add group column to nodes table if it doesn't exist."""
    db_path = Path(__file__).parent / "aegis.db"
    
    if not db_path.exists():
        print("[INFO] Database not found. No migration needed.")
        print("The group column will be created when you run database_setup.py")
        return
    
    print("=" * 70)
    print("DATABASE MIGRATION: Adding 'group' column to nodes table")
    print("=" * 70)
    print()
    
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if column already exists
        cursor.execute("PRAGMA table_info(nodes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'group' in columns:
            print("[OK] Column 'group' already exists in nodes table")
            print("No migration needed.")
        else:
            print("[MIGRATION] Adding 'group' column to nodes table...")
            cursor.execute("""
                ALTER TABLE nodes 
                ADD COLUMN "group" VARCHAR(100)
            """)
            
            # Create index on group column for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS ix_nodes_group 
                ON nodes ("group")
            """)
            
            conn.commit()
            print("[OK] Successfully added 'group' column to nodes table")
            print("[OK] Created index on 'group' column")
        
        conn.close()
        
        print()
        print("=" * 70)
        print("MIGRATION COMPLETE")
        print("=" * 70)
        print()
        print("You can now use the group feature to organize your nodes!")
        print("Example groups: 'IT', 'HR', 'Linux', 'Windows', 'Production', etc.")
        print()
        
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    asyncio.run(migrate_database())
