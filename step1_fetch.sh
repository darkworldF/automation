#!/bin/bash

echo "=========================================="
echo "    ENGWE 2-STEP IMPORTER - STEP 1"
echo "=========================================="
echo
echo "This will:"
echo "1. Fetch all products from engwe.com"
echo "2. Create a visual preview for you to review"
echo "3. Prepare products for Step 2 (upload to Shopify)"
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
pip3 install requests beautifulsoup4 lxml pandas
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install packages"
    exit 1
fi

echo
echo "=========================================="
echo "    STEP 1: FETCH AND PREVIEW"
echo "=========================================="
echo
echo "Starting product fetch from engwe.com..."
python3 two_step_importer.py

echo
echo "=========================================="
echo "    STEP 1 COMPLETE!"
echo "=========================================="
echo
echo "A preview has opened in your browser."
echo "Review all products, then run STEP 2:"
echo
echo "    ./step2_upload.sh"
echo