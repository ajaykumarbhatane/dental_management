"""
URL configuration for treatment endpoints.
"""

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from apps.treatments.views import TreatmentViewSet

router = SimpleRouter()
router.register(r'', TreatmentViewSet, basename='treatments')

urlpatterns = [
    path('', include(router.urls)),
]
