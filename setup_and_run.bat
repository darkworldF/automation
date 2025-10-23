@echo off
REM ENGWE Product Importer - Windows Quick Start Script

echo 🚲 ENGWE to NLEbike Product Importer Setup
echo ================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📦 Installing required packages...
pip install -r requirements.txt

echo.
echo ✅ Setup completed!
echo.
echo Choose an option:
echo 1. Run full product import (recommended)
echo 2. Check for duplicates against existing products
echo 3. Import via Shopify API (requires API credentials)
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo 🚀 Starting full product import...
    python run_import.py
) else if "%choice%"=="2" (
    set /p existing_file="Enter path to your existing products export file: "
    if exist "%existing_file%" (
        echo 🔍 Running duplicate detection...
        for /f "delims=" %%i in ('dir /b /od engwe_import_*\data\engwe_products_*.json 2^>nul ^| tail -1') do (
            python duplicate_detector.py "engwe_import_*\data\%%i" "%existing_file%"
        )
    ) else (
        echo ❌ File not found: %existing_file%
    )
) else if "%choice%"=="3" (
    echo 🔗 Starting Shopify API import...
    python shopify_api_importer.py
) else if "%choice%"=="4" (
    echo 👋 Goodbye!
    goto :end
) else (
    echo ❌ Invalid choice. Please run the script again.
    pause
    goto :end
)

echo.
echo ✅ Process completed!
echo.
echo 📁 Check the generated files in the output directory.
echo 📋 Review the summary report for any issues.
echo 🛒 Import the CSV file to your Shopify store when ready.

:end
REM Deactivate virtual environment
deactivate
pause
