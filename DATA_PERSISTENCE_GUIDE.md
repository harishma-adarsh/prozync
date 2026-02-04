# DATA PERSISTENCE DIAGNOSTIC GUIDE

## Issue: All data (posts, comments, likes, etc.) disappears after restart

## Possible Causes & Solutions:

### 1. **Are you running migrations on every restart?** ❌
If you're running `python manage.py migrate --run-syncdb` or deleting migrations, this will reset your database.

**Check:**
```bash
# DON'T do this on restart:
python manage.py flush  # This deletes all data!
python manage.py migrate --run-syncdb  # This can reset data
```

**Solution:**
Only run `python manage.py migrate` (without --run-syncdb)

---

### 2. **Are you using a deployment platform (Render, Heroku, etc.)?** 🔄
Many platforms use **ephemeral file systems** where SQLite databases are deleted on restart.

**Check:**
- Are you deploying to Render/Heroku/Railway?
- Is your DATABASE_URL environment variable set?

**Solution:**
Use PostgreSQL for production instead of SQLite.

**For Render/Heroku:**
```bash
# Add PostgreSQL database
# Set DATABASE_URL environment variable
# Your settings.py already supports this via dj_database_url
```

---

### 3. **Is db.sqlite3 in .gitignore?** 📁
If you're pulling from git and db.sqlite3 is ignored, you'll lose data.

**Check:**
```bash
cat .gitignore  # Look for db.sqlite3
```

**Current status:** ✓ db.sqlite3 IS in .gitignore (line 4)

**This is CORRECT for development** - each developer should have their own database.

---

### 4. **Are you deleting the database file manually?** 🗑️
Check if any scripts or processes are deleting db.sqlite3.

**Check:**
```bash
# Look for these commands in your scripts:
rm db.sqlite3
del db.sqlite3
python manage.py flush
```

---

### 5. **Are you using Docker with volumes not mounted?** 🐳
If using Docker without persistent volumes, data will be lost.

**Solution:**
Mount a volume for the database:
```yaml
volumes:
  - ./db.sqlite3:/app/db.sqlite3
```

---

## MOST LIKELY CAUSE FOR YOUR ISSUE:

### **You're deploying to a platform with ephemeral storage (Render/Heroku)**

**Evidence:**
- You have `Procfile` (Heroku/Render deployment)
- You have `build.sh` (Render deployment script)
- Settings use `dj_database_url` (for PostgreSQL)

**The Problem:**
Platforms like Render/Heroku have **ephemeral file systems**:
- SQLite database is stored in the file system
- On restart/redeploy, the file system is wiped
- All data in db.sqlite3 is lost

**The Solution:**
Use PostgreSQL instead of SQLite for production.

---

## IMMEDIATE FIX:

### Option 1: Add PostgreSQL to your deployment (RECOMMENDED)

1. **On Render:**
   - Create a PostgreSQL database
   - Copy the "Internal Database URL"
   - Add it as `DATABASE_URL` environment variable

2. **On Heroku:**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

3. **Your code already supports this!**
   ```python
   # settings.py line 70-73
   DATABASES = {
       'default': dj_database_url.config(
           default=f'sqlite:///{BASE_DIR}/db.sqlite3',  # Local fallback
           conn_max_age=600
       )
   }
   ```

4. **Run migrations on production:**
   ```bash
   python manage.py migrate
   ```

### Option 2: Use local development only

If you're only running locally (not deploying):
- Your data SHOULD persist
- Run the test: `python test_data_persistence.py`
- Restart server
- Run test again - data should still be there

---

## TESTING INSTRUCTIONS:

### Test 1: Verify data persists locally
```bash
# 1. Create test data
python test_data_persistence.py

# 2. Stop the server (Ctrl+C)

# 3. Restart the server
python manage.py runserver

# 4. Check data again
python test_data_persistence.py
```

**Expected:** All data should still be present

### Test 2: Check where you're running
```bash
# Are you running locally or on a platform?
echo "Local: Data persists in db.sqlite3"
echo "Render/Heroku: Need PostgreSQL"
```

---

## QUICK DIAGNOSIS:

Run this command to check your environment:
```bash
python diagnose_environment.py
```

This will tell you:
- ✓ Database type (SQLite/PostgreSQL)
- ✓ Database location
- ✓ If DATABASE_URL is set
- ✓ If you're using ephemeral storage
- ✓ Current data counts

---

## SUMMARY:

| Environment | Database | Data Persists? | Solution |
|-------------|----------|----------------|----------|
| Local Dev | SQLite | ✅ YES | Use as-is |
| Render/Heroku | SQLite | ❌ NO | Switch to PostgreSQL |
| Render/Heroku | PostgreSQL | ✅ YES | Already correct |

**Next Step:** Tell me where you're running this (local/Render/Heroku) and I'll provide the exact fix!
