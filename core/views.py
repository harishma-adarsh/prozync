from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Profile, Project, Post, Comment, Like, Collaboration, Follower, Notification, Invitation
from .serializers import (
    UserSerializer, ProfileSerializer, ProjectSerializer, 
    PostSerializer, CommentSerializer, NotificationSerializer,
    CollaborationSerializer, InvitationSerializer
)

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['project_name', 'technology', 'description']

    @action(detail=False, methods=['get'])
    def my_repos(self, request):
        if request.user.is_authenticated:
            projects = Project.objects.filter(owner=request.user)
            serializer = self.get_serializer(projects, many=True)
            return Response(serializer.data)
        return Response({"detail": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        if not request.user.is_authenticated:
            return Response({"detail": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        like, created = Like.objects.get_or_create(post=post, user=request.user)
        if not created:
            like.delete()
            return Response({"detail": "Unliked"})
        
        # Notify
        Notification.objects.create(
            sender=request.user,
            receiver=post.user,
            post=post,
            message=f"{request.user.username} liked your post"
        )
        return Response({"detail": "Liked"})

class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name', 'user__username', 'profession']

    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        profile = self.get_object()
        if not request.user.is_authenticated:
            return Response({"detail": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        if request.user == profile.user:
            return Response({"detail": "Cannot follow self"}, status=status.HTTP_400_BAD_REQUEST)
        
        follower_rel, created = Follower.objects.get_or_create(follower=request.user, following=profile.user)
        if not created:
            follower_rel.delete()
            return Response({"detail": "Unfollowed"})
            
        Notification.objects.create(
            sender=request.user,
            receiver=profile.user,
            message=f"{request.user.username} started following you"
        )
        return Response({"detail": "Followed"})

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user).order_by('-created_at')

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'])
    def signup(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        full_name = request.data.get('full_name', '')
        
        if not username or not email or not password:
            return Response({"detail": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({"detail": "Username exists"}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user, full_name=full_name)
        return Response({"detail": "Created"}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def forgot_password(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "User with this email not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # In a real app, you'd send an actual email/OTP here.
        # For now, we simulate the success.
        return Response({"detail": "OTP sent to your email (Dev mode: use 1234)"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        
        if not email or not otp or not new_password:
            return Response({"detail": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)
            
        if otp != "1234": # Simulated OTP check
            return Response({"detail": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password reset successful"}, status=status.HTTP_200_OK)
