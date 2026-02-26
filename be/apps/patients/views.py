"""
ViewSets for patients app.

Provides:
- Patient profile management
- Medical history access
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.patients.models import PatientProfile
from apps.patients.serializers import (
    PatientProfileSerializer,
    PatientDetailSerializer,
    PatientUpdateSerializer,
)
from core.permissions import IsPatient, IsClinicAdmin, IsSameClinic, IsOwnerOrClinicAdmin
from core.utils import filter_by_user_clinic
from core.exceptions import APIResponse
import logging

logger = logging.getLogger(__name__)


class PatientProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Patient Profile management.
    
    Endpoints:
    - GET /api/patients/ - List patients in user's clinic
    - POST /api/patients/ - Create patient profile (admin only)
    - GET /api/patients/{id}/ - Get patient profile
    - PUT /api/patients/{id}/ - Update patient profile (own or admin)
    - GET /api/patients/{id}/medical-summary/ - Get medical summary
    """

    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated, IsSameClinic]
    filterset_fields = ['gender', 'clinic']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    ordering_fields = ['user__first_name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter patients by user's clinic."""
        return filter_by_user_clinic(PatientProfile.objects.all(), self.request)

    def get_serializer_class(self):
        """Use detailed serializer for retrieve actions."""
        if self.action == 'retrieve':
            return PatientDetailSerializer
        elif self.action in ['partial_update', 'update']:
            return PatientUpdateSerializer
        return PatientProfileSerializer

    def get_permissions(self):
        """
        Customize permissions per action.
        
        - Create/delete: Clinic admin
        - Update: Patient (own) or clinic admin
        - Read: Clinic members
        """
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsClinicAdmin]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsSameClinic]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsClinicAdmin]
        else:
            permission_classes = [IsAuthenticated, IsSameClinic]

        return [permission() for permission in permission_classes]

    def check_object_permissions(self, request, obj):
        """Additional permission checks for object access."""
        super().check_object_permissions(request, obj)

        # Patient can only update their own profile
        if request.method in ['PUT', 'PATCH'] and request.user.is_patient():
            if obj.user != request.user:
                self.permission_denied(
                    request,
                    message='You can only update your own profile'
                )

    def perform_create(self, serializer):
        """Create patient profile."""
        serializer.save()

    def perform_update(self, serializer):
        """Update patient profile."""
        serializer.save()

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsSameClinic])
    def medical_summary(self, request, pk=None):
        """Get compact medical summary for patient."""
        try:
            patient = self.get_object()
            self.check_object_permissions(request, patient)

            return APIResponse.success(
                data=patient.get_medical_summary(),
                message='Medical summary retrieved'
            )
        except PatientProfile.DoesNotExist:
            return APIResponse.error(
                message='Patient not found',
                code='patient_not_found',
                status_code=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsPatient])
    def my_profile(self, request):
        """Get current patient's own profile."""
        try:
            patient = request.user.patient_profile
            serializer = PatientDetailSerializer(patient)
            return APIResponse.success(
                data=serializer.data,
                message='Your profile retrieved'
            )
        except PatientProfile.DoesNotExist:
            return APIResponse.error(
                message='Patient profile not found',
                code='patient_profile_not_found',
                status_code=status.HTTP_404_NOT_FOUND
            )
