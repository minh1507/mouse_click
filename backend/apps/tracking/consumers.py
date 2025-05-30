"""WebSocket consumers for the tracking app."""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

class TrackingConsumer(AsyncWebsocketConsumer):
    """Consumer for real-time tracking data."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        # Join tracking group
        await self.channel_layer.group_add(
            "tracking",
            self.channel_name
        )
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave tracking group
        await self.channel_layer.group_discard(
            "tracking",
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle received data from WebSocket."""
        data = json.loads(text_data)
        event_type = data.get('event_type')
        
        # Forward the event to the tracking group
        await self.channel_layer.group_send(
            "tracking",
            {
                "type": "tracking_event",
                "event_type": event_type,
                "data": data,
                "timestamp": timezone.now().isoformat()
            }
        )
        
        # Save to database asynchronously
        if 'session_id' in data:
            await self.save_event(data)
    
    async def tracking_event(self, event):
        """Send tracking event to WebSocket."""
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            "event_type": event["event_type"],
            "data": event["data"],
            "timestamp": event["timestamp"]
        }))
    
    @database_sync_to_async
    def save_event(self, data):
        """Save event to database."""
        from .models import Session, Event
        
        try:
            session = Session.objects.get(session_id=data['session_id'])
            Event.objects.create(
                session=session,
                event_type=data['event_type'],
                timestamp=timezone.now(),
                url=data.get('url', ''),
                data=data
            )
        except Session.DoesNotExist:
            pass  # Handle non-existent session 