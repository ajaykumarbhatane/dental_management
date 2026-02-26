"""
Django signals for user app.

Implements:
- Auto-creation of PatientProfile when a PATIENT user is created
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.users.models import CustomUser
from apps.patients.models import PatientProfile
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUser)
def create_patient_profile(sender, instance, created, **kwargs):
    """
    Auto-create PatientProfile when a user with role='PATIENT' is created.
    
    This signal ensures every patient has an associated PatientProfile
    for storing medical information.
    
    Args:
        sender: CustomUser model
        instance: The CustomUser instance being saved
        created: Boolean indicating if this is a new instance
        kwargs: Additional keyword arguments
    """
    # Only create profile for new PATIENT users
    if created and instance.role == 'PATIENT':
        try:
            PatientProfile.objects.create(
                user=instance,
                clinic=instance.clinic
            )
            logger.info(f"PatientProfile created for user {instance.id}")
        except Exception as e:
            logger.error(f"Error creating PatientProfile for user {instance.id}: {str(e)}")


@receiver(post_save, sender=CustomUser)
def update_patient_profile_clinic(sender, instance, created, **kwargs):
    """
    Update PatientProfile clinic when patient's clinic changes.
    
    Ensures clinic denormalization is kept in sync.
    """
    if instance.role == 'PATIENT' and not created:
        try:
            patient_profile = instance.patient_profile
            if patient_profile.clinic != instance.clinic:
                patient_profile.clinic = instance.clinic
                patient_profile.save(update_fields=['clinic'])
                logger.info(f"PatientProfile clinic updated for user {instance.id}")
        except PatientProfile.DoesNotExist:
            # If profile doesn't exist, create it
            try:
                PatientProfile.objects.create(
                    user=instance,
                    clinic=instance.clinic
                )
                logger.info(f"PatientProfile created for user {instance.id} (via clinic update signal)")
            except Exception as e:
                logger.error(f"Error creating PatientProfile for user {instance.id}: {str(e)}")
