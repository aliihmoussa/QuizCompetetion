#!/usr/bin/env python3
"""
UUID Migration Script
=====================
Migrates all database models from Integer IDs to UUIDs (UUID v7).

⚠️  WARNING: This is a DESTRUCTIVE migration that will DROP all existing data!
⚠️  This script should only be run on a FRESH database or after backing up.

For existing data migration, see: UUID_MIGRATION_WITH_DATA.md

Usage:
    python migrate_to_uuid.py

This script:
1. Drops all existing tables
2. Creates new UUID-based schema
3. Initializes fresh database with UUID support
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from database import engine, Base, init_db
from sqlalchemy import text

def confirm_migration():
    """Ask user to confirm destructive operation"""
    print("=" * 70)
    print("⚠️  UUID MIGRATION - DESTRUCTIVE OPERATION")
    print("=" * 70)
    print()
    print("This script will:")
    print("  1. DROP all existing tables and data")
    print("  2. Create new UUID-based schema")
    print("  3. Initialize fresh database")
    print()
    print("⚠️  ALL EXISTING DATA WILL BE LOST!")
    print()
    
    response = input("Type 'YES' to proceed with migration: ")
    return response.strip() == "YES"

def enable_uuid_extension():
    """Enable PostgreSQL UUID extension"""
    print("\n[1/4] Enabling PostgreSQL UUID extension...")
    with engine.connect() as conn:
        try:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";'))
            conn.commit()
            print("✅ UUID extension enabled")
        except Exception as e:
            print(f"⚠️  Warning: Could not enable uuid-ossp extension: {e}")
            print("   This is OK if using uuid7 library for generation")

def drop_all_tables():
    """Drop all existing tables"""
    print("\n[2/4] Dropping all existing tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped")
    except Exception as e:
        print(f"⚠️  Error dropping tables: {e}")
        print("   This is OK if tables don't exist yet")

def create_uuid_schema():
    """Create new UUID-based schema"""
    print("\n[3/4] Creating new UUID-based schema...")
    try:
        init_db()
        print("✅ UUID schema created successfully")
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        raise

def verify_migration():
    """Verify migration was successful"""
    print("\n[4/4] Verifying migration...")
    
    with engine.connect() as conn:
        # Check if tables exist
        result = conn.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """))
        
        tables = [row[0] for row in result]
        
        if not tables:
            print("❌ No tables found! Migration may have failed.")
            return False
        
        print(f"\n✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table}")
        
        # Check if UUID columns exist
        print("\n   Checking UUID columns...")
        for table in tables:
            result = conn.execute(text(f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table}' 
                AND column_name = 'id';
            """))
            
            row = result.fetchone()
            if row:
                col_name, data_type = row
                if data_type == 'uuid':
                    print(f"   ✅ {table}.id is UUID")
                else:
                    print(f"   ❌ {table}.id is {data_type} (expected UUID)")
                    return False
    
    print("\n✅ Migration verified successfully!")
    return True

def main():
    """Main migration function"""
    print("\n🚀 UUID Migration Script")
    print("=" * 70)
    
    # Check if user confirmed
    if not confirm_migration():
        print("\n❌ Migration cancelled by user")
        print("   No changes were made to the database")
        return 1
    
    try:
        # Step 1: Enable UUID extension
        enable_uuid_extension()
        
        # Step 2: Drop existing tables
        drop_all_tables()
        
        # Step 3: Create new UUID schema
        create_uuid_schema()
        
        # Step 4: Verify migration
        if not verify_migration():
            print("\n❌ Migration verification failed!")
            return 1
        
        print("\n" + "=" * 70)
        print("✅ UUID MIGRATION COMPLETE!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Test the application thoroughly")
        print("  2. Create initial admin/instructor users")
        print("  3. Create test quizzes")
        print("\nNOTE: All IDs are now UUIDs.")
        print("      Example: 018c-a5f2-7890-1234-5678-90ab-cdef")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\nPlease check:")
        print("  - Database connection is working")
        print("  - PostgreSQL server is running")
        print("  - User has necessary permissions")
        print("  - uuid7 package is installed (pip install uuid7)")
        return 1

if __name__ == "__main__":
    sys.exit(main())

