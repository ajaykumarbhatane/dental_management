"""
ViewSets for authentication endpoints.

Provides:
- User registration
- User login (with JWT token)
- Token refresh
- Logout
- Current user profile
"""

from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import CustomUser
from apps.users.serializers import (
    CustomUserSerializer,
    UserRegistrationSerializer,
    UserLoginSerializer,
    ChangePasswordSerializer,
    UpdateProfileSerializer,
)
from core.utils import filter_by_user_clinic
from core.exceptions import APIResponse
import logging

logger = logging.getLogger(__name__)


class AuthViewSet(viewsets.ViewSet):
    """
    ViewSet for authentication endpoints.
    
    Endpoints:
    - POST /api/auth/register/ - Register new user
    - POST /api/auth/login/ - Login and get JWT tokens
    - POST /api/auth/refresh/ - Refresh access token
    - POST /api/auth/logout/ - Logout (invalidate refresh token)
    - GET /api/auth/me/ - Get current user profile
    - PUT /api/auth/me/ - Update current user profile
    - POST /api/auth/change-password/ - Change password
    """

    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Register a new user."""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return APIResponse.success(
                data=CustomUserSerializer(user).data,
                message='User registered successfully',
                status_code=status.HTTP_201_CREATED
            )
        return APIResponse.error(
            message='Registration failed',
            code='registration_error',
            details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        Login user and return JWT tokens.
        
        Request:
            {
                "email": "user@example.com",
                "password": "password123"
            }
        
        Response:
            {
                "success": true,
                "data": {
                    "user": {...},
                    "access": "token...",
                    "refresh": "token..."
                }
            }
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return APIResponse.success(
                data={
                    'user': CustomUserSerializer(user).data,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
                message='Login successful'
            )

        return APIResponse.error(
            message='Login failed',
            code='login_error',
            details=serializer.errors,
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Logout user (add token to blacklist if using TokenBlacklistApp).
        
        For stateless JWT, client should simply delete the token.
        """
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception as e:
            logger.warning(f"Logout error: {str(e)}")

        return APIResponse.success(message='Logout successful')

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile."""
        user = request.user
        return APIResponse.success(
            data=CustomUserSerializer(user).data,
            message='Profile retrieved successfully'
        )

    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Update current user profile (limited fields)."""
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            user = serializer.save()
            return APIResponse.success(
                data=CustomUserSerializer(user).data,
                message='Profile updated successfully'
            )

        return APIResponse.error(
            message='Update failed',
            code='update_error',
            details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Change user password."""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user = serializer.save()
            return APIResponse.success(
                data=CustomUserSerializer(user).data,
                message='Password changed successfully'
            )

        return APIResponse.error(
            message='Password change failed',
            code='password_change_error',
            details=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Customized JWT token obtain view.
    
    Extends DRF SimpleJWT with custom token claims.
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        # Add additional user data to response
        if response.status_code == 200:
            try:
                user = CustomUser.objects.get(email=request.data.get('email'))
                response.data['user'] = CustomUserSerializer(user).data
            except CustomUser.DoesNotExist:
                pass

        return response
