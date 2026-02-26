"""
Custom validators for the application.

Provides:
- Phone number validation
- File size and type validation
- Domain/email validation
"""

import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


def validate_phone_number(value):
    """
    Validate phone number format.
    Accepts formats: +1234567890, 123-456-7890, (123) 456-7890
    """
    pattern = r'^(\+\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
    if not re.match(pattern, value):
        raise ValidationError(
            'Please provide a valid phone number format.',
            code='invalid_phone_number'
        )


def validate_file_size(file, max_size_mb=5):
    """
    Validate that file size does not exceed maximum allowed size.
    
    Args:
        file: Django UploadedFile object
        max_size_mb: Maximum file size in megabytes
    """
    file_size = file.size / (1024 * 1024)  # Convert to MB
    if file_size > max_size_mb:
        raise ValidationError(
            f'File size cannot exceed {max_size_mb}MB. Current size: {file_size:.2f}MB',
            code='file_too_large'
        )


def validate_image_file(file):
    """
    Validate that file is a valid image format.
    Allowed: JPEG, PNG, GIF, WebP
    """
    allowed_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_formats:
        raise ValidationError(
            'Invalid image format. Allowed formats: JPEG, PNG, GIF, WebP',
            code='invalid_image_format'
        )
    validate_file_size(file, max_size_mb=5)


def validate_pdf_file(file):
    """
    Validate that file is a PDF.
    """
    if file.content_type != 'application/pdf':
        raise ValidationError(
            'File must be a PDF document',
            code='invalid_pdf_format'
        )
    validate_file_size(file, max_size_mb=10)


phone_regex = RegexValidator(
    regex=r'^(\+\d{1,3})?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$',
    message='Please provide a valid phone number.',
    code='invalid_phone'
)
