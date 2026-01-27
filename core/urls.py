from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, ProfileViewSet, PostViewSet, NotificationViewSet, AuthViewSet
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'posts', PostViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/signup/', AuthViewSet.as_view({'post': 'signup'}), name='signup'),
    path('auth/login/', obtain_auth_token, name='login'),
]
