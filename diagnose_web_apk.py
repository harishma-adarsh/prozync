"""
Quick diagnostic to check your current API setup
"""

print("""
╔══════════════════════════════════════════════════════════════════════╗
║              WEB vs APK SYNC ISSUE - DIAGNOSTIC                      ║
╚══════════════════════════════════════════════════════════════════════╝

QUESTION 1: Where is your Django backend currently running?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

A) Locally on your computer (http://localhost:8000 or http://127.0.0.1:8000)
B) Deployed on Render (https://something.onrender.com)
C) Deployed on Heroku (https://something.herokuapp.com)
D) Other cloud platform

Your answer: _____


QUESTION 2: Where is your mobile APK connecting to?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Check your mobile app code for the API base URL.

Common file locations:
- Flutter: lib/config/api_config.dart or lib/services/api_service.dart
- React Native: src/config/api.js or src/services/api.js
- Native Android: app/src/main/java/.../ApiConfig.java

Look for something like:
  baseUrl = "http://..."
  API_URL = "http://..."
  BASE_URL = "http://..."

Your APK's current API URL: _____


QUESTION 3: What happens when you test?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Test A - Create account on WEB:
  1. Go to your web version
  2. Register a new user (e.g., username: "webtest")
  3. Did it work? YES / NO

Test B - Try to login with same account on APK:
  1. Open your mobile APK
  2. Try to login with username: "webtest"
  3. Did it work? YES / NO

If Test A = YES but Test B = NO:
  → Your web and APK are using DIFFERENT databases! ❌


DIAGNOSIS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Scenario 1: BOTH using localhost
  Web: http://localhost:8000
  APK: http://localhost:8000 or http://10.0.2.2:8000
  
  Problem: APK can't reach localhost on your computer!
  Solution: Deploy backend to production (Render/Heroku)


Scenario 2: Different backends
  Web: https://backend-a.onrender.com
  APK: https://backend-b.herokuapp.com
  
  Problem: Two different databases!
  Solution: Point APK to same URL as web


Scenario 3: Web on production, APK on localhost
  Web: https://your-app.onrender.com
  APK: http://localhost:8000
  
  Problem: APK using local database, web using production database
  Solution: Update APK to use production URL


THE FIX:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Deploy your backend to production
  → Get a public URL (e.g., https://prozync.onrender.com)

Step 2: Update your APK configuration
  → Change baseUrl to your production URL

Step 3: Rebuild your APK
  → flutter build apk (or equivalent)

Step 4: Test
  → Create user on web
  → Login with same user on APK
  → Should work! ✅


CURRENT STATUS CHECK:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your Django API endpoints:
  ✓ /api/auth/signup/
  ✓ /api/auth/signin/
  ✓ /api/profiles/
  ✓ /api/posts/
  ✓ /api/projects/

These endpoints work for BOTH web and APK if they point to the same URL!


NEXT STEPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Answer the questions above
2. Read: WEB_APK_SYNC_ISSUE.md
3. Deploy backend to production (if not already)
4. Update APK configuration
5. Rebuild and test

═══════════════════════════════════════════════════════════════════════

Need help? Tell me:
  1. Where is your web version running?
  2. What's in your APK's API configuration file?
  3. Are you using Flutter, React Native, or native Android?

""")
