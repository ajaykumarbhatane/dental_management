"""
Quick Reference Guide for Dental Clinic Management System

Common commands, patterns, and troubleshooting.
"""

# ============================================================================
# QUICK START COMMANDS
# ============================================================================

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database setup
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Access admin panel
http://localhost:8000/admin/

# Access API documentation
http://localhost:8000/api/docs/


# ============================================================================
# COMMON DJANGO COMMANDS
# ============================================================================

# Create new app
python manage.py startapp app_name

# Create an empty migration
python manage.py makemigrations --empty app_name --name describe_change

# Run specific migration
python manage.py migrate app_name 0001_initial

# Rollback all migrations
python manage.py migrate app_name zero

# Check for migrations
python manage.py showmigrations

# Run management command
python manage.py shell
python manage.py dbshell
python manage.py dumpdata > backup.json
python manage.py loaddata backup.json


# ============================================================================
# COMMON API PATTERNS
# ============================================================================

# Get User's Clinic (in ViewSet)
clinic = self.request.user.clinic

# Filter Queryset by User's Clinic
queryset = filter_by_user_clinic(Treatment.objects.all(), self.request)

# Add Clinic to Serializer Context (for validation)
context = super().get_serializer_context()
context['clinic'] = self.request.user.clinic
return context

# Create with Audit Logging
treatment = Treatment.objects.create(
    clinic=clinic,
    patient=patient,
    doctor=doctor,
    created_by=request.user,
    updated_by=request.user
)

# Soft Delete
instance.soft_delete()

# Restore Soft-Deleted Item
instance.restore()

# Get All Including Deleted
Treatment.all_objects.filter(patient=patient)

# Get Only Deleted
Treatment.all_objects.deleted()


# ============================================================================
# PERMISSION USAGE
# ============================================================================

# Check if user is admin
if request.user.role == 'ADMIN':
    # do admin stuff

# Check if user is doctor
if request.user.is_doctor():
    # do doctor stuff

# Check if user is patient
if request.user.is_patient():
    # do patient stuff

# Add permissions to ViewSet
permission_classes = [IsAuthenticated, IsSameClinic, IsClinicAdmin]

# Custom permission for specific actions
def get_permissions(self):
    if self.action == 'create':
        permission_classes = [IsAuthenticated, IsClinicAdmin]
    else:
        permission_classes = [IsAuthenticated]
    return [permission() for permission in permission_classes]


# ============================================================================
# SERIALIZER PATTERNS
# ============================================================================

# Validation at field level
def validate_contact_number(self, value):
    validate_phone_number(value)
    return value

# Cross-field validation
def validate(self, data):
    if data['email'] == data['existing_email']:
        raise ValidationError('Email cannot be the same')
    return data

# Dynamic fields
def get_clinic(self, obj):
    return {
        'id': obj.clinic.id,
        'name': obj.clinic.name,
    }


# ============================================================================
# FILTER PATTERNS
# ============================================================================

# Filter by role
GET /api/users/?role=DOCTOR

# Filter by status
GET /api/treatments/?status=ONGOING

# Filter by date range
GET /api/treatments/?next_visit_date_after=2026-03-01&next_visit_date_before=2026-03-31

# Search
GET /api/patients/?search=john

# Ordering
GET /api/treatments/?ordering=-created_at

# Multiple filters
GET /api/treatments/?status=ONGOING&treatment_type=BRACES&ordering=-next_visit_date


# ============================================================================
# TROUBLESHOOTING
# ============================================================================

## Issue: Import errors in migrations

Solution: Run makemigrations in correct order
```bash
python manage.py makemigrations apps.clinics
python manage.py makemigrations apps.users
python manage.py makemigrations apps.patients
python manage.py makemigrations apps.treatments
python manage.py migrate
```

## Issue: Clinic not automatically set

Solution: Clinic must be set when creating users
```python
user = CustomUser.objects.create_user(
    email=email,
    password=password,
    clinic=clinic_instance,  # ← Required
    role='DOCTOR'
)
```

## Issue: PatientProfile not created

Solution: PatientProfile is auto-created only with role='PATIENT'
```python
user = CustomUser.objects.create_user(
    email=email,
    role='PATIENT',  # ← Triggers signal
    clinic=clinic
)
# PatientProfile automatically created
```

## Issue: Permission denied on valid resource

Solution: Check clinic membership
```python
# User clinic must match resource clinic
assert user.clinic == treatment.clinic
```

## Issue: Cross-clinic data visible

Solution: Verify filter_by_user_clinic is called in get_queryset()
```python
def get_queryset(self):
    # This MUST filter by clinic
    return filter_by_user_clinic(Treatment.objects.all(), self.request)
```

## Issue: Deleted records showing

Solution: Use .all_objects for accessing deleted records
```python
# Default - excludes deleted
Treatment.objects.all()

# Includes deleted - for admin recovery
Treatment.all_objects.all()
```


# ============================================================================
# TESTING PATTERNS
# ============================================================================

# Create test user
user = CustomUser.objects.create_user(
    email='test@example.com',
    password='testpass123',
    clinic=clinic,
    role='DOCTOR'
)

# Create test clinic
clinic = Clinic.objects.create(
    name='Test Clinic',
    contact_number='(555) 123-4567',
    address='123 Test St'
)

# Authenticate in tests
client.force_authenticate(user=user)

# Make request
response = client.get('/api/treatments/')
assert response.status_code == 200

# Test permissions
user_other_clinic = CustomUser.objects.create_user(..., clinic=other_clinic)
client.force_authenticate(user=user_other_clinic)
response = client.get('/api/treatments/')
assert response.status_code == 403  # Forbidden


# ============================================================================
# USEFUL DJANGO SHORTCUTS
# ============================================================================

# Get or create
clinic, created = Clinic.objects.get_or_create(
    name='Default Clinic',
    defaults={'contact_number': '(555) 000-0000'}
)

# Bulk create
users = CustomUser.objects.bulk_create([
    CustomUser(...),
    CustomUser(...),
])

# Update multiple
Treatment.objects.filter(status='SCHEDULED').update(status='ONGOING')

# Count
Treatment.objects.filter(clinic=clinic).count()

# Exists
if Treatment.objects.filter(patient=patient).exists():
    print('Has treatments')

# Latest/First
latest_treatment = Treatment.objects.latest('created_at')
first_treatment = Treatment.objects.first()

# Distinct
unique_clinics = CustomUser.objects.values('clinic').distinct()


# ============================================================================
# PERFORMANCE TIPS
# ============================================================================

# Use select_related for ForeignKey
treatments = Treatment.objects.select_related('clinic', 'patient', 'doctor')

# Use prefetch_related for reverse relations
clinics = Clinic.objects.prefetch_related('users', 'treatments')

# Use only() to limit fields
users = CustomUser.objects.only('id', 'email', 'clinic')

# Use defer() to exclude fields
users = CustomUser.objects.defer('address', 'medical_history')

# Use values() for specific columns
emails = CustomUser.objects.values_list('email', flat=True)

# Use count() instead of len()
count = Treatment.objects.filter(status='ONGOING').count()

# Use exists() instead of count()
has_treatments = Treatment.objects.filter(clinic=clinic).exists()


# ============================================================================
# DEBUGGING TIPS
# ============================================================================

# Print SQL queries
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as queries:
    Treatment.objects.all()
    for q in queries:
        print(q)

# Django debug toolbar (development)
pip install django-debug-toolbar

# Print request user info
print(f"User: {request.user}")
print(f"Clinic: {request.user.clinic}")
print(f"Role: {request.user.role}")

# Django shell inspection
python manage.py shell
>>> from apps.users.models import CustomUser
>>> user = CustomUser.objects.get(email='test@example.com')
>>> user.clinic
>>> user.role


# ============================================================================
# DEPLOYMENT CHECKLIST
# ============================================================================

- [ ] DEBUG = False
- [ ] SECRET_KEY is secure
- [ ] ALLOWED_HOSTS configured
- [ ] CORS_ALLOWED_ORIGINS configured
- [ ] Database backed up
- [ ] Migrations run: python manage.py migrate
- [ ] Static files collected: python manage.py collectstatic
- [ ] Superuser created: python manage.py createsuperuser
- [ ] HTTPS enabled
- [ ] Security headers configured
- [ ] Logging configured
- [ ] Monitoring enabled
- [ ] Backup strategy implemented
- [ ] Rate limiting enabled
- [ ] CSRF protection enabled


---

For detailed documentation, see:
- README.md - Project overview
- API_EXAMPLES.md - API request/response examples
- DATABASE_SCHEMA.md - Database structure
- ARCHITECTURE.md - Architecture decisions
- DEPLOYMENT.md - Production deployment guide
