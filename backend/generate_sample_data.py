"""
Script để tạo dữ liệu mẫu cho MongoDB.
Sử dụng script này để kiểm tra kết nối và chức năng của MongoDB.
"""

import os
import sys
import uuid
import random
import datetime
import pymongo
from faker import Faker

# Khởi tạo Faker để tạo dữ liệu giả
fake = Faker()

def connect_to_mongodb():
    """Kết nối đến MongoDB."""
    try:
        # Kết nối đến MongoDB
        client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        # Kiểm tra kết nối
        client.admin.command('ping')
        print("✅ Kết nối thành công đến MongoDB server!")
        return client
    except Exception as e:
        print(f"❌ Lỗi kết nối MongoDB: {str(e)}")
        return None

def generate_sample_data(count=10):
    """Tạo dữ liệu mẫu cho MongoDB."""
    
    client = connect_to_mongodb()
    if not client:
        sys.exit(1)
    
    # Lấy database và collections
    db = client['mouse_tracker']
    sessions_collection = db['sessions']
    events_collection = db['events']
    
    # Xóa dữ liệu cũ nếu có
    sessions_collection.delete_many({})
    events_collection.delete_many({})
    
    print(f"Tạo {count} sessions và events mẫu...")
    
    # Tạo sessions
    sessions = []
    for _ in range(count):
        session_id = str(uuid.uuid4())
        session = {
            'session_id': session_id,
            'user_agent': fake.user_agent(),
            'ip_address': fake.ipv4(),
            'referrer': fake.uri(),
            'start_time': datetime.datetime.now() - datetime.timedelta(
                minutes=random.randint(0, 60)
            ),
            'is_active': random.choice([True, False]),
        }
        
        # Thêm end_time nếu session không active
        if not session['is_active']:
            session['end_time'] = session['start_time'] + datetime.timedelta(
                minutes=random.randint(5, 30)
            )
        
        sessions.append(session)
    
    # Lưu sessions vào MongoDB
    result = sessions_collection.insert_many(sessions)
    print(f"✅ Đã tạo {len(result.inserted_ids)} sessions")
    
    # Tạo events cho mỗi session
    all_events = []
    for session in sessions:
        # Số lượng events ngẫu nhiên cho mỗi session
        num_events = random.randint(5, 20)
        
        for _ in range(num_events):
            # Thời gian event sau start_time của session
            if session.get('is_active', True):
                max_minutes = (datetime.datetime.now() - session['start_time']).total_seconds() / 60
            else:
                max_minutes = (session['end_time'] - session['start_time']).total_seconds() / 60
            
            event_time = session['start_time'] + datetime.timedelta(
                minutes=random.uniform(0, max(1, max_minutes))
            )
            
            # Loại sự kiện ngẫu nhiên
            event_types = ['mousemove', 'mouseclick', 'keypress', 'scroll', 'pageview']
            event_type = random.choice(event_types)
            
            # Dữ liệu event tùy theo loại
            data = {
                'url': fake.uri(),
                'path': '/' + fake.uri_path(),
                'timestamp': event_time,
            }
            
            if event_type == 'mousemove':
                data.update({
                    'x': random.randint(0, 1920),
                    'y': random.randint(0, 1080),
                    'movement_x': random.randint(-20, 20),
                    'movement_y': random.randint(-20, 20),
                })
            elif event_type == 'mouseclick':
                data.update({
                    'x': random.randint(0, 1920),
                    'y': random.randint(0, 1080),
                    'button': random.choice([0, 1, 2]),  # 0: left, 1: middle, 2: right
                    'target': f'#{fake.word()}',
                })
            elif event_type == 'keypress':
                data.update({
                    'key': random.choice(['a', 'b', 'c', 'Enter', 'Escape', 'Space']),
                    'keyCode': random.randint(65, 90),
                })
            elif event_type == 'scroll':
                data.update({
                    'scrollX': random.randint(0, 100),
                    'scrollY': random.randint(0, 2000),
                })
            
            # Tạo event object
            event = {
                'event_id': str(uuid.uuid4()),
                'session_id': session['session_id'],
                'event_type': event_type,
                'timestamp': event_time,
                'url': data['url'],
                'data': data
            }
            
            all_events.append(event)
    
    # Lưu events vào MongoDB
    if all_events:
        result = events_collection.insert_many(all_events)
        print(f"✅ Đã tạo {len(result.inserted_ids)} events")
    
    # Hiển thị thống kê
    print("\nThống kê dữ liệu đã tạo:")
    print(f"- Sessions: {sessions_collection.count_documents({})}")
    print(f"- Events: {events_collection.count_documents({})}")
    
    return True

if __name__ == "__main__":
    # Số lượng sessions mẫu mặc định
    count = 10
    
    # Kiểm tra nếu có tham số dòng lệnh
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print(f"Lỗi: Tham số phải là số nguyên. Sử dụng giá trị mặc định {count}")
    
    generate_sample_data(count) 