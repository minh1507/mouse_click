# Script để cài đặt và cấu hình MongoDB trên Windows
# Chạy PowerShell với quyền Admin để sử dụng script này

# Kiểm tra MongoDB đã được cài đặt chưa
Write-Host "Kiểm tra MongoDB đã được cài đặt chưa..." -ForegroundColor Yellow

$mongoService = Get-Service -Name MongoDB -ErrorAction SilentlyContinue
if ($mongoService -ne $null) {
    Write-Host "MongoDB đã được cài đặt." -ForegroundColor Green
    
    # Kiểm tra trạng thái dịch vụ
    if ($mongoService.Status -eq "Running") {
        Write-Host "Dịch vụ MongoDB đang chạy." -ForegroundColor Green
    } else {
        Write-Host "Dịch vụ MongoDB không chạy. Đang khởi động..." -ForegroundColor Yellow
        Start-Service MongoDB
        Write-Host "Đã khởi động dịch vụ MongoDB." -ForegroundColor Green
    }
} else {
    Write-Host "MongoDB chưa được cài đặt hoặc không chạy như một dịch vụ Windows." -ForegroundColor Red
    Write-Host "Vui lòng tải và cài đặt MongoDB Community Edition từ: https://www.mongodb.com/try/download/community" -ForegroundColor Yellow
    
    # Hướng dẫn tải MongoDB
    Write-Host "Hướng dẫn cài đặt MongoDB:" -ForegroundColor Cyan
    Write-Host "1. Tải MongoDB Community Edition MSI installer từ trang web MongoDB" -ForegroundColor Cyan
    Write-Host "2. Chạy installer và làm theo hướng dẫn" -ForegroundColor Cyan
    Write-Host "3. Chọn 'Complete' setup và đảm bảo 'Install MongoDB as a Service' được chọn" -ForegroundColor Cyan
    Write-Host "4. Sau khi cài đặt, khởi động lại máy tính để đảm bảo dịch vụ hoạt động" -ForegroundColor Cyan
}

# Kiểm tra cổng 27017
Write-Host "Kiểm tra cổng 27017..." -ForegroundColor Yellow
$testPort = Test-NetConnection -ComputerName localhost -Port 27017 -InformationLevel Quiet
if ($testPort) {
    Write-Host "Cổng 27017 đang mở và MongoDB có thể đang chạy." -ForegroundColor Green
} else {
    Write-Host "Cổng 27017 không mở. MongoDB có thể không chạy." -ForegroundColor Red
    
    # Thử khởi động lại dịch vụ
    if ($mongoService -ne $null) {
        Write-Host "Thử khởi động lại dịch vụ MongoDB..." -ForegroundColor Yellow
        Restart-Service MongoDB
        Start-Sleep -Seconds 5
        
        # Kiểm tra lại cổng
        $testPort = Test-NetConnection -ComputerName localhost -Port 27017 -InformationLevel Quiet
        if ($testPort) {
            Write-Host "Khởi động lại thành công! Cổng 27017 đã mở." -ForegroundColor Green
        } else {
            Write-Host "Không thể mở cổng 27017 sau khi khởi động lại dịch vụ." -ForegroundColor Red
        }
    }
}

# Kiểm tra firewall
Write-Host "Kiểm tra cấu hình firewall..." -ForegroundColor Yellow
$firewallRule = Get-NetFirewallRule -DisplayName "MongoDB Server" -ErrorAction SilentlyContinue
if ($firewallRule -eq $null) {
    Write-Host "Không tìm thấy rule firewall cho MongoDB. Đang tạo rule..." -ForegroundColor Yellow
    try {
        New-NetFirewallRule -DisplayName "MongoDB Server" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 27017 -ErrorAction Stop
        Write-Host "Đã tạo rule firewall cho MongoDB." -ForegroundColor Green
    } catch {
        Write-Host "Không thể tạo rule firewall. Lỗi: $_" -ForegroundColor Red
        Write-Host "Vui lòng mở Windows Defender Firewall và tạo rule cho cổng 27017 thủ công." -ForegroundColor Yellow
    }
} else {
    Write-Host "Rule firewall đã tồn tại cho MongoDB." -ForegroundColor Green
}

# Thử kết nối MongoDB bằng pymongo
Write-Host "Thử kết nối đến MongoDB bằng pymongo..." -ForegroundColor Yellow
$pythonCode = @"
import sys
try:
    import pymongo
    client = pymongo.MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    print('Kết nối MongoDB thành công!')
    sys.exit(0)
except Exception as e:
    print(f'Lỗi kết nối MongoDB: {str(e)}')
    sys.exit(1)
"@

# Lưu mã Python vào file tạm thời
$tempFile = [System.IO.Path]::GetTempFileName() + ".py"
$pythonCode | Out-File -FilePath $tempFile -Encoding utf8

# Chạy mã Python
Write-Host "Chạy kiểm tra kết nối Python..." -ForegroundColor Yellow
$result = python $tempFile
if ($LASTEXITCODE -eq 0) {
    Write-Host "Python có thể kết nối đến MongoDB!" -ForegroundColor Green
} else {
    Write-Host "Python không thể kết nối đến MongoDB." -ForegroundColor Red
    Write-Host $result -ForegroundColor Red
}

# Xóa file tạm
Remove-Item $tempFile

Write-Host "Hoàn tất kiểm tra MongoDB." -ForegroundColor Yellow 