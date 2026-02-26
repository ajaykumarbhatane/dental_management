"""
Utility functions for common operations across the application.

Provides:
- Multi-tenant request filtering
- Pagination helpers
- Serializer helpers
- Cache helpers
"""

from functools import wraps
from django.core.cache import cache
from django.http import QueryDict
from rest_framework import status
from rest_framework.response import Response


def get_user_clinic(request):
    """
    Extract clinic from authenticated request.
    
    Returns:
        Clinic object or None if user is not authenticated or has no clinic
    """
    if request.user and request.user.is_authenticated:
        return request.user.clinic
    return None


def filter_by_user_clinic(queryset, request):
    """
    Filter queryset by the clinic of the authenticated user.
    
    This is the core function for multi-tenant data isolation.
    
    Args:
        queryset: Django QuerySet to filter
        request: HTTP request object
    
    Returns:
        Filtered QuerySet containing only records from user's clinic
    """
    clinic = get_user_clinic(request)
    if clinic:
        return queryset.filter(clinic=clinic)
    return queryset.none()  # No clinic = no access


def require_clinic(view_func):
    """
    Decorator to ensure user has a clinic assigned.
    
    Usage:
        @require_clinic
        def my_view(request, *args, **kwargs):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.clinic:
            return Response(
                {
                    'success': False,
                    'error': {
                        'code': 'no_clinic_assigned',
                        'message': 'User is not assigned to any clinic'
                    }
                },
                status=status.HTTP_403_FORBIDDEN
            )
        return view_func(request, *args, **kwargs)
    return wrapper


def cache_user_data(timeout=300):
    """
    Decorator for caching user-specific data.
    
    Usage:
        @cache_user_data(timeout=600)  # 10 minutes
        def get_user_dashboard_data(user):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(user, *args, **kwargs):
            if not user or not user.is_authenticated:
                return func(user, *args, **kwargs)

            cache_key = f"user_{user.id}_{func.__name__}"
            cached_data = cache.get(cache_key)

            if cached_data is not None:
                return cached_data

            result = func(user, *args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result

        return wrapper
    return decorator


def invalidate_user_cache(user, pattern='*'):
    """
    Invalidate cached data for a user.
    
    Args:
        user: User object
        pattern: Cache key pattern to match (default '*' clears all user cache)
    """
    if pattern == '*':
        # Clear all user cache keys
        cache_key = f"user_{user.id}_*"
        # Note: Basic cache doesn't support pattern deletion
        # For Redis, implement proper pattern-based deletion


class PaginationHelper:
    """Helper for handling pagination operations."""

    @staticmethod
    def get_paginated_response(serializer, paginator, request):
        """
        Create a standardized paginated response.
        
        Returns response with pagination metadata.
        """
        page = paginator.paginate_queryset(serializer.data, request)
        return {
            'data': page,
            'pagination': {
                'count': paginator.page.paginator.count,
                'next': paginator.get_next_link(),
                'previous': paginator.get_previous_link(),
                'page_size': paginator.page_size,
                'current_page': paginator.page.number,
                'total_pages': paginator.page.paginator.num_pages,
            }
        }


class SerializerHelper:
    """Helper for serializer operations."""

    @staticmethod
    def add_clinic_to_context(serializer_context, request):
        """
        Add the user's clinic to serializer context for validation.
        
        Useful for ensuring resources are created/updated within user's clinic.
        """
        serializer_context['clinic'] = get_user_clinic(request)
        return serializer_context

    @staticmethod
    def get_clinic_from_context(context):
        """Extract clinic from serializer context."""
        return context.get('clinic')


def get_query_param_as_list(query_params, key, default=None):
    """
    Extract query parameter that might have multiple values.
    
    Django QueryDict stores multiple values as QueryDict,
    this helper safely extracts them.
    
    Usage:
        # ?ids=1,2,3 or ?ids=1&ids=2&ids=3
        ids = get_query_param_as_list(request.query_params, 'ids')
    """
    value = query_params.get(key)
    if not value:
        return default or []

    if isinstance(value, list):
        return value

    # Split comma-separated values
    if ',' in value:
        return [v.strip() for v in value.split(',')]

    return [value]


def build_error_response(error_code, message, details=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Build a standardized error response.
    
    Usage:
        response = build_error_response(
            error_code='invalid_clinic',
            message='Clinic not found',
            details={'clinic_id': 'The specified clinic does not exist'},
            status_code=status.HTTP_404_NOT_FOUND
        )
    """
    response_data = {
        'success': False,
        'error': {
            'code': error_code,
            'message': message,
        }
    }

    if details:
        response_data['error']['details'] = details

    return Response(response_data, status=status_code)
