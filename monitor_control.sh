#!/bin/bash

echo "=========================================="
echo "    MONITOR MANAGEMENT"
echo "=========================================="
echo
echo "Choose an option:"
echo "1. Start Monitor"
echo "2. Check Status"
echo "3. Manual Scan"
echo "4. Stop Monitor"
echo "5. View Logs"
echo
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo "Starting monitor..."
        python3 engwe_monitor.py
        ;;
    2)
        echo "Checking status..."
        python3 engwe_monitor.py --status
        read -p "Press Enter to continue..."
        ;;
    3)
        echo "Performing manual scan..."
        python3 engwe_monitor.py --scan
        read -p "Press Enter to continue..."
        ;;
    4)
        echo "Stopping monitor..."
        python3 engwe_monitor.py --stop
        read -p "Press Enter to continue..."
        ;;
    5)
        echo "Opening monitoring log..."
        if [ -f "monitoring_log.json" ]; then
            less monitoring_log.json
        else
            echo "No log file found."
            read -p "Press Enter to continue..."
        fi
        ;;
    *)
        echo "Invalid choice."
        read -p "Press Enter to continue..."
        ;;
esac