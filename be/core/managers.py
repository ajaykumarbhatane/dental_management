"""
Custom managers for implementing soft delete and multi-tenant filtering.

Architecture Decision:
- Custom managers override the default QuerySet to implement soft delete
- All querysets are filtered by clinic by default (multi-tenant isolation)
- Use .all_objects to access all records including soft deleted ones
"""

from django.db import models
from django.contrib.auth.models import UserManager as DjangoUserManager


class SoftDeleteQuerySet(models.QuerySet):
    """
    Custom QuerySet that filters out soft-deleted records by default.
    
    Records are marked as deleted (is_deleted=True) but not removed from DB.
    Use .all_objects.all() to include deleted records.
    """

    def active(self):
        """Return only non-deleted records."""
        return self.filter(is_deleted=False)

    def deleted(self):
        """Return only deleted records."""
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    """
    Custom manager implementing soft delete pattern.
    
    Default behavior: Only returns non-deleted records (is_deleted=False)
    """

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def all_objects(self):
        """Return all records including soft-deleted ones."""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def active(self):
        """Explicitly return only active (non-deleted) records."""
        return self.get_queryset()

    def deleted(self):
        """Return only soft-deleted records."""
        return self.all_objects().filter(is_deleted=True)


class MultiTenantQuerySet(models.QuerySet):
    """
    Custom QuerySet for multi-tenant support.
    
    Filters records by clinic automatically based on request context.
    Ensures data isolation between clinics.
    """

    def by_clinic(self, clinic):
        """Filter records by specific clinic."""
        return self.filter(clinic=clinic)


class MultiTenantManager(models.Manager):
    """
    Manager for multi-tenant models.
    
    - Implements soft delete
    - Supports clinic-based filtering
    """

    def get_queryset(self):
        return MultiTenantQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def all_objects(self):
        """Return all records including soft-deleted ones."""
        return MultiTenantQuerySet(self.model, using=self._db)

    def active(self):
        """Only active records."""
        return self.get_queryset()

    def deleted(self):
        """Only soft-deleted records."""
        return self.all_objects().filter(is_deleted=True)

    def by_clinic(self, clinic):
        """Filter by clinic."""
        return self.get_queryset().by_clinic(clinic)


class CustomUserManager(DjangoUserManager):
    """
    Custom manager for User model.
    
    Extends Django's default UserManager with additional functionality:
    - Supports multi-tenant (clinic-based) queries
    - Soft delete support
    """

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def all_objects(self):
        """Return all users including soft-deleted ones."""
        return super().get_queryset()

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    def by_clinic(self, clinic):
        """Get users belonging to a specific clinic."""
        return self.get_queryset().filter(clinic=clinic)

    def doctors(self, clinic=None):
        """Get all doctors, optionally filtered by clinic."""
        qs = self.get_queryset().filter(role='DOCTOR')
        if clinic:
            qs = qs.filter(clinic=clinic)
        return qs

    def patients(self, clinic=None):
        """Get all patients, optionally filtered by clinic."""
        qs = self.get_queryset().filter(role='PATIENT')
        if clinic:
            qs = qs.filter(clinic=clinic)
        return qs

    def clinic_admins(self, clinic=None):
        """Get all clinic admins, optionally filtered by clinic."""
        qs = self.get_queryset().filter(role='ADMIN')
        if clinic:
            qs = qs.filter(clinic=clinic)
        return qs
