"""
Quick script to check if you're using PostgreSQL
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prozync.settings')
django.setup()

from django.conf import settings
from django.db import connection

print("\n" + "="*70)
print("  DATABASE CONFIGURATION CHECK")
print("="*70)

# Get database settings
db_settings = settings.DATABASES['default']

print("\n📊 Database Information:")
print("-" * 70)

# Database engine
engine = db_settings['ENGINE']
print(f"\nEngine: {engine}")

if 'postgresql' in engine:
    print("✅ Using PostgreSQL (CORRECT for production)")
    db_type = 'PostgreSQL'
elif 'sqlite' in engine:
    print("⚠️  Using SQLite (OK for local dev, use PostgreSQL for production)")
    db_type = 'SQLite'
else:
    print(f"❓ Using: {engine}")
    db_type = 'Other'

# Database details
print(f"\nDatabase Name: {db_settings.get('NAME', 'N/A')}")

if db_type == 'PostgreSQL':
    print(f"Host: {db_settings.get('HOST', 'N/A')}")
    print(f"Port: {db_settings.get('PORT', 'N/A')}")
    print(f"User: {db_settings.get('USER', 'N/A')}")
elif db_type == 'SQLite':
    import os.path
    db_path = db_settings['NAME']
    print(f"File Path: {db_path}")
    print(f"File Exists: {os.path.exists(db_path)}")
    if os.path.exists(db_path):
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        print(f"File Size: {size_mb:.2f} MB")

# Check environment variable
print("\n🔧 Environment Variables:")
print("-" * 70)
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Hide password for security
    if '@' in database_url:
        parts = database_url.split('@')
        safe_url = '***:***@' + parts[1]
    else:
        safe_url = database_url[:20] + '...'
    print(f"DATABASE_URL: {safe_url}")
    print("✅ DATABASE_URL is set (will use PostgreSQL if configured)")
else:
    print("DATABASE_URL: Not set")
    print("ℹ️  Using default database from settings.py")

# Test connection
print("\n🔌 Connection Test:")
print("-" * 70)
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connected successfully!")
        print(f"Version: {version[:100]}...")
except Exception as e:
    print(f"❌ Connection failed: {e}")

# Count tables
print("\n📋 Database Tables:")
print("-" * 70)
try:
    with connection.cursor() as cursor:
        if db_type == 'PostgreSQL':
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
        else:  # SQLite
            cursor.execute("""
                SELECT name 
                FROM sqlite_master 
                WHERE type='table'
                ORDER BY name;
            """)
        
        tables = cursor.fetchall()
        print(f"Total tables: {len(tables)}")
        
        # Show core tables
        core_tables = [t[0] for t in tables if 'core_' in t[0] or 'auth_' in t[0]]
        if core_tables:
            print("\nCore application tables:")
            for table in core_tables[:10]:
                print(f"  • {table}")
            if len(core_tables) > 10:
                print(f"  ... and {len(core_tables) - 10} more")
except Exception as e:
    print(f"❌ Could not list tables: {e}")

# Summary
print("\n" + "="*70)
print("  SUMMARY")
print("="*70)

if db_type == 'PostgreSQL':
    print("\n✅ You are using PostgreSQL!")
    print("\nBenefits:")
    print("  ✓ Data persists after restart")
    print("  ✓ Production-ready")
    print("  ✓ Scalable")
    print("  ✓ Supports concurrent connections")
elif db_type == 'SQLite':
    print("\n⚠️  You are using SQLite")
    print("\nCurrent setup:")
    print("  ✓ Good for local development")
    print("  ✓ Easy to set up")
    print("\nFor production:")
    print("  ⚠️  Switch to PostgreSQL")
    print("  ⚠️  SQLite data will be lost on Render/Heroku restart")
    print("\nTo switch to PostgreSQL:")
    print("  1. Create PostgreSQL database on Render/Heroku")
    print("  2. Set DATABASE_URL environment variable")
    print("  3. Deploy - your code already supports it!")

print("\n" + "="*70 + "\n")
