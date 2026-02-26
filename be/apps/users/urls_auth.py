"""
URL configuration for authentication endpoints.
"""

from django.urls import path
from rest_framework.routers import SimpleRouter
from apps.users.views import AuthViewSet, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

router = SimpleRouter()
router.register(r'', AuthViewSet, basename='auth')

urlpatterns = router.urls + [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
