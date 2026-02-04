"""
Environment Diagnostic Script
Identifies why data might not be persisting
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prozync.settings')
django.setup()

from django.conf import settings
from django.contrib.auth.models import User
from core.models import Post, Comment, Like, Project

def banner(text, char="="):
    print(f"\n{char*70}")
    print(f"  {text}")
    print(f"{char*70}")

def check_environment():
    """Check the deployment environment"""
    banner("ENVIRONMENT CHECK", "=")
    
    # Check if DATABASE_URL is set
    database_url = os.environ.get('DATABASE_URL')
    
    print(f"\n1. Environment Variables:")
    print(f"   DATABASE_URL: {'✓ SET' if database_url else '✗ NOT SET'}")
    if database_url:
        # Hide password in output
        safe_url = database_url.split('@')[1] if '@' in database_url else database_url
        print(f"   Value: ...@{safe_url}")
    
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    
    # Check deployment indicators
    has_procfile = Path('Procfile').exists()
    has_build_sh = Path('build.sh').exists()
    
    print(f"\n2. Deployment Indicators:")
    print(f"   Procfile exists: {'✓ YES' if has_procfile else '✗ NO'}")
    print(f"   build.sh exists: {'✓ YES' if has_build_sh else '✗ NO'}")
    
    if has_procfile or has_build_sh:
        print(f"\n   ⚠️  DEPLOYMENT DETECTED!")
        print(f"   This looks like a Render/Heroku deployment")
        return 'PRODUCTION'
    else:
        print(f"\n   ✓ Local development environment")
        return 'LOCAL'

def check_database():
    """Check database configuration"""
    banner("DATABASE CHECK", "=")
    
    db_config = settings.DATABASES['default']
    
    print(f"\n1. Database Configuration:")
    print(f"   Engine: {db_config['ENGINE']}")
    print(f"   Name: {db_config['NAME']}")
    
    # Determine database type
    if 'sqlite' in db_config['ENGINE']:
        db_type = 'SQLite'
        db_file = Path(db_config['NAME'])
        
        print(f"\n2. SQLite Database:")
        print(f"   File: {db_file}")
        print(f"   Exists: {'✓ YES' if db_file.exists() else '✗ NO'}")
        
        if db_file.exists():
            size_mb = db_file.stat().st_size / (1024 * 1024)
            print(f"   Size: {size_mb:.2f} MB")
            print(f"   Readable: {'✓ YES' if os.access(db_file, os.R_OK) else '✗ NO'}")
            print(f"   Writable: {'✓ YES' if os.access(db_file, os.W_OK) else '✗ NO'}")
        
        return 'SQLITE', db_file
        
    elif 'postgresql' in db_config['ENGINE']:
        db_type = 'PostgreSQL'
        print(f"\n2. PostgreSQL Database:")
        print(f"   Host: {db_config.get('HOST', 'N/A')}")
        print(f"   Port: {db_config.get('PORT', 'N/A')}")
        print(f"   Database: {db_config.get('NAME', 'N/A')}")
        
        return 'POSTGRESQL', None
    
    else:
        return 'UNKNOWN', None

def check_data():
    """Check current data in database"""
    banner("DATA CHECK", "=")
    
    models = [
        ('Users', User),
        ('Posts', Post),
        ('Comments', Comment),
        ('Likes', Like),
        ('Projects', Project),
    ]
    
    print("\nCurrent data counts:")
    total = 0
    for name, model in models:
        count = model.objects.count()
        total += count
        status = "✓" if count > 0 else "○"
        print(f"   {status} {name:15} : {count:4}")
    
    print(f"\n   Total records: {total}")
    return total

def diagnose_issue(env_type, db_type, db_file, data_count):
    """Diagnose the persistence issue"""
    banner("DIAGNOSIS", "=")
    
    print("\nAnalysis:")
    
    # Case 1: Production with SQLite
    if env_type == 'PRODUCTION' and db_type == 'SQLITE':
        print("\n❌ PROBLEM IDENTIFIED!")
        print("\n   Issue: Using SQLite on production platform")
        print("   Cause: Platforms like Render/Heroku have ephemeral storage")
        print("   Result: Database file is deleted on every restart/deploy")
        print("\n   SOLUTION:")
        print("   1. Add PostgreSQL database to your platform")
        print("   2. Set DATABASE_URL environment variable")
        print("   3. Run migrations: python manage.py migrate")
        print("   4. Your settings.py already supports PostgreSQL!")
        return 'EPHEMERAL_STORAGE'
    
    # Case 2: Local with SQLite (should work)
    elif env_type == 'LOCAL' and db_type == 'SQLITE':
        if db_file and db_file.exists():
            print("\n✓ Configuration looks correct")
            print("\n   Environment: Local development")
            print("   Database: SQLite (persistent file)")
            print("   File exists: YES")
            
            if data_count > 0:
                print(f"   Data present: YES ({data_count} records)")
                print("\n   ✅ Everything looks good!")
                print("\n   If data still disappears, check:")
                print("   1. Are you running 'python manage.py flush'?")
                print("   2. Are you deleting db.sqlite3 manually?")
                print("   3. Are you running migrations with --run-syncdb?")
                return 'OK'
            else:
                print(f"   Data present: NO (0 records)")
                print("\n   ⚠️  Database is empty")
                print("   This is normal for a fresh installation")
                print("   Create some data and test persistence")
                return 'EMPTY'
        else:
            print("\n⚠️  Database file missing!")
            print("   Run: python manage.py migrate")
            return 'NO_DB_FILE'
    
    # Case 3: Production with PostgreSQL (correct)
    elif env_type == 'PRODUCTION' and db_type == 'POSTGRESQL':
        print("\n✅ CORRECT CONFIGURATION!")
        print("\n   Environment: Production")
        print("   Database: PostgreSQL (persistent)")
        print("   Data should persist correctly")
        
        if data_count > 0:
            print(f"   Data present: YES ({data_count} records)")
        else:
            print(f"   Data present: NO (empty database)")
            print("   Run migrations if needed: python manage.py migrate")
        
        return 'OK'
    
    else:
        print("\n⚠️  Unusual configuration")
        print(f"   Environment: {env_type}")
        print(f"   Database: {db_type}")
        return 'UNKNOWN'

def provide_solution(diagnosis):
    """Provide specific solution based on diagnosis"""
    banner("SOLUTION", "=")
    
    if diagnosis == 'EPHEMERAL_STORAGE':
        print("\n🔧 IMMEDIATE FIX REQUIRED:")
        print("\n   Your platform (Render/Heroku) deletes SQLite on restart!")
        print("\n   Steps to fix:")
        print("\n   1. Add PostgreSQL database:")
        print("      - Render: Dashboard → New → PostgreSQL")
        print("      - Heroku: heroku addons:create heroku-postgresql:mini")
        print("\n   2. Get the database URL")
        print("\n   3. Add as environment variable:")
        print("      Variable name: DATABASE_URL")
        print("      Value: [your PostgreSQL connection string]")
        print("\n   4. Deploy and run migrations:")
        print("      python manage.py migrate")
        print("\n   ✅ Your code already supports this - no code changes needed!")
        
    elif diagnosis == 'OK':
        print("\n✅ Your configuration is correct!")
        print("\n   Data should persist after restart.")
        print("\n   To verify:")
        print("   1. Run: python test_data_persistence.py")
        print("   2. Restart server")
        print("   3. Run: python test_data_persistence.py again")
        print("   4. Data should still be there")
        
    elif diagnosis == 'EMPTY':
        print("\n📝 Database is empty but configured correctly")
        print("\n   To test persistence:")
        print("   1. Create some data (register users, create posts)")
        print("   2. Restart the server")
        print("   3. Check if data is still there")
        
    elif diagnosis == 'NO_DB_FILE':
        print("\n🔧 Database not initialized")
        print("\n   Run these commands:")
        print("   1. python manage.py makemigrations")
        print("   2. python manage.py migrate")
        print("   3. python manage.py createsuperuser (optional)")

def main():
    print("\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + "  DATA PERSISTENCE DIAGNOSTIC TOOL".center(68) + "#")
    print("#" + " "*68 + "#")
    print("#"*70)
    
    try:
        # Run diagnostics
        env_type = check_environment()
        db_type, db_file = check_database()
        data_count = check_data()
        
        # Diagnose issue
        diagnosis = diagnose_issue(env_type, db_type, db_file, data_count)
        
        # Provide solution
        provide_solution(diagnosis)
        
        # Final summary
        banner("SUMMARY", "=")
        print(f"\n   Environment: {env_type}")
        print(f"   Database: {db_type}")
        print(f"   Diagnosis: {diagnosis}")
        
        if diagnosis == 'EPHEMERAL_STORAGE':
            print(f"\n   ⚠️  ACTION REQUIRED: Switch to PostgreSQL")
            return 1
        elif diagnosis == 'OK':
            print(f"\n   ✅ Everything looks good!")
            return 0
        else:
            print(f"\n   ℹ️  See solution above")
            return 0
            
    except Exception as e:
        print(f"\n❌ Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
