"""Views for the tracking app."""

import uuid
import json
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from django.utils import timezone
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.conf import settings
from .utils.mongo_client import get_collection, ensure_collections
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Session, Event
from utils.mongo_client import save_event, save_session, get_events_by_session

logger = logging.getLogger(__name__)

class EventsView(APIView):
    """API endpoint for tracking events."""
    
    def post(self, request, format=None):
        """Handle POST requests to save tracking events."""
        try:
            # Log raw request data for debugging
            logger.info(f"Raw request data type: {type(request.data)}")
            logger.info(f"Raw request data: {request.data}")
            
            # Handle các cấu trúc dữ liệu khác nhau
            data = request.data
            
            # Check if data contains an "events" array
            if isinstance(data, dict) and 'events' in data and isinstance(data['events'], list):
                logger.info("Processing events array from object")
                responses = []
                for item in data['events']:
                    response = self.process_event(request, item)
                    responses.append(response.data)
                return Response({"results": responses}, status=status.HTTP_201_CREATED)
            
            # Handle both list and dictionary input
            elif isinstance(data, list):
                # Xử lý trường hợp data là list
                logger.info("Processing list of events")
                responses = []
                for item in data:
                    response = self.process_event(request, item)
                    responses.append(response.data)
                return Response({"results": responses}, status=status.HTTP_201_CREATED)
            else:
                # Xử lý trường hợp data là dictionary
                logger.info("Processing single event")
                return self.process_event(request, data)
                
        except Exception as e:
            logger.exception(f"Error processing tracking event: {str(e)}")
            return Response(
                {"error": f"Server error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def process_event(self, request, data):
        """Process a single tracking event."""
        try:
            if not isinstance(data, dict):
                logger.error(f"Invalid data type: {type(data)}")
                return Response(
                    {"error": f"Invalid data format. Expected dictionary, got {type(data)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Get or create session
            session_id = data.get('session_id')
            if not session_id:
                logger.error("Session ID is missing")
                return Response(
                    {"error": "Session ID is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            try:
                # Ensure MongoDB collections exist
                ensure_collections()
                
                # Get sessions collection
                sessions_collection = get_collection('sessions')
                if not sessions_collection:
                    return Response({'error': 'Failed to connect to MongoDB'}, status=500)
                
                # Check if session exists
                session = sessions_collection.find_one({'session_id': session_id})
                if not session:
                    # Create new session
                    session_data = {
                        'session_id': session_id,
                        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                        'referrer': request.META.get('HTTP_REFERER', ''),
                        'created_at': datetime.utcnow()
                    }
                    sessions_collection.insert_one(session_data)
                    logger.info(f"Created new session: {session_id}")
                
                # Get events collection
                events_collection = get_collection('events')
                if not events_collection:
                    return Response({'error': 'Failed to connect to MongoDB'}, status=500)
                
                # Save event
                event_data = {
                    'session_id': session_id,
                    'event_type': data.get('event_type', 'unknown'),
                    'data': data,
                    'timestamp': datetime.utcnow()
                }
                events_collection.insert_one(event_data)
                
                return Response({'status': 'success'})
            except Exception as e:
                logger.exception(f"Error processing event: {str(e)}")
                return Response({'error': str(e)}, status=500)
        except Exception as e:
            logger.exception(f"Error in process_event: {str(e)}")
            return Response(
                {"error": f"Server error in process_event: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip

class SessionView(APIView):
    """API endpoint for managing tracking sessions."""
    
    def get(self, request, session_id=None, format=None):
        """Get session info."""
        try:
            if session_id:
                # Get specific session
                try:
                    session = Session.objects.get(session_id=session_id)
                    events_count = Event.objects.filter(session=session).count()
                    
                    # Lấy thêm events từ MongoDB nếu có
                    mongo_events = get_events_by_session(session_id)
                    
                    return Response({
                        "session_id": str(session.session_id),
                        "user_agent": session.user_agent,
                        "ip_address": session.ip_address,
                        "referrer": session.referrer,
                        "start_time": session.start_time,
                        "end_time": session.end_time,
                        "is_active": session.is_active,
                        "events_count": events_count,
                        "mongo_events_count": len(mongo_events),
                        "mongo_events": mongo_events
                    })
                except Session.DoesNotExist:
                    return Response(
                        {"error": "Session not found"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            else:
                # List all sessions with pagination
                page = self.paginate_queryset(
                    Session.objects.all().order_by('-start_time'), 
                    request
                )
                
                data = []
                for session in page:
                    events_count = Event.objects.filter(session=session).count()
                    data.append({
                        "session_id": str(session.session_id),
                        "user_agent": session.user_agent[:50] + "..." if len(session.user_agent) > 50 else session.user_agent,
                        "start_time": session.start_time,
                        "is_active": session.is_active,
                        "events_count": events_count,
                    })
                
                return self.get_paginated_response(data)
        except Exception as e:
            logger.exception(f"Error retrieving session(s): {str(e)}")
            return Response(
                {"error": f"Error retrieving session(s): {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request, format=None):
        """Create a new tracking session."""
        try:
            logger.info("Creating new tracking session")
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            ip_address = self.get_client_ip(request)
            referrer = request.META.get('HTTP_REFERER', '')
            
            # Tạo session trong Django SQLite
            session = Session.objects.create(
                user_agent=user_agent,
                ip_address=ip_address,
                referrer=referrer,
                start_time=timezone.now(),
                is_active=True
            )
            
            # Lưu session vào MongoDB
            session_data = {
                'session_id': str(session.session_id),
                'user_agent': session.user_agent,
                'ip_address': session.ip_address,
                'referrer': session.referrer,
                'start_time': session.start_time,
                'is_active': session.is_active
            }
            
            mongo_saved = save_session(session_data)
            if mongo_saved:
                logger.info(f"Session saved to MongoDB: {session.session_id}")
            else:
                logger.warning(f"Failed to save session to MongoDB: {session.session_id}")
            
            logger.info(f"Session created: {session.session_id}")
            return Response({
                "session_id": session.session_id,
                "status": "created",
                "mongo_saved": mongo_saved
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception(f"Error creating session: {str(e)}")
            return Response(
                {"error": f"Server error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, session_id, format=None):
        """End a tracking session."""
        try:
            logger.info(f"Ending session: {session_id}")
            try:
                session = Session.objects.get(session_id=session_id)
                session.end_time = timezone.now()
                session.is_active = False
                session.save()
                
                # Cập nhật trạng thái session trong MongoDB
                try:
                    # Đây là ví dụ đơn giản để cập nhật MongoDB, bạn có thể mở rộng sau
                    from utils.mongo_client import get_collection
                    collection = get_collection('sessions')
                    if collection is None:  # Sửa lại cách kiểm tra
                        mongo_updated = False
                    else:
                        result = collection.update_one(
                            {'session_id': str(session_id)},
                            {'$set': {'is_active': False, 'end_time': session.end_time}}
                        )
                        mongo_updated = result.modified_count > 0
                except Exception as e:
                    logger.exception(f"Error updating MongoDB session: {str(e)}")
                    mongo_updated = False
                
                logger.info(f"Session ended: {session.session_id}")
                return Response({
                    "session_id": session.session_id,
                    "status": "ended",
                    "mongo_updated": mongo_updated
                })
            except Session.DoesNotExist:
                logger.error(f"Session not found: {session_id}")
                return Response(
                    {"error": "Session not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            logger.exception(f"Error ending session: {str(e)}")
            return Response(
                {"error": f"Server error: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR', '0.0.0.0')
        return ip
    
    # Add pagination mixin
    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            from rest_framework.pagination import PageNumberPagination
            self._paginator = PageNumberPagination()
        return self._paginator
    
    def paginate_queryset(self, queryset, request):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, request, view=self)
    
    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

def health_check(request):
    """Health check endpoint for Docker"""
    return JsonResponse({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})

@csrf_exempt
@require_http_methods(["POST"])
def process_event(request):
    try:
        # Log raw request body for debugging
        logger.info(f"Raw request body: {request.body}")
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
            
        logger.info(f"Parsed event data: {data}")
        
        # Ensure collections exist
        ensure_collections()
        
        # Get collections
        sessions_collection = get_collection('sessions')
        events_collection = get_collection('events')
        
        # Validate and transform data
        if isinstance(data, list):
            if not data:
                return JsonResponse({'error': 'Empty array'}, status=400)
            data = data[0]  # Take first item if array
            logger.info(f"Using first item from array: {data}")
        
        # Validate data
        if not isinstance(data, dict):
            logger.error(f"Invalid data type: {type(data)}")
            return JsonResponse({'error': 'Invalid data format. Expected JSON object'}, status=400)
            
        # Get or create session
        session_id = data.get('session_id')
        if not session_id:
            logger.error("Missing session_id in request")
            return JsonResponse({'error': 'session_id is required'}, status=400)
            
        # Get event data
        event_type = data.get('event_type')
        event_data = data.get('data', {})
        event_url = data.get('url', '')  # Get URL from event data
        
        if not event_type:
            logger.error("Missing event_type in request")
            return JsonResponse({'error': 'event_type is required'}, status=400)
            
        # Get or create session
        session = sessions_collection.find_one({'session_id': session_id})
        if not session:
            session = {
                'session_id': session_id,
                'created_at': datetime.utcnow(),
                'last_activity': datetime.utcnow(),
                'user_agent': request.headers.get('User-Agent', ''),
                'referer': request.headers.get('Referer', '')
            }
            try:
                sessions_collection.insert_one(session)
                logger.info(f"Created new session: {session_id}")
            except Exception as e:
                logger.error(f"Failed to save session to MongoDB: {session_id}")
                logger.error(str(e))
                return JsonResponse({'error': 'Failed to create session'}, status=500)
        else:
            # Update last activity
            try:
                sessions_collection.update_one(
                    {'session_id': session_id},
                    {'$set': {'last_activity': datetime.utcnow()}}
                )
            except Exception as e:
                logger.error(f"Failed to update session activity: {session_id}")
                logger.error(str(e))
        
        # Save event with URL from event data
        try:
            event = {
                'session_id': session_id,
                'event_type': event_type,
                'data': event_data,
                'timestamp': datetime.utcnow(),
                'url': event_url,  # Use URL from event data
                'path': request.path,
                'method': request.method,
                'user_agent': request.headers.get('User-Agent', '')
            }
            events_collection.insert_one(event)
            logger.info(f"Saved event for session {session_id}: {event_type} at URL: {event_url}")
        except Exception as e:
            logger.error(f"Failed to save event: {session_id}")
            logger.error(str(e))
            return JsonResponse({'error': 'Failed to save event'}, status=500)
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["PATCH"])
def update_session(request, session_id):
    try:
        # Log raw request body for debugging
        logger.info(f"Raw request body for session {session_id}: {request.body}")
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {str(e)}")
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
            
        logger.info(f"Parsed update data: {data}")
        
        # Ensure collections exist
        ensure_collections()
        
        # Get sessions collection
        sessions_collection = get_collection('sessions')
        
        # Validate data
        if not isinstance(data, dict):
            logger.error(f"Invalid data type: {type(data)}")
            return JsonResponse({'error': 'Invalid data format. Expected JSON object'}, status=400)
        
        # Update session
        try:
            update_data = {
                'last_activity': datetime.utcnow(),
                **data
            }
            result = sessions_collection.update_one(
                {'session_id': session_id},
                {'$set': update_data}
            )
            
            if result.matched_count == 0:
                logger.error(f"Session not found: {session_id}")
                return JsonResponse({'error': 'Session not found'}, status=404)
                
            logger.info(f"Updated session: {session_id}")
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            logger.error(f"Failed to update session: {session_id}")
            logger.error(str(e))
            return JsonResponse({'error': 'Failed to update session'}, status=500)
            
    except Exception as e:
        logger.error(f"Error updating session: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500) 