"""
Django admin configuration for users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Admin interface for CustomUser model."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Clinic & Role', {
            'fields': ('clinic', 'role'),
            'classes': ('wide',),
        }),
        ('Contact Information', {
            'fields': ('contact_number', 'secondary_contact_number', 'address'),
            'classes': ('collapse',),
        }),
        ('Professional Info', {
            'fields': ('degree',),
            'classes': ('collapse',),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Audit & Soft Delete', {
            'fields': ('is_deleted', 'created_by', 'updated_by', 'created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'Audit logging and soft delete information',
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
        ('Clinic & Role', {
            'classes': ('wide',),
            'fields': ('clinic', 'role', 'first_name', 'last_name'),
        }),
        ('Contact Information', {
            'fields': ('contact_number', 'secondary_contact_number', 'address'),
        }),
    )

    list_display = ('email', 'get_full_name', 'clinic', 'role', 'is_active', 'is_deleted', 'created_at')
    list_filter = ('role', 'clinic', 'is_active', 'is_deleted', 'created_at')
    search_fields = ('email', 'first_name', 'last_name', 'contact_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')

    def get_full_name(self, obj):
        """Display user's full name."""
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'

    def save_model(self, request, obj, form, change):
        """Override save to set created_by and updated_by."""
        if not change:  # Creating new object
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
