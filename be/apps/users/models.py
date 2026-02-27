"""
User model and authentication related models.

Architecture:
- CustomUser extends AbstractUser for fine-grained control
- Implements multi-tenant support (FK to Clinic)
- Supports role-based access control (ADMIN, DOCTOR, PATIENT)
- Audit logging (created_by, updated_by)
- Soft delete (is_deleted)
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from core.managers import CustomUserManager, SoftDeleteQuerySet, SoftDeleteManager
from core.validators import validate_phone_number
from datetime import datetime


class CustomUser(AbstractUser):
    """
    Extended User model with clinic assignment and role-based access control.
    
    Replaces Django's default User model (set as AUTH_USER_MODEL in settings).
    
    Attributes:
        email: Primary email (unique across system)
        clinic: Foreign key to Clinic (multi-tenant support)
        role: User's role in the system (ADMIN, DOCTOR, PATIENT)
        contact_number: Primary phone number
        secondary_contact_number: Backup phone number
        address: User's physical address
        degree: Professional degree (e.g., "BDS", "MDS") for doctors
        is_deleted: Soft delete flag
        created_at: Record creation timestamp
        updated_at: Last modification timestamp
        created_by: Audit log - who created this record
        updated_by: Audit log - who last updated this record
    
    Multi-tenant architecture:
        All users belong to exactly one clinic.
        A clinic cannot be changed after initial assignment.
    """

    ROLE_CHOICES = [
        ('ADMIN', 'Clinic Administrator'),
        ('DOCTOR', 'Doctor/Orthodontist'),
    ]

    # Override default username field to use email
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=False, null=True, blank=True)

    # Multi-tenant support
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.PROTECT,  # Prevent clinic deletion if users exist
        related_name='users',
        db_index=True,
        null=True,
        blank=True,
        help_text='The clinic this user belongs to (optional for admin/superuser)'
    )

    # Role-based access control
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='DOCTOR',
        db_index=True,
        help_text='User role determines access permissions'
    )

    # Contact Information
    contact_number = models.CharField(
        max_length=20,
        validators=[validate_phone_number],
        null=True,
        blank=True,
        help_text='Primary phone number in format: +1234567890 or (123) 456-7890'
    )

    secondary_contact_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[validate_phone_number],
        help_text='Alternative phone number'
    )

    address = models.TextField(
        blank=True,
        null=True,
        help_text='Complete physical address'
    )

    # Professional Information (mainly for doctors)
    degree = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Professional degree (e.g., BDS, MDS, DDS, DMD)'
    )

    # Soft Delete
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Not actually deleted, just marked as inactive'
    )

    # Audit Logging
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
        help_text='User who created this record'
    )

    updated_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_users',
        help_text='User who last modified this record'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Custom manager with soft delete support
    objects = CustomUserManager()
    all_objects = SoftDeleteManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'clinic']),
            models.Index(fields=['clinic', 'role']),
            models.Index(fields=['is_deleted', 'clinic']),
        ]
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def soft_delete(self):
        """Soft delete user (mark as deleted)."""
        self.is_deleted = True
        self.save(update_fields=['is_deleted', 'updated_at'])

    def restore(self):
        """Restore a soft-deleted user."""
        self.is_deleted = False
        self.save(update_fields=['is_deleted', 'updated_at'])

    def is_admin(self):
        """Check if user is a clinic admin."""
        return self.role == 'ADMIN'

    def is_doctor(self):
        """Check if user is a doctor."""
        return self.role == 'DOCTOR'

    def is_patient(self):
        """Patients are no longer stored in CustomUser; always returns False.

        This method remains only for compatibility with older code and should
        not be used in new development.
        """
        return False

    @property
    def full_contact_info(self):
        """Get complete contact information."""
        info = {
            'email': self.email,
            'primary_phone': self.contact_number,
            'secondary_phone': self.secondary_contact_number,
            'address': self.address,
        }
        return {k: v for k, v in info.items() if v}

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'contact_number']
