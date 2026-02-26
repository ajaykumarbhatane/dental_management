"""
Serializers for clinics app.
"""

from rest_framework import serializers
from apps.clinics.models import Clinic


class ClinicSerializer(serializers.ModelSerializer):
    """
    Serializer for Clinic model.
    
    Includes computed fields for statistics.
    """
    user_count = serializers.ReadOnlyField()
    doctor_count = serializers.ReadOnlyField()
    patient_count = serializers.ReadOnlyField()

    class Meta:
        model = Clinic
        fields = [
            'id',
            'name',
            'contact_number',
            'address',
            'description',
            'is_active',
            'user_count',
            'doctor_count',
            'patient_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClinicDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for Clinic with additional information.
    """
    user_count = serializers.ReadOnlyField()
    doctor_count = serializers.ReadOnlyField()
    patient_count = serializers.ReadOnlyField()
    active_treatments_count = serializers.ReadOnlyField()

    class Meta:
        model = Clinic
        fields = [
            'id',
            'name',
            'contact_number',
            'address',
            'description',
            'is_active',
            'user_count',
            'doctor_count',
            'patient_count',
            'active_treatments_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
