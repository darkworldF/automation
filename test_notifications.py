#!/usr/bin/env python3
"""
Notification Test Script
Test all notification methods to ensure they're working
"""

from engwe_monitor import EngweMonitor
from datetime import datetime

def test_notifications():
    """Test all notification methods"""
    print("🎧 Testing Notification System")
    print("=" * 40)
    
    monitor = EngweMonitor()
    
    # Test 1: Desktop notification
    print("\n1. Testing desktop notification...")
    monitor.send_desktop_notification(
        "🎧 Test Notification",
        "This is a test desktop notification from Engwe Monitor.",
        "info"
    )
    print("   Desktop notification sent (check your system tray)")
    
    # Test 2: Email notification (if configured)
    print("\n2. Testing email notification...")
    if monitor.config.has_section('EMAIL_NOTIFICATIONS'):
        try:
            monitor.send_email_notification(
                "Test Email",
                "This is a test email notification from Engwe Monitor."
            )
            print("   Email notification sent successfully")
        except Exception as e:
            print(f"   Email notification failed: {e}")
    else:
        print("   Email notifications not configured (optional)")
    
    # Test 3: Full notification system
    print("\n3. Testing full notification system...")
    monitor.send_notification(
        "🎧 Full Test Alert",
        "This tests all configured notification methods at once.",
        "info"
    )
    print("   Full notification system tested")
    
    # Test 4: Different notification types
    print("\n4. Testing different alert types...")
    
    # Info notification
    monitor.send_notification(
        "📊 Info Test",
        "This is an info-level notification test.",
        "info"
    )
    
    # Warning notification
    monitor.send_notification(
        "⚠️ Warning Test",
        "This is a warning-level notification test.",
        "warning"
    )
    
    # Error notification
    monitor.send_notification(
        "❌ Error Test",
        "This is an error-level notification test.",
        "error"
    )
    
    print("   All notification types tested")
    
    print("\n" + "=" * 40)
    print("✅ Notification testing complete!")
    print("\nIf you received notifications, the system is working correctly.")
    print("If not, check your configuration in config.ini")

def test_monitoring_scan():
    """Test a monitoring scan without saving results"""
    print("\n🔍 Testing monitoring scan...")
    print("=" * 40)
    
    monitor = EngweMonitor()
    
    try:
        # Perform a test scan
        result = monitor.scan_for_changes()
        
        if result['success']:
            print(f"\n✅ Scan completed successfully!")
            print(f"   Total products: {result['total_products']}")
            print(f"   New products: {result['new_products']}")
            print(f"   Stock alerts: {result['stock_alerts']}")
        else:
            print(f"\n❌ Scan failed: {result['error']}")
    
    except Exception as e:
        print(f"\n❌ Scan error: {e}")

def main():
    import sys
    
    print("🤖 Engwe Monitor - Notification & System Test")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if '--scan' in sys.argv:
        test_monitoring_scan()
    else:
        test_notifications()
    
    print("\n🔔 Test completed. Check for notifications!")

if __name__ == "__main__":
    main()