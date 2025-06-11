# Mouse Tracking Backend

Backend API cho hệ thống theo dõi chuột, xây dựng bằng Django REST Framework.

## Yêu cầu hệ thống

- Python 3.8+
- MongoDB (để lưu trữ dữ liệu tracking)

## Cài đặt

1. Cài đặt các dependencies:

```bash
pip install -r requirements/dev.txt  # cho môi trường development
```

2. Cài đặt và khởi động MongoDB:

- Windows:
  - Tải và cài đặt MongoDB từ [trang chủ MongoDB](https://www.mongodb.com/try/download/community)
  - Khởi động MongoDB service từ Services (services.msc)
  
- macOS (với Homebrew):
  ```bash
  brew tap mongodb/brew
  brew install mongodb-community
  brew services start mongodb-community
  ```

- Linux:
  ```bash
  sudo apt-get install mongodb
  sudo systemctl start mongodb
  ```

MongoDB sẽ chạy ở cổng mặc định 27017.

3. Khởi tạo cơ sở dữ liệu SQLite (cho Django):

```bash
python manage.py migrate
```

4. Chạy server:

```bash
python manage.py runserver
```

## API Endpoints

- `/api/tracking/events/` - Lưu trữ tracking events
- `/api/tracking/sessions/` - Quản lý tracking sessions
- `/api/tracking/mongo-status/` - Kiểm tra trạng thái kết nối MongoDB

## Kiểm tra MongoDB

Bạn có thể kiểm tra kết nối MongoDB bằng cách chạy:

```bash
python check_mongo.py
```

## Cấu hình

- Database được cấu hình trong `config/settings.py` và `config/settings/base.py`
- MongoDB kết nối đến `localhost:27017` mặc định
- Database có tên `mouse_tracker`

## Xử lý sự cố

### Lỗi cài đặt gói
Nếu gặp lỗi khi cài đặt các gói, hãy thử:

1. **Lỗi SSL/kết nối**:
   ```
   pip install -r requirements/base.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
   ```

2. **Lỗi distutils với Python 3.12**:
   ```
   pip install --upgrade setuptools pip wheel
   pip install --only-binary=:all: -r requirements/base.txt
   ```

3. **Lỗi hết dung lượng ổ đĩa**:
   - Dọn dẹp thư mục temp: `del %TEMP%\*.*` (Windows)
   - Cài đặt trên ổ đĩa khác: `python -m venv D:\other_drive\venv`

4. **Lỗi PowerShell**:
   - Nếu gặp lỗi "ArgumentOutOfRangeException" trong PowerShell, hãy sử dụng Command Prompt:
     ```
     cmd
     cd /d D:\study\mouse click event\backend
     venv\Scripts\activate.bat
     pip install -r requirements/base.txt
     ```

### Cài đặt từng gói một
Nếu không thể cài đặt tất cả cùng lúc:
```
pip install Django==4.2.3
pip install djangorestframework==3.14.0
pip install pymongo>=4.5.0
pip install djongo
pip install channels==4.0.0 channels-redis==4.1.0
```

### Vấn đề về MongoDB
- Đảm bảo MongoDB service đang chạy
- Kiểm tra kết nối: `mongosh` hoặc `mongo`
- Nếu không kết nối được, kiểm tra cổng và tường lửa 