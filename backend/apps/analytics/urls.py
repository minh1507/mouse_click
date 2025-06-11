"""URL configuration for the analytics app."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'heatmaps', views.HeatmapViewSet)
router.register(r'path-analysis', views.PathAnalysisViewSet)
router.register(r'funnels', views.FunnelViewSet)
router.register(r'funnel-steps', views.FunnelStepViewSet)
router.register(r'funnel-analysis', views.FunnelAnalysisViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('generate-heatmap/', views.generate_heatmap, name='generate-heatmap'),
    
    # Thêm URLs cho phân tích chuột
    path('mouse-positions/', views.MousePositionAnalyticsView.as_view(), name='mouse-positions'),
    path('sessions/<uuid:session_id>/mouse-analytics/', views.session_mouse_analytics, name='session-mouse-analytics'),
] 