"""
URL configuration for patient endpoints.
"""

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from apps.patients.views import PatientViewSet

router = SimpleRouter()
router.register(r'', PatientViewSet, basename='patients')

urlpatterns = [
    path('', include(router.urls)),
]
