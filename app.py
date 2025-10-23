from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import os
import json
import sqlite3
from datetime import datetime, timedelta
import threading
import time
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import requests
from bs4 import BeautifulSoup
import schedule

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
socketio = SocketIO(app, cors_allowed_origins="*")

# Database setup
def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('engwe_monitor.db')
    cursor = conn.cursor()
    
    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            handle TEXT UNIQUE,
            title TEXT,
            price REAL,
            available BOOLEAN,
            inventory_quantity INTEGER,
            variants_count INTEGER,
            url TEXT,
            image_url TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Monitoring logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monitoring_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT,
            message TEXT,
            details TEXT
        )
    ''')
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Import history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS import_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            product_count INTEGER,
            success_count INTEGER,
            failed_count INTEGER,
            status TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

class EngweWebMonitor:
    def __init__(self):
        self.monitoring_active = False
        self.monitoring_thread = None
        
    def get_db_connection(self):
        """Get database connection"""
        conn = sqlite3.connect('engwe_monitor.db')
        conn.row_factory = sqlite3.Row
        return conn
    
    def log_event(self, event_type, message, details=None):
        """Log monitoring event to database"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO monitoring_logs (event_type, message, details) VALUES (?, ?, ?)",
            (event_type, message, json.dumps(details) if details else None)
        )
        conn.commit()
        conn.close()
        
        # Emit to web clients
        socketio.emit('log_update', {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'message': message
        })
    
    def get_all_product_urls(self):
        """Get all product URLs from engwe.com sitemap"""
        try:
            sitemap_url = "https://engwe.com/sitemap_products_1.xml"
            response = requests.get(sitemap_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            urls = [loc.text for loc in soup.find_all('loc') if '/products/' in loc.text]
            
            return urls
        except Exception as e:
            self.log_event('ERROR', f'Failed to fetch product URLs: {str(e)}')
            return []
    
    def scrape_product_data(self, url):
        """Scrape product data from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find product JSON data
            product_script = soup.find('script', string=lambda text: text and 'product:' in text)
            if not product_script:
                return None
            
            # Extract JSON data
            script_content = product_script.string
            start_index = script_content.find('product:') + 8
            end_index = script_content.find(',\n', start_index)
            if end_index == -1:
                end_index = script_content.find('}', start_index) + 1
            
            product_json = script_content[start_index:end_index].strip()
            if product_json.endswith(','):
                product_json = product_json[:-1]
            
            product_data = json.loads(product_json)
            
            # Process product data
            processed_data = {
                'handle': product_data.get('handle', ''),
                'title': product_data.get('title', ''),
                'price': float(product_data.get('price', 0)) / 100,  # Shopify stores in cents
                'available': product_data.get('available', False),
                'inventory_quantity': sum(variant.get('inventory_quantity', 0) for variant in product_data.get('variants', [])),
                'variants_count': len(product_data.get('variants', [])),
                'url': url,
                'image_url': f"https:{product_data['featured_image']}" if product_data.get('featured_image') else None,
                'description': soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else '',
                'vendor': product_data.get('vendor', 'ENGWE')
            }
            
            return processed_data
            
        except Exception as e:
            self.log_event('ERROR', f'Failed to scrape {url}: {str(e)}')
            return None
    
    def scan_for_changes(self):
        """Scan for product changes"""
        try:
            self.log_event('SCAN_START', 'Starting product scan')
            socketio.emit('scan_status', {'status': 'scanning', 'message': 'Scanning engwe.com for products...'})
            
            # Get current products
            product_urls = self.get_all_product_urls()
            socketio.emit('scan_status', {'status': 'scanning', 'message': f'Found {len(product_urls)} product URLs'})
            
            new_products = []
            updated_products = []
            
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            for i, url in enumerate(product_urls[:50]):  # Limit to first 50 for demo
                socketio.emit('scan_progress', {'current': i + 1, 'total': min(len(product_urls), 50)})
                
                product_data = self.scrape_product_data(url)
                if not product_data:
                    continue
                
                handle = product_data['handle']
                
                # Check if product exists
                existing = cursor.execute(
                    "SELECT * FROM products WHERE handle = ?", (handle,)
                ).fetchone()
                
                if existing:
                    # Check for changes
                    if (existing['price'] != product_data['price'] or 
                        existing['available'] != product_data['available'] or
                        existing['inventory_quantity'] != product_data['inventory_quantity']):
                        
                        # Update existing product
                        cursor.execute(
                            """UPDATE products SET 
                               title=?, price=?, available=?, inventory_quantity=?, 
                               variants_count=?, url=?, image_url=?, last_updated=CURRENT_TIMESTAMP
                               WHERE handle=?""",
                            (product_data['title'], product_data['price'], product_data['available'],
                             product_data['inventory_quantity'], product_data['variants_count'],
                             product_data['url'], product_data['image_url'], handle)
                        )
                        updated_products.append(product_data)
                else:
                    # Insert new product
                    cursor.execute(
                        """INSERT INTO products 
                           (handle, title, price, available, inventory_quantity, variants_count, url, image_url)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (handle, product_data['title'], product_data['price'], product_data['available'],
                         product_data['inventory_quantity'], product_data['variants_count'],
                         product_data['url'], product_data['image_url'])
                    )
                    new_products.append(product_data)
            
            conn.commit()
            conn.close()
            
            # Log results
            self.log_event('SCAN_COMPLETE', f'Scan completed: {len(new_products)} new, {len(updated_products)} updated')
            
            # Emit notifications for new products
            for product in new_products:
                socketio.emit('new_product', {
                    'title': product['title'],
                    'price': product['price'],
                    'image_url': product['image_url'],
                    'url': product['url']
                })
            
            socketio.emit('scan_status', {
                'status': 'complete',
                'message': f'Scan complete: {len(new_products)} new products, {len(updated_products)} updated'
            })
            
            return {
                'success': True,
                'new_products': len(new_products),
                'updated_products': len(updated_products),
                'total_processed': len(product_urls)
            }
            
        except Exception as e:
            error_msg = f'Scan failed: {str(e)}'
            self.log_event('ERROR', error_msg)
            socketio.emit('scan_status', {'status': 'error', 'message': error_msg})
            return {'success': False, 'error': str(e)}
    
    def start_monitoring(self):
        """Start background monitoring"""
        if self.monitoring_active:
            return False
        
        self.monitoring_active = True
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    self.scan_for_changes()
                    # Wait 4 hours between scans
                    for _ in range(240):  # 240 minutes = 4 hours
                        if not self.monitoring_active:
                            break
                        time.sleep(60)  # Sleep 1 minute at a time
                except Exception as e:
                    self.log_event('ERROR', f'Monitoring error: {str(e)}')
                    time.sleep(300)  # Wait 5 minutes before retry
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.log_event('MONITOR_START', 'Background monitoring started')
        socketio.emit('monitor_status', {'active': True})
        return True
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        self.log_event('MONITOR_STOP', 'Background monitoring stopped')
        socketio.emit('monitor_status', {'active': False})
        return True
    
    def get_dashboard_data(self):
        """Get dashboard statistics"""
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Get total products
        total_products = cursor.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        
        # Get new products in last 24 hours
        new_products_24h = cursor.execute(
            "SELECT COUNT(*) FROM products WHERE first_seen >= datetime('now', '-1 day')"
        ).fetchone()[0]
        
        # Get recent logs
        recent_logs = cursor.execute(
            "SELECT * FROM monitoring_logs ORDER BY timestamp DESC LIMIT 10"
        ).fetchall()
        
        # Get all products for display
        all_products = cursor.execute(
            "SELECT * FROM products ORDER BY last_updated DESC LIMIT 50"
        ).fetchall()
        
        conn.close()
        
        return {
            'total_products': total_products,
            'new_products_24h': new_products_24h,
            'monitoring_active': self.monitoring_active,
            'recent_logs': [dict(log) for log in recent_logs],
            'products': [dict(product) for product in all_products]
        }

# Initialize monitor
monitor = EngweWebMonitor()

# Routes
@app.route('/')
def dashboard():
    """Main dashboard"""
    data = monitor.get_dashboard_data()
    return render_template('dashboard.html', **data)

@app.route('/api/scan', methods=['POST'])
def api_scan():
    """Manual scan trigger"""
    result = monitor.scan_for_changes()
    return jsonify(result)

@app.route('/api/monitor/start', methods=['POST'])
def api_start_monitor():
    """Start monitoring"""
    success = monitor.start_monitoring()
    return jsonify({'success': success})

@app.route('/api/monitor/stop', methods=['POST'])
def api_stop_monitor():
    """Stop monitoring"""
    success = monitor.stop_monitoring()
    return jsonify({'success': success})

@app.route('/api/dashboard')
def api_dashboard():
    """Get dashboard data"""
    data = monitor.get_dashboard_data()
    return jsonify(data)

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')

@app.route('/api/settings', methods=['GET', 'POST'])
def api_settings():
    """Handle settings"""
    conn = monitor.get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        settings_data = request.json
        
        for key, value in settings_data.items():
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value)
            )
        
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    else:
        settings_rows = cursor.execute("SELECT key, value FROM settings").fetchall()
        settings_dict = {row['key']: row['value'] for row in settings_rows}
        conn.close()
        return jsonify(settings_dict)

# WebSocket events
@socketio.on('connect')
def handle_connect():
    emit('connected', {'message': 'Connected to Engwe Monitor'})

@socketio.on('request_status')
def handle_status_request():
    data = monitor.get_dashboard_data()
    emit('status_update', data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)