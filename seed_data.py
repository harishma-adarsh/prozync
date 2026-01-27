import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prozync.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import Profile, Project, Post, Collaboration, Follower, Notification

def seed():
    # User 1
    user1, _ = User.objects.get_or_create(username='johndoe', email='john@example.com')
    user1.set_password('password123')
    user1.save()
    Profile.objects.get_or_create(
        user=user1, 
        full_name='John Doe', 
        profession='Full Stack Developer',
        bio='I love building things.'
    )

    # User 2
    user2, _ = User.objects.get_or_create(username='developer10', email='dev10@example.com')
    user2.set_password('password123')
    user2.save()
    Profile.objects.get_or_create(
        user=user2, 
        full_name='Jane Smith', 
        profession='Expert in Flutter',
        bio='Flutter enthusiast.'
    )

    # Project
    project, _ = Project.objects.get_or_create(
        owner=user1,
        project_name='prozync-mobile',
        slug='prozync-mobile',
        defaults={
            'description': 'A professional cross-platform mobile application built with Flutter.',
            'technology': 'Flutter'
        }
    )

    # Collaboration
    Collaboration.objects.get_or_create(
        project=project,
        user=user2,
        defaults={'role': 'Contributor'}
    )

    # Post
    post, _ = Post.objects.get_or_create(
        user=user1,
        project=project,
        content='Just launched the new UI design for ProSync!'
    )

    # Follower
    Follower.objects.get_or_create(follower=user2, following=user1)

    # Notification
    Notification.objects.create(
        sender=user2,
        receiver=user1,
        message='Jane Smith started following you',
        is_read=False
    )

    print("Database seeded with ProSync Diagram structure!")

if __name__ == '__main__':
    seed()
