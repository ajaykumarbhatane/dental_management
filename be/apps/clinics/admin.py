"""
Django admin configuration for clinics app.
"""
from django.contrib import admin
from .models import Clinic


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    """Admin interface for Clinic model."""

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'contact_number', 'is_active'),
        }),
        ('Address & Details', {
            'fields': ('address', 'description'),
            'classes': ('wide',),
        }),
        ('Audit & Soft Delete', {
            'fields': ('is_deleted', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    list_display = ('name', 'contact_number', 'is_active', 'is_deleted', 'user_count', 'doctor_count', 'patient_count')
    list_filter = ('is_active', 'is_deleted', 'created_at')
    search_fields = ('name', 'contact_number', 'address')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'user_count', 'doctor_count', 'patient_count')

    def user_count(self, obj):
        """Display active user count."""
        return obj.user_count
    user_count.short_description = 'Active Users'

    def doctor_count(self, obj):
        """Display doctor count."""
        return obj.doctor_count
    doctor_count.short_description = 'Doctors'

    def patient_count(self, obj):
        """Display patient count."""
        return obj.patient_count
    patient_count.short_description = 'Patients'
