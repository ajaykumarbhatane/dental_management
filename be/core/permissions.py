"""
Custom DRF permission classes for role-based access control and multi-tenant support.

Architecture:
- IsClinicAdmin: Only clinic admins can access
- IsDoctor: Only doctors can access
- IsPatient: Only patients can access
- IsSameClinic: User must belong to same clinic as resource
- IsClinicAdminOrReadOnly: Clinic admins can edit, others can only read
"""

from rest_framework import permissions
from django.core.exceptions import PermissionDenied


class IsClinicAdmin(permissions.BasePermission):
    """
    Permission check: User must be a clinic admin.
    """

    message = 'Only clinic administrators can access this resource.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'ADMIN'
        )


class IsDoctor(permissions.BasePermission):
    """
    Permission check: User must be a doctor.
    """

    message = 'Only doctors can access this resource.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'DOCTOR'
        )


class IsPatient(permissions.BasePermission):
    """
    Permission check: User must be a patient.
    """

    message = 'Only patients can access this resource.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'PATIENT'
        )


class IsSameClinic(permissions.BasePermission):
    """
    Multi-tenant permission: User must belong to the same clinic as the resource.
    
    This is the core permission for multi-tenant data isolation.
    Every resource must be checked against the user's clinic.
    """

    message = 'You do not have permission to access resources from other clinics.'

    def has_permission(self, request, view):
        """
        Check if user belongs to a clinic.
        Superusers/admins without clinic assignment can still access.
        """
        return (
            request.user 
            and request.user.is_authenticated 
            and (request.user.clinic is not None or request.user.is_superuser)
        )

    def has_object_permission(self, request, view, obj):
        """
        Check if user's clinic matches the object's clinic.
        
        Handles both direct clinic FK and nested relationships.
        """
        # Direct clinic FK (most common)
        if hasattr(obj, 'clinic'):
            return obj.clinic == request.user.clinic

        # Nested clinic relationship (e.g., patient.clinic through user.clinic)
        if hasattr(obj, 'patient') and hasattr(obj.patient, 'clinic'):
            return obj.patient.clinic == request.user.clinic

        # User to user comparison
        if hasattr(obj, 'clinic'):
            return obj.clinic == request.user.clinic

        return False


class IsClinicAdminOrReadOnly(permissions.BasePermission):
    """
    Clinic admins can edit objects. Other authenticated users can only read.
    """

    message = 'Only clinic administrators can edit this resource.'

    def has_permission(self, request, view):
        # Allow read access to authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Only clinic admins can write
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'ADMIN'
        )

    def has_object_permission(self, request, view, obj):
        # Read permissions allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user.clinic == getattr(obj, 'clinic', None)

        # Write permissions only for clinic admins in same clinic
        return (
            request.user.role == 'ADMIN'
            and request.user.clinic == getattr(obj, 'clinic', None)
        )


class IsClinicAdminAndSameClinic(permissions.BasePermission):
    """
    User must be a clinic admin AND belong to the same clinic as the resource.
    """

    message = 'Only administrators of your clinic can access this resource.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'ADMIN'
        )

    def has_object_permission(self, request, view, obj):
        return request.user.clinic == getattr(obj, 'clinic', None)


class IsOwnerOrClinicAdmin(permissions.BasePermission):
    """
    Allow access if:
    - User is the owner of the object (for patient profiles)
    - User is a clinic admin
    """

    message = 'You do not have permission to access this resource.'

    def has_object_permission(self, request, view, obj):
        # Clinic admin can access anything in their clinic
        if request.user.role == 'ADMIN' and request.user.clinic == obj.clinic:
            return True

        # User can access their own profile
        if hasattr(obj, 'user'):
            return obj.user == request.user

        return False


class IsDoctorOrClinicAdmin(permissions.BasePermission):
    """
    User must be a doctor or clinic admin.
    """

    message = 'Only doctors and clinic administrators can access this resource.'

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ['DOCTOR', 'ADMIN']
        )
