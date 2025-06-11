"""
Utility functions for analyzing mouse tracking data
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple

def process_mouse_positions(events: List[Dict]) -> pd.DataFrame:
    """
    Process mouse position events and convert to a DataFrame
    for analysis.
    
    Args:
        events: List of mouse events from the database
        
    Returns:
        DataFrame with processed mouse position data
    """
    mouse_events = []
    
    for event in events:
        # Chỉ xử lý các sự kiện liên quan đến chuột
        if event['event_type'] not in ('mouse_move', 'mouse_click'):
            continue
            
        # Lấy dữ liệu từ JSON
        data = event.get('data', {})
        
        # Kiểm tra xem data có phải là string không (MongoDB trả về string)
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                data = {}
        
        # Chỉ xử lý nếu có tọa độ x, y
        if 'x' not in data or 'y' not in data:
            continue
            
        # Tạo entry mới
        entry = {
            'timestamp': event.get('timestamp'),
            'session_id': event.get('session_id'),
            'event_type': event.get('event_type'),
            'x': data.get('x'),
            'y': data.get('y'),
            'url': event.get('url', ''),
        }
        
        # Thêm button cho mouse_click
        if event['event_type'] == 'mouse_click':
            entry['button'] = data.get('button')
            
        # Thêm thông tin target nếu có
        target = data.get('target', {})
        if target:
            entry['target_tag'] = target.get('tagName')
            entry['target_id'] = target.get('id')
            entry['target_class'] = target.get('className')
            
            # Lấy thông tin rectangle nếu có
            rect = target.get('rect', {})
            if rect:
                entry['target_top'] = rect.get('top')
                entry['target_left'] = rect.get('left')
                entry['target_width'] = rect.get('width')
                entry['target_height'] = rect.get('height')
        
        mouse_events.append(entry)
    
    # Tạo DataFrame từ dữ liệu đã xử lý
    if not mouse_events:
        # Trả về DataFrame rỗng với các cột cần thiết
        return pd.DataFrame(columns=[
            'timestamp', 'session_id', 'event_type', 'x', 'y', 
            'button', 'url', 'target_tag', 'target_id', 'target_class',
            'target_top', 'target_left', 'target_width', 'target_height'
        ])
    
    df = pd.DataFrame(mouse_events)
    
    # Chuyển đổi timestamp thành datetime
    if 'timestamp' in df.columns:
        if df['timestamp'].dtype == object:
            # Nếu timestamp là string
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        elif pd.api.types.is_numeric_dtype(df['timestamp']):
            # Nếu timestamp là milliseconds
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    # Sắp xếp theo timestamp
    df = df.sort_values('timestamp')
    
    return df

def calculate_mouse_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate metrics from mouse tracking data
    
    Args:
        df: DataFrame containing mouse tracking data
        
    Returns:
        Dictionary of metrics
    """
    metrics = {}
    
    if df.empty:
        return metrics
    
    # Số lượng sự kiện
    metrics['total_events'] = len(df)
    metrics['move_events'] = len(df[df['event_type'] == 'mouse_move'])
    metrics['click_events'] = len(df[df['event_type'] == 'mouse_click'])
    
    # Phân tích click
    if 'button' in df.columns and metrics['click_events'] > 0:
        click_df = df[df['event_type'] == 'mouse_click']
        button_counts = click_df['button'].value_counts().to_dict()
        metrics['left_clicks'] = button_counts.get(0, 0)  # 0 = chuột trái
        metrics['middle_clicks'] = button_counts.get(1, 0)  # 1 = chuột giữa
        metrics['right_clicks'] = button_counts.get(2, 0)  # 2 = chuột phải
    
    # Tính toán vùng hoạt động (heatmap)
    if 'x' in df.columns and 'y' in df.columns:
        # Giới hạn x, y
        metrics['min_x'] = df['x'].min()
        metrics['max_x'] = df['x'].max()
        metrics['min_y'] = df['y'].min()
        metrics['max_y'] = df['y'].max()
        
        # Tính phân phối
        try:
            x_bins = min(100, int((metrics['max_x'] - metrics['min_x']) / 10))
            y_bins = min(100, int((metrics['max_y'] - metrics['min_y']) / 10))
            
            if x_bins > 0 and y_bins > 0:
                heatmap, xedges, yedges = np.histogram2d(
                    df['x'], df['y'], 
                    bins=[x_bins, y_bins],
                    range=[[metrics['min_x'], metrics['max_x']], 
                           [metrics['min_y'], metrics['max_y']]]
                )
                
                # Chuyển đổi thành danh sách để serialize
                metrics['heatmap'] = heatmap.tolist()
                metrics['heatmap_x'] = xedges.tolist()
                metrics['heatmap_y'] = yedges.tolist()
                
                # Tìm điểm nóng (hotspots)
                hotspots = []
                threshold = np.percentile(heatmap, 90)  # Lấy top 10% giá trị
                for i in range(len(xedges) - 1):
                    for j in range(len(yedges) - 1):
                        if heatmap[i, j] > threshold:
                            hotspots.append({
                                'x': (xedges[i] + xedges[i+1]) / 2,
                                'y': (yedges[j] + yedges[j+1]) / 2,
                                'intensity': float(heatmap[i, j])
                            })
                
                metrics['hotspots'] = sorted(hotspots, key=lambda x: x['intensity'], reverse=True)[:10]
        except Exception as e:
            metrics['heatmap_error'] = str(e)
    
    # Thời gian di chuyển
    if 'timestamp' in df.columns and len(df) > 1:
        df_sorted = df.sort_values('timestamp')
        duration = (df_sorted['timestamp'].max() - df_sorted['timestamp'].min()).total_seconds()
        metrics['duration_seconds'] = duration
        
        # Tốc độ di chuyển trung bình (chỉ tính cho mouse_move)
        if metrics['move_events'] > 1:
            move_df = df[df['event_type'] == 'mouse_move'].sort_values('timestamp')
            
            # Tính khoảng cách giữa các điểm liên tiếp
            move_df['next_x'] = move_df['x'].shift(-1)
            move_df['next_y'] = move_df['y'].shift(-1)
            move_df['next_time'] = move_df['timestamp'].shift(-1)
            
            # Loại bỏ hàng cuối cùng (không có "next")
            move_df = move_df.dropna(subset=['next_x', 'next_y', 'next_time'])
            
            # Tính khoảng cách và thời gian
            move_df['distance'] = np.sqrt((move_df['next_x'] - move_df['x'])**2 + 
                                         (move_df['next_y'] - move_df['y'])**2)
            move_df['time_diff'] = (move_df['next_time'] - move_df['timestamp']).dt.total_seconds()
            
            # Loại bỏ thời gian diff quá lớn (> 2 giây, có thể là nghỉ hoặc chuyển trang)
            move_df = move_df[move_df['time_diff'] < 2.0]
            
            if len(move_df) > 0:
                # Tính tốc độ (pixel/giây)
                move_df['speed'] = move_df['distance'] / move_df['time_diff']
                metrics['avg_speed'] = move_df['speed'].mean()
                metrics['max_speed'] = move_df['speed'].max()
                metrics['total_distance'] = move_df['distance'].sum()
    
    return metrics

def analyze_cursor_path(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze the cursor path to detect patterns
    
    Args:
        df: DataFrame containing mouse tracking data
        
    Returns:
        Dictionary of pattern analysis
    """
    patterns = {}
    
    if df.empty or 'event_type' not in df.columns:
        return patterns
    
    # Chỉ phân tích các sự kiện mouse_move
    move_df = df[df['event_type'] == 'mouse_move'].copy()
    
    if len(move_df) < 10:  # Cần ít nhất 10 điểm để phân tích
        return {'error': 'Not enough data points for analysis'}
    
    # Sắp xếp theo thời gian
    move_df = move_df.sort_values('timestamp')
    
    # Tính độ cong của đường đi (curvature)
    try:
        # Tính vector chuyển động
        move_df['dx'] = move_df['x'].diff()
        move_df['dy'] = move_df['y'].diff()
        
        # Loại bỏ hàng đầu tiên (không có diff)
        move_df = move_df.dropna(subset=['dx', 'dy'])
        
        # Tính góc của vector chuyển động (trong radian)
        move_df['angle'] = np.arctan2(move_df['dy'], move_df['dx'])
        
        # Tính sự thay đổi góc (độ cong)
        move_df['angle_change'] = move_df['angle'].diff().abs()
        
        # Xử lý trường hợp góc thay đổi qua 2π
        move_df['angle_change'] = move_df['angle_change'].apply(
            lambda x: min(x, 2*np.pi - x) if not pd.isna(x) else np.nan
        )
        
        # Tính các thông số về độ cong
        avg_curvature = move_df['angle_change'].mean()
        max_curvature = move_df['angle_change'].max()
        
        patterns['avg_curvature'] = float(avg_curvature) if not pd.isna(avg_curvature) else 0
        patterns['max_curvature'] = float(max_curvature) if not pd.isna(max_curvature) else 0
        
        # Phát hiện các kiểu di chuyển
        # Hesitation: nhiều góc cong lớn trong thời gian ngắn
        hesitation_threshold = np.pi/4  # 45 độ
        hesitation_points = move_df[move_df['angle_change'] > hesitation_threshold]
        patterns['hesitation_count'] = len(hesitation_points)
        
        # Straight lines: ít góc cong
        straight_threshold = np.pi/36  # 5 độ
        straight_points = move_df[move_df['angle_change'] < straight_threshold]
        patterns['straight_segments'] = len(straight_points) / len(move_df)
        
        # Circular movements: các góc cong đều nhau
        # TODO: Thuật toán phức tạp hơn để phát hiện chuyển động tròn
        
        # Tính tốc độ thay đổi (acceleration)
        if 'time_diff' in move_df.columns:
            move_df['speed'] = np.sqrt(move_df['dx']**2 + move_df['dy']**2) / move_df['time_diff']
            move_df['acceleration'] = move_df['speed'].diff() / move_df['time_diff']
            
            avg_acceleration = move_df['acceleration'].mean()
            patterns['avg_acceleration'] = float(avg_acceleration) if not pd.isna(avg_acceleration) else 0
    
    except Exception as e:
        patterns['analysis_error'] = str(e)
    
    return patterns

def generate_cursor_heatmap(df: pd.DataFrame, width: int = 1000, height: int = 800) -> Dict[str, Any]:
    """
    Generate a heatmap visualization data for the cursor movements
    
    Args:
        df: DataFrame containing mouse tracking data
        width: Width of the heatmap
        height: Height of the heatmap
        
    Returns:
        Dictionary with heatmap data
    """
    if df.empty or 'x' not in df.columns or 'y' not in df.columns:
        return {'error': 'No cursor position data available'}
    
    try:
        # Chuẩn hóa tọa độ về kích thước chuẩn
        x_scale = width / (df['x'].max() - df['x'].min() or 1)
        y_scale = height / (df['y'].max() - df['y'].min() or 1)
        
        x_min = df['x'].min()
        y_min = df['y'].min()
        
        # Tạo tọa độ chuẩn hóa
        x_normalized = ((df['x'] - x_min) * x_scale).astype(int)
        y_normalized = ((df['y'] - y_min) * y_scale).astype(int)
        
        # Đảm bảo trong khoảng hợp lệ
        x_normalized = x_normalized.clip(0, width - 1)
        y_normalized = y_normalized.clip(0, height - 1)
        
        # Tạo heatmap
        heatmap_data = np.zeros((height, width))
        
        # Đếm số lần xuất hiện của mỗi tọa độ
        for x, y in zip(x_normalized, y_normalized):
            heatmap_data[y, x] += 1
        
        # Làm mịn heatmap bằng Gaussian blur
        from scipy.ndimage import gaussian_filter
        heatmap_data = gaussian_filter(heatmap_data, sigma=10)
        
        # Chuẩn hóa về khoảng [0, 1]
        max_value = heatmap_data.max()
        if max_value > 0:
            heatmap_data = heatmap_data / max_value
        
        # Chuyển đổi thành định dạng cho visualization
        heatmap_list = []
        for y in range(0, height, 5):  # Giảm độ phân giải để giảm kích thước dữ liệu
            for x in range(0, width, 5):
                value = float(heatmap_data[y, x])
                if value > 0.05:  # Chỉ giữ lại các điểm có giá trị đáng kể
                    heatmap_list.append({
                        'x': int(x),
                        'y': int(y),
                        'value': value
                    })
        
        return {
            'width': width,
            'height': height,
            'points': heatmap_list,
            'max_value': float(max_value)
        }
    
    except Exception as e:
        return {'error': str(e)} 