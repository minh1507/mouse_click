"""Serializers for the API app."""

from rest_framework import serializers
from apps.tracking.models import Session, Event

class EventSerializer(serializers.ModelSerializer):
    """Serializer for Event model."""
    class Meta:
        model = Event
        fields = ['id', 'session', 'event_type', 'timestamp', 'url', 'data']

class SessionSerializer(serializers.ModelSerializer):
    """Serializer for Session model."""
    class Meta:
        model = Session
        fields = ['id', 'session_id', 'user_agent', 'screen_width', 'screen_height',
                 'language', 'ip_address', 'referrer', 'timezone',
                 'is_active', 'start_time', 'end_time']

class SessionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Session model with events count."""
    events_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Session
        fields = ['id', 'session_id', 'user_agent', 'screen_width', 'screen_height',
                 'language', 'ip_address', 'referrer', 'timezone',
                 'is_active', 'start_time', 'end_time', 'events_count']
    
    def get_events_count(self, obj):
        """Get the count of events for this session."""
        return obj.events.count() 