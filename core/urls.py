from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProjectViewSet, ProfileViewSet, PostViewSet, NotificationViewSet, 
    AuthViewSet, ChatMessageViewSet, InvitationViewSet, ConnectionRequestViewSet
)
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'posts', PostViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'messages', ChatMessageViewSet, basename='message')
router.register(r'invitations', InvitationViewSet, basename='invitation')
router.register(r'connections', ConnectionRequestViewSet, basename='connection')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', AuthViewSet.as_view({'post': 'signup'}), name='signup'),
    path('auth/signin/', AuthViewSet.as_view({'post': 'signin'}), name='signin'),
    path('auth/login/', obtain_auth_token, name='login'),
    path('auth/forgot-password/', AuthViewSet.as_view({'post': 'forgot_password'}), name='forgot_password'),
    path('auth/reset-password/', AuthViewSet.as_view({'post': 'reset_password'}), name='reset_password'),
]
