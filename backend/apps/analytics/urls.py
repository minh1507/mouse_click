"""URLs for the analytics app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    HeatmapViewSet, PathAnalysisViewSet, FunnelViewSet,
    FunnelStepViewSet, FunnelAnalysisViewSet
)

router = DefaultRouter()
router.register('heatmaps', HeatmapViewSet)
router.register('paths', PathAnalysisViewSet)
router.register('funnels', FunnelViewSet)
router.register('funnel-steps', FunnelStepViewSet)
router.register('funnel-analyses', FunnelAnalysisViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 