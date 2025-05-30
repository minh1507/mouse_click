"""URL configuration for the API app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DummyViewSet

# Create a router and register viewsets
router = DefaultRouter()
router.register('test', DummyViewSet, basename='test')

urlpatterns = [
    path('', include(router.urls)),
    # Add authentication URLs
    path('auth/', include('rest_framework.urls')),
] 