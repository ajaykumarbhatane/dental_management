"""
Comprehensive README for Dental Clinic Management System.
"""
# Dental Clinic Management System

A production-ready, multi-tenant SaaS dental clinic management system built with Django and Django REST Framework.

## 🏗️ Architecture Overview

### Multi-Tenant Architecture
- Complete data isolation between clinics
- Clinic-based filtering on all endpoints
- Secure access control with role-based permissions

### Technology Stack
- **Backend**: Django 4.2.10, Django REST Framework 3.14.0
- **Database**: PostgreSQL (recommended for production)
- **Authentication**: JWT (SimpleJWT)
- **Caching**: Redis
- **File Storage**: Local (or AWS S3 in production)
- **API Documentation**: OpenAPI/Swagger (drf-spectacular)

## 📁 Project Structure

```
be/
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
├── .env.example                   # Example environment variables
│
├── config/                        # Django configuration
│   ├── settings.py               # Main settings (production-ready)
│   ├── urls.py                   # Root URL configuration
│   ├── wsgi.py                   # WSGI application
│   ├── asgi.py                   # ASGI application
│   └── openapi.py                # OpenAPI customization
│
├── core/                          # Shared utilities and base classes
│   ├── managers.py               # Custom Django managers (soft delete, multi-tenant)
│   ├── permissions.py            # DRF permission classes
│   ├── exceptions.py             # Custom exception handlers
│   ├── validators.py             # Field validators
│   └── utils.py                  # Helper functions
│
├── apps/                          # Clean architecture: Each app is independent
│   │
│   ├── users/                    # User authentication and management
│   │   ├── models.py             # CustomUser model (multi-tenant)
│   │   ├── serializers.py        # User serializers
│   │   ├── views.py              # Auth viewsets
│   │   ├── views_management.py   # User management viewsets
│   │   ├── urls_auth.py          # Auth endpoints
│   │   ├── urls.py               # User management endpoints
│   │   ├── admin.py              # Django admin config
│   │   ├── apps.py               # App configuration
│   │   ├── signals.py            # Django signals (auto-create patient profile)
│   │   └── managers.py            # (optional) Custom user managers
│   │
│   ├── clinics/                  # Clinic management (tenants)
│   │   ├── models.py             # Clinic model
│   │   ├── serializers.py        # Clinic serializers
│   │   ├── views.py              # Clinic viewsets
│   │   ├── urls.py               # Clinic endpoints
│   │   ├── admin.py              # Django admin config
│   │   └── apps.py               # App configuration
│   │
│   ├── patients/                 # Patient profiles and medical records
│   │   ├── models.py             # PatientProfile model
│   │   ├── serializers.py        # Patient serializers
│   │   ├── views.py              # Patient viewsets
│   │   ├── urls.py               # Patient endpoints
│   │   ├── admin.py              # Django admin config
│   │   ├── apps.py               # App configuration
│   │   └── signals.py            # Patient-related signals
│   │
│   └── treatments/               # Treatment management (orthodontics)
│       ├── models.py             # Treatment model
│       ├── serializers.py        # Treatment serializers
│       ├── views.py              # Treatment viewsets
│       ├── urls.py               # Treatment endpoints
│       ├── admin.py              # Django admin config
│       └── apps.py               # App configuration
│
├── static/                        # Static files (CSS, JS, images)
└── media/                         # User-uploaded files
```

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone/navigate to the project
cd be/

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 2. Database Setup

```bash
# For SQLite (development - default)
python manage.py migrate
python manage.py createsuperuser

# For PostgreSQL (production)
# createdb dental_clinic_db
# python manage.py migrate
# python manage.py createsuperuser
```

### 3. Run Development Server

```bash
python manage.py runserver
```

Visit: http://localhost:8000/api/docs/

## 🔐 Authentication

### JWT Tokens

The system uses JWT for stateless authentication.

**Token Endpoints:**
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get access + refresh tokens
- `POST /api/auth/token/` - Get JWT tokens (email + password)
- `POST /api/auth/token/refresh/` - Refresh access token
- `POST /api/auth/logout/` - Logout

**Headers for Authenticated Requests:**
```
Authorization: Bearer <access_token>
```

## 📋 Multi-Tenant Architecture

### Data Isolation
Every resource is automatically scoped to the requesting user's clinic:

```python
# Automatic clinic filtering
def get_queryset(self):
    return filter_by_user_clinic(Treatment.objects.all(), self.request)
```

### User Roles

1. **ADMIN** - Clinic administrator
   - Full control within their clinic
   - Can create/manage users and treatments
   - Can view statistics

2. **DOCTOR** - Orthodontist/Doctor
   - Create and manage treatments
   - View patient profiles
   - Limited to their clinic

3. **PATIENT** - Patient
   - View own profile and treatments
   - Cannot access other patients
   - View medical records and appointments

## 📚 API Endpoints

### Authentication
```
POST   /api/auth/register/        - Register new user
POST   /api/auth/login/           - Login with email/password
POST   /api/auth/logout/          - Logout
GET    /api/auth/me/              - Get current user profile
PUT    /api/auth/me/              - Update profile
POST   /api/auth/change-password/ - Change password
```

### Clinics
```
GET    /api/clinics/              - List clinics
POST   /api/clinics/              - Create clinic (admin)
GET    /api/clinics/<id>/         - Get clinic details
PUT    /api/clinics/<id>/         - Update clinic (admin)
DELETE /api/clinics/<id>/         - Delete clinic (soft delete)
GET    /api/clinics/<id>/statistics/ - Get clinic statistics
```

### Users Management
```
GET    /api/users/                - List users in clinic
POST   /api/users/                - Create user (admin)
GET    /api/users/<id>/           - Get user details
PUT    /api/users/<id>/           - Update user (admin)
DELETE /api/users/<id>/           - Delete user (soft delete)
GET    /api/users/doctors/        - List doctors
GET    /api/users/patients/       - List patients
GET    /api/users/admin_users/    - List admin users
```

### Patients
```
GET    /api/patients/                    - List patients in clinic
POST   /api/patients/                    - Create patient (admin)
GET    /api/patients/<id>/               - Get patient details
PUT    /api/patients/<id>/               - Update patient
DELETE /api/patients/<id>/               - Delete patient (soft delete)
GET    /api/patients/<id>/medical-summary/ - Get medical summary
GET    /api/patients/my_profile/         - Get own profile (patient)
```

### Treatments
```
GET    /api/treatments/                  - List treatments
POST   /api/treatments/                  - Create treatment (doctor/admin)
GET    /api/treatments/<id>/             - Get treatment details
PUT    /api/treatments/<id>/             - Update treatment
DELETE /api/treatments/<id>/             - Delete treatment (soft delete)
GET    /api/treatments/upcoming/         - List upcoming treatments
GET    /api/treatments/overdue/          - List overdue treatments
GET    /api/treatments/by_status/        - Filter by status
POST   /api/treatments/<id>/mark_completed/ - Mark as completed
POST   /api/treatments/<id>/mark_cancelled/ - Mark as cancelled
```

### API Documentation
```
GET    /api/docs/                 - Swagger UI (Interactive)
GET    /api/redoc/                - ReDoc
GET    /api/schema/               - OpenAPI schema JSON
```

## 🔒 Security Features

### 1. Multi-Tenant Security
- Clinic-based data isolation on every query
- `IsSameClinic` permission validates clinic membership
- Cross-clinic data access is blocked

### 2. Role-Based Access Control (RBAC)
- Custom permission classes for each role
- Granular endpoint-level permissions
- Audit logging (created_by, updated_by)

### 3. Soft Delete
- Models use `is_deleted` flag instead of hard delete
- Data retention for compliance
- `.all_objects.all()` to access deleted records

### 4. Password Security
- Minimum 8 characters
- Password validation rules applied
- Change password endpoint with old password verification

### 5. File Upload Security
- File size validation (5MB max)
- File type validation (images only)
- Stored outside web root

## 📊 Database Schema

### CustomUser
```
email (unique, indexed)
first_name, last_name
clinic (FK to Clinic)
role (ADMIN, DOCTOR, PATIENT)
contact_number, secondary_contact_number
address, degree (for doctors)
is_active, is_deleted
created_by, updated_by (audit)
created_at, updated_at
```

### Clinic
```
name (unique, indexed)
contact_number, address
description
is_active, is_deleted
created_at, updated_at
```

### PatientProfile
```
user (OneToOne to CustomUser)
clinic (FK to Clinic)
gender, date_of_birth
medical_history, allergies
created_at, updated_at
```

### Treatment
```
clinic (FK to Clinic, indexed)
patient (FK to CustomUser, indexed)
doctor (FK to CustomUser, indexed)
treatment_type (BRACES, ALIGNERS, etc.)
treatment_information, treatment_findings
upload_image (ImageField)
next_visit_date (indexed for scheduling)
status (ONGOING, COMPLETED, etc.)
is_deleted
created_by, updated_by (audit logging)
created_at, updated_at
```

## 🔄 Signals and Auto-Operations

### Patient Profile Auto-Creation
When a user with `role='PATIENT'` is created, a `PatientProfile` is automatically created via Django signals.

```python
# In apps/users/signals.py
@receiver(post_save, sender=CustomUser)
def create_patient_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'PATIENT':
        PatientProfile.objects.create(
            user=instance,
            clinic=instance.clinic
        )
```

## 💾 Custom Managers

### SoftDeleteManager
Filters out soft-deleted records by default:
```python
# Returns only active records
User.objects.all()

# Get all records including deleted ones
User.all_objects.all()

# Get only deleted records
User.all_objects.deleted()
```

### MultiTenantManager
Implements both soft delete and clinic filtering:
```python
# Filter by specific clinic
Treatment.objects.by_clinic(clinic)
```

## 🧪 Example API Usage

### 1. Register User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "doctor@clinic.com",
    "first_name": "John",
    "last_name": "Doe",
    "contact_number": "(123) 456-7890",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!",
    "clinic_id": 1,
    "role": "DOCTOR",
    "degree": "BDS"
}'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "doctor@clinic.com",
    "password": "SecurePass123!"
}'
```

### 3. Create Treatment
```bash
curl -X POST http://localhost:8000/api/treatments/ \\
  -H "Authorization: Bearer <access_token>" \\
  -H "Content-Type: application/json" \\
  -d '{
    "patient": 5,
    "doctor": 2,
    "treatment_type": "BRACES",
    "treatment_information": "Metal braces for upper jaw alignment",
    "next_visit_date": "2026-03-25T14:00:00Z",
    "status": "ONGOING"
}'
```

### 4. Get Patient Profile
```bash
curl -X GET http://localhost:8000/api/patients/5/ \\
  -H "Authorization: Bearer <access_token>"
```

## 📈 Filtering and Search

All list endpoints support:

### Filtering
```
GET /api/treatments/?status=ONGOING&treatment_type=BRACES
GET /api/patients/?gender=MALE
GET /api/users/?role=DOCTOR
```

### Search
```
GET /api/treatments/?search=john
GET /api/patients/?search=doe
```

### Ordering
```
GET /api/treatments/?ordering=-created_at
GET /api/patients/?ordering=user__first_name
```

### Pagination
```
GET /api/treatments/?page=1&page_size=20
```

## 🚀 Production Deployment

### Environment Configuration
Create `.env` with production values:
```
DEBUG=False
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

DB_ENGINE=django.db.backends.postgresql
DB_NAME=dental_clinic_prod
DB_USER=postgres
DB_PASSWORD=secure-password
DB_HOST=db-server-ip
DB_PORT=5432

USE_S3=True
AWS_STORAGE_BUCKET_NAME=dental-clinic-media
AWS_S3_REGION_NAME=us-east-1
```

### Run Migrations
```bash
python manage.py migrate --noinput
```

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Run with Gunicorn
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## 📖 Key Features

✅ **Multi-tenant Architecture** - Complete clinic isolation  
✅ **JWT Authentication** - Stateless, scalable auth  
✅ **Role-Based Access Control** - Fine-grained permissions  
✅ **Soft Delete** - Data retention and compliance  
✅ **Audit Logging** - Track who created/updated data  
✅ **Advanced Filtering** - Search, filter, and sort options  
✅ **Image Uploads** - Before/after treatment documentation  
✅ **Pagination** - Handle large datasets efficiently  
✅ **API Documentation** - Interactive Swagger UI  
✅ **Production Ready** - Security, caching, logging configured  

## 🤝 Support

For issues or questions, refer to Django and DRF documentation:
- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/)

---

**Built with ❤️ for Production-Grade SaaS Applications**
