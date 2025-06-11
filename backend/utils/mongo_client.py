"""MongoDB client utility for direct access to the database."""

import pymongo
import logging
import json
import traceback
from datetime import datetime
from bson import json_util
from django.conf import settings

logger = logging.getLogger(__name__)

def get_mongo_client():
    """Get a MongoDB client instance."""
    try:
        # In ra thông báo debug
        print("Đang thử kết nối đến MongoDB...")
        logger.info("Đang thử kết nối đến MongoDB...")
        
        # Thử nhiều cách kết nối khác nhau
        mongo_urls = [
            'mongodb://localhost:27017/',
            'mongodb://127.0.0.1:27017/',
            'mongodb://0.0.0.0:27017/'
        ]
        
        client = None
        last_error = None
        
        for url in mongo_urls:
            try:
                print(f"Thử kết nối với {url}...")
                client = pymongo.MongoClient(url, serverSelectionTimeoutMS=5000)
                # Kiểm tra kết nối
                client.admin.command('ping')
                print(f"✅ Kết nối thành công đến MongoDB với URL: {url}")
                logger.info(f"MongoDB connection successful with URL: {url}")
                break
            except Exception as e:
                print(f"Không kết nối được với {url}: {str(e)}")
                last_error = e
                client = None
        
        if client is None:
            logger.error(f"MongoDB connection failed with all URLs. Last error: {str(last_error)}")
            traceback.print_exc()
            return None
            
        return client
    except Exception as e:
        logger.error(f"MongoDB connection failed: {str(e)}")
        print(f"❌ Lỗi kết nối MongoDB: {str(e)}")
        traceback.print_exc()
        # Trả về None nếu kết nối thất bại
        return None

def get_database():
    """Get the MongoDB database instance."""
    client = get_mongo_client()
    if client is None:
        logger.error("Failed to get MongoDB client")
        return None
    
    db_name = 'mouse_tracker'
    logger.info(f"Using MongoDB database: {db_name}")
    return client[db_name]

def get_collection(collection_name):
    """Get a specific MongoDB collection."""
    db = get_database()
    if db is None:
        logger.error("Failed to get MongoDB database")
        return None
    
    logger.info(f"Using MongoDB collection: {collection_name}")
    return db[collection_name]

def save_event(event_data):
    """Save event data to MongoDB."""
    try:
        collection = get_collection('events')
        if collection is None:
            logger.error("Failed to get events collection")
            print("❌ Không thể lưu event vào MongoDB: Collection không tồn tại")
            return False
        
        # Đảm bảo timestamp là đối tượng datetime
        if 'timestamp' not in event_data:
            event_data['timestamp'] = datetime.now()
        elif isinstance(event_data['timestamp'], str):
            try:
                event_data['timestamp'] = datetime.fromisoformat(event_data['timestamp'].replace('Z', '+00:00'))
            except ValueError:
                event_data['timestamp'] = datetime.now()
        
        # Chuyển đổi session_id thành string nếu cần
        if 'session_id' in event_data and not isinstance(event_data['session_id'], str):
            event_data['session_id'] = str(event_data['session_id'])
        
        # In ra dữ liệu đang lưu
        print(f"Đang lưu event vào MongoDB: {event_data}")
        
        # Lưu event vào MongoDB
        result = collection.insert_one(event_data)
        logger.info(f"Event saved to MongoDB with ID: {result.inserted_id}")
        print(f"✅ Event đã được lưu vào MongoDB với ID: {result.inserted_id}")
        return True
    except Exception as e:
        logger.exception(f"Error saving event to MongoDB: {str(e)}")
        print(f"❌ Lỗi khi lưu event vào MongoDB: {str(e)}")
        traceback.print_exc()
        return False

def save_session(session_data):
    """Save session data to MongoDB."""
    try:
        collection = get_collection('sessions')
        if collection is None:
            logger.error("Failed to get sessions collection")
            print("❌ Không thể lưu session vào MongoDB: Collection không tồn tại")
            return False
        
        # Đảm bảo timestamp là đối tượng datetime
        if 'start_time' not in session_data:
            session_data['start_time'] = datetime.now()
        elif isinstance(session_data['start_time'], str):
            try:
                session_data['start_time'] = datetime.fromisoformat(session_data['start_time'].replace('Z', '+00:00'))
            except ValueError:
                session_data['start_time'] = datetime.now()
        
        # Chuyển đổi session_id thành string nếu cần
        if 'session_id' in session_data and not isinstance(session_data['session_id'], str):
            session_data['session_id'] = str(session_data['session_id'])
        
        # In ra dữ liệu đang lưu
        print(f"Đang lưu session vào MongoDB: {session_data}")
        
        # Lưu session vào MongoDB
        result = collection.insert_one(session_data)
        logger.info(f"Session saved to MongoDB with ID: {result.inserted_id}")
        print(f"✅ Session đã được lưu vào MongoDB với ID: {result.inserted_id}")
        return True
    except Exception as e:
        logger.exception(f"Error saving session to MongoDB: {str(e)}")
        print(f"❌ Lỗi khi lưu session vào MongoDB: {str(e)}")
        traceback.print_exc()
        return False

def get_events_by_session(session_id):
    """Get all events for a session."""
    try:
        collection = get_collection('events')
        if collection is None:
            logger.error("Failed to get events collection")
            return []
        
        events = list(collection.find({'session_id': str(session_id)}))
        # Chuyển đổi ObjectId thành string để có thể serialize
        return json.loads(json_util.dumps(events))
    except Exception as e:
        logger.exception(f"Error getting events from MongoDB: {str(e)}")
        print(f"❌ Lỗi khi lấy events từ MongoDB: {str(e)}")
        traceback.print_exc()
        return [] 