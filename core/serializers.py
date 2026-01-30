from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import serializers
from .models import (
    Profile, Project, Post, Comment, Like, Collaboration, Follower, 
    Notification, Invitation, ChatMessage, ConnectionRequest
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    receiver_name = serializers.CharField(source='receiver.username', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'sender', 'sender_name', 'receiver', 'receiver_name', 'message', 'is_read', 'timestamp']
        read_only_fields = ['sender']

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

    def get_follower_count(self, obj):
        return obj.user.follower_set.count()

    def get_repo_count(self, obj):
        return obj.user.owned_projects.count()

    def get_connection_status(self, obj):
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
    
    class Meta:
        model = Project
        fields = ['id', 'owner', 'owner_name', 'project_name', 'slug', 'description', 'technology', 'project_zip', 'cover_image', 'is_private', 'collaborator_count', 'created_at']

    def get_collaborator_count(self, obj):
        return obj.collaborators_list.count()

class PostSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    like_count = serializers.IntegerField(source='likes.count', read_only=True)
    comment_count = serializers.IntegerField(source='comments.count', read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'user', 'username', 'project', 'image', 'content', 'like_count', 'comment_count', 'created_at']

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

# --- Auth Serializers for Documentation ---

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
