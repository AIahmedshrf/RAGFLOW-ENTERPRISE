"""
Real-time Service Monitoring with WebSocket support
Provides live service status updates and alerts
"""
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
from admin.server.admin_server import app
from admin.server.services import ServiceMgr
from admin.server.auth import check_admin_auth
from admin.server.responses import success_response, error_response
from admin.server.routes import admin_bp
import threading
import time
import psutil
from datetime import datetime

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Store service alerts
service_alerts = []
MAX_ALERTS = 100


class ServiceMonitor:
    """Background service monitoring"""
    def __init__(self):
        self.monitoring = False
        self.thread = None
        self.alert_thresholds = {
            'cpu': 80.0,  # CPU usage %
            'memory': 85.0,  # Memory usage %
            'disk': 90.0,  # Disk usage %
        }
    
    def start(self):
        """Start monitoring thread"""
        if not self.monitoring:
            self.monitoring = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop monitoring"""
        self.monitoring = False
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                # Check system resources
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                disk_percent = psutil.disk_usage('/').percent
                
                # Check for alerts
                if cpu_percent > self.alert_thresholds['cpu']:
                    self._create_alert('cpu', f'High CPU usage: {cpu_percent:.1f}%', 'warning')
                
                if memory_percent > self.alert_thresholds['memory']:
                    self._create_alert('memory', f'High memory usage: {memory_percent:.1f}%', 'warning')
                
                if disk_percent > self.alert_thresholds['disk']:
                    self._create_alert('disk', f'High disk usage: {disk_percent:.1f}%', 'critical')
                
                # Check service status
                services = ServiceMgr.get_all_services()
                for service in services:
                    if service.get('status') != 'running':
                        self._create_alert(
                            'service',
                            f"Service {service.get('name')} is {service.get('status')}",
                            'critical'
                        )
                
                # Emit status update via WebSocket
                socketio.emit('service_status_update', {
                    'timestamp': datetime.now().isoformat(),
                    'cpu': cpu_percent,
                    'memory': memory_percent,
                    'disk': disk_percent,
                    'services': services,
                }, room='monitoring')
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(5)
    
    def _create_alert(self, alert_type: str, message: str, severity: str):
        """Create and store alert"""
        global service_alerts
        
        alert = {
            'id': len(service_alerts) + 1,
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat(),
            'acknowledged': False,
        }
        
        service_alerts.insert(0, alert)
        
        # Limit alerts to MAX_ALERTS
        if len(service_alerts) > MAX_ALERTS:
            service_alerts = service_alerts[:MAX_ALERTS]
        
        # Emit alert via WebSocket
        socketio.emit('new_alert', alert, room='monitoring')


# Initialize monitor
service_monitor = ServiceMonitor()


@admin_bp.route('/monitoring/alerts', methods=['GET'])
@check_admin_auth
def get_alerts():
    """Get all service alerts"""
    try:
        return success_response({
            'alerts': service_alerts,
            'total': len(service_alerts),
        })
    except Exception as e:
        return error_response(str(e), 500)


@admin_bp.route('/monitoring/alerts/<int:alert_id>/acknowledge', methods=['POST'])
@check_admin_auth
def acknowledge_alert(alert_id: int):
    """Acknowledge an alert"""
    try:
        for alert in service_alerts:
            if alert['id'] == alert_id:
                alert['acknowledged'] = True
                alert['acknowledged_at'] = datetime.now().isoformat()
                return success_response(alert)
        
        return error_response('Alert not found', 404)
    except Exception as e:
        return error_response(str(e), 500)


@admin_bp.route('/monitoring/alerts/clear', methods=['DELETE'])
@check_admin_auth
def clear_alerts():
    """Clear all acknowledged alerts"""
    try:
        global service_alerts
        service_alerts = [a for a in service_alerts if not a.get('acknowledged')]
        return success_response({'cleared': True})
    except Exception as e:
        return error_response(str(e), 500)


@admin_bp.route('/monitoring/thresholds', methods=['GET'])
@check_admin_auth
def get_thresholds():
    """Get alert thresholds"""
    try:
        return success_response(service_monitor.alert_thresholds)
    except Exception as e:
        return error_response(str(e), 500)


@admin_bp.route('/monitoring/thresholds', methods=['PUT'])
@check_admin_auth
def update_thresholds():
    """Update alert thresholds"""
    try:
        data = request.json
        if 'cpu' in data:
            service_monitor.alert_thresholds['cpu'] = float(data['cpu'])
        if 'memory' in data:
            service_monitor.alert_thresholds['memory'] = float(data['memory'])
        if 'disk' in data:
            service_monitor.alert_thresholds['disk'] = float(data['disk'])
        
        return success_response(service_monitor.alert_thresholds)
    except Exception as e:
        return error_response(str(e), 500)


# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


@socketio.on('join_monitoring')
def handle_join_monitoring():
    """Join monitoring room"""
    join_room('monitoring')
    emit('monitoring_joined', {'status': 'connected'})


@socketio.on('leave_monitoring')
def handle_leave_monitoring():
    """Leave monitoring room"""
    leave_room('monitoring')
    emit('monitoring_left', {'status': 'disconnected'})


# Start monitoring on import
service_monitor.start()
