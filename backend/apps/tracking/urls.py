"""URL configuration for the tracking app."""

from django.urls import path
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . import views

def test_view(request):
    """Simple test view to verify API connectivity."""
    return JsonResponse({"status": "ok", "message": "API is working!"})

@api_view(['POST'])
def simple_event(request):
    """Simplified endpoint for tracking events."""
    try:
        # Get session or create new one
        session_id = request.data.get('session_id')
        if not session_id:
            return Response({"error": "Session ID is required"}, status=400)
            
        # Process the event directly
        response = views.EventsView().process_event(request, request.data)
        return response
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def mongo_status(request):
    """Check MongoDB connection status."""
    from utils.mongo_client import get_mongo_client
    
    try:
        client = get_mongo_client()
        if client is None:
            return Response({
                "status": "disconnected",
                "error": "Could not connect to MongoDB"
            }, status=500)
        else:
            # Kiểm tra kết nối
            client.admin.command('ping')
            
            # Lấy thông tin cơ bản về database
            db = client['mouse_tracker']
            collections = db.list_collection_names()
            
            stats = {}
            for collection in collections:
                stats[collection] = db[collection].count_documents({})
            
            return Response({
                "status": "connected",
                "database": "mouse_tracker",
                "collections": collections,
                "stats": stats
            })
    except Exception as e:
        return Response({
            "status": "error",
            "error": str(e)
        }, status=500)

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('events/', views.process_event, name='process_event'),
    path('sessions/', views.SessionView.as_view(), name='tracking-sessions-list'),
    path('sessions/<uuid:session_id>/', views.SessionView.as_view(), name='tracking-sessions-detail'),
    path('test/', test_view, name='tracking-test'),
    path('simple-event/', simple_event, name='tracking-simple-event'),
    path('mongo-status/', mongo_status, name='tracking-mongo-status'),
    path('sessions/<str:session_id>/', views.update_session, name='update_session'),
] 