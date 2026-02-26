"""
API EXAMPLES AND RESPONSES

This document provides examples of common API requests and their responses.
"""

# ============================================================================
# AUTHENTICATION
# ============================================================================

## Register New User

POST /api/auth/register/
Content-Type: application/json

{
  "email": "doctor@clinic.com",
  "first_name": "John",
  "last_name": "Doe",
  "contact_number": "(555) 123-4567",
  "password": "SecurePassword123!",
  "password_confirm": "SecurePassword123!",
  "clinic_id": 1,
  "role": "DOCTOR",
  "degree": "DDS"
}

RESPONSE 201 Created:
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": 5,
    "email": "doctor@clinic.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "clinic": 1,
    "clinic_name": "Bright Smile Dental",
    "role": "DOCTOR",
    "role_display": "Doctor/Orthodontist",
    "contact_number": "(555) 123-4567",
    "secondary_contact_number": null,
    "address": null,
    "degree": "DDS",
    "is_active": true,
    "created_at": "2026-02-25T10:30:00Z",
    "updated_at": "2026-02-25T10:30:00Z"
  }
}


## Login

POST /api/auth/login/
Content-Type: application/json

{
  "email": "doctor@clinic.com",
  "password": "SecurePassword123!"
}

RESPONSE 200 OK:
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": 5,
      "email": "doctor@clinic.com",
      "first_name": "John",
      "last_name": "Doe",
      "clinic": 1,
      "clinic_name": "Bright Smile Dental",
      "role": "DOCTOR",
      "contact_number": "(555) 123-4567",
      "is_active": true,
      "created_at": "2026-02-25T10:30:00Z"
    },
    "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}


## Get Current User Profile

GET /api/auth/me/
Authorization: Bearer <access_token>

RESPONSE 200 OK:
{
  "success": true,
  "message": "Profile retrieved successfully",
  "data": {
    "id": 5,
    "email": "doctor@clinic.com",
    "first_name": "John",
    "last_name": "Doe",
    "clinic": 1,
    "clinic_name": "Bright Smile Dental",
    "role": "DOCTOR",
    "contact_number": "(555) 123-4567",
    "is_active": true,
    "created_at": "2026-02-25T10:30:00Z"
  }
}


# ============================================================================
# CLINICS
# ============================================================================

## List Clinics

GET /api/clinics/
Authorization: Bearer <access_token>

RESPONSE 200 OK:
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Bright Smile Dental",
      "contact_number": "(555) 111-2222",
      "address": "123 Main St, Denver, CO 80202",
      "description": "Leading orthodontic clinic in Denver",
      "is_active": true,
      "user_count": 12,
      "doctor_count": 3,
      "patient_count": 8,
      "created_at": "2026-01-15T08:00:00Z",
      "updated_at": "2026-02-20T14:30:00Z"
    }
  ]
}


## Get Clinic Statistics

GET /api/clinics/1/statistics/
Authorization: Bearer <access_token>

RESPONSE 200 OK:
{
  "success": true,
  "message": "Clinic statistics retrieved",
  "data": {
    "total_users": 12,
    "total_doctors": 3,
    "total_patients": 8,
    "active_treatments": 15,
    "is_active": true
  }
}


# ============================================================================
# PATIENTS
# ============================================================================

## List Patients in Clinic

GET /api/patients/
Authorization: Bearer <access_token>

QUERY PARAMETERS:
  ?gender=FEMALE
  ?search=john
  ?ordering=-created_at
  ?page=1&page_size=20

RESPONSE 200 OK:
{
  "count": 8,
  "next": "http://localhost:8000/api/patients/?page=2",
  "previous": null,
  "results": [
    {
      "id": 3,
      "user": 4,
      "user_email": "john.patient@clinic.com",
      "user_full_name": "John Smith",
      "clinic": 1,
      "clinic_name": "Bright Smile Dental",
      "gender": "MALE",
      "date_of_birth": "1995-06-15",
      "age": 30,
      "medical_history": "Severe crowding, previous braces",
      "allergies": "Penicillin",
      "created_at": "2026-01-20T09:15:00Z",
      "updated_at": "2026-02-20T11:00:00Z"
    }
  ]
}


## Get Patient Profile

GET /api/patients/3/
Authorization: Bearer <access_token>

RESPONSE 200 OK:
{
  "id": 3,
  "user": {
    "id": 4,
    "email": "john.patient@clinic.com",
    "first_name": "John",
    "last_name": "Smith",
    "clinic": 1,
    "role": "PATIENT",
    "contact_number": "(555) 234-5678",
    "created_at": "2026-01-20T09:15:00Z"
  },
  "clinic": 1,
  "gender": "MALE",
  "date_of_birth": "1995-06-15",
  "age": 30,
  "active_treatments_count": 2,
  "medical_history": "Severe crowding, previous braces",
  "allergies": "Penicillin",
  "medical_summary": {
    "age": 30,
    "gender": "Male",
    "medical_history": "Severe crowding, previous braces",
    "allergies": "Penicillin"
  },
  "created_at": "2026-01-20T09:15:00Z",
  "updated_at": "2026-02-20T11:00:00Z"
}


## Get Patient Medical Summary

GET /api/patients/3/medical-summary/
Authorization: Bearer <access_token>

RESPONSE 200 OK:
{
  "success": true,
  "message": "Medical summary retrieved",
  "data": {
    "age": 30,
    "gender": "Male",
    "medical_history": "Severe crowding, previous braces",
    "allergies": "Penicillin"
  }
}


# ============================================================================
# TREATMENTS
# ============================================================================

## List Treatments

GET /api/treatments/
Authorization: Bearer <access_token>

QUERY PARAMETERS:
  ?status=ONGOING
  ?treatment_type=BRACES
  ?next_visit_date_after=2026-03-01&next_visit_date_before=2026-03-31
  ?search=john
  ?ordering=-next_visit_date
  ?page=1&page_size=20

RESPONSE 200 OK:
{
  "count": 15,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 8,
      "clinic": 1,
      "clinic_name": "Bright Smile Dental",
      "patient": 4,
      "patient_name": "John Smith",
      "patient_email": "john.patient@clinic.com",
      "doctor": 5,
      "doctor_name": "John Doe",
      "treatment_type": "BRACES",
      "treatment_information": "Metal braces for comprehensive correction",
      "treatment_findings": "Severe crowding, skeletal class II",
      "upload_image": "https://..../treatments/2026/02/before_abc123.jpg",
      "next_visit_date": "2026-03-15T14:00:00Z",
      "status": "ONGOING",
      "is_upcoming": true,
      "is_overdue": false,
      "created_at": "2026-02-15T10:00:00Z",
      "updated_at": "2026-02-20T15:30:00Z"
    }
  ]
}


## Create Treatment

POST /api/treatments/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "patient": 4,
  "doctor": 5,
  "treatment_type": "BRACES",
  "treatment_information": "Metal braces for comprehensive correction",
  "treatment_findings": "Severe crowding, skeletal class II",
  "next_visit_date": "2026-03-15T14:00:00Z",
  "status": "SCHEDULED"
}

// With image upload:
POST /api/treatments/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

{
  "patient": 4,
  "doctor": 5,
  "treatment_type": "BRACES",
  "treatment_information": "Metal braces for comprehensive correction",
  "upload_image": <binary_image_data>,
  "status": "SCHEDULED"
}

RESPONSE 201 Created:
{
  "id": 8,
  "clinic": 1,
  "clinic_name": "Bright Smile Dental",
  "patient": 4,
  "patient_name": "John Smith",
  "doctor": 5,
  "doctor_name": "John Doe",
  "treatment_type": "BRACES",
  "treatment_information": "Metal braces for comprehensive correction",
  "treatment_findings": "Severe crowding, skeletal class II",
  "upload_image": "https://..../treatments/2026/02/image_xyz.jpg",
  "next_visit_date": "2026-03-15T14:00:00Z",
  "status": "SCHEDULED",
  "is_upcoming": true,
  "is_overdue": false,
  "created_at": "2026-02-25T11:00:00Z",
  "updated_at": "2026-02-25T11:00:00Z"
}


## Get Upcoming Treatments

GET /api/treatments/upcoming/
Authorization: Bearer <access_token>

RESPONSE 200 OK:
{
  "success": true,
  "message": "Upcoming treatments retrieved",
  "data": [
    {
      "id": 8,
      "patient": 4,
      "patient_name": "John Smith",
      "doctor": 5,
      "doctor_name": "John Doe",
      "treatment_type": "BRACES",
      "status": "ONGOING",
      "next_visit_date": "2026-03-15T14:00:00Z",
      "is_upcoming": true,
      "is_overdue": false
    }
  ]
}


## Get Overdue Treatments

GET /api/treatments/overdue/
Authorization: Bearer <access_token>

RESPONSE 200 OK:
{
  "success": true,
  "message": "Overdue treatments retrieved",
  "data": []
}


## Filter Treatments by Status

GET /api/treatments/by_status/?status=COMPLETED
Authorization: Bearer <access_token>

RESPONSE 200 OK:
{
  "success": true,
  "message": "Treatments with status COMPLETED retrieved",
  "data": [...]
}


## Update Treatment

PUT /api/treatments/8/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "doctor": 5,
  "treatment_information": "Updated treatment plan",
  "treatment_findings": "Progress observed",
  "next_visit_date": "2026-03-22T14:00:00Z",
  "status": "ONGOING"
}

RESPONSE 200 OK:
{
  "id": 8,
  "clinic": 1,
  "patient": 4,
  "doctor": 5,
  "treatment_type": "BRACES",
  "treatment_information": "Updated treatment plan",
  "next_visit_date": "2026-03-22T14:00:00Z",
  "status": "ONGOING",
  "updated_at": "2026-02-25T12:30:00Z"
}


## Mark Treatment Completed

POST /api/treatments/8/mark_completed/
Authorization: Bearer <access_token>

RESPONSE 200 OK:
{
  "success": true,
  "message": "Treatment marked as completed",
  "data": {
    "id": 8,
    "status": "COMPLETED",
    "updated_at": "2026-02-25T13:00:00Z"
  }
}


# ============================================================================
# USER MANAGEMENT
# ============================================================================

## List Users in Clinic

GET /api/users/
Authorization: Bearer <access_token>

QUERY PARAMETERS:
  ?role=DOCTOR
  ?is_active=true
  ?search=john

RESPONSE 200 OK:
{
  "count": 12,
  "results": [
    {
      "id": 5,
      "email": "doctor@clinic.com",
      "first_name": "John",
      "last_name": "Doe",
      "clinic": 1,
      "role": "DOCTOR",
      "contact_number": "(555) 123-4567",
      "is_active": true,
      "created_at": "2026-01-20T09:15:00Z"
    }
  ]
}


## List Doctors

GET /api/users/doctors/
Authorization: Bearer <access_token>

RESPONSE 200 OK:
{
  "success": true,
  "message": "Doctors retrieved",
  "data": [...]
}


## List Patients

GET /api/users/patients/
Authorization: Bearer <access_token>

RESPONSE 200 OK:
{
  "success": true,
  "message": "Patients retrieved",
  "data": [...]
}


# ============================================================================
# ERROR RESPONSES
# ============================================================================

## Invalid Request (Validation Error)

POST /api/auth/register/
Content-Type: application/json

{
  "email": "invalid-email",
  "password": "short"
}

RESPONSE 400 Bad Request:
{
  "success": false,
  "error": {
    "code": "validation_error",
    "message": "Validation failed",
    "details": {
      "email": ["Enter a valid email address."],
      "password": ["Ensure this field has at least 8 characters."],
      "first_name": ["This field is required."]
    }
  }
}


## Authentication Required

GET /api/treatments/
[No Authorization header]

RESPONSE 401 Unauthorized:
{
  "success": false,
  "error": {
    "code": "authentication_failed",
    "message": "Authentication credentials were not provided."
  }
}


## Permission Denied

POST /api/clinics/
Authorization: Bearer <patient_token>
Content-Type: application/json

{
  "name": "New Clinic",
  "contact_number": "(555) 999-9999",
  "address": "123 Clinic Ave"
}

RESPONSE 403 Forbidden:
{
  "success": false,
  "error": {
    "code": "permission_denied",
    "message": "Only clinic administrators can access this resource."
  }
}


## Resource Not Found

GET /api/treatments/999/
Authorization: Bearer <access_token>

RESPONSE 404 Not Found:
{
  "success": false,
  "error": {
    "code": "not_found",
    "message": "Not found."
  }
}


# ============================================================================
# PAGINATION EXAMPLE
# ============================================================================

GET /api/treatments/?page=1&page_size=20
Authorization: Bearer <access_token>

RESPONSE 200 OK:
{
  "count": 150,
  "next": "http://localhost:8000/api/treatments/?page=2&page_size=20",
  "previous": null,
  "results": [
    {...},
    {...},
    ...
  ]
}


---

For more information, visit: http://localhost:8000/api/docs/ (Swagger UI)
