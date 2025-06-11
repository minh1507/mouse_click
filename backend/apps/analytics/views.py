"""Views for the analytics app."""

from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Count
from rest_framework.views import APIView

from .models import Heatmap, PathAnalysis, Funnel, FunnelStep, FunnelAnalysis
from .serializers import (
    HeatmapSerializer, PathAnalysisSerializer, FunnelSerializer, 
    FunnelStepSerializer, FunnelAnalysisSerializer, FunnelWithStepsSerializer
)
from apps.tracking.models import Event, Session
from utils.mongo_client import get_collection
from .utils import (
    process_mouse_positions, 
    calculate_mouse_metrics, 
    analyze_cursor_path,
    generate_cursor_heatmap
)

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

@api_view(['GET'])
def session_mouse_analytics(request, session_id):
    """
    Endpoint để phân tích dữ liệu vị trí chuột cho một session cụ thể
    """
    try:
        # Kiểm tra session tồn tại
        try:
            session = Session.objects.get(session_id=session_id)
        except Session.DoesNotExist:
            return Response(
                {"error": f"Session with ID {session_id} not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Lấy dữ liệu từ SQLite
        events = Event.objects.filter(
            session=session, 
            event_type__in=['mouse_move', 'mouse_click']
        ).values('id', 'event_type', 'timestamp', 'url', 'data')
        
        # Chuyển đổi queryset thành list để xử lý
        events_list = list(events)
        
        # Bổ sung dữ liệu từ MongoDB nếu có
        try:
            mongo_events_collection = get_collection('events')
            if mongo_events_collection is not None:
                mongo_events = list(mongo_events_collection.find(
                    {'session_id': str(session_id), 'event_type': {'$in': ['mouse_move', 'mouse_click']}}
                ))
                
                # Thêm vào events_list, tránh trùng lặp dựa trên ID
                sqlite_ids = set(e['id'] for e in events_list)
                for mongo_event in mongo_events:
                    event_id = mongo_event.get('event_id')
                    if event_id and int(event_id) not in sqlite_ids:
                        events_list.append({
                            'id': event_id,
                            'event_type': mongo_event.get('event_type'),
                            'timestamp': mongo_event.get('timestamp'),
                            'url': mongo_event.get('url'),
                            'data': mongo_event.get('data'),
                            'source': 'mongodb'
                        })
        except Exception as e:
            # Log lỗi nhưng vẫn tiếp tục với dữ liệu từ SQLite
            print(f"Error fetching MongoDB data: {str(e)}")
        
        # Không có dữ liệu
        if not events_list:
            return Response(
                {"message": "No mouse events found for this session"},
                status=status.HTTP_200_OK
            )
        
        # Xử lý dữ liệu vị trí chuột
        df = process_mouse_positions(events_list)
        
        # Tính toán các chỉ số phân tích
        metrics = calculate_mouse_metrics(df)
        patterns = analyze_cursor_path(df)
        
        # Tạo dữ liệu heatmap
        heatmap = generate_cursor_heatmap(df)
        
        # Trả về kết quả
        result = {
            'session_id': str(session_id),
            'events_count': len(events_list),
            'metrics': metrics,
            'patterns': patterns,
            'heatmap': heatmap
        }
        
        return Response(result, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {"error": f"Error analyzing mouse data: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class MousePositionAnalyticsView(APIView):
    """
    API view for mouse position analytics
    """
    
    def get(self, request, format=None):
        """
        Get summary statistics for all mouse position data
        """
        try:
            # Lấy tham số từ query
            limit = int(request.query_params.get('limit', 1000))
            time_range = request.query_params.get('time_range', '7d')  # 7d, 30d, all
            
            # Xác định time filter
            from django.utils import timezone
            now = timezone.now()
            
            if time_range == '7d':
                time_filter = now - timezone.timedelta(days=7)
            elif time_range == '30d':
                time_filter = now - timezone.timedelta(days=30)
            else:
                time_filter = None
            
            # Query events
            events_query = Event.objects.filter(
                event_type__in=['mouse_move', 'mouse_click']
            )
            
            if time_filter:
                events_query = events_query.filter(timestamp__gte=time_filter)
            
            events_query = events_query.order_by('-timestamp')[:limit]
            
            # Chuyển đổi queryset thành list
            events_list = list(events_query.values('id', 'event_type', 'timestamp', 'url', 'session_id', 'data'))
            
            # Xử lý dữ liệu
            df = process_mouse_positions(events_list)
            
            # Tính toán số liệu
            metrics = calculate_mouse_metrics(df)
            
            # Tạo heatmap
            heatmap = generate_cursor_heatmap(df)
            
            # Thêm thông tin tổng quan
            metrics['total_sessions'] = len(df['session_id'].unique()) if not df.empty else 0
            metrics['total_urls'] = len(df['url'].unique()) if not df.empty else 0
            metrics['time_range'] = time_range
            
            return Response({
                'metrics': metrics,
                'heatmap': heatmap
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": f"Error analyzing mouse data: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            ) 