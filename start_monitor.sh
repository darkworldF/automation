#!/bin/bash

echo "=========================================="
echo "    ENGWE PRODUCT MONITOR"
echo "=========================================="
echo
echo "This will start monitoring engwe.com for:"
echo "- New products"
echo "- Stock level changes"
echo "- Out of stock alerts"
echo
echo "Make sure you have configured:"
echo "1. Monitoring settings in config.ini"
echo "2. Email notifications (optional)"
echo
read -p "Start monitoring service? (y/n): " confirm
if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    echo "Monitoring cancelled."
    exit 0
fi

echo
echo "Installing monitoring dependencies..."
pip3 install schedule

echo
echo "=========================================="
echo "    STARTING MONITOR SERVICE"
echo "=========================================="
echo
echo "Monitor is now running in background..."
echo "Press Ctrl+C to stop monitoring"
echo
python3 engwe_monitor.py

echo
echo "Monitor stopped."