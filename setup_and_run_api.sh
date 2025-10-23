#!/bin/bash

echo "=========================================="
echo "    ENGWE Product Importer - API Mode"
echo "=========================================="
echo
echo "Setting up environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed"
    echo "Please install Python3 from your package manager"
    exit 1
fi

# Install required packages
echo "Installing required packages..."
pip3 install requests beautifulsoup4 lxml pandas shopifyapi python-dotenv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install packages"
    exit 1
fi

echo
echo "=========================================="
echo "    Starting API Import Process"
echo "=========================================="
echo
echo "This will import all products from engwe.com"
echo "directly to your Shopify store via API."
echo
echo "Make sure you have:"
echo "1. Created the Private App in Shopify"
echo "2. Updated config.ini with your API credentials"
echo "3. Set the correct permissions in your app"
echo
read -p "Continue with API import? (y/n): " confirm
if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    echo "Import cancelled."
    exit 0
fi

echo
echo "Starting import..."
python3 run_api_import.py

echo
echo "=========================================="
echo "    Import Process Complete"
echo "=========================================="
echo
echo "Check your Shopify admin to review imported products."
echo "Products are created as drafts for your review."
echo