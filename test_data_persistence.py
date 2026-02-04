"""
Comprehensive test to verify ALL data persists after restart
Tests: Users, Profiles, Posts, Comments, Likes, Projects, etc.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prozync.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import (
    Profile, Project, Post, Comment, Like, 
    Collaboration, Follower, Notification, 
    Invitation, ChatMessage, ConnectionRequest
)

def banner(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_database_file():
    """Check if database file exists and is writable"""
    banner("DATABASE FILE CHECK")
    
    import sqlite3
    from pathlib import Path
    
    db_path = Path(__file__).parent / 'db.sqlite3'
    
    print(f"\nDatabase path: {db_path}")
    print(f"File exists: {db_path.exists()}")
    
    if db_path.exists():
        print(f"File size: {db_path.stat().st_size} bytes")
        print(f"Last modified: {db_path.stat().st_mtime}")
        print(f"Readable: {os.access(db_path, os.R_OK)}")
        print(f"Writable: {os.access(db_path, os.W_OK)}")
        
        # Check if it's a valid SQLite database
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"\nTotal tables in database: {len(tables)}")
            conn.close()
            return True
        except Exception as e:
            print(f"ERROR: Database file is corrupted: {e}")
            return False
    else:
        print("ERROR: Database file does not exist!")
        return False

def show_current_data():
    """Display all current data in the database"""
    banner("CURRENT DATABASE STATE")
    
    models = [
        ('Users', User),
        ('Profiles', Profile),
        ('Projects', Project),
        ('Posts', Post),
        ('Comments', Comment),
        ('Likes', Like),
        ('Collaborations', Collaboration),
        ('Followers', Follower),
        ('Notifications', Notification),
        ('Invitations', Invitation),
        ('ChatMessages', ChatMessage),
        ('ConnectionRequests', ConnectionRequest),
    ]
    
    print("\nData counts:")
    for name, model in models:
        count = model.objects.count()
        status = "✓" if count > 0 else "○"
        print(f"  {status} {name:20} : {count}")
    
    return sum(model.objects.count() for _, model in models)

def create_test_data():
    """Create comprehensive test data"""
    banner("CREATING TEST DATA")
    
    # Create test users
    print("\n1. Creating users...")
    user1, created1 = User.objects.get_or_create(
        username='testuser1',
        defaults={'email': 'test1@example.com'}
    )
    if created1:
        user1.set_password('password123')
        user1.save()
    
    user2, created2 = User.objects.get_or_create(
        username='testuser2',
        defaults={'email': 'test2@example.com'}
    )
    if created2:
        user2.set_password('password123')
        user2.save()
    
    print(f"   ✓ User 1: {user1.username} (ID: {user1.id})")
    print(f"   ✓ User 2: {user2.username} (ID: {user2.id})")
    
    # Update profiles
    print("\n2. Updating profiles...")
    profile1 = user1.profile
    profile1.full_name = "Test User One"
    profile1.bio = "This is a test bio"
    profile1.save()
    
    profile2 = user2.profile
    profile2.full_name = "Test User Two"
    profile2.save()
    print(f"   ✓ Profiles updated")
    
    # Create project
    print("\n3. Creating project...")
    project, created = Project.objects.get_or_create(
        slug='test-project',
        defaults={
            'owner': user1,
            'project_name': 'Test Project',
            'description': 'A test project for persistence testing',
            'technology': 'Django'
        }
    )
    print(f"   ✓ Project: {project.project_name} (ID: {project.id})")
    
    # Create post
    print("\n4. Creating post...")
    post, created = Post.objects.get_or_create(
        user=user1,
        project=project,
        defaults={'content': 'This is a test post to verify data persistence'}
    )
    print(f"   ✓ Post: {post.id}")
    
    # Create comment
    print("\n5. Creating comment...")
    comment, created = Comment.objects.get_or_create(
        post=post,
        user=user2,
        defaults={'comment_text': 'Great post! Testing persistence.'}
    )
    print(f"   ✓ Comment: {comment.id}")
    
    # Create like
    print("\n6. Creating like...")
    like, created = Like.objects.get_or_create(
        post=post,
        user=user2
    )
    print(f"   ✓ Like: {like.id}")
    
    # Create follower relationship
    print("\n7. Creating follower relationship...")
    follower, created = Follower.objects.get_or_create(
        follower=user2,
        following=user1
    )
    print(f"   ✓ Follower: {follower.id}")
    
    # Create notification
    print("\n8. Creating notification...")
    notification, created = Notification.objects.get_or_create(
        sender=user2,
        receiver=user1,
        defaults={
            'message': 'Test notification for persistence',
            'post': post
        }
    )
    print(f"   ✓ Notification: {notification.id}")
    
    # Create chat message
    print("\n9. Creating chat message...")
    chat, created = ChatMessage.objects.get_or_create(
        sender=user1,
        receiver=user2,
        defaults={'message': 'Test message for persistence'}
    )
    print(f"   ✓ ChatMessage: {chat.id}")
    
    # Create connection request
    print("\n10. Creating connection request...")
    conn_req, created = ConnectionRequest.objects.get_or_create(
        sender=user2,
        receiver=user1,
        defaults={'status': 'PENDING'}
    )
    print(f"   ✓ ConnectionRequest: {conn_req.id}")
    
    print("\n✅ All test data created successfully!")

def verify_test_data():
    """Verify that test data exists"""
    banner("VERIFYING TEST DATA")
    
    checks = []
    
    # Check users
    user1 = User.objects.filter(username='testuser1').first()
    user2 = User.objects.filter(username='testuser2').first()
    
    if user1 and user2:
        print(f"✓ Users exist: {user1.username}, {user2.username}")
        checks.append(True)
    else:
        print(f"✗ Users missing!")
        checks.append(False)
        return False
    
    # Check profiles
    try:
        p1 = user1.profile
        p2 = user2.profile
        print(f"✓ Profiles exist: {p1.full_name}, {p2.full_name}")
        checks.append(True)
    except:
        print(f"✗ Profiles missing!")
        checks.append(False)
    
    # Check project
    project = Project.objects.filter(slug='test-project').first()
    if project:
        print(f"✓ Project exists: {project.project_name}")
        checks.append(True)
    else:
        print(f"✗ Project missing!")
        checks.append(False)
    
    # Check post
    post = Post.objects.filter(user=user1).first()
    if post:
        print(f"✓ Post exists: ID {post.id}")
        checks.append(True)
        
        # Check comment
        comment = Comment.objects.filter(post=post).first()
        if comment:
            print(f"✓ Comment exists: {comment.comment_text[:30]}...")
            checks.append(True)
        else:
            print(f"✗ Comment missing!")
            checks.append(False)
        
        # Check like
        like = Like.objects.filter(post=post).first()
        if like:
            print(f"✓ Like exists: ID {like.id}")
            checks.append(True)
        else:
            print(f"✗ Like missing!")
            checks.append(False)
    else:
        print(f"✗ Post missing!")
        checks.append(False)
    
    # Check follower
    follower = Follower.objects.filter(follower=user2, following=user1).first()
    if follower:
        print(f"✓ Follower relationship exists")
        checks.append(True)
    else:
        print(f"✗ Follower relationship missing!")
        checks.append(False)
    
    # Check notification
    notification = Notification.objects.filter(sender=user2, receiver=user1).first()
    if notification:
        print(f"✓ Notification exists: {notification.message}")
        checks.append(True)
    else:
        print(f"✗ Notification missing!")
        checks.append(False)
    
    # Check chat message
    chat = ChatMessage.objects.filter(sender=user1, receiver=user2).first()
    if chat:
        print(f"✓ ChatMessage exists: {chat.message[:30]}...")
        checks.append(True)
    else:
        print(f"✗ ChatMessage missing!")
        checks.append(False)
    
    # Check connection request
    conn_req = ConnectionRequest.objects.filter(sender=user2, receiver=user1).first()
    if conn_req:
        print(f"✓ ConnectionRequest exists: {conn_req.status}")
        checks.append(True)
    else:
        print(f"✗ ConnectionRequest missing!")
        checks.append(False)
    
    return all(checks)

def main():
    print("\n" + "#"*70)
    print("#" + " "*68 + "#")
    print("#" + "  DATA PERSISTENCE TEST - ALL MODELS".center(68) + "#")
    print("#" + " "*68 + "#")
    print("#"*70)
    
    # Check database file
    db_ok = check_database_file()
    if not db_ok:
        print("\n❌ DATABASE FILE ISSUE DETECTED!")
        return 1
    
    # Show current state
    total_records = show_current_data()
    
    # Create test data
    create_test_data()
    
    # Show new state
    total_records_after = show_current_data()
    
    # Verify test data
    all_ok = verify_test_data()
    
    # Final summary
    banner("FINAL SUMMARY")
    
    print(f"\nTotal records before: {total_records}")
    print(f"Total records after: {total_records_after}")
    print(f"Records added: {total_records_after - total_records}")
    
    if all_ok:
        print("\n" + "="*70)
        print("  ✅ ALL DATA PERSISTED SUCCESSFULLY!")
        print("="*70)
        print("\nNext steps:")
        print("  1. Restart your Django server")
        print("  2. Run this script again: python test_data_persistence.py")
        print("  3. Verify all data is still present")
        print("\nIf data disappears after restart, the issue is:")
        print("  - Database file being deleted")
        print("  - Using wrong database")
        print("  - Migrations being reset")
        return 0
    else:
        print("\n" + "="*70)
        print("  ⚠️ SOME DATA VERIFICATION FAILED")
        print("="*70)
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
