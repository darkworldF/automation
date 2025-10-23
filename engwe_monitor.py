#!/usr/bin/env python3
"""
Engwe Product Monitor
Monitors for new products and stock changes on engwe.com
Sends notifications when changes are detected
"""

import os
import json
import time
import smtplib
import schedule
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from engwe_product_importer import EngweProductImporter
import configparser

class EngweMonitor:
    def __init__(self):
        self.config = self.load_config()
        self.previous_products_file = "previous_products.json"
        self.monitoring_log_file = "monitoring_log.json"
        self.previous_products = self.load_previous_products()
        self.monitoring_active = False
        
    def load_config(self):
        """Load monitoring configuration"""
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config
    
    def load_previous_products(self):
        """Load previously scanned products for comparison"""
        if os.path.exists(self.previous_products_file):
            with open(self.previous_products_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def save_current_products(self, products):
        """Save current products for next comparison"""
        product_data = {}
        for product in products:
            product_id = product.get('handle', product.get('title', ''))
            product_data[product_id] = {
                'title': product.get('title', ''),
                'price': product.get('price', 0),
                'available': product.get('available', True),
                'inventory_quantity': product.get('inventory_quantity', 0),
                'variants': len(product.get('variants', [])),
                'last_seen': datetime.now().isoformat(),
                'url': product.get('url', '')
            }
        
        with open(self.previous_products_file, 'w', encoding='utf-8') as f:
            json.dump(product_data, f, indent=2, ensure_ascii=False)
        
        self.previous_products = product_data
    
    def log_monitoring_event(self, event_type, message, details=None):
        """Log monitoring events"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'message': message,
            'details': details or {}
        }
        
        # Load existing log
        log_data = []
        if os.path.exists(self.monitoring_log_file):
            with open(self.monitoring_log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
        
        # Add new entry
        log_data.append(log_entry)
        
        # Keep only last 1000 entries
        if len(log_data) > 1000:
            log_data = log_data[-1000:]
        
        # Save log
        with open(self.monitoring_log_file, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2, ensure_ascii=False)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {event_type}: {message}")
    
    def send_notification(self, subject, message, notification_type="info"):
        """Send notification via multiple channels"""
        # Desktop notification
        self.send_desktop_notification(subject, message, notification_type)
        
        # Email notification (if configured)
        if self.config.has_section('EMAIL_NOTIFICATIONS'):
            self.send_email_notification(subject, message)
        
        # Log notification
        self.log_monitoring_event('NOTIFICATION', f"{subject}: {message}")
    
    def send_desktop_notification(self, title, message, notification_type="info"):
        """Send desktop notification"""
        try:
            if os.name == 'nt':  # Windows
                import win10toast
                toaster = win10toast.ToastNotifier()
                icon_path = None
                if notification_type == "warning":
                    icon_path = "warning.ico"
                elif notification_type == "error":
                    icon_path = "error.ico"
                toaster.show_toast(title, message, icon_path=icon_path, duration=10)
            else:  # Linux/Mac
                os.system(f'notify-send "{title}" "{message}"')
        except Exception as e:
            print(f"Desktop notification failed: {e}")
    
    def send_email_notification(self, subject, message):
        """Send email notification"""
        try:
            smtp_server = self.config.get('EMAIL_NOTIFICATIONS', 'smtp_server')
            smtp_port = self.config.getint('EMAIL_NOTIFICATIONS', 'smtp_port')
            username = self.config.get('EMAIL_NOTIFICATIONS', 'username')
            password = self.config.get('EMAIL_NOTIFICATIONS', 'password')
            to_email = self.config.get('EMAIL_NOTIFICATIONS', 'to_email')
            
            msg = MIMEMultipart()
            msg['From'] = username
            msg['To'] = to_email
            msg['Subject'] = f"Engwe Monitor: {subject}"
            
            body = f"""
{message}

---
Engwe Product Monitor
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Store: nlebike.com
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            text = msg.as_string()
            server.sendmail(username, to_email, text)
            server.quit()
            
            print("Email notification sent successfully")
        except Exception as e:
            print(f"Email notification failed: {e}")
    
    def detect_new_products(self, current_products):
        """Detect new products that weren't in previous scan"""
        new_products = []
        current_handles = {p.get('handle', p.get('title', '')) for p in current_products}
        previous_handles = set(self.previous_products.keys())
        
        for product in current_products:
            handle = product.get('handle', product.get('title', ''))
            if handle not in previous_handles:
                new_products.append(product)
        
        return new_products
    
    def detect_stock_changes(self, current_products):
        """Detect products with low stock or out of stock"""
        low_stock_threshold = self.config.getint('MONITORING', 'low_stock_threshold', fallback=5)
        stock_alerts = []
        
        for product in current_products:
            handle = product.get('handle', product.get('title', ''))
            current_stock = product.get('inventory_quantity', 0)
            current_available = product.get('available', True)
            
            # Check if we have previous data for this product
            if handle in self.previous_products:
                previous_data = self.previous_products[handle]
                previous_stock = previous_data.get('inventory_quantity', 0)
                previous_available = previous_data.get('available', True)
                
                # Stock went from available to unavailable
                if previous_available and not current_available:
                    stock_alerts.append({
                        'type': 'OUT_OF_STOCK',
                        'product': product,
                        'message': f"Product went out of stock: {product.get('title', 'Unknown')}"
                    })
                
                # Stock dropped below threshold
                elif current_stock <= low_stock_threshold and previous_stock > low_stock_threshold:
                    stock_alerts.append({
                        'type': 'LOW_STOCK',
                        'product': product,
                        'message': f"Low stock alert: {product.get('title', 'Unknown')} - Only {current_stock} left"
                    })
                
                # Significant stock drop (>50%)
                elif current_stock < previous_stock * 0.5 and previous_stock > 10:
                    stock_alerts.append({
                        'type': 'STOCK_DROP',
                        'product': product,
                        'message': f"Stock dropped significantly: {product.get('title', 'Unknown')} - From {previous_stock} to {current_stock}"
                    })
        
        return stock_alerts
    
    def scan_for_changes(self):
        """Perform a scan for product and stock changes"""
        try:
            self.log_monitoring_event('SCAN_START', 'Starting product scan')
            
            # Get current products
            importer = EngweProductImporter()
            product_urls = importer.get_all_product_urls()
            
            current_products = []
            for url in product_urls:
                product_data = importer.scrape_product_data(url)
                if product_data:
                    current_products.append(product_data)
            
            self.log_monitoring_event('SCAN_COMPLETE', f'Scanned {len(current_products)} products')
            
            # Detect new products
            new_products = self.detect_new_products(current_products)
            if new_products:
                for product in new_products:
                    title = product.get('title', 'Unknown Product')
                    price = product.get('price', 'Unknown')
                    self.send_notification(
                        "🆕 New Product Alert",
                        f"New product found on engwe.com:\n\n{title}\nPrice: ${price}\n\nReady to import to your store!",
                        "info"
                    )
                
                self.log_monitoring_event('NEW_PRODUCTS', f'Found {len(new_products)} new products', 
                                         {'products': [p.get('title', '') for p in new_products]})
            
            # Detect stock changes
            stock_alerts = self.detect_stock_changes(current_products)
            if stock_alerts:
                for alert in stock_alerts:
                    notification_type = "warning" if alert['type'] in ['LOW_STOCK', 'STOCK_DROP'] else "error"
                    self.send_notification(
                        f"⚠️ Stock Alert - {alert['type']}",
                        alert['message'],
                        notification_type
                    )
                
                self.log_monitoring_event('STOCK_ALERTS', f'Generated {len(stock_alerts)} stock alerts',
                                         {'alerts': [a['message'] for a in stock_alerts]})
            
            # Save current state for next comparison
            self.save_current_products(current_products)
            
            # Summary notification if configured
            if self.config.getboolean('MONITORING', 'send_summary_notifications', fallback=False):
                if new_products or stock_alerts:
                    summary = f"Monitoring Summary:\n\n"
                    summary += f"• {len(new_products)} new products found\n"
                    summary += f"• {len(stock_alerts)} stock alerts generated\n"
                    summary += f"• {len(current_products)} total products monitored"
                    
                    self.send_notification("📊 Monitoring Summary", summary)
            
            return {
                'success': True,
                'new_products': len(new_products),
                'stock_alerts': len(stock_alerts),
                'total_products': len(current_products)
            }
            
        except Exception as e:
            error_msg = f"Monitoring scan failed: {str(e)}"
            self.log_monitoring_event('ERROR', error_msg)
            self.send_notification("❌ Monitoring Error", error_msg, "error")
            return {'success': False, 'error': str(e)}
    
    def start_monitoring(self):
        """Start the monitoring service"""
        if self.monitoring_active:
            print("Monitoring is already active")
            return
        
        self.monitoring_active = True
        
        # Get monitoring interval from config
        check_interval = self.config.getint('MONITORING', 'check_interval_hours', fallback=4)
        
        # Schedule monitoring
        schedule.every(check_interval).hours.do(self.scan_for_changes)
        
        # Initial scan
        print(f"🚀 Starting Engwe Product Monitor")
        print(f"📅 Checking every {check_interval} hours")
        print(f"🔔 Notifications enabled")
        
        self.send_notification(
            "🚀 Monitor Started",
            f"Engwe product monitoring is now active.\nChecking every {check_interval} hours for new products and stock changes."
        )
        
        # Perform initial scan
        self.scan_for_changes()
        
        # Keep monitoring
        try:
            while self.monitoring_active:
                schedule.run_pending()
                time.sleep(60)  # Check every minute for scheduled tasks
        except KeyboardInterrupt:
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """Stop the monitoring service"""
        self.monitoring_active = False
        schedule.clear()
        print("\n🛑 Monitoring stopped")
        self.send_notification(
            "🛑 Monitor Stopped",
            "Engwe product monitoring has been stopped."
        )
        self.log_monitoring_event('MONITOR_STOPPED', 'Monitoring service stopped')
    
    def get_monitoring_status(self):
        """Get current monitoring status and statistics"""
        status = {
            'active': self.monitoring_active,
            'total_products_tracked': len(self.previous_products),
            'last_scan': None,
            'recent_alerts': []
        }
        
        # Get last scan time from log
        if os.path.exists(self.monitoring_log_file):
            with open(self.monitoring_log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
                
            # Find last scan
            for entry in reversed(log_data):
                if entry['type'] == 'SCAN_COMPLETE':
                    status['last_scan'] = entry['timestamp']
                    break
            
            # Get recent alerts (last 24 hours)
            recent_time = datetime.now() - timedelta(hours=24)
            for entry in reversed(log_data):
                entry_time = datetime.fromisoformat(entry['timestamp'])
                if entry_time > recent_time and entry['type'] in ['NEW_PRODUCTS', 'STOCK_ALERTS']:
                    status['recent_alerts'].append(entry)
        
        return status

def main():
    monitor = EngweMonitor()
    
    import sys
    if '--status' in sys.argv:
        status = monitor.get_monitoring_status()
        print(f"Monitoring Status: {'Active' if status['active'] else 'Inactive'}")
        print(f"Products Tracked: {status['total_products_tracked']}")
        print(f"Last Scan: {status['last_scan'] or 'Never'}")
        print(f"Recent Alerts: {len(status['recent_alerts'])}")
    elif '--scan' in sys.argv:
        print("Performing manual scan...")
        result = monitor.scan_for_changes()
        print(f"Scan result: {result}")
    elif '--stop' in sys.argv:
        monitor.stop_monitoring()
    else:
        # Start monitoring
        monitor.start_monitoring()

if __name__ == "__main__":
    main()