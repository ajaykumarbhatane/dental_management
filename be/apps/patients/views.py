"""
ViewSets for standalone Patient model.

Provides:
- Patient CRUD operations
- Doctor assignment
- Filtering and search
- Medical history management
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from apps.patients.models import Patient
from apps.patients.serializers import (
    PatientSerializer,
    PatientDetailSerializer,
    PatientCreateSerializer,
    PatientUpdateSerializer,
)
from core.permissions import IsSameClinic, IsClinicAdmin, IsDoctorOrClinicAdmin
from core.utils import filter_by_user_clinic
from core.exceptions import APIResponse
import logging

logger = logging.getLogger(__name__)


class PatientFilter(filters.FilterSet):
    """Custom filters for patients."""

    assigned_doctor = filters.NumberFilter(field_name='assigned_doctor__id')

    class Meta:
        model = Patient
        fields = ['assigned_doctor']


class PatientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Patient management.
    
    Endpoints:
    - GET /api/patients/ - List patients in user's clinic
    - POST /api/patients/ - Create patient (admin only)
    - GET /api/patients/{id}/ - Get patient details
    - PUT /api/patients/{id}/ - Update patient
    - DELETE /api/patients/{id}/ - Delete patient (soft delete)
    - GET /api/patients/{id}/assign-doctor/ - Assign doctor to patient
    """

    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsSameClinic]
    filterset_class = PatientFilter
    search_fields = ['first_name', 'last_name']
    ordering_fields = ['first_name', 'last_name', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter patients by user's clinic."""
        return filter_by_user_clinic(Patient.objects.all(), self.request)

    def get_serializer_class(self):
        """Use appropriate serializer for different actions."""
        if self.action == 'create':
            return PatientCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PatientUpdateSerializer
        elif self.action == 'retrieve':
            return PatientDetailSerializer
        return PatientSerializer

    def get_serializer_context(self):
        """Add clinic to serializer context for validation."""
        context = super().get_serializer_context()
        
        # Try to get clinic from user's clinic assignment
        clinic = self.request.user.clinic
        
        # If user doesn't have a clinic, check request data for clinic_id
        if not clinic and self.action == 'create':
            clinic_id = self.request.data.get('clinic_id')
            if clinic_id:
                from apps.clinics.models import Clinic
                try:
                    clinic = Clinic.objects.get(id=clinic_id)
                except:
                    # Let serializer handle the error with proper validation message
                    clinic = None
        
        # Add clinic to context if found
        if clinic:
            context['clinic'] = clinic
        
        return context

    def get_permissions(self):
        """
        Customize permissions per action.
        
        - Create: Clinic admin
        - Update: Clinic admin or doctor managing patient
        - Delete: Clinic admin
        - Read: Clinic members
        """
        if self.action == 'create':
            # Allow both clinic admins and doctors to create patients
            permission_classes = [IsAuthenticated, IsDoctorOrClinicAdmin, IsSameClinic]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsSameClinic]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsClinicAdmin, IsSameClinic]
        else:
            permission_classes = [IsAuthenticated, IsSameClinic]

        return [permission() for permission in permission_classes]

    def check_object_permissions(self, request, obj):
        """Additional permission checks for object modification."""
        super().check_object_permissions(request, obj)

        # No extra restrictions: doctors are allowed to update patients in their clinic.

    def perform_create(self, serializer):
        """Create patient record."""
        serializer.save()

    def perform_update(self, serializer):
        """Update patient record."""
        serializer.save()

    def perform_destroy(self, instance):
        """Delete patient record."""
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsClinicAdmin, IsSameClinic])
    def assign_doctor(self, request, pk=None):
        """Assign a doctor to a patient."""
        try:
            patient = self.get_object()
            doctor_id = request.data.get('doctor_id')

            if not doctor_id:
                return APIResponse.error(
                    message='doctor_id is required',
                    code='missing_doctor_id',
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Validate doctor exists and belongs to same clinic
            from apps.users.models import CustomUser
            try:
                doctor = CustomUser.objects.get(
                    id=doctor_id,
                    clinic=request.user.clinic,
                    role='DOCTOR'
                )
            except CustomUser.DoesNotExist:
                return APIResponse.error(
                    message='Doctor not found in your clinic',
                    code='doctor_not_found',
                    status_code=status.HTTP_404_NOT_FOUND
                )

            patient.assigned_doctor = doctor
            patient.save()

            serializer = PatientDetailSerializer(patient)
            return APIResponse.success(
                data=serializer.data,
                message=f'Doctor {doctor.get_full_name()} assigned to patient'
            )
        except Patient.DoesNotExist:
            return APIResponse.error(
                message='Patient not found',
                code='patient_not_found',
                status_code=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsSameClinic])
    def my_patients(self, request):
        """Get patients assigned to the current doctor."""
        if not request.user.is_doctor():
            return APIResponse.error(
                message='Only doctors can view their assigned patients',
                code='not_a_doctor',
                status_code=status.HTTP_403_FORBIDDEN
            )

        patients = self.get_queryset().filter(assigned_doctor=request.user)

        page = self.paginate_queryset(patients)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(patients, many=True)
        return APIResponse.success(
            data=serializer.data,
            message='Your assigned patients retrieved'
        )
