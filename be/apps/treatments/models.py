"""
Treatment model - Core model for managing patient treatments.

Architecture:
- Focuses on orthodontics treatments
- Links patient, doctor, and clinic
- Supports image uploads for before/after documentation
- Multi-tenant support (scoped to clinic)
- Soft delete and audit logging
"""

from django.db import models
from django.core.validators import FileExtensionValidator
from core.managers import MultiTenantManager
from core.validators import validate_file_size, validate_image_file


class Treatment(models.Model):
    """
    Represents a patient treatment (orthodontic focus).
    
    Core treatment record connecting:
    - Patient (CustomUser with role='PATIENT')
    - Doctor (CustomUser with role='DOCTOR')
    - Clinic (for multi-tenant data isolation)
    
    Attributes:
        clinic: FK to Clinic (multi-tenant)
        patient: FK to Patient User
        doctor: FK to Doctor User
        treatment_type: Type of orthodontic treatment
        treatment_information: Detailed treatment plan
        treatment_findings: Clinical findings and observations
        upload_image: Before/after images
        next_visit_date: Date of next appointment
        status: Current treatment status
        is_deleted: Soft delete flag
        created_by: Audit log
        updated_by: Audit log
        created_at: Record creation timestamp
        updated_at: Last modification timestamp
    """

    TREATMENT_TYPE_CHOICES = [
        ('BRACES', 'Traditional Braces'),
        ('ALIGNERS', 'Clear Aligners (Invisalign)'),
        ('RETAINER', 'Retainer'),
        ('EXTRACTION', 'Extraction'),
        ('SCALING', 'Scaling & Root Planing'),
        ('ORTHOGNATHIC', 'Orthognathic Surgery Planning'),
        ('PROPHYLAXIS', 'Prophylaxis (Cleaning)'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('ONGOING', 'Ongoing'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
        ('ON_HOLD', 'On Hold'),
        ('SCHEDULED', 'Scheduled'),
    ]

    # Multi-tenant support
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        related_name='treatments',
        db_index=True,
        help_text='Clinic where treatment is being provided'
    )

    # Patient reference
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        related_name='treatments',
        db_index=True,
        help_text='Patient receiving the treatment'
    )

    # Doctor reference
    doctor = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='treatments_provided',
        limit_choices_to={'role': 'DOCTOR'},
        db_index=True,
        help_text='Doctor/Orthodontist providing the treatment'
    )

    # Treatment Information
    treatment_type = models.CharField(
        max_length=50,
        choices=TREATMENT_TYPE_CHOICES,
        db_index=True,
        help_text='Type of orthodontic treatment'
    )

    treatment_information = models.TextField(
        help_text='Detailed treatment plan and objectives'
    )

    treatment_findings = models.TextField(
        blank=True,
        null=True,
        help_text='Clinical findings, observations, and notes'
    )

    # Image Upload (Before/After documentation)
    upload_image = models.ImageField(
        upload_to='treatments/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp']),
        ],
        help_text='Treatment documentation image (max 5MB)'
    )

    # Schedule
    next_visit_date = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
        help_text='Date and time of next scheduled visit'
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='SCHEDULED',
        db_index=True,
        help_text='Current status of the treatment'
    )

    # Soft Delete
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text='Soft delete flag'
    )

    # Audit Logging
    created_by = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='treatments_created',
        help_text='User who created this treatment record'
    )

    updated_by = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='treatments_updated',
        help_text='User who last updated this treatment record'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Custom manager
    objects = MultiTenantManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['clinic', 'patient']),
            models.Index(fields=['clinic', 'doctor']),
            models.Index(fields=['clinic', 'status']),
            models.Index(fields=['next_visit_date', 'status']),
        ]
        unique_together = []  # Allow multiple treatments per patient
        verbose_name = 'Treatment'
        verbose_name_plural = 'Treatments'

    def __str__(self):
        return f"Treatment {self.id} - {self.patient.get_full_name()} ({self.treatment_type})"

    def soft_delete(self):
        """Soft delete the treatment record."""
        self.is_deleted = True
        self.save(update_fields=['is_deleted', 'updated_at'])

    def restore(self):
        """Restore a soft-deleted treatment."""
        self.is_deleted = False
        self.save(update_fields=['is_deleted', 'updated_at'])

    def mark_completed(self):
        """Mark treatment as completed."""
        self.status = 'COMPLETED'
        self.save(update_fields=['status', 'updated_at'])

    def mark_cancelled(self):
        """Mark treatment as cancelled."""
        self.status = 'CANCELLED'
        self.save(update_fields=['status', 'updated_at'])

    def is_upcoming(self):
        """Check if next visit is in the future."""
        from django.utils import timezone
        if not self.next_visit_date:
            return False
        return self.next_visit_date > timezone.now()

    def is_overdue(self):
        """Check if next visit is overdue."""
        from django.utils import timezone
        if not self.next_visit_date:
            return False
        return self.next_visit_date < timezone.now() and self.status == 'ONGOING'

    def save(self, *args, **kwargs):
        """Custom save with validation."""
        # Validate image file if uploaded
        if self.upload_image:
            try:
                # Check file size (5MB max)
                if self.upload_image.size > 5 * 1024 * 1024:
                    from django.core.exceptions import ValidationError
                    raise ValidationError('Image file size cannot exceed 5MB')
            except AttributeError:
                pass  # File might be string path in admin

        super().save(*args, **kwargs)
