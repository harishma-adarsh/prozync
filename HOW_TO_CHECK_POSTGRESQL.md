# How to Check PostgreSQL - Complete Guide

## Method 1: Quick Check Script ⚡ (EASIEST)

Run this command:
```bash
python check_database.py
```

This will show you:
- ✅ Database type (PostgreSQL or SQLite)
- ✅ Connection details
- ✅ Database version
- ✅ List of tables
- ✅ Environment variables

---

## Method 2: Django Shell 🐍

```bash
python manage.py shell
```

Then run:
```python
from django.conf import settings
from django.db import connection

# Check database engine
print(settings.DATABASES['default']['ENGINE'])

# If it shows 'postgresql', you're using PostgreSQL ✅
# If it shows 'sqlite3', you're using SQLite

# Get database version
with connection.cursor() as cursor:
    cursor.execute("SELECT version();")
    print(cursor.fetchone()[0])
```

---

## Method 3: Check Environment Variable 🔧

**Windows PowerShell:**
```powershell
$env:DATABASE_URL
```

**If set:** You're configured for PostgreSQL ✅  
**If empty:** Using default (SQLite for local dev)

---

## Method 4: Check settings.py 📄

Look at your `prozync/settings.py` (lines 69-73):

```python
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR}/db.sqlite3',
        conn_max_age=600
    )
}
```

This means:
- ✅ If `DATABASE_URL` env var is set → Uses PostgreSQL
- ✅ If `DATABASE_URL` is NOT set → Uses SQLite (local dev)

---

## Method 5: Check on Render/Heroku Dashboard 🌐

### For Render:
1. Go to https://dashboard.render.com
2. Click on your **PostgreSQL** database (if created)
3. You'll see:
   - Database name
   - Connection details
   - Status (should be "Available")
4. Click on your **Web Service**
5. Go to **Environment** tab
6. Check if `DATABASE_URL` is set

### For Heroku:
```bash
heroku config:get DATABASE_URL
```

If it returns a PostgreSQL URL, you're using PostgreSQL ✅

---

## Method 6: Check Database File 📁

**If using SQLite locally:**
```bash
# Check if db.sqlite3 exists
ls db.sqlite3

# Check file size
Get-Item db.sqlite3 | Select-Object Length
```

**If using PostgreSQL:**
- No local database file
- Data is on remote server

---

## Method 7: Run Diagnostic Script 🔍

```bash
python diagnose_environment.py
```

This will tell you:
- Environment type (local/production)
- Database type
- Whether you need to switch to PostgreSQL

---

## What You Should See

### ✅ Using PostgreSQL (Production):
```
Engine: django.db.backends.postgresql
✅ Using PostgreSQL (CORRECT for production)
Database Name: prozync
Host: dpg-xxxxx-a.oregon-postgres.render.com
Port: 5432
User: prozync_user
```

### ⚠️ Using SQLite (Local Dev):
```
Engine: django.db.backends.sqlite3
⚠️  Using SQLite (OK for local dev, use PostgreSQL for production)
Database Name: C:\...\db.sqlite3
File Exists: True
File Size: 0.30 MB
```

---

## How to Switch to PostgreSQL

If you're currently using SQLite and want to switch to PostgreSQL:

### Step 1: Create PostgreSQL Database
**On Render:**
1. Dashboard → New + → PostgreSQL
2. Fill out form and create
3. Copy "Internal Database URL"

**On Heroku:**
```bash
heroku addons:create heroku-postgresql:mini
```

### Step 2: Set Environment Variable

**Locally (for testing):**
```powershell
# Windows PowerShell
$env:DATABASE_URL="postgresql://user:pass@host/db"
```

**On Render:**
1. Web Service → Environment tab
2. Add: `DATABASE_URL` = [your PostgreSQL URL]

**On Heroku:**
```bash
heroku config:set DATABASE_URL="postgresql://..."
```

### Step 3: Run Migrations
```bash
python manage.py migrate
```

### Step 4: Verify
```bash
python check_database.py
```

Should now show PostgreSQL ✅

---

## Quick Reference Commands

| Task | Command |
|------|---------|
| Check database type | `python check_database.py` |
| Check environment | `python diagnose_environment.py` |
| Check via shell | `python manage.py shell` |
| Check DATABASE_URL | `echo $env:DATABASE_URL` (PowerShell) |
| List tables | `python manage.py dbshell` then `\dt` (PostgreSQL) |
| Check migrations | `python manage.py showmigrations` |

---

## Troubleshooting

### "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### "Could not connect to database"
- Check DATABASE_URL is correct
- Verify PostgreSQL database is running
- Check firewall/network settings

### "Using SQLite but want PostgreSQL"
- Set DATABASE_URL environment variable
- Restart your application
- Run `python check_database.py` to verify

---

## Summary

**To check if you're using PostgreSQL:**

1. **Quickest:** `python check_database.py`
2. **On Render:** Check dashboard for PostgreSQL database
3. **Via code:** Check if `DATABASE_URL` is set
4. **Via Django:** `python manage.py dbshell` (shows `psql` for PostgreSQL)

**Current Status:**
- **Local development:** Probably using SQLite ✓
- **Production (Render/Heroku):** Should use PostgreSQL ✓

Run `python check_database.py` now to see your current setup!
