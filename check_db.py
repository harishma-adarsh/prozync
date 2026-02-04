import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prozync.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile

print(f"Total Users: {User.objects.count()}")
print(f"Total Profiles: {Profile.objects.count()}")
print("\nUser Details:")
for user in User.objects.all():
    try:
        profile = user.profile
        print(f"✓ User: {user.username}, Email: {user.email}, Profile exists: YES")
    except Profile.DoesNotExist:
        print(f"✗ User: {user.username}, Email: {user.email}, Profile exists: NO")
