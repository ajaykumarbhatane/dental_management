"""
ViewSets for clinics app.

Provides:
- Clinic management
- Clinic statistics
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.clinics.models import Clinic
from apps.clinics.serializers import ClinicSerializer, ClinicDetailSerializer
from core.permissions import IsClinicAdmin, IsSameClinic
from core.exceptions import APIResponse
import logging

logger = logging.getLogger(__name__)


class ClinicViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Clinic management.
    
    Endpoints:
    - GET /api/clinics/ - List all clinics
    - POST /api/clinics/ - Create clinic (admin only)
    - GET /api/clinics/{id}/ - Get clinic details
    - PUT /api/clinics/{id}/ - Update clinic
    - DELETE /api/clinics/{id}/ - Delete clinic (soft delete)
    - GET /api/clinics/{id}/statistics/ - Get clinic statistics
    """

    serializer_class = ClinicSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name', 'contact_number', 'address']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter clinics based on user role."""
        user = self.request.user

        # Admins can only see their own clinic
        if user.role == 'ADMIN':
            return Clinic.objects.filter(id=user.clinic_id)

        # Other roles: return their clinic
        if user.clinic:
            return Clinic.objects.filter(id=user.clinic_id)

        return Clinic.objects.none()

    def get_serializer_class(self):
        """Use detailed serializer for retrieve actions."""
        if self.action == 'retrieve':
            return ClinicDetailSerializer
        return ClinicSerializer

    def get_permissions(self):
        """
        Customize permissions per action.
        
        - Create: Super admin only
        - Update: Clinic admin of that clinic
        - Retrieve: Clinic members
        """
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsClinicAdmin]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsClinicAdmin]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        """Create clinic (audit logging)."""
        serializer.save()

    def perform_update(self, serializer):
        """Update clinic."""
        serializer.save()

    def perform_destroy(self, instance):
        """Soft delete clinic."""
        instance.soft_delete()

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def statistics(self, request, pk=None):
        """Get clinic statistics."""
        try:
            clinic = self.get_object()

            stats = {
                'total_users': clinic.user_count,
                'total_doctors': clinic.doctor_count,
                'total_patients': clinic.patient_count,
                'active_treatments': clinic.active_treatments_count,
                'is_active': clinic.is_active,
            }

            return APIResponse.success(
                data=stats,
                message='Clinic statistics retrieved'
            )
        except Clinic.DoesNotExist:
            return APIResponse.error(
                message='Clinic not found',
                code='clinic_not_found',
                status_code=status.HTTP_404_NOT_FOUND
            )
