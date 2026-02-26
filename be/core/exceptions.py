"""
Custom exception handlers and response formatting for consistent API responses.

Provides:
- Custom exception handler for DRF
- Standardized error response format
- Proper HTTP status codes for different error types
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides standardized error responses.
    
    Returns error responses in format:
    {
        "success": false,
        "error": {
            "code": "error_code",
            "message": "Human-readable error message",
            "details": {...}
        }
    }
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize the error response format
        error_response = {
            'success': False,
            'error': {
                'code': get_error_code(exc),
                'message': response.data.get('detail', str(exc)),
            }
        }

        # Include field-level details for validation errors
        if isinstance(exc, (DjangoValidationError, DRFValidationError)):
            error_response['error']['details'] = response.data

        response.data = error_response

    return response


def get_error_code(exception):
    """
    Extract or generate error code from exception.
    """
    if hasattr(exception, 'default_code'):
        return exception.default_code

    exception_class_name = exception.__class__.__name__
    # Convert CamelCase to SNAKE_CASE
    code = ''.join(['_' + c.lower() if c.isupper() else c for c in exception_class_name]).lstrip('_')
    return code


class APIResponse:
    """
    Helper class for creating standardized API responses.
    """

    @staticmethod
    def success(data=None, message='Success', status_code=status.HTTP_200_OK):
        """Create a success response."""
        return Response(
            {
                'success': True,
                'message': message,
                'data': data,
            },
            status=status_code,
        )

    @staticmethod
    def error(message, code='error', details=None, status_code=status.HTTP_400_BAD_REQUEST):
        """Create an error response."""
        response_data = {
            'success': False,
            'error': {
                'code': code,
                'message': message,
            }
        }

        if details:
            response_data['error']['details'] = details

        return Response(response_data, status=status_code)

    @staticmethod
    def paginated(data, paginator, message='Success'):
        """Create a paginated success response."""
        return Response(
            {
                'success': True,
                'message': message,
                'data': data,
                'pagination': {
                    'count': paginator.page.paginator.count,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'page_size': paginator.page_size,
                    'current_page': paginator.page.number,
                    'total_pages': paginator.page.paginator.num_pages,
                }
            }
        )
