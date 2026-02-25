from django.contrib import admin
from .models import (
    Profile, Project, Post, Comment, Like, Collaboration, Follower, 
    Notification, Invitation, ChatMessage, ConnectionRequest,
    SavedProject, SavedPost
)

admin.site.register(Profile)
admin.site.register(Project)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Collaboration)
admin.site.register(Follower)
admin.site.register(Notification)
admin.site.register(Invitation)
admin.site.register(ChatMessage)
admin.site.register(ConnectionRequest)
admin.site.register(SavedProject)
admin.site.register(SavedPost)
