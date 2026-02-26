"""
Clinic model - Represents a dental clinic in the system.

Architecture:
- Base model for multi-tenant support
- All other entities are scoped to a clinic
- Soft delete support
- Audit logging
"""

from django.db import models
from core.managers import SoftDeleteManager


class Clinic(models.Model):
    """
    Represents a dental clinic in the multi-tenant system.
    
    Each clinic is a completely isolated tenant with its own:
    - Users (doctors, admins, patients)
    - Patients
    - Treatments
    - Prescriptions
    - Appointments
    
    Attributes:
        name: Clinic name (required)
        contact_number: Main clinic phone number
        address: Physical address of clinic
        description: Additional information about the clinic
        is_active: Whether clinic is currently active
        is_deleted: Soft delete flag
        created_at: Record creation timestamp
        updated_at: Last modification timestamp
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        help_text='Name of the dental clinic'
    )

    contact_number = models.CharField(
        max_length=20,
        help_text='Primary contact phone number'
    )

    address = models.TextField(
        help_text='Complete physical address of the clinic'
    )

    description = models.TextField(
        blank=True,
        null=True,
        help_text='Description of clinic, services, etc.'
    )

    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text='Whether this clinic is active and accepting patients'
    )

    # Soft Delete
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Soft delete flag for data retention'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Custom manager
    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'is_deleted']),
        ]
        verbose_name = 'Clinic'
        verbose_name_plural = 'Clinics'

    def __str__(self):
        return self.name

    def soft_delete(self):
        """Soft delete the clinic."""
        self.is_deleted = True
        self.save(update_fields=['is_deleted', 'updated_at'])

    def restore(self):
        """Restore a soft-deleted clinic."""
        self.is_deleted = False
        self.save(update_fields=['is_deleted', 'updated_at'])

    @property
    def user_count(self):
        """Get count of active users in the clinic."""
        return self.users.filter(is_deleted=False).count()

    @property
    def doctor_count(self):
        """Get count of active doctors in the clinic."""
        return self.users.filter(role='DOCTOR', is_deleted=False).count()

    @property
    def patient_count(self):
        """Get count of active patients in the clinic."""
        return self.users.filter(role='PATIENT', is_deleted=False).count()

    @property
    def active_treatments_count(self):
        """Get count of ongoing treatments."""
        return self.treatments.filter(status='ONGOING').count()
