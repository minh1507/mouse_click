FROM python:3.11-slim

WORKDIR /app

# Cài đặt các phụ thuộc
COPY requirements/ requirements/
RUN pip install --no-cache-dir -r requirements/base.txt -r requirements/prod.txt

# Sao chép mã nguồn
COPY . .

# Thiết lập biến môi trường
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV PYTHONUNBUFFERED=1
ENV DJANGO_PRODUCTION=1

# Mở port cho Django
EXPOSE 8000

# Chạy migrations và khởi động server
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000"] 