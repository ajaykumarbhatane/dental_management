"""
Django admin configuration for treatments app.
"""
from django.contrib import admin
from .models import Treatment


@admin.register(Treatment)
class TreatmentAdmin(admin.ModelAdmin):
    """Admin interface for Treatment model."""

    fieldsets = (
        ('Treatment Information', {
            'fields': ('clinic', 'patient', 'doctor', 'treatment_type', 'status'),
        }),
        ('Treatment Details', {
            'fields': ('treatment_information', 'treatment_findings'),
            'classes': ('wide',),
        }),
        ('Documentation & Schedule', {
            'fields': ('upload_image', 'next_visit_date'),
            'classes': ('wide',),
        }),
        ('Audit & Soft Delete', {
            'fields': ('is_deleted', 'created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    list_display = ('id', 'get_patient_name', 'clinic', 'treatment_type', 'doctor', 'status', 'next_visit_date', 'is_upcoming')
    list_filter = ('clinic', 'treatment_type', 'status', 'created_at')
    search_fields = ('patient__first_name', 'patient__last_name', 'patient__email', 'treatment_type')
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
    ordering = ('-created_at',)

    def get_patient_name(self, obj):
        """Display patient name."""
        return obj.patient.get_full_name()
    get_patient_name.short_description = 'Patient'

    def is_upcoming(self, obj):
        """Display if treatment is upcoming."""
        return obj.is_upcoming()
    is_upcoming.short_description = 'Upcoming'
    is_upcoming.boolean = True

    def save_model(self, request, obj, form, change):
        """Override save to set created_by and updated_by."""
        if not change:  # Creating new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
