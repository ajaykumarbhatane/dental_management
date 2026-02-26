"""
User management ViewSet (for admin to manage users in clinic).

Provides:
- List users in clinic
- Create users
- Manage user roles
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.users.models import CustomUser
from apps.users.serializers import CustomUserSerializer
from core.permissions import IsClinicAdmin, IsSameClinic
from core.utils import filter_by_user_clinic
from core.exceptions import APIResponse
import logging

logger = logging.getLogger(__name__)


class UserManagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user management within a clinic.
    
    Endpoints:
    - GET /api/users/ - List users in clinic
    - POST /api/users/ - Create user (admin only)
    - GET /api/users/{id}/ - Get user details
    - PUT /api/users/{id}/ - Update user (admin only)
    - DELETE /api/users/{id}/ - Delete user (soft delete, admin only)
    - GET /api/users/doctors/ - List doctors in clinic
    - GET /api/users/patients/ - List patients in clinic
    """

    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated, IsSameClinic]
    filterset_fields = ['role', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'contact_number']
    ordering_fields = ['first_name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter users by clinic."""
        return filter_by_user_clinic(CustomUser.objects.all(), self.request)

    def get_permissions(self):
        """
        Customize permissions per action.
        
        - Create/update/delete: Clinic admin
        - Read: Clinic members
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsClinicAdmin]
        else:
            permission_classes = [IsAuthenticated, IsSameClinic]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Create user."""
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        """Update user."""
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        """Soft delete user."""
        instance.soft_delete()

    @action(detail=False, methods=['get'])
    def doctors(self, request):
        """Get all doctors in clinic."""
        doctors = self.get_queryset().filter(role='DOCTOR')

        page = self.paginate_queryset(doctors)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(doctors, many=True)
        return APIResponse.success(
            data=serializer.data,
            message='Doctors retrieved'
        )

    @action(detail=False, methods=['get'])
    def patients(self, request):
        """Get all patients in clinic."""
        patients = self.get_queryset().filter(role='PATIENT')

        page = self.paginate_queryset(patients)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(patients, many=True)
        return APIResponse.success(
            data=serializer.data,
            message='Patients retrieved'
        )

    @action(detail=False, methods=['get'])
    def admin_users(self, request):
        """Get all admin users in clinic."""
        if not request.user.is_admin():
            return APIResponse.error(
                message='Only admins can view admin users',
                code='admin_only',
                status_code=status.HTTP_403_FORBIDDEN
            )

        admins = self.get_queryset().filter(role='ADMIN')

        page = self.paginate_queryset(admins)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(admins, many=True)
        return APIResponse.success(
            data=serializer.data,
            message='Admin users retrieved'
        )
