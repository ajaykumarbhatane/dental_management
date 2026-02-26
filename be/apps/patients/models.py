"""
Patient Profile model.

Architecture:
- OneToOneField relationship with CustomUser
- Separate from User to allow flexible patient-specific information
- Auto-created via signals when a user with role='PATIENT' is created
"""

from django.db import models
from django.core.validators import URLValidator
from core.managers import MultiTenantManager


class PatientProfile(models.Model):
    """
    Extended patient profile separate from User model.
    
    This model is automatically created via Django signals when a user
    with role='PATIENT' is created.
    
    Attributes:
        user: OneToOne link to CustomUser
        clinic: FK to clinic (for easy filtering)
        gender: Patient's gender
        date_of_birth: Patient's date of birth
        medical_history: Detailed medical history
        allergies: Known allergies
        created_at: Record creation timestamp
    """

    GENDER_CHOICES = [
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('OTHER', 'Other'),
        ('NOT_SPECIFIED', 'Prefer not to specify'),
    ]

    # Link to User
    user = models.OneToOneField(
        'users.CustomUser',
        on_delete=models.CASCADE,
        related_name='patient_profile',
        help_text='Link to the patient user account'
    )

    # Multi-tenant support (denormalized for query efficiency)
    clinic = models.ForeignKey(
        'clinics.Clinic',
        on_delete=models.CASCADE,
        related_name='patient_profiles',
        db_index=True,
        help_text='Clinic where the patient is registered'
    )

    # Personal Information
    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
        help_text='Patient gender'
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text='Patient date of birth'
    )

    # Medical Information
    medical_history = models.TextField(
        blank=True,
        null=True,
        help_text='Detailed medical history and conditions'
    )

    allergies = models.TextField(
        blank=True,
        null=True,
        help_text='Known allergies and sensitivities'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True, help_text='Soft delete flag')

    # Custom manager
    objects = MultiTenantManager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'
        indexes = [
            models.Index(fields=['clinic', 'user']),
        ]

    def __str__(self):
        return f"Patient Profile - {self.user.get_full_name()}"

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
            - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        )

    @property
    def active_treatments_count(self):
        """Get count of active treatments for this patient."""
        return self.user.treatments.filter(status='ONGOING').count()

    def get_medical_summary(self):
        """Get compact medical information for quick access."""
        return {
            'age': self.age,
            'gender': self.get_gender_display(),
            'medical_history': self.medical_history,
            'allergies': self.allergies,
        }
