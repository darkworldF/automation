// Main JavaScript for Engwe Monitor Web App

class EngweMonitorApp {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.init();
    }

    init() {
        this.initializeSocket();
        this.setupEventListeners();
        this.startHeartbeat();
    }

    initializeSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.isConnected = true;
            this.updateConnectionStatus(true);
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.isConnected = false;
            this.updateConnectionStatus(false);
        });

        this.socket.on('reconnect', () => {
            console.log('Reconnected to server');
            this.isConnected = true;
            this.updateConnectionStatus(true);
            this.refreshData();
        });

        // Listen for specific events
        this.socket.on('scan_status', (data) => this.handleScanStatus(data));
        this.socket.on('scan_progress', (data) => this.handleScanProgress(data));
        this.socket.on('new_product', (data) => this.handleNewProduct(data));
        this.socket.on('monitor_status', (data) => this.handleMonitorStatus(data));
        this.socket.on('log_update', (data) => this.handleLogUpdate(data));
    }

    setupEventListeners() {
        // Auto-refresh dashboard data
        setInterval(() => {
            if (this.isConnected) {
                this.refreshDashboardData();
            }
        }, 30000); // Every 30 seconds

        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && this.isConnected) {
                this.refreshData();
            }
        });
    }

    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('connection-status');
        if (statusEl) {
            if (connected) {
                statusEl.innerHTML = '<i class="fas fa-circle text-success me-1"></i>Connected';
            } else {
                statusEl.innerHTML = '<i class="fas fa-circle text-danger me-1"></i>Disconnected';
            }
        }
    }

    handleScanStatus(data) {
        console.log('Scan status:', data);
        const progressEl = document.getElementById('scan-progress');
        
        if (progressEl) {
            if (data.status === 'scanning') {
                progressEl.textContent = 'Scanning';
                progressEl.parentElement.className = 'card bg-warning text-white';
            } else if (data.status === 'complete') {
                progressEl.textContent = 'Complete';
                progressEl.parentElement.className = 'card bg-success text-white';
                setTimeout(() => {
                    progressEl.textContent = 'Ready';
                    progressEl.parentElement.className = 'card bg-warning text-white';
                    this.refreshDashboardData();
                }, 3000);
            } else if (data.status === 'error') {
                progressEl.textContent = 'Error';
                progressEl.parentElement.className = 'card bg-danger text-white';
                setTimeout(() => {
                    progressEl.textContent = 'Ready';
                    progressEl.parentElement.className = 'card bg-warning text-white';
                }, 5000);
            }
        }

        // Update scan modal if open
        const scanModal = document.getElementById('scanModal');
        if (scanModal && scanModal.classList.contains('show')) {
            const messageEl = document.getElementById('scan-message');
            if (messageEl) {
                messageEl.textContent = data.message;
            }

            if (data.status === 'complete' || data.status === 'error') {
                setTimeout(() => {
                    const modalInstance = bootstrap.Modal.getInstance(scanModal);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                }, 2000);
            }
        }

        // Show toast notification
        if (data.status === 'complete') {
            this.showToast('Scan Complete', data.message, 'success');
        } else if (data.status === 'error') {
            this.showToast('Scan Error', data.message, 'error');
        }
    }

    handleScanProgress(data) {
        const progressBar = document.getElementById('scan-progress-bar');
        if (progressBar) {
            const percentage = (data.current / data.total) * 100;
            progressBar.style.width = percentage + '%';
            progressBar.textContent = `${data.current}/${data.total}`;
        }
    }

    handleNewProduct(product) {
        console.log('New product detected:', product);
        
        // Show notification
        const message = `${product.title} - $${product.price}`;
        this.showToast('🆕 New Product Found!', message, 'success');
        
        // Update new products counter
        const newProductsEl = document.getElementById('new-products-24h');
        if (newProductsEl) {
            const current = parseInt(newProductsEl.textContent) || 0;
            newProductsEl.textContent = current + 1;
        }
        
        // Add pulse animation to new products card
        const newProductsCard = newProductsEl?.closest('.card');
        if (newProductsCard) {
            newProductsCard.classList.add('animate-pulse');
            setTimeout(() => {
                newProductsCard.classList.remove('animate-pulse');
            }, 3000);
        }
    }

    handleMonitorStatus(data) {
        const statusEl = document.getElementById('monitor-status');
        const iconEl = document.getElementById('monitor-icon');
        
        if (statusEl && iconEl) {
            if (data.active) {
                statusEl.textContent = 'ON';
                statusEl.parentElement.parentElement.className = 'card bg-success text-white';
                iconEl.className = 'fas fa-radar fa-2x opacity-75';
            } else {
                statusEl.textContent = 'OFF';
                statusEl.parentElement.parentElement.className = 'card bg-info text-white';
                iconEl.className = 'fas fa-radar fa-2x opacity-75';
            }
        }

        // Update control buttons
        const startBtn = document.getElementById('btn-start-monitor');
        const stopBtn = document.getElementById('btn-stop-monitor');
        
        if (startBtn && stopBtn) {
            if (data.active) {
                startBtn.disabled = true;
                stopBtn.disabled = false;
            } else {
                startBtn.disabled = false;
                stopBtn.disabled = true;
            }
        }
    }

    handleLogUpdate(logData) {
        console.log('Log update:', logData);
        
        const logContainer = document.getElementById('activity-log');
        if (!logContainer) return;

        const logEntry = document.createElement('div');
        logEntry.className = 'list-group-item animate-fade-in';
        
        const iconClass = this.getLogIconClass(logData.type);
        const timestamp = new Date(logData.timestamp).toLocaleTimeString();
        
        logEntry.innerHTML = `
            <div class="d-flex justify-content-between">
                <div>
                    <i class="fas fa-${iconClass} me-2"></i>
                    <small>${logData.message}</small>
                </div>
                <small class="text-muted">${timestamp}</small>
            </div>
        `;
        
        logContainer.insertBefore(logEntry, logContainer.firstChild);
        
        // Keep only last 10 entries
        while (logContainer.children.length > 10) {
            logContainer.removeChild(logContainer.lastChild);
        }
    }

    getLogIconClass(eventType) {
        const iconMap = {
            'SCAN_COMPLETE': 'check-circle text-success',
            'SCAN_START': 'info-circle text-info',
            'NEW_PRODUCTS': 'plus-circle text-success',
            'STOCK_ALERTS': 'exclamation-triangle text-warning',
            'ERROR': 'times-circle text-danger',
            'MONITOR_START': 'play-circle text-success',
            'MONITOR_STOP': 'stop-circle text-warning'
        };
        return iconMap[eventType] || 'info-circle text-info';
    }

    refreshData() {
        this.refreshDashboardData();
        this.socket.emit('request_status');
    }

    refreshDashboardData() {
        fetch('/api/dashboard')
            .then(response => response.json())
            .then(data => {
                this.updateDashboardStats(data);
            })
            .catch(error => {
                console.error('Error refreshing dashboard:', error);
            });
    }

    updateDashboardStats(data) {
        const elements = {
            'total-products': data.total_products,
            'new-products-24h': data.new_products_24h
        };

        Object.entries(elements).forEach(([id, value]) => {
            const el = document.getElementById(id);
            if (el && el.textContent !== value.toString()) {
                el.textContent = value;
                el.classList.add('animate-pulse');
                setTimeout(() => el.classList.remove('animate-pulse'), 1000);
            }
        });

        // Update monitor status
        this.handleMonitorStatus({ active: data.monitoring_active });
    }

    showToast(title, message, type = 'info', duration = 5000) {
        const toastContainer = this.getOrCreateToastContainer();
        const toastId = 'toast-' + Date.now();
        
        const toastEl = document.createElement('div');
        toastEl.id = toastId;
        toastEl.className = 'toast';
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('data-bs-autohide', 'true');
        toastEl.setAttribute('data-bs-delay', duration.toString());
        
        const iconClasses = {
            'success': 'fas fa-check-circle text-success',
            'warning': 'fas fa-exclamation-triangle text-warning',
            'error': 'fas fa-times-circle text-danger',
            'info': 'fas fa-info-circle text-info'
        };
        
        toastEl.innerHTML = `
            <div class="toast-header">
                <i class="${iconClasses[type]} me-2"></i>
                <strong class="me-auto">${title}</strong>
                <small class="text-muted">now</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        `;
        
        toastContainer.appendChild(toastEl);
        
        const toast = new bootstrap.Toast(toastEl);
        toast.show();
        
        // Remove toast element after it's hidden
        toastEl.addEventListener('hidden.bs.toast', () => {
            toastEl.remove();
        });
    }

    getOrCreateToastContainer() {
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(container);
        }
        return container;
    }

    startHeartbeat() {
        setInterval(() => {
            if (this.socket && this.socket.connected) {
                this.socket.emit('ping');
            }
        }, 30000); // Every 30 seconds
    }

    // API Methods
    async startScan() {
        try {
            const response = await fetch('/api/scan', { method: 'POST' });
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Scan error:', error);
            this.showToast('Error', 'Failed to start scan', 'error');
            return { success: false, error: error.message };
        }
    }

    async startMonitoring() {
        try {
            const response = await fetch('/api/monitor/start', { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                this.showToast('Monitor Started', 'Background monitoring is now active', 'success');
            }
            return data;
        } catch (error) {
            console.error('Monitor start error:', error);
            this.showToast('Error', 'Failed to start monitoring', 'error');
            return { success: false, error: error.message };
        }
    }

    async stopMonitoring() {
        try {
            const response = await fetch('/api/monitor/stop', { method: 'POST' });
            const data = await response.json();
            if (data.success) {
                this.showToast('Monitor Stopped', 'Background monitoring has been stopped', 'warning');
            }
            return data;
        } catch (error) {
            console.error('Monitor stop error:', error);
            this.showToast('Error', 'Failed to stop monitoring', 'error');
            return { success: false, error: error.message };
        }
    }
}

// Global app instance
let app;

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    app = new EngweMonitorApp();
});

// Global functions for button handlers
function startScan() {
    const scanModal = new bootstrap.Modal(document.getElementById('scanModal'));
    scanModal.show();
    app.startScan();
}

function startMonitoring() {
    app.startMonitoring();
}

function stopMonitoring() {
    app.stopMonitoring();
}

function refreshDashboard() {
    app.refreshData();
    app.showToast('Dashboard Updated', 'Data refreshed successfully', 'info');
}

function exportProducts() {
    app.showToast('Export Started', 'Preparing product export...', 'info');
    // TODO: Implement export functionality
}

// Utility functions
function toggleView() {
    const icon = document.getElementById('view-toggle-icon');
    const container = document.getElementById('products-grid');
    
    if (container.classList.contains('row')) {
        // Switch to list view
        icon.className = 'fas fa-th';
        container.className = 'list-group list-group-flush p-3';
    } else {
        // Switch to grid view
        icon.className = 'fas fa-list';
        container.className = 'row g-3 p-3';
    }
}