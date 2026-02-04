# 🔴 DATA LOSS ISSUE - ROOT CAUSE IDENTIFIED

## THE PROBLEM

**Your data (posts, comments, likes, etc.) disappears after restart because:**

You're deploying to **Render/Heroku** which has **EPHEMERAL STORAGE**:
- ❌ SQLite database is stored as a file (`db.sqlite3`)
- ❌ On restart/redeploy, the entire file system is wiped
- ❌ Your `db.sqlite3` file is deleted
- ❌ All data is lost

## THE SOLUTION

**Switch from SQLite to PostgreSQL** for production deployment.

---

## 🚀 STEP-BY-STEP FIX

### For RENDER:

#### Step 1: Create PostgreSQL Database

1. Go to your Render Dashboard
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `prozync-db` (or any name)
   - **Database**: `prozync`
   - **User**: `prozync_user`
   - **Region**: Same as your web service
   - **Plan**: Free tier is fine for testing
4. Click **"Create Database"**
5. Wait for it to provision (1-2 minutes)

#### Step 2: Get Database URL

1. Open your new PostgreSQL database in Render
2. Scroll down to **"Connections"**
3. Copy the **"Internal Database URL"**
   - It looks like: `postgresql://user:password@host/database`

#### Step 3: Add Environment Variable

1. Go to your **Web Service** in Render
2. Go to **"Environment"** tab
3. Add new environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: [paste the Internal Database URL you copied]
4. Click **"Save Changes"**

#### Step 4: Deploy

1. Render will automatically redeploy
2. Or manually click **"Manual Deploy"** → **"Deploy latest commit"**

#### Step 5: Run Migrations

1. Go to **"Shell"** tab in your Render web service
2. Run:
   ```bash
   python manage.py migrate
   ```

3. (Optional) Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

---

### For HEROKU:

#### Step 1: Add PostgreSQL

```bash
heroku addons:create heroku-postgresql:mini
```

#### Step 2: Verify DATABASE_URL

```bash
heroku config:get DATABASE_URL
```

This should show your PostgreSQL connection string.

#### Step 3: Deploy

```bash
git push heroku main
```

#### Step 4: Run Migrations

```bash
heroku run python manage.py migrate
```

#### Step 5: (Optional) Create Superuser

```bash
heroku run python manage.py createsuperuser
```

---

## ✅ VERIFICATION

After switching to PostgreSQL:

1. **Create test data**:
   - Register users
   - Create posts
   - Add comments
   - Add likes

2. **Restart your service**:
   - Render: Click "Manual Deploy"
   - Heroku: `heroku restart`

3. **Check data**:
   - Login again
   - Data should still be there! ✅

---

## 📋 WHY THIS WORKS

### Before (SQLite):
```
Deployment → Creates db.sqlite3 file
Add data → Saved to db.sqlite3
Restart → File system wiped → db.sqlite3 deleted ❌
Result → All data lost
```

### After (PostgreSQL):
```
Deployment → Connects to PostgreSQL server
Add data → Saved to PostgreSQL (separate server)
Restart → File system wiped → PostgreSQL untouched ✅
Result → All data persists
```

---

## 🔧 YOUR CODE ALREADY SUPPORTS THIS!

**No code changes needed!** Your `settings.py` already has:

```python
# Line 69-73 in settings.py
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR}/db.sqlite3',  # Local fallback
        conn_max_age=600
    )
}
```

This means:
- ✅ If `DATABASE_URL` is set → Uses PostgreSQL
- ✅ If `DATABASE_URL` is not set → Uses SQLite (local dev)
- ✅ Automatically switches based on environment

---

## 📦 DEPENDENCIES

Make sure these are in your `requirements.txt`:

```txt
psycopg2-binary>=2.9.0  # PostgreSQL adapter
dj-database-url>=2.0.0  # Database URL parser
```

Check your `requirements.txt`:
```bash
cat requirements.txt | grep -E "psycopg2|dj-database-url"
```

If missing, add them:
```bash
pip install psycopg2-binary dj-database-url
pip freeze > requirements.txt
```

---

## 🎯 SUMMARY

| Issue | Solution | Status |
|-------|----------|--------|
| Data disappears after restart | Switch to PostgreSQL | ✅ Ready to implement |
| Code changes needed | None! Already configured | ✅ No changes needed |
| Dependencies needed | psycopg2-binary, dj-database-url | ✅ Check requirements.txt |
| Platform setup | Add PostgreSQL + DATABASE_URL | ⏳ Follow steps above |

---

## ⚡ QUICK START (RENDER)

```bash
# 1. Create PostgreSQL database in Render Dashboard
# 2. Copy "Internal Database URL"
# 3. Add as DATABASE_URL environment variable
# 4. Redeploy
# 5. Run: python manage.py migrate
# 6. Done! Data will now persist ✅
```

---

## 🆘 TROUBLESHOOTING

### "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Add PostgreSQL support"
git push
```

### "Could not connect to database"
- Check DATABASE_URL is set correctly
- Verify PostgreSQL database is running
- Check firewall/network settings

### "Relation does not exist"
```bash
# Run migrations
python manage.py migrate
```

---

## 📞 NEED HELP?

If you encounter issues:
1. Check Render/Heroku logs
2. Verify DATABASE_URL environment variable
3. Ensure PostgreSQL database is running
4. Run migrations: `python manage.py migrate`

---

## ✅ AFTER FIX

Once PostgreSQL is set up:
- ✅ Users persist after restart
- ✅ Posts persist after restart
- ✅ Comments persist after restart
- ✅ Likes persist after restart
- ✅ All data persists after restart

**Your data loss issue will be completely resolved!** 🎉
