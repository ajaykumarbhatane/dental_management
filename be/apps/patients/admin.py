"""
Django admin configuration for patients app.
"""
from django.contrib import admin
from .models import PatientProfile


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    """Admin interface for PatientProfile model."""

    fieldsets = (
        ('User Information', {
            'fields': ('user', 'clinic'),
        }),
        ('Personal Information', {
            'fields': ('gender', 'date_of_birth'),
        }),
        ('Medical Information', {
            'fields': ('medical_history', 'allergies'),
            'classes': ('wide',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    list_display = ('get_full_name', 'clinic', 'gender', 'age', 'active_treatments_count', 'created_at')
    list_filter = ('clinic', 'gender', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'age')

    def get_full_name(self, obj):
        """Display patient's full name."""
        return obj.user.get_full_name()
    get_full_name.short_description = 'Patient Name'

    def age(self, obj):
        """Display calculated age."""
        return obj.age
    age.short_description = 'Age'
