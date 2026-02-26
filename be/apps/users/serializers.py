"""
Serializers for user app.

Includes:
- CustomUserSerializer: Main user serializer with validation
- UserRegistrationSerializer: Registration with validation
- UserLoginSerializer: Login credentials
- ChangePasswordSerializer: Password change
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.users.models import CustomUser
from core.validators import validate_phone_number


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Main serializer for CustomUser.
    
    Includes clinic relationship and computed fields.
    """
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'clinic',
            'clinic_name',
            'role',
            'role_display',
            'contact_number',
            'secondary_contact_number',
            'address',
            'degree',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_contact_number(self, value):
        """Validate phone number format."""
        validate_phone_number(value)
        return value

    def validate_secondary_contact_number(self, value):
        """Validate secondary phone number if provided."""
        if value:
            validate_phone_number(value)
        return value

    def validate(self, attrs):
        """Cross-field validation."""
        # Ensure clinic is provided
        if 'clinic' not in attrs and not self.instance:
            raise serializers.ValidationError(
                {'clinic': 'Clinic must be specified for new users'}
            )

        return attrs


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed user serializer with related data.
    
    Used for user detail endpoints.
    """
    clinic = serializers.SerializerMethodField()
    is_doctor = serializers.SerializerMethodField()
    is_patient = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'clinic',
            'role',
            'contact_number',
            'secondary_contact_number',
            'address',
            'degree',
            'is_active',
            'is_doctor',
            'is_patient',
            'is_admin',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_clinic(self, obj):
        """Return clinic information."""
        return {
            'id': obj.clinic.id,
            'name': obj.clinic.name,
            'contact_number': obj.clinic.contact_number,
        }

    def get_is_doctor(self, obj):
        """Check if user is a doctor."""
        return obj.is_doctor()

    def get_is_patient(self, obj):
        """Check if user is a patient."""
        return obj.is_patient()

    def get_is_admin(self, obj):
        """Check if user is an admin."""
        return obj.is_admin()


class UserRegistrationSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    
    Validates and creates a new user account.
    """
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    contact_number = serializers.CharField(max_length=20, validators=[validate_phone_number])
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    clinic_id = serializers.IntegerField()
    role = serializers.ChoiceField(choices=['DOCTOR', 'PATIENT', 'ADMIN'])
    degree = serializers.CharField(required=False, allow_blank=True)
    secondary_contact_number = serializers.CharField(
        required=False,
        allow_blank=True,
        validators=[validate_phone_number]
    )
    address = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        """Ensure email is unique if provided."""
        if not value:
            return value
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already registered.')
        return value

    def validate(self, data):
        """Cross-field validation."""
        # Verify passwords match
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {'password': 'Passwords do not match.'}
            )

        # Check if clinic exists
        from apps.clinics.models import Clinic
        try:
            clinic = Clinic.objects.get(id=data['clinic_id'])
        except Clinic.DoesNotExist:
            raise serializers.ValidationError(
                {'clinic_id': 'Clinic not found.'}
            )

        # Remove confirm password from validated data
        data.pop('password_confirm', None)

        return data

    def create(self, validated_data):
        """Create the user."""
        from apps.clinics.models import Clinic
        import uuid

        clinic = Clinic.objects.get(id=validated_data.pop('clinic_id'))
        password = validated_data.pop('password')

        # generate placeholder email if none provided
        email = validated_data.get('email')
        if not email:
            email = f"patient-{uuid.uuid4()}@noemail.local"
            validated_data['email'] = email

        user = CustomUser.objects.create_user(
            **validated_data,
            clinic=clinic,
        )
        user.set_password(password)
        user.save()

        # if registering a patient, create associated PatientProfile
        if user.role == 'PATIENT':
            try:
                from apps.patients.models import PatientProfile
                # only create if not exist
                if not hasattr(user, 'patient_profile'):
                    PatientProfile.objects.create(user=user, clinic=clinic)
            except ImportError:
                # patients app may not be available in some contexts
                pass

        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    
    Authenticates user and returns basic info.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Authenticate user."""
        user = authenticate(
            email=data['email'],
            password=data['password']
        )

        if not user:
            raise serializers.ValidationError('Invalid credentials.')

        if user.is_deleted:
            raise serializers.ValidationError('This account has been deleted.')

        if not user.is_active:
            raise serializers.ValidationError('This account is inactive.')

        data['user'] = user
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password.
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        """Validate passwords."""
        request = self.context.get('request')
        user = request.user

        # Check old password
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError(
                {'old_password': 'Incorrect password.'}
            )

        # Check new passwords match
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password': 'New passwords do not match.'}
            )

        # Ensure new password differs from old
        if data['new_password'] == data['old_password']:
            raise serializers.ValidationError(
                {'new_password': 'New password must be different from old password.'}
            )

        return data

    def save(self):
        """Update the password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UpdateProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile (non-admin fields).
    """
    class Meta:
        model = CustomUser
        fields = [
            'first_name',
            'last_name',
            'contact_number',
            'secondary_contact_number',
            'address',
            'degree',
        ]

    def validate_contact_number(self, value):
        """Validate phone number format."""
        validate_phone_number(value)
        return value

    def validate_secondary_contact_number(self, value):
        """Validate secondary phone number if provided."""
        if value:
            validate_phone_number(value)
        return value
