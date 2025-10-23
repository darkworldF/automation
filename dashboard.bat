@echo off
echo ==========================================
echo    ENGWE MONITORING DASHBOARD
echo ==========================================
echo.
echo Choose an option:
echo 1. View Dashboard
echo 2. Test Notifications
echo 3. Test Full System
echo 4. Back to Monitor Control
echo.
set /p choice="Enter choice (1-4): "

if "%choice%"=="1" (
    echo Opening monitoring dashboard...
    python monitoring_dashboard.py
) else if "%choice%"=="2" (
    echo Testing notifications...
    python test_notifications.py
    pause
) else if "%choice%"=="3" (
    echo Testing full monitoring system...
    python test_notifications.py --scan
    pause
) else if "%choice%"=="4" (
    monitor_control.bat
) else (
    echo Invalid choice.
    pause
)