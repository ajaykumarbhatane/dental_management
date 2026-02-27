"""
Django admin configuration for patients app.
"""
from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Admin interface for standalone Patient model."""

    fieldsets = (
        ('Basic Information', {
            'fields': ('first_name', 'last_name'),
        }),
        ('Assignment', {
            'fields': ('clinic', 'assigned_doctor'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    list_display = ('get_full_name', 'clinic', 'assigned_doctor', 'created_at')
    list_filter = ('clinic', 'assigned_doctor', 'created_at')
    search_fields = ('first_name', 'last_name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at',)

    def get_full_name(self, obj):
        """Display patient's full name."""
        return obj.get_full_name()
    get_full_name.short_description = 'Patient Name'

    def save_model(self, request, obj, form, change):
        """Set audit fields on save."""
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

