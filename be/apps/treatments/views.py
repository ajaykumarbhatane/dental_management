"""
ViewSets for treatments app.

Provides:
- Treatment management
- Treatment filtering and search
- Image uploads
"""

from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters import rest_framework as filters
from apps.treatments.models import Treatment
from apps.treatments.serializers import (
    TreatmentSerializer,
    TreatmentDetailSerializer,
    TreatmentCreateSerializer,
    TreatmentUpdateSerializer,
)
from core.permissions import IsSameClinic, IsDoctorOrClinicAdmin
from core.utils import filter_by_user_clinic, SerializerHelper
from core.exceptions import APIResponse
import logging

logger = logging.getLogger(__name__)


class TreatmentFilter(filters.FilterSet):
    """Custom filters for treatments."""

    status = filters.CharFilter(field_name='status')
    treatment_type = filters.CharFilter(field_name='treatment_type')
    next_visit_date = filters.DateFromToRangeFilter()

    class Meta:
        model = Treatment
        fields = ['status', 'treatment_type', 'next_visit_date']


class TreatmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Treatment management.
    
    Endpoints:
    - GET /api/treatments/ - List treatments in user's clinic
    - POST /api/treatments/ - Create treatment (doctor/admin)
    - GET /api/treatments/{id}/ - Get treatment details
    - PUT /api/treatments/{id}/ - Update treatment
    - DELETE /api/treatments/{id}/ - Delete treatment (soft delete)
    - GET /api/treatments/{id}/upcoming/ - Get upcoming treatments
    - GET /api/treatments/{id}/by-status/ - Filter by status
    """

    serializer_class = TreatmentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAuthenticated, IsSameClinic]
    filterset_class = TreatmentFilter
    search_fields = [
        'patient__first_name',
        'patient__last_name',
        'patient__email',
        'treatment_type',
        'treatment_information'
    ]
    ordering_fields = ['next_visit_date', 'created_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        """Filter treatments by user's clinic."""
        return filter_by_user_clinic(Treatment.objects.all(), self.request)

    def get_serializer_class(self):
        """Use appropriate serializer for different actions."""
        if self.action == 'create':
            return TreatmentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return TreatmentUpdateSerializer
        elif self.action == 'retrieve':
            return TreatmentDetailSerializer
        return TreatmentSerializer

    def get_serializer_context(self):
        """Add clinic to serializer context for validation."""
        context = super().get_serializer_context()
        # For superusers without a clinic, require clinic_id in the request
        if self.request.user.clinic:
            context['clinic'] = self.request.user.clinic
        elif 'clinic' in self.request.data:
            from apps.clinics.models import Clinic
            try:
                context['clinic'] = Clinic.objects.get(id=self.request.data['clinic'])
            except:
                context['clinic'] = None
        return context

    def get_permissions(self):
        """
        Customize permissions per action.
        
        - Create: Doctor or clinic admin
        - Update: Doctor (own treatments) or clinic admin
        - Delete: Clinic admin
        - Read: Clinic members
        """
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsDoctorOrClinicAdmin, IsSameClinic]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsSameClinic]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsDoctorOrClinicAdmin, IsSameClinic]
        else:
            permission_classes = [IsAuthenticated, IsSameClinic]

        return [permission() for permission in permission_classes]

    def check_object_permissions(self, request, obj):
        """Additional permission checks for object modification."""
        super().check_object_permissions(request, obj)

        # Doctors can only update their own treatments
        if request.method in ['PUT', 'PATCH'] and request.user.is_doctor():
            if obj.doctor != request.user:
                self.permission_denied(
                    request,
                    message='You can only update treatments you created'
                )

    def perform_create(self, serializer):
        """Create treatment with audit logging."""
        serializer.save()

    def create(self, request, *args, **kwargs):
        """Override create to sanitize upload_image payloads from some frontends.

        Some clients send an empty object (`{}`) for file fields when no file
        is selected which DRF's ImageField can reject. Normalize `{}` and
        empty strings to `None` so our serializer accepts them.
        """
        data = request.data.copy()
        ui = data.get('upload_image', None)

        # If upload_image is an empty dict-like or the string representation
        # of an empty object, treat it as None.
        if ui == {} or ui == '' or ui == 'null' or ui == 'None' or ui == '[]':
            data['upload_image'] = None

        # Some parsers produce an actual Python dict for empty JSON object
        if isinstance(ui, dict) and not ui:
            data['upload_image'] = None

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        """Update treatment with audit logging."""
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        """Soft delete treatment."""
        instance.soft_delete()

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming treatments."""
        treatments = self.get_queryset().filter(status='ONGOING')
        treatments = [t for t in treatments if t.is_upcoming()]

        page = self.paginate_queryset(treatments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(treatments, many=True)
        return APIResponse.success(
            data=serializer.data,
            message='Upcoming treatments retrieved'
        )

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue treatments."""
        treatments = self.get_queryset().filter(status='ONGOING')
        treatments = [t for t in treatments if t.is_overdue()]

        page = self.paginate_queryset(treatments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(treatments, many=True)
        return APIResponse.success(
            data=serializer.data,
            message='Overdue treatments retrieved'
        )

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get treatments filtered by status."""
        status_param = request.query_params.get('status')
        if not status_param:
            return APIResponse.error(
                message='Status parameter is required',
                code='missing_status',
                status_code=status.HTTP_400_BAD_REQUEST
            )

        treatments = self.get_queryset().filter(status=status_param)

        page = self.paginate_queryset(treatments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(treatments, many=True)
        return APIResponse.success(
            data=serializer.data,
            message=f'Treatments with status {status_param} retrieved'
        )

    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark a treatment as completed."""
        try:
            treatment = self.get_object()
            self.check_object_permissions(request, treatment)

            treatment.mark_completed()

            serializer = TreatmentDetailSerializer(treatment)
            return APIResponse.success(
                data=serializer.data,
                message='Treatment marked as completed'
            )
        except Treatment.DoesNotExist:
            return APIResponse.error(
                message='Treatment not found',
                code='treatment_not_found',
                status_code=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def mark_cancelled(self, request, pk=None):
        """Mark a treatment as cancelled."""
        try:
            treatment = self.get_object()
            self.check_object_permissions(request, treatment)

            treatment.mark_cancelled()

            serializer = TreatmentDetailSerializer(treatment)
            return APIResponse.success(
                data=serializer.data,
                message='Treatment marked as cancelled'
            )
        except Treatment.DoesNotExist:
            return APIResponse.error(
                message='Treatment not found',
                code='treatment_not_found',
                status_code=status.HTTP_404_NOT_FOUND
            )
