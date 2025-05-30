"""Models for the tracking app."""

import uuid
from django.db import models

class Session(models.Model):
    """Model to store user sessions."""
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_agent = models.TextField()
    ip_address = models.GenericIPAddressField()
    referrer = models.URLField(null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Session {self.session_id}"

class Event(models.Model):
    """Model to store tracking events."""
    EVENT_TYPES = (
        ('mouse_move', 'Mouse Move'),
        ('mouse_click', 'Mouse Click'),
        ('scroll', 'Scroll'),
        ('form_input', 'Form Input'),
        ('page_view', 'Page View'),
        ('custom', 'Custom Event'),
    )
    
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    timestamp = models.DateTimeField()
    url = models.URLField()
    data = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.event_type} at {self.timestamp}"
        
    class Meta:
        indexes = [
            models.Index(fields=['session', 'event_type']),
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['url']),
        ] 