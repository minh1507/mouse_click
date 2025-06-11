"""
Script đơn giản để kiểm tra kết nối MongoDB và lưu dữ liệu mẫu
"""

import pymongo
import datetime
import uuid

def test_mongodb():
    """Kiểm tra kết nối MongoDB và lưu dữ liệu mẫu đơn giản."""
    print("Thử kết nối MongoDB và lưu dữ liệu mẫu...")
    
    # Thử kết nối
    try:
        print("Kết nối đến MongoDB...")
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        
        # Kiểm tra kết nối
        client.admin.command('ping')
        print("✅ Kết nối thành công!")
        
        # Tạo document test
        db = client["test_db"]
        collection = db["test_collection"]
        
        # Tạo document
        document = {
            "id": str(uuid.uuid4()),
            "name": "Test Document",
            "timestamp": datetime.datetime.now(),
            "test": True
        }
        
        # Lưu document
        print("Lưu document vào MongoDB...")
        result = collection.insert_one(document)
        print(f"✅ Đã lưu document với ID: {result.inserted_id}")
        
        # Đọc lại document
        print("Đọc lại document...")
        found = collection.find_one({"_id": result.inserted_id})
        print(f"✅ Đã đọc document: {found}")
        
        return True
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        
        # Thử kết nối khác
        try:
            print("\nThử kết nối với 127.0.0.1...")
            client = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
            client.admin.command('ping')
            print("✅ Kết nối thành công với 127.0.0.1!")
            return True
        except Exception as e2:
            print(f"❌ Lỗi khi kết nối với 127.0.0.1: {str(e2)}")
            return False

if __name__ == "__main__":
    test_mongodb() 