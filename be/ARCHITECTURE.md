"""
Architecture and Design Decisions Documentation

This document explains the architectural choices made in the Dental Clinic 
Management System project.
"""

# ============================================================================
# PROJECT ARCHITECTURE OVERVIEW
# ============================================================================

## Clean Architecture Principles

The project follows clean architecture principles with clear separation of concerns:

```
┌─────────────────────────────────────┐
│   Views (REST API - Serializers)    │  ← DRF Serializers
├─────────────────────────────────────┤
│  ViewSets (API Endpoints - Views)   │  ← Business Logic Entry Points
├─────────────────────────────────────┤
│  Managers & Querysets               │  ← Data access abstraction
├─────────────────────────────────────┤
│  Models (Database Layer)            │  ← ORM Models
├─────────────────────────────────────┤
│  Database (PostgreSQL)              │  ← Persistent Storage
└─────────────────────────────────────┘
```

### Why These Layers?

1. **Serializers** - Validate input, format output, decouple API from models
2. **ViewSets** - Handle HTTP requests, implement business logic
3. **Managers** - Custom query logic for soft delete and multi-tenant filtering
4. **Models** - Define data structure and relationships
5. **Database** - Persist data reliably


# ============================================================================
# MULTI-TENANT ARCHITECTURE
# ============================================================================

## Why Multi-Tenant?

A multi-tenant architecture is essential for a SaaS product:

✅ **Cost Efficiency**
   - Single database/server serves multiple clinics
   - Reduced infrastructure costs
   - Economies of scale

✅ **Data Isolation**
   - Complete clinic separation
   - HIPAA/privacy compliance
   - No cross-clinic data leaks

✅ **Scalability**
   - Add new clinics without infrastructure changes
   - Database scales with data, not clinic count
   - Shared resources efficiently

## Implementation Strategy

### 1. Foreign Key to Clinic (Primary Approach)
```python
class Treatment(models.Model):
    clinic = models.ForeignKey('clinics.Clinic', ...)  # ← Required FK
    patient = models.ForeignKey('users.CustomUser', ...)
    doctor = models.ForeignKey('users.CustomUser', ...)
```

**Advantages:**
- Explicit clinic ownership
- Database enforces relationships
- Efficient filtering with indexes

**Disadvantages:**
- Must set clinic on every create

### 2. Automatic Filtering via Middleware/Context
```python
def get_queryset(self):
    return filter_by_user_clinic(Model.objects.all(), self.request)
```

**Advantages:**
- Transparent filtering
- No manual clinic assignment
- Defense in depth

**Disadvantages:**
- Easy to accidentally bypass
- Less explicit


## Architecture Decision: HYBRID APPROACH

We use **BOTH** strategies:

1. **Foreign Key** - Explicit clinic ownership on models
2. **Filtering** - Automatic queryset filtering in views

This provides **defense in depth**:
- Models enforce clinic relationships
- Views filter by user's clinic
- Even if filtering is bypassed, models prevent cross-clinic access


# ============================================================================
# ROLE-BASED ACCESS CONTROL (RBAC)
# ============================================================================

## Three-Tier Role System

### ADMIN (Clinic Administrator)
- Full control within their clinic
- Can create/manage users
- Can create/update treatments
- Can view all patient records
- Can generate reports
- Cannot access other clinics

### DOCTOR (Orthodontist/Doctor)
- Create and manage treatments
- View patient profiles/medical history
- Cannot delete user accounts
- Cannot access other clinics
- Limited to assigned clinic

### PATIENT (Patient)
- View own profile
- View own treatment records
- View own medical history
- Cannot access other patients' data
- Limited to own records

## Permission Hierarchy

```
ADMIN > DOCTOR > PATIENT

ADMIN
├── Can access all clinic resources
├── Can manage users
├── Can create/edit/delete treatments
└── Can view clinic statistics

DOCTOR
├── Can view patient records
├── Can create/edit treatments
├── Can view clinic calendar
└── Cannot delete users or other clinic data

PATIENT
├── Can view own profile
├── Can view own treatments
├── Can view own medical history
└── Cannot modify any records
```

## Implementation

```python
# Core permission classes in core/permissions.py
class IsClinicAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'ADMIN'

class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'DOCTOR'

class IsSameClinic(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.clinic == request.user.clinic
```

## Usage in ViewSets

```python
class TreatmentViewSet(viewsets.ModelViewSet):
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAuthenticated, IsDoctorOrClinicAdmin, IsSameClinic]
        elif self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsClinicAdmin, IsSameClinic]
        # ...
        return [permission() for permission in permission_classes]
```


# ============================================================================
# DATA ISOLATION STRATEGIES
# ============================================================================

## Defense in Depth Approach

We implement multiple layers of protection:

### Layer 1: Database Constraints
- Foreign keys enforce relationships
- Indexes enable efficient filtering

### Layer 2: ORM Managers
- Custom managers filter by clinic
- `.all_objects` for admin overrides

### Layer 3: ViewSet Filtering
- `filter_by_user_clinic()` in get_queryset()
- Automatic clinic filtering

### Layer 4: Permissions
- `IsSameClinic` permission class
- Checked at object level

### Layer 5: Serializer Validation
- Validates clinic ownership before save
- Cross-clinic assignments rejected

```python
def validate(self, data):
    if data['patient'].clinic != self.context['clinic']:
        raise ValidationError('Patient must be from same clinic')
    return data
```


# ============================================================================
# JWT AUTHENTICATION DESIGN
# ============================================================================

## Why JWT?

✅ **Stateless** - No server-side session storage required
✅ **Scalable** - Works with distributed systems
✅ **Mobile-Friendly** - Easy to use in mobile apps
✅ **Secure** - HMAC signed tokens
✅ **Standard** - RFC 7519 compliant

## Token Strategy

### Access Token
- **Lifetime**: 15 minutes
- **Purpose**: Authorization for API requests
- **Usage**: Include in `Authorization: Bearer <token>` header
- **Revocation**: Expires automatically (cannot be revoked)

### Refresh Token
- **Lifetime**: 7 days
- **Purpose**: Obtain new access tokens
- **Usage**: POST to `/api/auth/token/refresh/`
- **Revocation**: Can be added to blacklist (optional)

## Token Flow

```
1. User logs in with email/password
   → POST /api/auth/login/
   → Returns: access_token + refresh_token

2. Use access token for API requests
   → GET /api/treatments/
   → Header: Authorization: Bearer <access_token>

3. When access token expires
   → POST /api/auth/token/refresh/
   → Returns: new access_token

4. Logout
   → POST /api/auth/logout/
   → Optionally blacklist refresh_token
```

## Security Considerations

- Tokens stored in HttpOnly cookies (frontend responsibility)
- Short expiry time (15 min) for access token
- Refresh token with longer expiry for UX
- HTTPS required in production
- Secret key must be secure (use Django's key generator)


# ============================================================================
# SOFT DELETE PATTERN
# ============================================================================

## Why Soft Delete?

✅ **Compliance** - GDPR, HIPAA retain data
✅ **Auditability** - Track what was deleted and when
✅ **Recovery** - Restore accidentally deleted records
✅ **Analytics** - Historical data analysis
✅ **Referential Integrity** - Foreign keys still valid

## Implementation

```python
# In Model
is_deleted = models.BooleanField(default=False, db_index=True)

created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)

objects = SoftDeleteManager()  # Returns non-deleted records only
all_objects = SoftDeleteManager()  # Returns all records

def soft_delete(self):
    self.is_deleted = True
    self.save()

def restore(self):
    self.is_deleted = False
    self.save()
```

## Query Patterns

```python
# Normal queries exclude deleted records
Treatment.objects.all()  # is_deleted=False only

# Access all records
Treatment.all_objects.all()

# Only deleted records
Treatment.all_objects.filter(is_deleted=True)

# Permanently delete (hard delete)
Treatment.all_objects.filter(is_deleted=True).delete()
```

## Advantages

- **Records preserved** - Original data intact
- **Audit trail** - When/who deleted
- **Recovery** - Can restore within compliance window
- **Analytics** - Historical reporting
- **Compliance** - Regulatory requirements


# ============================================================================
# CUSTOM MANAGER PATTERN
# ============================================================================

## SoftDeleteManager

Hides soft-deleted records by default:

```python
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model).filter(is_deleted=False)

    def all_objects(self):
        return SoftDeleteQuerySet(self.model)

    def deleted(self):
        return self.all_objects().filter(is_deleted=True)
```

## MultiTenantManager

Combines soft delete with clinic filtering:

```python
class MultiTenantManager(models.Manager):
    def get_queryset(self):
        return MultiTenantQuerySet(self.model).filter(is_deleted=False)

    def by_clinic(self, clinic):
        return self.get_queryset().filter(clinic=clinic)
```

## CustomUserManager

Specialized for user operations:

```python
class CustomUserManager(DjangoUserManager):
    def doctors(self, clinic=None):
        qs = self.get_queryset().filter(role='DOCTOR')
        if clinic:
            qs = qs.filter(clinic=clinic)
        return qs

    def patients(self, clinic=None):
        qs = self.get_queryset().filter(role='PATIENT')
        if clinic:
            qs = qs.filter(clinic=clinic)
        return qs
```


# ============================================================================
# SIGNAL-DRIVEN ARCHITECTURE
# ============================================================================

## Auto-Creating PatientProfile

When a user with `role='PATIENT'` is created, a PatientProfile is automatically created:

```python
@receiver(post_save, sender=CustomUser)
def create_patient_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'PATIENT':
        PatientProfile.objects.create(user=instance, clinic=instance.clinic)
```

**Benefits:**
- No manual profile creation
- Consistency guaranteed
- Clean separation of concerns
- Easy to extend with other signals


# ============================================================================
# VALIDATION ARCHITECTURE
# ============================================================================

## Layers of Validation

### 1. Field-Level Validation
```python
contact_number = models.CharField(
    validators=[validate_phone_number]
)
```

### 2. Model-Level Validation
```python
def clean(self):
    if self.date_of_birth > timezone.now().date():
        raise ValidationError('DOB cannot be in future')
```

### 3. Serializer-Level Validation
```python
def validate_patient(self, value):
    if value.clinic != self.context['clinic']:
        raise ValidationError('Patient must be from same clinic')
    return value
```

### 4. View-Level Validation
```python
def check_object_permissions(self, request, obj):
    if obj.patient != request.user:
        self.permission_denied(request)
```

## Validation Best Practices

- **Fail Fast** - Validate early, catch errors immediately
- **Specific Messages** - Clear error messages for users
- **Normalize Input** - Standardize data format
- **Security First** - Validate all external input


# ============================================================================
# API RESPONSE FORMAT
# ============================================================================

## Standardized Response Structure

All API responses follow consistent format:

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {...},
  "pagination": {  // For list endpoints
    "count": 100,
    "next": "...",
    "previous": "..."
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "error_code",
    "message": "Human-readable message",
    "details": {}
  }
}
```

## Benefits

- **Consistency** - Predictable format for clients
- **Easy Parsing** - Standard structure for all endpoints
- **Proper Codes** - HTTP status codes aligned with REST
- **Details** - Field-level errors included
- **Pagination** - Metadata for list endpoints


# ============================================================================
# PERFORMANCE OPTIMIZATION
# ============================================================================

## Database Optimization

### Indexing Strategy
```python
class Meta:
    indexes = [
        models.Index(fields=['clinic', 'patient']),
        models.Index(fields=['clinic', 'status']),
        models.Index(fields=['next_visit_date', 'status']),
    ]
```

**Indexes on:**
- Multi-tenant fields (clinic)
- Filtering fields (status, role)
- Sorting fields (created_at, next_visit_date)

### Query Optimization
```python
# BadQuerySet
Treatment.objects.all().select_related('clinic', 'patient', 'doctor')

# Good - Avoid N+1 queries
treatments = Treatment.objects.select_related(
    'clinic',
    'patient',
    'doctor'
).prefetch_related(
    'created_by'
)
```

## Caching Strategy

### Redis Caching
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/0',
    }
}
```

**Cache Strategies:**
- User data (5 min)
- Clinic statistics (1 hour)
- Clinic member lists (10 min)
- Treatment lists (5 min)

## Pagination

- Default page size: 20 items
- Configurable per endpoint
- Cursor-based for large datasets (optional)


# ============================================================================
# SECURITY ARCHITECTURE
# ============================================================================

## Security Layers

1. **Transport Security** - HTTPS/TLS
2. **Authentication** - JWT tokens
3. **Authorization** - Role-based permissions
4. **Data Isolation** - Clinic-scoped queries
5. **Input Validation** - Sanitize all inputs
6. **File Upload** - Validate type and size
7. **Rate Limiting** - Prevent abuse
8. **Logging** - Audit trail


# ============================================================================
# TESTING ARCHITECTURE
# ============================================================================

## Test Structure

```
tests/
├── test_models.py         # Model behavior tests
├── test_serializers.py    # Serializer validation tests
├── test_views.py          # API endpoint tests
├── test_permissions.py    # Permission enforcement tests
└── factories.py           # Test data factories
```

## Testing Priorities

1. **Permission Tests** - Verify access control
2. **Multi-tenant Tests** - Verify clinic isolation
3. **API Tests** - Endpoint functionality
4. **Integration Tests** - End-to-end flows


---

This architecture provides:
✅ Clean separation of concerns
✅ Multi-tenant data isolation
✅ Flexible role-based access
✅ Secure JWT authentication
✅ Auditable soft delete
✅ Production-ready scalability
✅ Easy to extend and maintain
