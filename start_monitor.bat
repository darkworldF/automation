@echo off
echo ==========================================
echo    ENGWE PRODUCT MONITOR
echo ==========================================
echo.
echo This will start monitoring engwe.com for:
echo - New products
echo - Stock level changes  
echo - Out of stock alerts
echo.
echo Make sure you have configured:
echo 1. Monitoring settings in config.ini
echo 2. Email notifications (optional)
echo.
set /p confirm="Start monitoring service? (y/n): "
if /i "%confirm%" neq "y" (
    echo Monitoring cancelled.
    pause
    exit /b 0
)

echo.
echo Installing monitoring dependencies...
pip install schedule win10toast

echo.
echo ==========================================
echo    STARTING MONITOR SERVICE
echo ==========================================
echo.
echo Monitor is now running in background...
echo Press Ctrl+C to stop monitoring
echo.
python engwe_monitor.py

echo.
echo Monitor stopped.
pause