from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import (
    Profile, Project, Post, Comment, Like, Collaboration, Follower, 
    Notification, Invitation, ChatMessage, ConnectionRequest,
    SavedProject, SavedPost
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    receiver_name = serializers.CharField(source='receiver.username', read_only=True)
    receiver_username = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'sender_name', 'receiver', 'receiver_name', 'receiver_username', 'message', 'is_read', 'timestamp']
        read_only_fields = ['sender']

    def validate(self, attrs):
        # Prevent messaging self
        request = self.context.get('request')
        if request and request.user:
            receiver = attrs.get('receiver')
            if receiver == request.user:
                raise serializers.ValidationError({"detail": "You cannot send messages to yourself."})
            
            # If username is provided, we'll handle the lookup in perform_create, 
            # but we can do a quick check here if receiver ID is 0 or missing
            if not receiver and not attrs.get('receiver_username'):
                raise serializers.ValidationError({"receiver": "Either receiver ID or receiver_username is required."})
        
        return attrs

class ConnectionRequestSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    receiver_name = serializers.CharField(source='receiver.username', read_only=True)

    class Meta:
        model = ConnectionRequest
        fields = ['id', 'sender', 'sender_name', 'receiver', 'receiver_name', 'status', 'created_at']
        read_only_fields = ['sender', 'status']

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', required=False)
    follower_count = serializers.SerializerMethodField()
    repo_count = serializers.SerializerMethodField()
    connection_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'username', 'email', 'full_name', 'phone', 'bio', 'profession', 'profile_pic', 'follower_count', 'repo_count', 'connection_status']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        email = user_data.get('email')
        
        if email:
            instance.user.email = email
            instance.user.save()
            
        return super().update(instance, validated_data)

    @extend_schema_field(serializers.IntegerField())
    def get_follower_count(self, obj) -> int:
        return obj.user.follower_set.count()

    @extend_schema_field(serializers.IntegerField())
    def get_repo_count(self, obj) -> int:
        return obj.user.owned_projects.count()

    @extend_schema_field(serializers.CharField())
    def get_connection_status(self, obj) -> str:
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
        
        if request.user == obj.user:
            return "SELF"
        
        rel = ConnectionRequest.objects.filter(
            (Q(sender=request.user, receiver=obj.user)) |
            (Q(sender=obj.user, receiver=request.user))
        ).first()
        
        if rel:
            if rel.status == 'ACCEPTED':
                return "CONNECTED"
            if rel.sender == request.user:
                return "PENDING_SENT"
            return "PENDING_RECEIVED"
            
        return "NONE"

class ProjectSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    collaborator_count = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()

    def get_cover_image(self, obj):
        if obj.cover_image:
            # Try to get request from context
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            # Fallback for localhost if request is missing
            return f"http://127.0.0.1:8000{obj.cover_image.url}"
        return None

    class Meta:
        model = Project
        fields = ['id', 'owner', 'owner_name', 'project_name', 'slug', 'description', 'technology', 'project_zip', 'cover_image', 'is_private', 'is_pinned', 'collaborator_count', 'is_saved', 'created_at']
        read_only_fields = ['owner', 'slug']

    @extend_schema_field(serializers.BooleanField())
    def get_is_saved(self, obj) -> bool:
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return SavedProject.objects.filter(user=request.user, project=obj).exists()

    @extend_schema_field(serializers.IntegerField())
    def get_collaborator_count(self, obj) -> int:
        return obj.collaborators_list.count()

class PostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'user', 'username', 'project', 'image', 'content', 'like_count', 'comment_count', 'is_liked', 'is_saved', 'created_at']

    @extend_schema_field(serializers.BooleanField())
    def get_is_liked(self, obj) -> bool:
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return Like.objects.filter(post=obj, user=request.user).exists()

    @extend_schema_field(serializers.BooleanField())
    def get_is_saved(self, obj) -> bool:
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return SavedPost.objects.filter(user=request.user, post=obj).exists()

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'user', 'username', 'comment_text', 'created_at']

class NotificationSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'sender', 'sender_name', 'receiver', 'status', 'post', 'project', 'message', 'is_read', 'created_at']

class CollaborationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Collaboration
        fields = ['id', 'project', 'user', 'username', 'role', 'joined_at']

class InvitationSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    sender_name = serializers.CharField(source='project.owner.username', read_only=True)
    
    class Meta:
        model = Invitation
        fields = ['id', 'project', 'project_name', 'sender_name', 'receiver', 'status', 'sent_at']

class SavedProjectSerializer(serializers.ModelSerializer):
    project_details = ProjectSerializer(source='project', read_only=True)
    
    class Meta:
        model = SavedProject
        fields = ['id', 'user', 'project', 'project_details', 'saved_at']

class SavedPostSerializer(serializers.ModelSerializer):
    post_details = PostSerializer(source='post', read_only=True)
    
    class Meta:
        model = SavedPost
        fields = ['id', 'user', 'post', 'post_details', 'saved_at']

class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New passwords do not match."})
        return attrs

class SignupSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(max_length=200, required=False)

class SigninSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
