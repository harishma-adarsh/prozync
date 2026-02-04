from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Profile


class Command(BaseCommand):
    help = 'Ensure all users have profiles'

    def handle(self, *args, **options):
        users_without_profile = []
        users_with_profile = []
        
        for user in User.objects.all():
            try:
                # Try to access the profile
                _ = user.profile
                users_with_profile.append(user.username)
            except Profile.DoesNotExist:
                # Create profile if it doesn't exist
                Profile.objects.create(user=user)
                users_without_profile.append(user.username)
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created profile for user: {user.username}')
                )
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(f'Total users: {User.objects.count()}')
        self.stdout.write(f'Users with profiles: {len(users_with_profile)}')
        self.stdout.write(f'Profiles created: {len(users_without_profile)}')
        self.stdout.write('='*50)
        
        if not users_without_profile:
            self.stdout.write(
                self.style.SUCCESS('\n✓ All users already have profiles!')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\n✓ Successfully created missing profiles!')
            )
