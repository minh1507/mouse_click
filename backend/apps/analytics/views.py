"""Views for the analytics app."""

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Count

from .models import Heatmap, PathAnalysis, Funnel, FunnelStep, FunnelAnalysis
from .serializers import (
    HeatmapSerializer, PathAnalysisSerializer, FunnelSerializer, 
    FunnelStepSerializer, FunnelAnalysisSerializer, FunnelWithStepsSerializer
)
from apps.tracking.models import Event, Session

class HeatmapViewSet(viewsets.ModelViewSet):
    """ViewSet for Heatmap model."""
    queryset = Heatmap.objects.all()
    serializer_class = HeatmapSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['heatmap_type', 'url_pattern', 'is_processed']
    search_fields = ['name', 'url_pattern']
    ordering_fields = ['created_at', 'date_from', 'date_to']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate heatmap data based on events."""
        heatmap = self.get_object()
        # Logic to generate heatmap data would go here
        # This would typically be a celery task
        return Response({'status': 'processing started'})

class PathAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for PathAnalysis model."""
    queryset = PathAnalysis.objects.all()
    serializer_class = PathAnalysisSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_processed']
    search_fields = ['name']
    ordering_fields = ['created_at', 'date_from', 'date_to']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate path analysis data based on events."""
        path_analysis = self.get_object()
        # Logic to generate path analysis data would go here
        # This would typically be a celery task
        return Response({'status': 'processing started'})

class FunnelViewSet(viewsets.ModelViewSet):
    """ViewSet for Funnel model."""
    queryset = Funnel.objects.all()
    serializer_class = FunnelSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']

class FunnelStepViewSet(viewsets.ModelViewSet):
    """ViewSet for FunnelStep model."""
    queryset = FunnelStep.objects.all()
    serializer_class = FunnelStepSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['funnel']

class FunnelAnalysisViewSet(viewsets.ModelViewSet):
    """ViewSet for FunnelAnalysis model."""
    queryset = FunnelAnalysis.objects.all()
    serializer_class = FunnelAnalysisSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['funnel', 'is_processed']
    search_fields = ['funnel__name']
    ordering_fields = ['created_at', 'date_from', 'date_to']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate funnel analysis data based on events."""
        funnel_analysis = self.get_object()
        # Logic to generate funnel analysis data would go here
        # This would typically be a celery task
        return Response({'status': 'processing started'}) 