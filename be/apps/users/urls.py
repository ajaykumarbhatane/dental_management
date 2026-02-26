"""
URL configuration for user management endpoints.
"""

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from apps.users.views_management import UserManagementViewSet

router = SimpleRouter()
router.register(r'', UserManagementViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]
