#!/bin/bash

echo "=========================================="
echo "    ENGWE MONITORING DASHBOARD"
echo "=========================================="
echo
echo "Choose an option:"
echo "1. View Dashboard"
echo "2. Test Notifications"
echo "3. Test Full System"
echo "4. Back to Monitor Control"
echo
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo "Opening monitoring dashboard..."
        python3 monitoring_dashboard.py
        ;;
    2)
        echo "Testing notifications..."
        python3 test_notifications.py
        read -p "Press Enter to continue..."
        ;;
    3)
        echo "Testing full monitoring system..."
        python3 test_notifications.py --scan
        read -p "Press Enter to continue..."
        ;;
    4)
        ./monitor_control.sh
        ;;
    *)
        echo "Invalid choice."
        read -p "Press Enter to continue..."
        ;;
esac