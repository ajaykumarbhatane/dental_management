"""
Serializers for treatments app.
"""

from rest_framework import serializers
from apps.treatments.models import Treatment
from apps.users.serializers import CustomUserSerializer


class TreatmentSerializer(serializers.ModelSerializer):
    """
    Serializer for Treatment model.
    
    Includes doctor and patient information.
    """
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    patient_email = serializers.CharField(source='patient.email', read_only=True)
    doctor_name = serializers.CharField(source='doctor.get_full_name', read_only=True, allow_null=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    is_upcoming = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Treatment
        fields = [
            'id',
            'clinic',
            'clinic_name',
            'patient',
            'patient_name',
            'patient_email',
            'doctor',
            'doctor_name',
            'treatment_type',
            'treatment_information',
            'treatment_findings',
            'upload_image',
            'next_visit_date',
            'status',
            'is_upcoming',
            'is_overdue',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'clinic', 'clinic_name', 'patient_name', 'patient_email',
            'doctor_name', 'is_upcoming', 'is_overdue', 'created_at', 'updated_at'
        ]

    def get_is_upcoming(self, obj):
        """Check if treatment is upcoming."""
        return obj.is_upcoming()

    def get_is_overdue(self, obj):
        """Check if treatment is overdue."""
        return obj.is_overdue()

    def validate(self, data):
        """Validate treatment data."""
        # Get current clinic from context
        clinic = self.context.get('clinic')
        request = self.context.get('request')

        # Ensure patient belongs to same clinic
        if 'patient' in data:
            patient = data['patient']
            if patient.clinic != clinic:
                raise serializers.ValidationError(
                    {'patient': 'Patient must belong to the same clinic.'}
                )

        # Ensure doctor (if specified) belongs to same clinic
        if 'doctor' in data and data['doctor']:
            doctor = data['doctor']
            if doctor.clinic != clinic or doctor.role != 'DOCTOR':
                raise serializers.ValidationError(
                    {'doctor': 'Doctor must belong to the same clinic and have doctor role.'}
                )

        return data


class TreatmentDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for treatment with full relationships.
    """
    patient = CustomUserSerializer(read_only=True)
    doctor = CustomUserSerializer(read_only=True)
    is_upcoming = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Treatment
        fields = [
            'id',
            'clinic',
            'patient',
            'doctor',
            'treatment_type',
            'treatment_information',
            'treatment_findings',
            'upload_image',
            'next_visit_date',
            'status',
            'is_upcoming',
            'is_overdue',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'clinic', 'patient', 'doctor', 'is_upcoming', 'is_overdue',
            'created_at', 'updated_at'
        ]

    def get_is_upcoming(self, obj):
        """Check if treatment is upcoming."""
        return obj.is_upcoming()

    def get_is_overdue(self, obj):
        """Check if treatment is overdue."""
        return obj.is_overdue()


class TreatmentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating treatments (with validation).
    """
    class Meta:
        model = Treatment
        fields = [
            'patient',
            'doctor',
            'treatment_type',
            'treatment_information',
            'treatment_findings',
            'upload_image',
            'next_visit_date',
            'status',
        ]

    def validate_upload_image(self, value):
        """Validate image file."""
        if value:
            # Check file size
            if value.size > 5 * 1024 * 1024:  # 5MB
                raise serializers.ValidationError(
                    'Image file size cannot exceed 5MB.'
                )
            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if value.content_type not in allowed_types:
                raise serializers.ValidationError(
                    'Invalid image format. Allowed: JPEG, PNG, GIF, WebP'
                )
        return value

    def validate(self, data):
        """Validate treatment data."""
        clinic = self.context.get('clinic')
        request = self.context.get('request')

        # Ensure patient belongs to same clinic
        patient = data.get('patient')
        if patient and patient.clinic != clinic:
            raise serializers.ValidationError(
                {'patient': 'Patient must belong to your clinic.'}
            )

        # Ensure doctor belongs to same clinic and has doctor role
        doctor = data.get('doctor')
        if doctor:
            if doctor.clinic != clinic:
                raise serializers.ValidationError(
                    {'doctor': 'Doctor must belong to your clinic.'}
                )
            if doctor.role != 'DOCTOR':
                raise serializers.ValidationError(
                    {'doctor': 'Selected user must have doctor role.'}
                )

        return data

    def create(self, validated_data):
        """Create treatment with audit logging."""
        request = self.context.get('request')
        clinic = self.context.get('clinic')

        treatment = Treatment.objects.create(
            clinic=clinic,
            created_by=request.user,
            updated_by=request.user,
            **validated_data
        )
        return treatment


class TreatmentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating treatments.
    """
    class Meta:
        model = Treatment
        fields = [
            'doctor',
            'treatment_information',
            'treatment_findings',
            'upload_image',
            'next_visit_date',
            'status',
        ]
