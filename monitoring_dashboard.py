#!/usr/bin/env python3
"""
Monitoring Dashboard
Provides a visual overview of monitoring status and recent activity
"""

import os
import json
from datetime import datetime, timedelta
from engwe_monitor import EngweMonitor

def create_dashboard_html():
    """Create an HTML dashboard showing monitoring status"""
    monitor = EngweMonitor()
    status = monitor.get_monitoring_status()
    
    # Get detailed statistics
    total_products = status['total_products_tracked']
    last_scan = status['last_scan']
    recent_alerts = status['recent_alerts']
    
    # Load recent log entries
    log_entries = []
    if os.path.exists('monitoring_log.json'):
        with open('monitoring_log.json', 'r', encoding='utf-8') as f:
            all_logs = json.load(f)
            log_entries = all_logs[-20:]  # Last 20 entries
    
    # Calculate stats
    new_products_today = len([alert for alert in recent_alerts if alert['type'] == 'NEW_PRODUCTS'])
    stock_alerts_today = len([alert for alert in recent_alerts if alert['type'] == 'STOCK_ALERTS'])
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Engwe Monitor Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
            padding: 2rem;
        }}
        
        .dashboard {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 2rem;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .status-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .status-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .status-card.active {{
            border-left: 4px solid #4caf50;
        }}
        
        .status-card.inactive {{
            border-left: 4px solid #f44336;
        }}
        
        .status-number {{
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }}
        
        .status-number.green {{ color: #4caf50; }}
        .status-number.orange {{ color: #ff9800; }}
        .status-number.red {{ color: #f44336; }}
        .status-number.blue {{ color: #2196f3; }}
        
        .status-label {{
            color: #666;
            font-size: 1rem;
            margin-bottom: 0.5rem;
        }}
        
        .status-detail {{
            font-size: 0.9rem;
            color: #999;
        }}
        
        .content-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
        }}
        
        .panel {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .panel h3 {{
            color: #333;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .log-entry {{
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 6px;
            border-left: 3px solid #ddd;
            background: #f9f9f9;
        }}
        
        .log-entry.info {{ border-left-color: #2196f3; }}
        .log-entry.warning {{ border-left-color: #ff9800; }}
        .log-entry.error {{ border-left-color: #f44336; }}
        .log-entry.success {{ border-left-color: #4caf50; }}
        
        .log-time {{
            font-size: 0.8rem;
            color: #666;
            margin-bottom: 0.3rem;
        }}
        
        .log-message {{
            font-size: 0.9rem;
        }}
        
        .actions {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-top: 2rem;
            text-align: center;
        }}
        
        .btn {{
            display: inline-block;
            padding: 0.75rem 1.5rem;
            margin: 0.5rem;
            border: none;
            border-radius: 6px;
            font-size: 1rem;
            text-decoration: none;
            cursor: pointer;
            transition: transform 0.2s ease;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
        }}
        
        .btn-primary {{
            background: #667eea;
            color: white;
        }}
        
        .btn-success {{
            background: #4caf50;
            color: white;
        }}
        
        .btn-warning {{
            background: #ff9800;
            color: white;
        }}
        
        .auto-refresh {{
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255,255,255,0.9);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.8rem;
            color: #666;
        }}
        
        @media (max-width: 768px) {{
            .content-grid {{
                grid-template-columns: 1fr;
            }}
            
            body {{
                padding: 1rem;
            }}
        }}
    </style>
    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => {{
            location.reload();
        }}, 30000);
    </script>
</head>
<body>
    <div class="auto-refresh">
        🔄 Auto-refresh: 30s
    </div>
    
    <div class="dashboard">
        <div class="header">
            <h1>📊 Engwe Monitor Dashboard</h1>
            <p>Real-time monitoring of engwe.com products</p>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card {'active' if status['active'] else 'inactive'}">
                <div class="status-number {'green' if status['active'] else 'red'}">
                    {'ACTIVE' if status['active'] else 'INACTIVE'}
                </div>
                <div class="status-label">Monitor Status</div>
                <div class="status-detail">
                    {'Running continuously' if status['active'] else 'Not running'}
                </div>
            </div>
            
            <div class="status-card">
                <div class="status-number blue">{total_products}</div>
                <div class="status-label">Products Tracked</div>
                <div class="status-detail">From engwe.com</div>
            </div>
            
            <div class="status-card">
                <div class="status-number orange">{new_products_today}</div>
                <div class="status-label">New Products (24h)</div>
                <div class="status-detail">Ready to import</div>
            </div>
            
            <div class="status-card">
                <div class="status-number {'red' if stock_alerts_today > 0 else 'green'}">{stock_alerts_today}</div>
                <div class="status-label">Stock Alerts (24h)</div>
                <div class="status-detail">{'Attention needed' if stock_alerts_today > 0 else 'All good'}</div>
            </div>
        </div>
        
        <div class="content-grid">
            <div class="panel">
                <h3>🔔 Recent Alerts</h3>
"""
    
    if recent_alerts:
        for alert in recent_alerts[-5:]:  # Last 5 alerts
            alert_type = alert['type']
            alert_class = 'warning' if alert_type in ['LOW_STOCK', 'STOCK_DROP'] else 'info'
            if alert_type == 'NEW_PRODUCTS':
                alert_class = 'success'
            
            alert_time = datetime.fromisoformat(alert['timestamp']).strftime('%H:%M')
            
            html_content += f"""
                <div class="log-entry {alert_class}">
                    <div class="log-time">{alert_time}</div>
                    <div class="log-message">{alert['message']}</div>
                </div>
"""
    else:
        html_content += """
                <div class="log-entry info">
                    <div class="log-message">No recent alerts</div>
                </div>
"""
    
    html_content += """
            </div>
            
            <div class="panel">
                <h3>📋 Activity Log</h3>
"""
    
    if log_entries:
        for entry in reversed(log_entries[-10:]):  # Last 10 log entries
            entry_type = entry['type'].lower()
            entry_class = 'info'
            if 'error' in entry_type:
                entry_class = 'error'
            elif 'scan_complete' in entry_type:
                entry_class = 'success'
            elif 'alert' in entry_type:
                entry_class = 'warning'
            
            entry_time = datetime.fromisoformat(entry['timestamp']).strftime('%H:%M')
            
            html_content += f"""
                <div class="log-entry {entry_class}">
                    <div class="log-time">{entry_time}</div>
                    <div class="log-message">{entry['message']}</div>
                </div>
"""
    else:
        html_content += """
                <div class="log-entry info">
                    <div class="log-message">No activity logged yet</div>
                </div>
"""
    
    html_content += f"""
            </div>
        </div>
        
        <div class="actions">
            <h3>🎯 Quick Actions</h3>
            <p>Management commands - run these in your terminal:</p>
            <br>
            <div>
                <span class="btn btn-success">python engwe_monitor.py --scan</span>
                <span style="margin: 0 1rem; color: #666;">→ Manual scan now</span>
            </div>
            <div>
                <span class="btn btn-primary">step1_fetch.bat</span>
                <span style="margin: 0 1rem; color: #666;">→ Import new products</span>
            </div>
            <div>
                <span class="btn btn-warning">python engwe_monitor.py --status</span>
                <span style="margin: 0 1rem; color: #666;">→ Detailed status</span>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    with open('monitoring_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Dashboard created: monitoring_dashboard.html")
    return 'monitoring_dashboard.html'

def main():
    dashboard_file = create_dashboard_html()
    
    # Open dashboard in browser
    import webbrowser
    import os
    webbrowser.open(f"file://{os.path.abspath(dashboard_file)}")
    
    print(f"Dashboard opened in browser: {dashboard_file}")
    print("Dashboard will auto-refresh every 30 seconds")

if __name__ == "__main__":
    main()