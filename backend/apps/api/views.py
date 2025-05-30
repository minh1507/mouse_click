"""Views for the API app."""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.tracking.models import Session, Event
from .serializers import SessionSerializer, EventSerializer, SessionDetailSerializer

class EventViewSet(viewsets.ModelViewSet):
    """ViewSet for Event model."""
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['event_type', 'session', 'url']
    search_fields = ['url']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def create(self, request, *args, **kwargs):
        """Handle single and batch event creation."""
        # Batch insert to optimize performance
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=201)
        return super().create(request, *args, **kwargs)

class SessionViewSet(viewsets.ModelViewSet):
    """ViewSet for Session model."""
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['user_agent', 'ip_address', 'referrer']
    ordering_fields = ['start_time', 'end_time']
    ordering = ['-start_time']
    
    def get_serializer_class(self):
        """Return different serializer for detail view."""
        if self.action == 'retrieve':
            return SessionDetailSerializer
        return SessionSerializer
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a session."""
        session = self.get_object()
        session.is_active = False
        session.end_time = timezone.now()
        session.save()
        return Response({'status': 'session ended'})
    
    @action(detail=True, methods=['get'])
    def events(self, request, pk=None):
        """Get events for a session."""
        session = self.get_object()
        events = Event.objects.filter(session=session)
        
        # Apply filters
        event_type = request.query_params.get('event_type')
        if event_type:
            events = events.filter(event_type=event_type)
        
        # Apply pagination
        page = self.paginate_queryset(events)
        if page is not None:
            serializer = EventSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

class DummyViewSet(viewsets.ViewSet):
    """Dummy viewset for testing."""
    
    def list(self, request):
        """Return a simple response."""
        return Response({"message": "API is working"}) 