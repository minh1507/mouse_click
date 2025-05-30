"""Celery tasks for the analytics app."""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from .models import Heatmap, PathAnalysis, FunnelAnalysis, Funnel
from apps.tracking.models import Event, Session

@shared_task
def generate_heatmap(heatmap_id):
    """Generate heatmap data from events asynchronously."""
    try:
        heatmap = Heatmap.objects.get(id=heatmap_id)
        
        # Skip if already processed
        if heatmap.is_processed:
            return f"Heatmap {heatmap_id} already processed"
        
        event_type = 'mouse_click' if heatmap.heatmap_type == 'click' else 'mouse_move'
        
        # Get events matching criteria
        events = Event.objects.filter(
            event_type=event_type,
            timestamp__gte=heatmap.date_from,
            timestamp__lte=heatmap.date_to,
            url__contains=heatmap.url_pattern
        )
        
        # Process events to generate heatmap data
        grid_size = 10  # 10x10 pixels per cell
        cols = heatmap.resolution_width // grid_size
        rows = heatmap.resolution_height // grid_size
        
        # Initialize empty grid
        grid = [[0 for _ in range(cols)] for _ in range(rows)]
        
        # Count events in each cell
        for event in events:
            if 'x' in event.data and 'y' in event.data:
                x, y = event.data['x'], event.data['y']
                
                # Ensure coordinates are within bounds
                if 0 <= x < heatmap.resolution_width and 0 <= y < heatmap.resolution_height:
                    col = min(int(x // grid_size), cols - 1)
                    row = min(int(y // grid_size), rows - 1)
                    grid[row][col] += 1
        
        # Format data for visualization
        heatmap_data = {
            'grid': grid,
            'grid_size': grid_size,
            'max_value': max([max(row) for row in grid]) if grid else 0,
            'total_events': sum([sum(row) for row in grid]) if grid else 0,
            'resolution': {
                'width': heatmap.resolution_width,
                'height': heatmap.resolution_height
            }
        }
        
        # Update heatmap with processed data
        heatmap.data = heatmap_data
        heatmap.is_processed = True
        heatmap.save()
        
        return f"Heatmap {heatmap_id} processed successfully"
        
    except Heatmap.DoesNotExist:
        return f"Heatmap {heatmap_id} not found"
    except Exception as e:
        return f"Error processing heatmap {heatmap_id}: {str(e)}"

@shared_task
def generate_path_analysis(path_analysis_id):
    """Generate path analysis data from sessions asynchronously."""
    try:
        path_analysis = PathAnalysis.objects.get(id=path_analysis_id)
        
        # Skip if already processed
        if path_analysis.is_processed:
            return f"Path analysis {path_analysis_id} already processed"
        
        # Get sessions in the date range
        sessions = Session.objects.filter(
            start_time__gte=path_analysis.date_from,
            start_time__lte=path_analysis.date_to
        )
        
        # Get all page_view events for each session, ordered by timestamp
        paths = {}
        total_sessions = 0
        
        for session in sessions:
            events = Event.objects.filter(
                session=session,
                event_type='page_view'
            ).order_by('timestamp')
            
            if events.exists():
                total_sessions += 1
                
                # Extract path as sequence of URLs
                path = [event.url for event in events]
                path_key = ' -> '.join(path)
                
                # Count occurrences of each path
                if path_key in paths:
                    paths[path_key]['count'] += 1
                else:
                    paths[path_key] = {
                        'path': path,
                        'count': 1
                    }
        
        # Sort paths by count
        sorted_paths = sorted(paths.values(), key=lambda x: x['count'], reverse=True)
        
        # Format data for visualization
        path_data = {
            'paths': sorted_paths,
            'total_sessions': total_sessions,
        }
        
        # Update path analysis with processed data
        path_analysis.data = path_data
        path_analysis.is_processed = True
        path_analysis.save()
        
        return f"Path analysis {path_analysis_id} processed successfully"
        
    except PathAnalysis.DoesNotExist:
        return f"Path analysis {path_analysis_id} not found"
    except Exception as e:
        return f"Error processing path analysis {path_analysis_id}: {str(e)}"

@shared_task
def generate_funnel_analysis(funnel_analysis_id):
    """Generate funnel analysis data from events asynchronously."""
    try:
        funnel_analysis = FunnelAnalysis.objects.get(id=funnel_analysis_id)
        
        # Skip if already processed
        if funnel_analysis.is_processed:
            return f"Funnel analysis {funnel_analysis_id} already processed"
        
        funnel = funnel_analysis.funnel
        steps = funnel.steps.all().order_by('step_order')
        
        if not steps.exists():
            return f"Funnel {funnel.id} has no steps"
        
        # Get sessions that started within the analysis period
        sessions = Session.objects.filter(
            start_time__gte=funnel_analysis.date_from,
            start_time__lte=funnel_analysis.date_to
        )
        
        step_data = []
        step_counts = []
        prev_sessions = set()
        
        # Process each step
        for i, step in enumerate(steps):
            # Find sessions that visited this step's URL
            current_sessions = set()
            
            for session in sessions:
                # Check if session had a page_view event for this URL pattern
                has_view = Event.objects.filter(
                    session=session,
                    event_type='page_view',
                    url__contains=step.url_pattern,
                    timestamp__gte=funnel_analysis.date_from,
                    timestamp__lte=funnel_analysis.date_to
                ).exists()
                
                if has_view:
                    current_sessions.add(session.session_id)
            
            # Calculate conversion rate
            total_count = len(current_sessions)
            
            if i == 0:
                conversion_rate = 100.0  # First step is the baseline
                prev_sessions = current_sessions
            else:
                # Calculate conversion from previous step
                continued_sessions = current_sessions.intersection(prev_sessions)
                prev_count = len(prev_sessions)
                continued_count = len(continued_sessions)
                conversion_rate = (continued_count / prev_count * 100) if prev_count > 0 else 0
                prev_sessions = continued_sessions
            
            step_counts.append(total_count)
            
            # Add step data
            step_data.append({
                'name': step.name,
                'url_pattern': step.url_pattern,
                'step_order': step.step_order,
                'sessions_count': total_count,
                'conversion_rate': round(conversion_rate, 2),
                'drop_off_rate': round(100 - conversion_rate, 2) if i > 0 else 0
            })
        
        # Format data for visualization
        funnel_data = {
            'steps': step_data,
            'total_sessions': len(sessions),
            'completion_rate': round(step_counts[-1] / step_counts[0] * 100, 2) if step_counts[0] > 0 else 0,
        }
        
        # Update funnel analysis with processed data
        funnel_analysis.data = funnel_data
        funnel_analysis.is_processed = True
        funnel_analysis.save()
        
        return f"Funnel analysis {funnel_analysis_id} processed successfully"
        
    except FunnelAnalysis.DoesNotExist:
        return f"Funnel analysis {funnel_analysis_id} not found"
    except Exception as e:
        return f"Error processing funnel analysis {funnel_analysis_id}: {str(e)}"

@shared_task
def generate_daily_analytics():
    """Generate daily analytics for yesterday."""
    yesterday = timezone.now().date() - timedelta(days=1)
    date_from = timezone.datetime.combine(yesterday, timezone.time.min)
    date_to = timezone.datetime.combine(yesterday, timezone.time.max)
    
    # Create heatmaps for popular URLs
    popular_urls = Event.objects.filter(
        event_type='page_view',
        timestamp__gte=date_from,
        timestamp__lte=date_to
    ).values('url').annotate(count=Count('id')).order_by('-count')[:5]
    
    for url_data in popular_urls:
        url = url_data['url']
        
        # Create click heatmap
        click_heatmap = Heatmap.objects.create(
            name=f"Daily Click Heatmap - {url} - {yesterday}",
            url_pattern=url,
            heatmap_type='click',
            date_from=date_from,
            date_to=date_to
        )
        generate_heatmap.delay(click_heatmap.id)
        
        # Create movement heatmap
        move_heatmap = Heatmap.objects.create(
            name=f"Daily Movement Heatmap - {url} - {yesterday}",
            url_pattern=url,
            heatmap_type='move',
            date_from=date_from,
            date_to=date_to
        )
        generate_heatmap.delay(move_heatmap.id)
    
    # Create path analysis for yesterday
    path_analysis = PathAnalysis.objects.create(
        name=f"Daily Path Analysis - {yesterday}",
        date_from=date_from,
        date_to=date_to
    )
    generate_path_analysis.delay(path_analysis.id)
    
    # Create funnel analyses for all funnels
    for funnel in Funnel.objects.all():
        funnel_analysis = FunnelAnalysis.objects.create(
            funnel=funnel,
            date_from=date_from,
            date_to=date_to
        )
        generate_funnel_analysis.delay(funnel_analysis.id)
    
    return "Daily analytics generation scheduled" 