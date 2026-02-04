import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prozync.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

# Test existing users
users = User.objects.all()
print("Testing authentication for existing users:\n")

for user in users:
    print(f"User: {user.username}")
    print(f"  - Has usable password: {user.has_usable_password()}")
    print(f"  - Is active: {user.is_active}")
    
    # Try to authenticate with a test password
    # Note: We can't test with actual password without knowing it
    test_auth = authenticate(username=user.username, password='wrongpassword')
    print(f"  - Auth with wrong password: {test_auth}")
    print()

# Show password hash for debugging
print("\nPassword hash info:")
for user in users:
    print(f"{user.username}: {user.password[:50]}...")
