#!/usr/bin/env python
import os
import sys

# Setup path before Django
sys.path.insert(0, '/home/amazatic/Dental_Pro/be')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.users.models import CustomUser
from apps.clinics.models import Clinic
from apps.patients.models import Patient

# Create a clinic
clinic = Clinic.objects.create(name="Test Clinic", address="123 Main St")
print(f"✓ Created clinic: {clinic.name}")

# Create a doctor
doctor = CustomUser.objects.create_user(
    username="doctor_test",
    email="doctor@test.com",
    password="testpass123",
    clinic=clinic,
    role="DOCTOR",
    first_name="Dr.",
    last_name="Smith"
)
print(f"✓ Created doctor: {doctor.get_full_name()}")

# Create a patient
patient = Patient.objects.create(
    clinic=clinic,
    assigned_doctor=doctor,
    first_name="John",
    last_name="Doe",
)
print(f"✓ Created patient: {patient.get_full_name()}")

# Create an admin user
admin = CustomUser.objects.create_superuser(
    username="admin",
    email="admin@test.com",
    password="admin123",
    clinic=clinic
)
print(f"✓ Created admin: {admin.get_full_name()}")

print("\n✓ Test data created successfully!")
print(f"\nCredentials for testing:")
print(f"  Admin: admin / admin123")
print(f"  Doctor: doctor_test / testpass123")
