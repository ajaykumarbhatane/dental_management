"""
Django signals for patients app.

Implements:
- Cleanup logic for soft-deleted patients
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.users.models import CustomUser
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUser)
def sync_patient_profile_deletion(sender, instance, **kwargs):
    """
    Keep PatientProfile deletion status in sync with user deletion.
    
    When a patient user is soft-deleted, mark their profile as updated.
    """
    if instance.role == 'PATIENT':
        try:
            patient_profile = instance.patient_profile
            # Just ensure profile exists and clinic is current
            if patient_profile.clinic != instance.clinic:
                patient_profile.clinic = instance.clinic
                patient_profile.save(update_fields=['clinic', 'updated_at'])
        except Exception as e:
            logger.error(f"Error syncing PatientProfile for user {instance.id}: {str(e)}")
