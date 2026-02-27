"""
Serializers for Patient model (standalone patient records).

Supports:
- Patient CRUD operations
- Doctor assignment
- Medical history and clinical information
- Read-only computed fields (age, active treatments count)
"""

from rest_framework import serializers
from apps.patients.models import Patient
from apps.users.serializers import CustomUserSerializer


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for standalone Patient model.
    
    Exposes doctor information and computed fields.
    """
    doctor_name = serializers.CharField(source='assigned_doctor.get_full_name', read_only=True, allow_null=True)
    doctor_email = serializers.CharField(source='assigned_doctor.email', read_only=True, allow_null=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    active_treatments_count = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()

    class Meta:
        model = Patient
        fields = [
            'id',
            'clinic',
            'clinic_name',
            'first_name',
            'last_name',
            'email',
            'contact_number',
            'secondary_contact_number',
            'address',
            'gender',
            'date_of_birth',
            'age',
            'assigned_doctor',
            'doctor_name',
            'doctor_email',
            'clinical_history',
            'notes',
            'active_treatments_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'clinic', 'clinic_name', 'doctor_name', 'doctor_email',
            'age', 'active_treatments_count', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        """Validate patient data."""
        clinic = self.context.get('clinic')

        # Ensure assigned doctor belongs to same clinic
        if 'assigned_doctor' in data and data['assigned_doctor']:
            doctor = data['assigned_doctor']
            if doctor.clinic != clinic or doctor.role != 'DOCTOR':
                raise serializers.ValidationError(
                    {'assigned_doctor': 'Doctor must belong to your clinic and have doctor role.'}
                )

        return data


class PatientDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Patient with full relationships.
    """
    assigned_doctor = CustomUserSerializer(read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    active_treatments_count = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    treatments = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = [
            'id',
            'clinic',
            'clinic_name',
            'first_name',
            'last_name',
            'email',
            'contact_number',
            'secondary_contact_number',
            'address',
            'gender',
            'date_of_birth',
            'age',
            'assigned_doctor',
            'clinical_history',
            'notes',
            'active_treatments_count',
            'treatments',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'clinic', 'clinic_name', 'age', 'active_treatments_count',
            'treatments', 'created_at', 'updated_at'
        ]

    def get_treatments(self, obj):
        """Return list of treatments for this patient."""
        from apps.treatments.serializers import TreatmentSerializer
        treatments = obj.treatments.filter(is_deleted=False)
        return TreatmentSerializer(treatments, many=True).data


class PatientCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating patients (with full field support and clinic validation).
    """
    class Meta:
        model = Patient
        fields = [
            'first_name',
            'last_name',
            'email',
            'contact_number',
            'secondary_contact_number',
            'address',
            'gender',
            'date_of_birth',
            'assigned_doctor',
            'clinical_history',
            'notes',
        ]

    def validate(self, data):
        """Validate patient data and ensure clinic is set."""
        clinic = self.context.get('clinic')
        
        if not clinic:
            raise serializers.ValidationError(
                {'clinic': 'Clinic must be provided. Contact administrator.'}
            )

        # Ensure assigned doctor belongs to same clinic
        if 'assigned_doctor' in data and data['assigned_doctor']:
            doctor = data['assigned_doctor']
            if doctor.clinic != clinic or doctor.role != 'DOCTOR':
                raise serializers.ValidationError(
                    {'assigned_doctor': 'Doctor must belong to your clinic and have doctor role.'}
                )

        return data

    def create(self, validated_data):
        """Create patient tied to clinic."""
        clinic = self.context.get('clinic')
        # If the request user is a doctor and no assigned_doctor was provided,
        # default the assigned_doctor to the logged-in doctor.
        request = self.context.get('request')
        if (not validated_data.get('assigned_doctor')) and request is not None:
            user = getattr(request, 'user', None)
            if user is not None and getattr(user, 'role', None) == 'DOCTOR':
                validated_data['assigned_doctor'] = user

        return Patient.objects.create(clinic=clinic, **validated_data)


class PatientUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating patients.
    """
    class Meta:
        model = Patient
        fields = [
            'first_name',
            'last_name',
            'email',
            'contact_number',
            'secondary_contact_number',
            'address',
            'gender',
            'date_of_birth',
            'assigned_doctor',
            'clinical_history',
            'notes',
        ]

    def validate(self, data):
        """Validate patient data."""
        clinic = self.context.get('clinic')

        # Ensure assigned doctor belongs to same clinic
        if 'assigned_doctor' in data and data['assigned_doctor']:
            doctor = data['assigned_doctor']
            if doctor.clinic != clinic or doctor.role != 'DOCTOR':
                raise serializers.ValidationError(
                    {'assigned_doctor': 'Doctor must belong to your clinic and have doctor role.'}
                )

        return data

