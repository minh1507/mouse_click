"""
Script để kiểm tra kết nối MongoDB và hiển thị thống kê cơ bản
"""

import sys
import os
import pymongo
import traceback
import socket
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def check_mongodb_connection():
    """Kiểm tra kết nối MongoDB và hiển thị thông tin cơ bản."""
    print("=== KIỂM TRA KẾT NỐI MONGODB ===")
    
    # Kiểm tra xem cổng 27017 có đang mở không
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)  # Timeout 1 giây
        result = s.connect_ex(('localhost', 27017))
        if result == 0:
            print("✅ Cổng 27017 đang mở và có thể kết nối")
        else:
            print("❌ Cổng 27017 không mở. MongoDB có thể không chạy.")
        s.close()
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra cổng: {str(e)}")
    
    # Thử nhiều cách kết nối khác nhau
    mongo_urls = [
        'mongodb://localhost:27017/',
        'mongodb://127.0.0.1:27017/',
        'mongodb://0.0.0.0:27017/'
    ]
    
    connected = False
    
    for url in mongo_urls:
        try:
            print(f"\nThử kết nối với {url}...")
            client = pymongo.MongoClient(url, serverSelectionTimeoutMS=5000)
            
            # Kiểm tra kết nối
            client.admin.command('ping')
            print(f"✅ Kết nối thành công đến MongoDB server với URL: {url}")
            
            # Lấy thông tin server
            server_info = client.server_info()
            print(f"MongoDB version: {server_info.get('version', 'unknown')}")
            
            # Lấy danh sách các database
            databases = client.list_database_names()
            print(f"\nDatabases hiện có: {', '.join(databases)}")
            
            # Tạo database mouse_tracker nếu không tồn tại
            db = client['mouse_tracker']
            
            # Tạo collections nếu chưa tồn tại
            if 'sessions' not in db.list_collection_names():
                db.create_collection('sessions')
                print("✅ Đã tạo collection 'sessions'")
            
            if 'events' not in db.list_collection_names():
                db.create_collection('events')
                print("✅ Đã tạo collection 'events'")
            
            # Kiểm tra collections
            collections = db.list_collection_names()
            
            if collections:
                print(f"\nCollections trong database 'mouse_tracker':")
                for collection in collections:
                    count = db[collection].count_documents({})
                    print(f"  - {collection}: {count} documents")
                    
                    # Hiển thị mẫu dữ liệu
                    if count > 0:
                        sample = db[collection].find_one()
                        print(f"    Mẫu dữ liệu: {sample}")
            else:
                print("\nDatabase 'mouse_tracker' chưa có collections nào.")
            
            # Thử tạo document
            print("\nThử tạo document test...")
            result = db.test.insert_one({"test": "data", "created_at": pymongo.datetime.datetime.now()})
            print(f"✅ Đã tạo document test với ID: {result.inserted_id}")
            
            connected = True
            break
        except ServerSelectionTimeoutError:
            print(f"❌ Không thể kết nối đến MongoDB server với URL {url} (timeout)")
        except ConnectionFailure:
            print(f"❌ Không thể kết nối đến MongoDB server với URL {url} (connection failure)")
        except Exception as e:
            print(f"❌ Lỗi khi kết nối với {url}: {str(e)}")
            traceback.print_exc()
    
    if not connected:
        print("\n=== KIỂM TRA TÌNH TRẠNG MONGODB ===")
        print("❌ Không thể kết nối đến MongoDB server. Vui lòng kiểm tra:")
        print("  1. MongoDB service đã được cài đặt và khởi động chưa?")
        print("  2. MongoDB đang chạy ở cổng 27017?")
        print("  3. Có firewall chặn kết nối đến cổng 27017?")
        
        # Kiểm tra MongoDB có được cài đặt không
        if os.name == 'nt':  # Windows
            print("\nKiểm tra dịch vụ MongoDB trên Windows:")
            try:
                import subprocess
                result = subprocess.run(["sc", "query", "MongoDB"], capture_output=True, text=True)
                if "RUNNING" in result.stdout:
                    print("✅ Dịch vụ MongoDB đang chạy.")
                else:
                    print("❌ Dịch vụ MongoDB không chạy. Hãy chạy: sc start MongoDB")
            except:
                print("❓ Không thể kiểm tra trạng thái dịch vụ MongoDB.")
        
        print("\nCách khởi động MongoDB:")
        print("  - Windows: Start service MongoDB hoặc chạy cmd với quyền admin: ")
        print("      sc start MongoDB")
        print("  - Mac: brew services start mongodb-community")
        print("  - Linux: sudo systemctl start mongod")
        return False
    
    return True

if __name__ == "__main__":
    success = check_mongodb_connection()
    sys.exit(0 if success else 1) 