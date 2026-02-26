"""
URL configuration for clinic endpoints.
"""

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from apps.clinics.views import ClinicViewSet

router = SimpleRouter()
router.register(r'', ClinicViewSet, basename='clinics')

urlpatterns = [
    path('', include(router.urls)),
]
