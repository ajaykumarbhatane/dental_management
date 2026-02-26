"""
Serializers for patients app.
"""

from rest_framework import serializers
from apps.patients.models import PatientProfile
from apps.users.serializers import CustomUserSerializer
from apps.treatments.serializers import TreatmentSerializer


class PatientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for PatientProfile model.
    """
    age = serializers.ReadOnlyField()
    # expose user attributes directly for frontend convenience
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.contact_number', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            'id',
            'user',
            'first_name',
            'last_name',
            'email',
            'phone',
            'user_email',
            'user_full_name',
            'clinic',
            'clinic_name',
            'gender',
            'date_of_birth',
            'age',
            'medical_history',
            'allergies',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'clinic', 'first_name', 'last_name', 'email', 'phone', 'user_email', 'user_full_name', 'clinic_name', 'age', 'created_at', 'updated_at']


class PatientDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for patient with user information.
    """
    user = CustomUserSerializer(read_only=True)
    age = serializers.ReadOnlyField()
    active_treatments_count = serializers.ReadOnlyField()
    # convenience fields copied from user
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    phone = serializers.CharField(source='user.contact_number', read_only=True)
    address = serializers.CharField(source='user.address', read_only=True)
    medical_summary = serializers.SerializerMethodField()
    treatments = serializers.SerializerMethodField()

    class Meta:
        model = PatientProfile
        fields = [
            'id',
            'user',
            'first_name',
            'last_name',
            'email',
            'phone',
            'address',
            'clinic',
            'gender',
            'date_of_birth',
            'age',
            'active_treatments_count',
            'medical_history',
            'allergies',
            'medical_summary',
            'treatments',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'clinic', 'medical_history', 'allergies',
            'active_treatments_count', 'medical_summary', 'treatments', 'created_at', 'updated_at'
        ]

    def get_medical_summary(self, obj):
        """Get compact medical summary."""
        return obj.get_medical_summary()

    def get_treatments(self, obj):
        """Return list of treatments for this patient."""
        # treatments are stored on the user foreign key
        treatments = obj.user.treatments.filter(is_deleted=False)
        return TreatmentSerializer(treatments, many=True).data


class PatientUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating patient profile (patient-editable fields).
    """
    class Meta:
        model = PatientProfile
        fields = [
            'gender',
            'date_of_birth',
            'medical_history',
            'allergies',
        ]
