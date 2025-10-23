@echo off
echo ==========================================
echo    ENGWE Product Importer - API Mode
echo ==========================================
echo.
echo Setting up environment...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

:: Install required packages
echo Installing required packages...
pip install requests beautifulsoup4 lxml pandas shopifyapi python-dotenv
if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo ==========================================
echo    Starting API Import Process
echo ==========================================
echo.
echo This will import all products from engwe.com
echo directly to your Shopify store via API.
echo.
echo Make sure you have:
echo 1. Created the Private App in Shopify
echo 2. Updated config.ini with your API credentials
echo 3. Set the correct permissions in your app
echo.
set /p confirm="Continue with API import? (y/n): "
if /i "%confirm%" neq "y" (
    echo Import cancelled.
    pause
    exit /b 0
)

echo.
echo Starting import...
python run_api_import.py

echo.
echo ==========================================
echo    Import Process Complete
echo ==========================================
echo.
echo Check your Shopify admin to review imported products.
echo Products are created as drafts for your review.
echo.
pause