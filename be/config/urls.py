"""
URL Configuration for Dental Clinic Management System.

API Routes:
- /api/auth/ - Authentication endpoints (register, login, refresh token, logout)
- /api/users/ - User management endpoints
- /api/clinics/ - Clinic management endpoints
- /api/patients/ - Patient management endpoints  
- /api/treatments/ - Treatment management endpoints
- /api/schema/ - API documentation (OpenAPI/Swagger)
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # API Schema and Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # API Routes
    path('api/auth/', include('apps.users.urls_auth')),
    path('api/users/', include('apps.users.urls')),
    path('api/clinics/', include('apps.clinics.urls')),
    path('api/patients/', include('apps.patients.urls')),
    path('api/treatments/', include('apps.treatments.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site branding
admin.site.site_header = "Dental Clinic Management System"
admin.site.site_title = "Dental Clinic Admin"
admin.site.index_title = "Welcome to Dental Clinic Administration"
