@echo off
echo ==========================================
echo    MONITOR MANAGEMENT
echo ==========================================
echo.
echo Choose an option:
echo 1. Start Monitor
echo 2. Check Status
echo 3. Manual Scan
echo 4. Stop Monitor
echo 5. View Logs
echo.
set /p choice="Enter choice (1-5): "

if "%choice%"=="1" (
    echo Starting monitor...
    python engwe_monitor.py
) else if "%choice%"=="2" (
    echo Checking status...
    python engwe_monitor.py --status
    pause
) else if "%choice%"=="3" (
    echo Performing manual scan...
    python engwe_monitor.py --scan
    pause
) else if "%choice%"=="4" (
    echo Stopping monitor...
    python engwe_monitor.py --stop
    pause
) else if "%choice%"=="5" (
    echo Opening monitoring log...
    if exist monitoring_log.json (
        notepad monitoring_log.json
    ) else (
        echo No log file found.
    )
    pause
) else (
    echo Invalid choice.
    pause
)