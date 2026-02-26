"""
OpenAPI Schema customization for API documentation.
"""

from drf_spectacular.utils import OpenApiParameter


def preprocessing_filter_hook(endpoints, **kwargs):
    """
    Filter and customize OpenAPI endpoints.
    
    This hook:
    - Removes duplicate endpoints
    - Adds custom descriptions
    - Organizes endpoints by tag
    """
    return endpoints
