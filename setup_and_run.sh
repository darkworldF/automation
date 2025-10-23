#!/bin/bash

# ENGWE Product Importer - Quick Start Script
# This script helps you set up and run the product import easily

echo "🚲 ENGWE to NLEbike Product Importer Setup"
echo "================================================"
echo

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Python 3 found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📦 Installing required packages..."
pip install -r requirements.txt

echo
echo "✅ Setup completed!"
echo
echo "Choose an option:"
echo "1. Run full product import (recommended)"
echo "2. Check for duplicates against existing products"
echo "3. Import via Shopify API (requires API credentials)"
echo "4. Exit"
echo

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🚀 Starting full product import..."
        python run_import.py
        ;;
    2)
        read -p "Enter path to your existing products export file: " existing_file
        if [ -f "$existing_file" ]; then
            echo "🔍 Running duplicate detection..."
            python duplicate_detector.py engwe_import_*/data/engwe_products_*.json "$existing_file"
        else
            echo "❌ File not found: $existing_file"
        fi
        ;;
    3)
        echo "🔗 Starting Shopify API import..."
        python shopify_api_importer.py
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo
echo "✅ Process completed!"
echo
echo "📁 Check the generated files in the output directory."
echo "📋 Review the summary report for any issues."
echo "🛒 Import the CSV file to your Shopify store when ready."

# Deactivate virtual environment
deactivate
