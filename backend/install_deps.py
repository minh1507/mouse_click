"""
Script để cài đặt các dependencies cho dự án Mouse Tracker.
Giải quyết các vấn đề phổ biến khi cài đặt.
"""

import subprocess
import sys
import os
import platform

def run_command(cmd):
    """Chạy lệnh và hiển thị output"""
    print(f"Đang chạy: {' '.join(cmd)}")
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # Hiển thị output theo thời gian thực
    for line in process.stdout:
        print(line, end='')
    
    process.wait()
    return process.returncode

def main():
    """Cài đặt các dependencies"""
    print("=== Cài đặt dependencies cho Mouse Tracker Backend ===")
    
    # Cập nhật pip, setuptools, wheel
    print("\n[1/5] Cập nhật pip, setuptools, wheel...")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    
    # Cài đặt Django và REST framework
    print("\n[2/5] Cài đặt Django và REST framework...")
    run_command([sys.executable, "-m", "pip", "install", "Django==4.2.3", "djangorestframework==3.14.0", 
                "django-cors-headers==4.2.0", "django-filter==23.2"])
    
    # Cài đặt MongoDB libraries
    print("\n[3/5] Cài đặt MongoDB libraries...")
    run_command([sys.executable, "-m", "pip", "install", "pymongo>=4.5.0"])
    run_command([sys.executable, "-m", "pip", "install", "djongo"])
    
    # Cài đặt Channels
    print("\n[4/5] Cài đặt Channels...")
    run_command([sys.executable, "-m", "pip", "install", "channels==4.0.0", "channels-redis==4.1.0", 
                "daphne==4.0.0"])
    
    # Cài đặt các gói khác
    print("\n[5/5] Cài đặt các gói khác...")
    run_command([sys.executable, "-m", "pip", "install", "celery==5.3.1", "redis==4.6.0", 
                "Pillow==10.0.0", "python-dotenv==1.0.0", "gunicorn==21.2.0"])
    
    # Thử cài đặt các gói data science nếu cần
    print("\n[Bonus] Cài đặt các gói data science...")
    try:
        run_command([sys.executable, "-m", "pip", "install", "--only-binary=:all:", 
                    "numpy>=1.26.0", "pandas>=2.0.3", "scikit-learn>=1.3.0"])
    except Exception as e:
        print(f"Không thể cài đặt các gói data science: {e}")
        print("Bạn có thể sử dụng dự án mà không cần các gói này.")
    
    print("\n=== Cài đặt hoàn tất ===")
    print("Bây giờ bạn có thể chạy server với lệnh: python manage.py runserver")

if __name__ == "__main__":
    main() 