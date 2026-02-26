"""
Database Models Summary and Relationships
"""

# ============================================================================
# DATA MODEL OVERVIEW
# ============================================================================

## Entity Relationship Diagram

Clinic (1) ---|---< (Many) CustomUser
              |
              |---< (Many) PatientProfile
              |
              |---< (Many) Treatment

CustomUser (1) ---|---< (Many) PatientProfile (OneToOne - Patient side)
               |
               |---< (Many) Treatment (as Patient)
               |---< (Many) Treatment (as Doctor)
               |---< (Many) Treatment (as created_by)
               |---< (Many) Treatment (as updated_by)


## Model Relationships Summary

Clinic
  └── users * (CustomUser)
  └── patient_profiles * (PatientProfile)
  └── treatments * (Treatment)

CustomUser
  ├── clinic → Clinic (ForeignKey)
  ├── patient_profile ← PatientProfile (OneToOneField, if role='PATIENT')
  ├── treatments * (as patient, ForeignKey)
  ├── treatments_provided * (as doctor, ForeignKey)
  ├── treatments_created * (as created_by, ForeignKey)
  └── treatments_updated * (as updated_by, ForeignKey)

PatientProfile
  ├── user → CustomUser (OneToOneField)
  └── clinic → Clinic (ForeignKey, denormalized for query efficiency)

Treatment
  ├── clinic → Clinic (ForeignKey, multi-tenant)
  ├── patient → CustomUser (ForeignKey, with role='PATIENT')
  ├── doctor → CustomUser (ForeignKey, with role='DOCTOR')
  ├── created_by → CustomUser (ForeignKey, audit logging)
  └── updated_by → CustomUser (ForeignKey, audit logging)


# ============================================================================
# INDEXES FOR PERFORMANCE
# ============================================================================

CustomUser Indexes:
  - (email, clinic)           - User lookup by clinic
  - (clinic, role)            - Filter users by role within clinic
  - (is_deleted, clinic)      - Active users in clinic

Treatment Indexes:
  - (clinic, patient)         - Patient's treatments
  - (clinic, doctor)          - Doctor's treatments
  - (clinic, status)          - Treatments by status
  - (next_visit_date, status) - Upcoming/overdue appointments

PatientProfile Indexes:
  - (clinic, user)            - Patient lookup


# ============================================================================
# AUDIT LOGGING
# ============================================================================

All models track creation and updates:

- created_at: Record creation timestamp
- updated_at: Last modification timestamp
- created_by: User who created the record (for Treatment)
- updated_by: User who last updated the record (for Treatment)


# ============================================================================
# SOFT DELETE IMPLEMENTATION
# ============================================================================

Instead of hard deletion, records are marked as deleted:

Model.objects.all()          # Returns only active records (is_deleted=False)
Model.all_objects.all()      # Returns all records including deleted ones
Model.objects.deleted()      # Returns only deleted records 
Model.objects.active()       # Explicitly returns active records


# ============================================================================
# DATA ISOLATION FOR MULTI-TENANCY
# ============================================================================

Every query is automatically scoped to the user's clinic:

```python
def get_queryset(self):
    return filter_by_user_clinic(Treatment.objects.all(), self.request)
```

This ensures:
1. Users cannot see data from other clinics
2. Clinic admin cannot see other clinics' data
3. All reports/analytics are clinic-specific


# ============================================================================
# FIELD CONSTRAINTS AND VALIDATION
# ============================================================================

CustomUser:
  - email: unique across system, indexed
  - contact_number: validated format
  - secondary_contact_number: optional, validated format
  - role: one of ADMIN, DOCTOR, PATIENT (indexed)
  - clinic: required, non-null

PatientProfile:
  - user: unique one-to-one relationship
  - gender: one of MALE, FEMALE, OTHER, NOT_SPECIFIED
  - date_of_birth: optional

Treatment:
  - patient: required, must have role='PATIENT'
  - doctor: optional, must have role='DOCTOR' or null
  - treatment_type: one of predefined choices
  - next_visit_date: optional, but indexed for scheduling
  - status: one of ONGOING, COMPLETED, CANCELLED, ON_HOLD, SCHEDULED
  - upload_image: max 5MB, validated image format


# ============================================================================
# DATABASE CREATION EXAMPLE
# ============================================================================

PostgreSQL setup:

```sql
CREATE USER dental_user WITH PASSWORD 'secure_password';
CREATE DATABASE dental_clinic_db OWNER dental_user;
GRANT ALL PRIVILEGES ON DATABASE dental_clinic_db TO dental_user;

-- For production, restrict permissions:
-- GRANT CONNECT ON DATABASE dental_clinic_db TO dental_user;
-- GRANT USAGE ON SCHEMA public TO dental_user;
-- GRANT CREATE ON SCHEMA public TO dental_user;
```

After Django models:

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates all tables with proper indexes and constraints.


# ============================================================================
# BACKUP AND RECOVERY
# ============================================================================

### Dumping Data (Regular Backups)

```bash
# Dump entire database
pg_dump dental_clinic_db > backup.sql

# Dump specific table
pg_dump -t treatment dental_clinic_db > treatments_backup.sql

# Backup with compression
pg_dump dental_clinic_db | gzip > backup.tar.gz
```

### Restoring Data

```bash
# Restore entire database
psql dental_clinic_db < backup.sql

# Restore from compressed backup
gunzip -c backup.tar.gz | psql dental_clinic_db
```

### Django Data Export/Import

```bash
# Export data
python manage.py dumpdata > backup.json

# Export specific app
python manage.py dumpdata apps.treatments > treatments.json

# Import data
python manage.py loaddata backup.json
```


# ============================================================================
# MIGRATION MANAGEMENT
# ============================================================================

### Making Changes to Models

```bash
# Create migrations after model changes
python manage.py makemigrations

# Review migration before applying
cat migrations/0001_initial.py

# Apply migrations
python manage.py migrate

# Migrate specific app
python manage.py migrate apps.treatments

# Rollback migration
python manage.py migrate apps.treatments 0001_initial
```

### Data Migrations

For complex changes requiring data manipulation:

```bash
# Create empty migration
python manage.py makemigrations --empty app_name --name migration_name

# Edit the migration file to add data transformation logic
# Then apply:
python manage.py migrate
```


# ============================================================================
# PERFORMANCE OPTIMIZATION QUERIES
# ============================================================================

### Optimized Queries with select_related and prefetch_related

```python
# Get treatments with related data (reduces queries)
treatments = Treatment.objects.select_related(
    'clinic',
    'patient',
    'doctor'
).prefetch_related(
    'created_by'
)

# Get patient profiles with user data
patients = PatientProfile.objects.select_related(
    'user',
    'clinic'
).all()
```

### Pagination for Large Datasets

DRF pagination handles this automatically, but important for production:
- PAGE_SIZE=20 (configurable)
- Supports page-based or cursor-based pagination
- Use ordering_fields for consistency


---

For detailed information on each model, see the respective model files in apps/
