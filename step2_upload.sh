#!/bin/bash

echo "=========================================="
echo "    ENGWE 2-STEP IMPORTER - STEP 2"
echo "=========================================="
echo
echo "This will upload all fetched products"
echo "from Step 1 to your Shopify store."
echo
echo "Make sure you have:"
echo "1. Completed Step 1 (fetch and preview)"
echo "2. Reviewed products in the preview"
echo "3. Configured your API credentials in config.ini"
echo
read -p "Continue with upload to Shopify? (y/n): " confirm
if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    echo "Upload cancelled."
    exit 0
fi

echo
echo "=========================================="
echo "    STEP 2: UPLOAD TO SHOPIFY"
echo "=========================================="
echo
echo "Starting upload to your Shopify store..."
python3 two_step_importer.py --step2

echo
echo "=========================================="
echo "    STEP 2 COMPLETE!"
echo "=========================================="
echo
echo "Check your Shopify admin to review uploaded products."
echo "Products are created as drafts for your review."
echo