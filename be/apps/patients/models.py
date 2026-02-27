"""
Patient model - Standalone patient records with doctor assignment.

Architecture:
- Independent Patient model (not tied to CustomUser)
- Links to Clinic for multi-tenant support
- Can be assigned to a Doctor (CustomUser with role='DOCTOR')
- Supports medical history and contact information
"""

from django.db import models
from django.core.validators import EmailValidator
from core.managers import MultiTenantManager


class Patient(models.Model):
    """
    Patient record - Medical and contact information.

    Patients do **not** have credentials; only doctors and admins are valid
    users of the system. The model stores complete patient information for
    medical records and appointment management.
    """

    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
        ('NOT_SPECIFIED', 'Prefer not to specify'),
    ]

    # Multi-tenant support
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        related_name='patients',
        db_index=True,
        help_text='Clinic where patient is registered'
    )

    # Basic information
    first_name = models.CharField(max_length=150, help_text='Patient first name')
    last_name = models.CharField(max_length=150, help_text='Patient last name')
    email = models.EmailField(blank=True, null=True, help_text='Patient email address')
    contact_number = models.CharField(max_length=20, blank=True, null=True, help_text='Primary phone number')
    secondary_contact_number = models.CharField(max_length=20, blank=True, null=True, help_text='Alternative phone number')
    address = models.TextField(blank=True, null=True, help_text='Patient address')

    # Personal information
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True, help_text='Patient gender')
    date_of_birth = models.DateField(blank=True, null=True, help_text='Patient date of birth')

    # Doctor assignment
    assigned_doctor = models.ForeignKey(
        'users.CustomUser',
        null=True,
        blank=True,
        limit_choices_to={'role': 'DOCTOR'},
        on_delete=models.SET_NULL,
        related_name='assigned_patients',
        help_text='Doctor assigned to this patient (optional)'
    )

    # Medical information
    clinical_history = models.TextField(blank=True, null=True, help_text='Clinical history and notes')
    notes = models.TextField(blank=True, null=True, help_text='Additional notes about the patient')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['clinic', 'assigned_doctor']),
            models.Index(fields=['clinic', 'first_name', 'last_name']),
        ]

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def age(self):
        """Calculate patient's current age."""
        from datetime import date
        if not self.date_of_birth:
            return None
        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )

    @property
    def active_treatments_count(self):
        """Get count of active treatments for this patient."""
        return self.treatments.filter(status='ONGOING', is_deleted=False).count()



