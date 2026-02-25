"""
Script to create a superuser automatically
Run this after deployment to create an admin user
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prozync.settings')
django.setup()

from django.contrib.auth.models import User

# Superuser credentials (change these!)
SUPERUSER_USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@prozync.com')
SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'changeme123')

# Create superuser if it doesn't exist
if not User.objects.filter(username=SUPERUSER_USERNAME).exists():
    User.objects.create_superuser(
        username=SUPERUSER_USERNAME,
        email=SUPERUSER_EMAIL,
        password=SUPERUSER_PASSWORD
    )
    print(f"✅ Superuser '{SUPERUSER_USERNAME}' created successfully!")
else:
    print(f"ℹ️  Superuser '{SUPERUSER_USERNAME}' already exists.")
