@echo off
echo ==========================================
echo    ENGWE 2-STEP IMPORTER - STEP 1
echo ==========================================
echo.
echo This will:
echo 1. Fetch all products from engwe.com
echo 2. Create a visual preview for you to review
echo 3. Prepare products for Step 2 (upload to Shopify)
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
pip install requests beautifulsoup4 lxml pandas
if %errorlevel% neq 0 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)

echo.
echo ==========================================
echo    STEP 1: FETCH AND PREVIEW
echo ==========================================
echo.
echo Starting product fetch from engwe.com...
python two_step_importer.py

echo.
echo ==========================================
echo    STEP 1 COMPLETE!
echo ==========================================
echo.
echo A preview has opened in your browser.
echo Review all products, then run STEP 2:
echo.
echo    step2_upload.bat
echo.
pause