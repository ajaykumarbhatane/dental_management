"""
URL configuration for patient endpoints.
"""

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from apps.patients.views import PatientProfileViewSet

router = SimpleRouter()
router.register(r'', PatientProfileViewSet, basename='patients')

urlpatterns = [
    path('', include(router.urls)),
]
