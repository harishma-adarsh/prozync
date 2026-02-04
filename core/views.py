from django.db.models import Q
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone
import random
import string
from .models import (
    Profile, Project, Post, Comment, Like, Collaboration, Follower, 
    Notification, Invitation, ChatMessage, ConnectionRequest
)
from .serializers import (
    UserSerializer, ProfileSerializer, ProjectSerializer, 
    PostSerializer, CommentSerializer, NotificationSerializer,
    CollaborationSerializer, InvitationSerializer,
    SignupSerializer, SigninSerializer, ForgotPasswordSerializer, ResetPasswordSerializer,
    ChatMessageSerializer, ConnectionRequestSerializer
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

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        post = self.get_object()
        if not request.user.is_authenticated:
            return Response({"detail": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        comment_text = request.data.get('comment_text')
        if not comment_text:
            return Response({"detail": "Comment text is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        comment = Comment.objects.create(post=post, user=request.user, comment_text=comment_text)
        
        # Notify
        if post.user != request.user:
            Notification.objects.create(
                sender=request.user,
                receiver=post.user,
                post=post,
                message=f"{request.user.username} commented on your post"
            )
            
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        post = self.get_object()
        comments = post.comments.all().order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['full_name', 'user__username', 'profession']

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    @action(detail=False, methods=['get', 'patch', 'put'])
    def me(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        profile = request.user.profile
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

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

    @action(detail=True, methods=['post'])
    def connect(self, request, pk=None):
        profile = self.get_object()
        if not request.user.is_authenticated:
            return Response({"detail": "Not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        if request.user == profile.user:
            return Response({"detail": "Cannot connect to yourself"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already connected or pending
        existing = ConnectionRequest.objects.filter(
            (Q(sender=request.user, receiver=profile.user)) |
            (Q(sender=profile.user, receiver=request.user))
        ).first()
        
        if existing:
            if existing.status == 'ACCEPTED':
                return Response({"detail": "Already connected"})
            if existing.sender == request.user:
                return Response({"detail": "Request already sent"})
            else:
                return Response({"detail": "He/She already sent you a request. Please accept it."})
        
        con_request = ConnectionRequest.objects.create(sender=request.user, receiver=profile.user)
        
        # Notify
        Notification.objects.create(
            sender=request.user,
            receiver=profile.user,
            message=f"{request.user.username} sent you a connection request"
        )
        
        return Response(ConnectionRequestSerializer(con_request).data, status=status.HTTP_201_CREATED)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(receiver=self.request.user).order_by('-created_at')

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = SignupSerializer

    @extend_schema(request=SignupSerializer)
    @action(detail=False, methods=['post'])
    def signup(self, request):
        from django.db import transaction
        
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        full_name = request.data.get('full_name', '')
        
        # Validate required fields
        if not username or not email or not password:
            return Response({
                "detail": "Username, email, and password are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response({
                "detail": "Username already exists"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return Response({
                "detail": "Email already registered"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create user and profile in a transaction
        try:
            with transaction.atomic():
                # Create user with hashed password
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                
                # Profile will be created automatically by signal
                # But we'll update the full_name if provided
                if full_name:
                    profile = user.profile
                    profile.full_name = full_name
                    profile.save()
                
                return Response({
                    "detail": "Registration successful",
                    "username": user.username,
                    "email": user.email
                }, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({
                "detail": f"Registration failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(request=SigninSerializer)
    @action(detail=False, methods=['post'])
    def signin(self, request):
        from django.contrib.auth import authenticate
        from rest_framework.authtoken.models import Token
        
        username = request.data.get('username')
        password = request.data.get('password')
        
        # Validate input
        if not username or not password:
            return Response({
                "detail": "Username and password are required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        
        if user:
            # Ensure user is active
            if not user.is_active:
                return Response({
                    "detail": "This account has been deactivated"
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Ensure profile exists (for backward compatibility)
            if not hasattr(user, 'profile'):
                Profile.objects.create(user=user)
            
            # Get or create auth token
            token, created = Token.objects.get_or_create(user=user)
            
            # Return successful response
            return Response({
                'token': token.key,
                'user_id': user.pk,
                'username': user.username,
                'email': user.email
            })
        
        # Authentication failed
        return Response({
            "detail": "Invalid username or password"
        }, status=status.HTTP_401_UNAUTHORIZED)

    @extend_schema(request=ForgotPasswordSerializer)
    @action(detail=False, methods=['post'])
    def forgot_password(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "User with this email not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Generate 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Save OTP to profile
        profile = user.profile
        profile.otp = otp
        profile.otp_created_at = timezone.now()
        profile.save()
        
        # Send Email
        subject = 'Password Reset OTP for ProSync'
        message = f'Your OTP for password reset is: {otp}. It will expire in 10 minutes.'
        from_email = 'no-reply@prosync.com'
        recipient_list = [email]
        
        try:
            send_mail(subject, message, from_email, recipient_list)
            return Response({"detail": f"OTP sent to {email}"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(request=ResetPasswordSerializer)
    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')
        
        if not email or not otp or not new_password:
            return Response({"detail": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
            
        profile = user.profile
        
        # Check if OTP matches
        if profile.otp != otp:
            return Response({"detail": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if OTP is expired (e.g., 10 minutes)
        if profile.otp_created_at:
            expiry_time = profile.otp_created_at + timezone.timedelta(minutes=10)
            if timezone.now() > expiry_time:
                return Response({"detail": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Reset password
        user.set_password(new_password)
        user.save()
        
        # Clear OTP after successful reset
        profile.otp = None
        profile.otp_created_at = None
        profile.save()
        
        return Response({"detail": "Password reset successful"}, status=status.HTTP_200_OK)

class ChatMessageViewSet(viewsets.ModelViewSet):
    queryset = ChatMessage.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        user = self.request.user
        return ChatMessage.objects.filter(Q(sender=user) | Q(receiver=user))

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=False, methods=['get'])
    def conversation(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"detail": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        messages = ChatMessage.objects.filter(
            (Q(sender=request.user, receiver_id=user_id)) |
            (Q(sender_id=user_id, receiver=request.user))
        ).order_by('timestamp')
        
        # Mark as read
        messages.filter(receiver=request.user).update(is_read=True)
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

class InvitationViewSet(viewsets.ModelViewSet):
    queryset = Invitation.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = InvitationSerializer

    def get_queryset(self):
        return Invitation.objects.filter(receiver=self.request.user)

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        invitation = self.get_object()
        action_type = request.data.get('action') # 'ACCEPT' or 'REJECT'
        
        if action_type == 'ACCEPT':
            invitation.status = 'ACCEPTED'
            invitation.save()
            
            # Create collaboration
            Collaboration.objects.get_or_create(
                project=invitation.project,
                user=request.user,
                defaults={'role': 'Collaborator'}
            )
            
            # Notify owner
            Notification.objects.create(
                sender=request.user,
                receiver=invitation.project.owner,
                project=invitation.project,
                message=f"{request.user.username} accepted your invitation to {invitation.project.project_name}"
            )
            
            return Response({"detail": "Invitation accepted"})
        elif action_type == 'REJECT':
            invitation.status = 'REJECTED'
            invitation.save()
            return Response({"detail": "Invitation rejected"})
        
        return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def invite(self, request):
        project_id = request.data.get('project_id')
        user_id = request.data.get('user_id')
        
        if not project_id or not user_id:
            return Response({"detail": "project_id and user_id are required"}, status=status.HTTP_400_BAD_REQUEST)
            
        project = Project.objects.filter(id=project_id, owner=request.user).first()
        if not project:
            return Response({"detail": "Project not found or you are not the owner"}, status=status.HTTP_404_NOT_FOUND)
            
        receiver = User.objects.filter(id=user_id).first()
        if not receiver:
            return Response({"detail": "User to invite not found"}, status=status.HTTP_404_NOT_FOUND)
            
        invitation, created = Invitation.objects.get_or_create(
            project=project,
            receiver=receiver,
            defaults={'status': 'PENDING'}
        )
        
        if not created:
             return Response({"detail": "Invitation already sent"})
             
        Notification.objects.create(
            sender=request.user,
            receiver=receiver,
            project=project,
            message=f"{request.user.username} invited you to collaborate on {project.project_name}"
        )
        
        return Response(InvitationSerializer(invitation).data, status=status.HTTP_201_CREATED)

class ConnectionRequestViewSet(viewsets.ModelViewSet):
    queryset = ConnectionRequest.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConnectionRequestSerializer

    def get_queryset(self):
        return ConnectionRequest.objects.filter(receiver=self.request.user, status='PENDING')

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        con_request = self.get_object()
        action_type = request.data.get('action') # 'ACCEPT' or 'REJECT'
        
        if action_type == 'ACCEPT':
            con_request.status = 'ACCEPTED'
            con_request.save()
            
            # Notify sender
            Notification.objects.create(
                sender=request.user,
                receiver=con_request.sender,
                message=f"{request.user.username} accepted your connection request"
            )
            
            return Response({"detail": "Connection accepted"})
        elif action_type == 'REJECT':
            con_request.status = 'REJECTED'
            con_request.delete() # Or keep with status REJECTED
            return Response({"detail": "Connection rejected"})
        
        return Response({"detail": "Invalid action"}, status=status.HTTP_400_BAD_REQUEST)
