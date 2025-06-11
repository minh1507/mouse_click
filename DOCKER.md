# Hướng dẫn sử dụng Docker cho Mouse Tracker

## Yêu cầu hệ thống
- Docker Desktop (Windows/Mac) hoặc Docker Engine (Linux)
- Docker Compose

## Khởi động ứng dụng

Để khởi động toàn bộ ứng dụng (backend, frontend, MongoDB, Redis):

```bash
docker-compose up -d
```

Các dịch vụ sẽ được khởi động:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- MongoDB: localhost:27017
- Redis: localhost:6379

## Dừng ứng dụng

```bash
docker-compose down
```

## Xem logs

Xem logs của tất cả các dịch vụ:
```bash
docker-compose logs -f
```

Xem logs của một dịch vụ cụ thể:
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongo
```

## Khởi động lại một dịch vụ

```bash
docker-compose restart backend
docker-compose restart frontend
```

## Xóa tất cả dữ liệu (volumes)

Cẩn thận: Lệnh này sẽ xóa tất cả dữ liệu đã lưu:
```bash
docker-compose down -v
```

## Tạo dữ liệu mẫu trong container

```bash
docker-compose exec backend python generate_sample_data.py
```

## Truy cập MongoDB shell

```bash
docker-compose exec mongo mongosh
``` 