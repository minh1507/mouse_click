# Hướng dẫn cài đặt và sử dụng MongoDB

MongoDB là cơ sở dữ liệu NoSQL được sử dụng để lưu trữ dữ liệu tracking trong ứng dụng này. Dưới đây là hướng dẫn chi tiết cách cài đặt và cấu hình MongoDB.

## 1. Cài đặt MongoDB trên Windows

### Cách 1: Sử dụng installer chính thức (Khuyến nghị)

1. Truy cập trang tải MongoDB Community Edition: https://www.mongodb.com/try/download/community
2. Chọn phiên bản (Latest), Platform: Windows, Package: MSI
3. Tải về và chạy file cài đặt
4. Làm theo hướng dẫn trong installer
   - Chọn "Complete" installation
   - Đảm bảo đã chọn "Install MongoDB as a Service" để tự động khởi động cùng Windows
   - Mặc định MongoDB sẽ được cài đặt vào `C:\Program Files\MongoDB\Server\<version>`
5. Sau khi cài đặt hoàn tất, dịch vụ MongoDB sẽ tự động chạy ở cổng 27017

### Cách 2: Sử dụng Chocolatey (cho người dùng nâng cao)

```
choco install mongodb
```

## 2. Kiểm tra cài đặt

### Kiểm tra dịch vụ MongoDB

1. Mở Services (Nhấn `Win+R`, gõ `services.msc`)
2. Tìm dịch vụ có tên "MongoDB"
3. Đảm bảo nó có trạng thái "Running"

### Kiểm tra kết nối từ dòng lệnh

```
mongosh
```

Nếu kết nối thành công, bạn sẽ thấy MongoDB shell prompt:
```
Current Mongosh Log ID: <some-id>
Connecting to:          mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+1.x
Using MongoDB:          x.y.z
>
```

## 3. Kiểm tra MongoDB với ứng dụng

Chạy script kiểm tra kết nối trong thư mục backend:

```
python check_mongo.py
```

hoặc:

```
python test_mongo.py
```

Nếu kết nối thành công, bạn sẽ thấy thông báo "✅ Kết nối thành công đến MongoDB với URL: mongodb://localhost:27017/"

## 4. Khắc phục sự cố

### MongoDB không khởi động

1. Thử khởi động lại dịch vụ:
   ```
   sc stop MongoDB
   sc start MongoDB
   ```

2. Kiểm tra cổng 27017 có đang mở không:
   ```
   netstat -ano | findstr 27017
   ```

3. Nếu thấy lỗi quyền truy cập, chạy lại PowerShell với quyền Administrator

### Không thể kết nối từ ứng dụng

1. Kiểm tra MongoDB đã chạy chưa
2. Kiểm tra firewall có chặn cổng 27017 không
3. Thử chạy script kiểm tra với quyền Administrator:
   ```
   powershell -Command "Start-Process python -ArgumentList 'check_mongo.py' -Verb RunAs"
   ```

### Script PowerShell để chuẩn đoán

Chạy script chuẩn đoán trong PowerShell với quyền Administrator:

```
.\mongodb_windows_setup.ps1
```

## 5. Xem và quản lý dữ liệu

### Sử dụng MongoDB Compass (GUI Tool)

1. Tải và cài đặt MongoDB Compass từ: https://www.mongodb.com/try/download/compass
2. Mở MongoDB Compass và kết nối đến `mongodb://localhost:27017`
3. Bạn sẽ thấy database `mouse_tracker` với các collections `sessions` và `events`

### Sử dụng mongosh (command line)

```
mongosh
use mouse_tracker
db.sessions.find()  # Xem tất cả sessions
db.events.find()    # Xem tất cả events
```

## 6. Tạo dữ liệu mẫu

Để tạo dữ liệu mẫu cho việc kiểm thử, chạy script:

```
python generate_sample_data.py [số_lượng_session]
```

Mặc định script sẽ tạo 10 sessions và khoảng 5-20 events cho mỗi session. 