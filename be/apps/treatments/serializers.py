"""
Serializers for treatments app.
"""

from rest_framework import serializers
import base64
import imghdr
import uuid
from django.core.files.base import ContentFile


class Base64ImageField(serializers.ImageField):
    """A Django REST framework field for handling image-uploads through
    raw base64-encoded strings, empty dicts (from some frontends), or
    standard multipart file uploads.
    """

    def to_internal_value(self, data):
        # Handle empty values
        if data is None or data == '' or (isinstance(data, dict) and not data):
            return None

        # Handle base64 string
        if isinstance(data, str):
            try:
                if data.startswith('data:'):
                    header, b64data = data.split(',', 1)
                else:
                    b64data = data
                decoded_file = base64.b64decode(b64data)
            except Exception:
                raise serializers.ValidationError('Invalid base64 image')

            extension = imghdr.what(None, h=decoded_file) or 'jpg'
            file_name = f"{uuid.uuid4().hex[:12]}.{extension}"
            data = ContentFile(decoded_file, name=file_name)

        # If dict provided with data key, try to extract
        if isinstance(data, dict):
            if 'data' in data:
                return self.to_internal_value(data['data'])
            if not data:
                return None
            raise serializers.ValidationError('Invalid data for image upload')

        return super().to_internal_value(data)
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
    # Accept either multipart file uploads or base64-encoded image strings
    upload_image = Base64ImageField(required=False, allow_null=True)

    # Support base64-encoded images: if a base64 string is passed, we'll
    # convert it to a Django ContentFile in `validate_upload_image` below.
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
        if not value:
            return value

        # If a base64 string was passed, convert it to ContentFile
        if isinstance(value, str):
            try:
                # Data URI scheme: data:<mime>;base64,<data>
                if value.startswith('data:'):
                    header, b64data = value.split(',', 1)
                    mime_part = header.split(';')[0]
                    content_type = mime_part.split(':')[1] if ':' in mime_part else None
                else:
                    b64data = value
                    content_type = None

                decoded_file = base64.b64decode(b64data)
            except Exception:
                raise serializers.ValidationError('Invalid base64 image')

            # Determine file extension
            extension = imghdr.what(None, h=decoded_file) or 'jpg'
            file_name = f"{uuid.uuid4().hex[:12]}.{extension}"
            content_file = ContentFile(decoded_file, name=file_name)
            # Attach metadata used elsewhere
            content_file.size = len(decoded_file)
            content_file.content_type = content_type or f'image/{extension}'

            value = content_file

        # Now `value` should be a file-like object (ContentFile or UploadedFile)
        size = getattr(value, 'size', None)
        if size is None:
            try:
                # Fallback: try to get length of file's bytes
                size = len(value.read())
                value.seek(0)
            except Exception:
                size = 0

        if size > 5 * 1024 * 1024:  # 5MB
            raise serializers.ValidationError('Image file size cannot exceed 5MB.')

        # Determine content type
        content_type = getattr(value, 'content_type', None)
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if content_type and content_type not in allowed_types:
            raise serializers.ValidationError('Invalid image format. Allowed: JPEG, PNG, GIF, WebP')

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
        """Create treatment with audit logging and proper image naming."""
        from datetime import datetime
        import uuid
        
        request = self.context.get('request')
        clinic = self.context.get('clinic')
        
        # Handle image naming if present
        upload_image = validated_data.get('upload_image')
        if upload_image:
            patient = validated_data.get('patient')
            treatment_type = validated_data.get('treatment_type', 'treatment')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            random_id = str(uuid.uuid4())[:8]
            
            # Generate filename: patient_id_treatmenttype_date_randomid.ext
            ext = upload_image.name.split('.')[-1]
            upload_image.name = f"{patient.id}_{treatment_type}_{timestamp}_{random_id}.{ext}"

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
    # Allow file uploads or base64 strings when updating
    upload_image = Base64ImageField(required=False, allow_null=True)

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
