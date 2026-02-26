"""
Testing Guide for Dental Clinic Management System

Instructions for writing and running tests.
"""

# ============================================================================
# TESTING SETUP
# ============================================================================

## Install Testing Dependencies

```bash
pip install pytest pytest-django pytest-cov factory-boy faker
```

## Create conftest.py

Create `be/conftest.py` in the project root:

```python
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import pytest
from django.test import Client
from apps.clinics.models import Clinic
from apps.users.models import CustomUser


@pytest.fixture
def clinic():
    """Create a test clinic."""
    return Clinic.objects.create(
        name='Test Clinic',
        contact_number='(555) 123-4567',
        address='123 Test St',
        description='Test clinic for testing'
    )


@pytest.fixture
def admin_user(clinic):
    """Create an admin user."""
    return CustomUser.objects.create_user(
        email='admin@test.com',
        password='testpass123',
        first_name='Admin',
        last_name='User',
        contact_number='(555) 111-1111',
        clinic=clinic,
        role='ADMIN'
    )


@pytest.fixture
def doctor_user(clinic):
    """Create a doctor user."""
    return CustomUser.objects.create_user(
        email='doctor@test.com',
        password='testpass123',
        first_name='Dr',
        last_name='Smith',
        contact_number='(555) 222-2222',
        clinic=clinic,
        role='DOCTOR',
        degree='DDS'
    )


@pytest.fixture
def patient_user(clinic):
    """Create a patient user (auto-creates PatientProfile)."""
    return CustomUser.objects.create_user(
        email='patient@test.com',
        password='testpass123',
        first_name='John',
        last_name='Doe',
        contact_number='(555) 333-3333',
        clinic=clinic,
        role='PATIENT'
    )


@pytest.fixture
def api_client():
    """DRF API client."""
    return Client()


@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    """API client authenticated as admin."""
    api_client.force_login(admin_user)
    return api_client


@pytest.fixture
def authenticated_doctor_client(api_client, doctor_user):
    """API client authenticated as doctor."""
    api_client.force_login(doctor_user)
    return api_client


@pytest.fixture
def authenticated_patient_client(api_client, patient_user):
    """API client authenticated as patient."""
    api_client.force_login(patient_user)
    return api_client
```


# ============================================================================
# UNIT TESTS EXAMPLES
# ============================================================================

## Test User Model

Create `be/tests/test_models_user.py`:

```python
import pytest
from apps.users.models import CustomUser
from apps.patients.models import PatientProfile


@pytest.mark.django_db
class TestCustomUser:
    """Test CustomUser model."""

    def test_create_user(self, clinic):
        """Test creating a user."""
        user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
            clinic=clinic,
            contact_number='(555) 123-4567'
        )
        assert user.email == 'test@example.com'
        assert user.check_password('testpass123')
        assert user.clinic == clinic

    def test_user_full_name(self, clinic):
        """Test get_full_name method."""
        user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe',
            clinic=clinic,
            contact_number='(555) 123-4567'
        )
        assert user.get_full_name() == 'John Doe'

    def test_is_doctor(self, doctor_user):
        """Test is_doctor method."""
        assert doctor_user.is_doctor() is True
        assert doctor_user.is_patient() is False
        assert doctor_user.is_admin() is False

    def test_soft_delete_user(self, admin_user):
        """Test soft delete functionality."""
        assert admin_user.is_deleted is False
        admin_user.soft_delete()
        assert admin_user.is_deleted is True
        # User should not appear in normal queries
        assert not CustomUser.objects.filter(id=admin_user.id).exists()
        # But should appear in all_objects
        assert CustomUser.all_objects.filter(id=admin_user.id).exists()

    def test_patient_profile_auto_created(self, clinic):
        """Test that PatientProfile is auto-created for patients."""
        user = CustomUser.objects.create_user(
            email='patient@example.com',
            password='testpass123',
            clinic=clinic,
            contact_number='(555) 123-4567',
            role='PATIENT'
        )
        # PatientProfile should be auto-created
        assert hasattr(user, 'patient_profile')
        assert user.patient_profile.clinic == clinic
```

## Test Clinic Model

Create `be/tests/test_models_clinic.py`:

```python
import pytest
from apps.clinics.models import Clinic


@pytest.mark.django_db
class TestClinic:
    """Test Clinic model."""

    def test_create_clinic(self):
        """Test creating a clinic."""
        clinic = Clinic.objects.create(
            name='Test Clinic',
            contact_number='(555) 123-4567',
            address='123 Test St'
        )
        assert clinic.name == 'Test Clinic'
        assert clinic.is_active is True
        assert clinic.is_deleted is False

    def test_clinic_soft_delete(self, clinic):
        """Test clinic soft delete."""
        assert clinic.is_deleted is False
        clinic.soft_delete()
        assert clinic.is_deleted is True
        # Should not appear in normal queries
        assert not Clinic.objects.filter(id=clinic.id).exists()

    def test_clinic_user_count(self, clinic, admin_user, doctor_user):
        """Test clinic user count property."""
        assert clinic.user_count == 2
        assert clinic.doctor_count == 1
        assert clinic.patient_count == 0
```


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================

## Test Authentication Endpoints

Create `be/tests/test_api_auth.py`:

```python
import pytest
from rest_framework.test import APIClient
from rest_framework import status


@pytest.mark.django_db
class TestAuthAPI:
    """Test authentication endpoints."""

    def setUp(self):
        self.client = APIClient()

    def test_register_user(self):
        """Test user registration."""
        response = self.client.post('/api/auth/register/', {
            'email': 'newuser@example.com',
            'first_name': 'John',
            'last_name': 'Doe',
            'contact_number': '(555) 123-4567',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!',
            'clinic_id': 1,
            'role': 'DOCTOR'
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True

    def test_login_user(self, admin_user):
        """Test user login."""
        response = self.client.post('/api/auth/login/', {
            'email': 'admin@test.com',
            'password': 'testpass123'
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data['data']
        assert 'refresh' in response.data['data']

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = self.client.post('/api/auth/login/', {
            'email': 'nonexistent@example.com',
            'password': 'wrongpass'
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False

    def test_get_current_user(self, admin_user):
        """Test getting current user profile."""
        self.client.force_login(admin_user)
        response = self.client.get('/api/auth/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['email'] == 'admin@test.com'
```

## Test Treatment API

Create `be/tests/test_api_treatments.py`:

```python
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from apps.treatments.models import Treatment


@pytest.mark.django_db
class TestTreatmentAPI:
    """Test treatment endpoints."""

    def test_list_treatments_admin(self, authenticated_admin_client, clinic, admin_user, doctor_user, patient_user):
        """Test listing treatments as admin."""
        # Create a treatment
        Treatment.objects.create(
            clinic=clinic,
            patient=patient_user,
            doctor=doctor_user,
            treatment_type='BRACES',
            treatment_information='Standard braces',
            status='ONGOING',
            created_by=admin_user,
            updated_by=admin_user
        )

        response = authenticated_admin_client.get('/api/treatments/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_create_treatment(self, authenticated_doctor_client, clinic, doctor_user, patient_user):
        """Test creating a treatment."""
        response = authenticated_doctor_client.post('/api/treatments/', {
            'patient': patient_user.id,
            'doctor': doctor_user.id,
            'treatment_type': 'ALIGNERS',
            'treatment_information': 'Clear aligners treatment',
            'status': 'SCHEDULED',
            'next_visit_date': '2026-03-25T14:00:00Z'
        })
        assert response.status_code == status.HTTP_201_CREATED

    def test_cannot_access_other_clinic_data(self, clinic, admin_user):
        """Test that users cannot access other clinic data."""
        # Create another clinic and user
        from apps.clinics.models import Clinic
        other_clinic = Clinic.objects.create(
            name='Other Clinic',
            contact_number='(555) 999-9999',
            address='999 Other St'
        )
        other_user = CustomUser.objects.create_user(
            email='other@example.com',
            password='testpass123',
            clinic=other_clinic,
            role='ADMIN',
            contact_number='(555) 999-9999'
        )

        # Create treatment in first clinic
        patient = CustomUser.objects.create_user(
            email='patient@test.com',
            password='testpass123',
            clinic=clinic,
            role='PATIENT',
            contact_number='(555) 111-1111'
        )

        treatment = Treatment.objects.create(
            clinic=clinic,
            patient=patient,
            treatment_type='BRACES',
            treatment_information='Test',
            created_by=admin_user,
            updated_by=admin_user
        )

        # Try to access with user from other clinic
        client = APIClient()
        client.force_login(other_user)
        response = client.get(f'/api/treatments/{treatment.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
```

## Test Permissions

Create `be/tests/test_permissions.py`:

```python
import pytest
from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestPermissions:
    """Test permission enforcement."""

    def test_patient_cannot_create_treatment(self, patient_user, clinic):
        """Test that patients cannot create treatments."""
        client = APIClient()
        client.force_login(patient_user)
        response = client.post('/api/treatments/', {
            'patient': patient_user.id,
            'treatment_type': 'BRACES',
            'treatment_information': 'Test'
        })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_doctor_can_view_own_clinic_treatments(self, doctor_user, clinic, patient_user):
        """Test that doctors can view treatments in their clinic."""
        from apps.treatments.models import Treatment
        Treatment.objects.create(
            clinic=clinic,
            patient=patient_user,
            doctor=doctor_user,
            treatment_type='BRACES',
            treatment_information='Test',
            created_by=doctor_user,
            updated_by=doctor_user
        )

        client = APIClient()
        client.force_login(doctor_user)
        response = client.get('/api/treatments/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_patient_can_view_own_profile(self, patient_user):
        """Test that patients can view their own profile."""
        client = APIClient()
        client.force_login(patient_user)
        response = client.get('/api/patients/my_profile/')
        assert response.status_code == status.HTTP_200_OK
```


# ============================================================================
# RUNNING TESTS
# ============================================================================

## Run All Tests

```bash
pytest
```

## Run Tests with Coverage

```bash
pytest --cov=apps --cov=core --cov-report=html
```

## Run Specific Test File

```bash
pytest tests/test_api_auth.py
```

## Run Specific Test Class

```bash
pytest tests/test_api_auth.py::TestAuthAPI
```

## Run Specific Test Method

```bash
pytest tests/test_api_auth.py::TestAuthAPI::test_login_user
```

## Run Tests with Verbose Output

```bash
pytest -v
```

## Run Tests in Parallel

```bash
pytest -n auto
```


# ============================================================================
# TEST ORGANIZATION
# ============================================================================

Create tests directory structure:

```
be/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Shared fixtures
│   ├── factories.py             # Test data factories
│   │
│   ├── models/
│   │   ├── test_user.py
│   │   ├── test_clinic.py
│   │   ├── test_patient.py
│   │   └── test_treatment.py
│   │
│   ├── api/
│   │   ├── test_auth.py
│   │   ├── test_users.py
│   │   ├── test_clinics.py
│   │   ├── test_patients.py
│   │   └── test_treatments.py
│   │
│   ├── permissions/
│   │   └── test_permissions.py
│   │
│   └── integration/
│       └── test_user_flow.py
└── pytest.ini                    # Pytest configuration
```


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

Create `be/pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --tb=short
    --disable-warnings

markers =
    integration: mark test as an integration test
    slow: mark test as slow running
```


# ============================================================================
# CONTINUOUS INTEGRATION
# ============================================================================

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_DB: test_db
          POSTGRES_PASSWORD: password
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-django pytest-cov
    
    - name: Run migrations
      run: python manage.py migrate
    
    - name: Run tests
      run: pytest --cov=apps --cov=core
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```


# ============================================================================
# TEST BEST PRACTICES
# ============================================================================

✅ **Use Fixtures** - DRY and reusable test data
✅ **Use Markers** - Organize and categorize tests
✅ **Test One Thing** - Single assertion per test
✅ **Clear Names** - Descriptive test names
✅ **Use Factories** - Easy test data creation
✅ **Isolate Tests** - No test dependencies
✅ **Mock External APIs** - Don't call real services
✅ **Test Edge Cases** - Don't just test happy path
✅ **Test Permissions** - Critical for multi-tenant apps
✅ **Test Data Isolation** - Verify clinic isolation


# ============================================================================
# DEBUGGING TESTS
# ============================================================================

## Print Statement Debugging

```python
def test_something(client):
    response = client.get('/api/users/')
    print(response.data)  # Will show in pytest -s output
    assert ...
```

Run with: `pytest -s`

## Use pdb

```python
def test_something(client):
    response = client.get('/api/users/')
    import pdb; pdb.set_trace()  # Debugger will pause here
    assert ...
```

Run with: `pytest --pdb`

## Use pytest fixtures for debugging

```python
@pytest.fixture
def debug_clinic(clinic):
    print(f"Clinic ID: {clinic.id}")
    yield clinic
```


---

For more information, see:
- [pytest documentation](https://docs.pytest.org/)
- [pytest-django documentation](https://pytest-django.readthedocs.io/)
- [Django testing documentation](https://docs.djangoproject.com/en/4.2/topics/testing/)
