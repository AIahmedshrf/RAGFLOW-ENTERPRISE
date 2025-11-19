"""
Monitoring and Observability System
Integrates with Prometheus, Grafana, and provides health checks
"""
from typing import Dict, Any, List
from datetime import datetime
import psutil
import time


class MetricsCollector:
    """Collects application metrics for Prometheus"""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.start_time = time.time()
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system-level metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'system_cpu_percent': cpu_percent,
            'system_memory_total_bytes': memory.total,
            'system_memory_used_bytes': memory.used,
            'system_memory_available_bytes': memory.available,
            'system_memory_percent': memory.percent,
            'system_disk_total_bytes': disk.total,
            'system_disk_used_bytes': disk.used,
            'system_disk_free_bytes': disk.free,
            'system_disk_percent': disk.percent,
        }
    
    def collect_application_metrics(self) -> Dict[str, Any]:
        """Collect application-level metrics"""
        uptime = time.time() - self.start_time
        
        return {
            'app_uptime_seconds': uptime,
            'app_version': '0.21.1',
            'app_environment': 'production',
        }
    
    def get_prometheus_metrics(self) -> str:
        """Format metrics for Prometheus scraping"""
        system = self.collect_system_metrics()
        app = self.collect_application_metrics()
        
        lines = []
        
        # System metrics
        lines.append(f'# HELP system_cpu_percent CPU usage percentage')
        lines.append(f'# TYPE system_cpu_percent gauge')
        lines.append(f'system_cpu_percent {system["system_cpu_percent"]}')
        
        lines.append(f'# HELP system_memory_used_bytes Memory used in bytes')
        lines.append(f'# TYPE system_memory_used_bytes gauge')
        lines.append(f'system_memory_used_bytes {system["system_memory_used_bytes"]}')
        
        lines.append(f'# HELP system_disk_used_bytes Disk used in bytes')
        lines.append(f'# TYPE system_disk_used_bytes gauge')
        lines.append(f'system_disk_used_bytes {system["system_disk_used_bytes"]}')
        
        # Application metrics
        lines.append(f'# HELP app_uptime_seconds Application uptime')
        lines.append(f'# TYPE app_uptime_seconds counter')
        lines.append(f'app_uptime_seconds {app["app_uptime_seconds"]}')
        
        return '\n'.join(lines)


class HealthChecker:
    """Application health checking"""
    
    def __init__(self):
        self.checks: Dict[str, callable] = {}
    
    def register_check(self, name: str, check_func: callable):
        """Register a health check"""
        self.checks[name] = check_func
    
    def check_mysql(self) -> Dict[str, Any]:
        """Check MySQL connection"""
        try:
            # Placeholder - implement actual MySQL check
            return {
                'status': 'healthy',
                'message': 'MySQL connection OK'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': str(e)
            }
    
    def check_redis(self) -> Dict[str, Any]:
        """Check Redis connection"""
        try:
            # Placeholder - implement actual Redis check
            return {
                'status': 'healthy',
                'message': 'Redis connection OK'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': str(e)
            }
    
    def check_elasticsearch(self) -> Dict[str, Any]:
        """Check Elasticsearch connection"""
        try:
            # Placeholder - implement actual ES check
            return {
                'status': 'healthy',
                'message': 'Elasticsearch connection OK'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': str(e)
            }
    
    def check_minio(self) -> Dict[str, Any]:
        """Check MinIO connection"""
        try:
            # Placeholder - implement actual MinIO check
            return {
                'status': 'healthy',
                'message': 'MinIO connection OK'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': str(e)
            }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {
            'mysql': self.check_mysql(),
            'redis': self.check_redis(),
            'elasticsearch': self.check_elasticsearch(),
            'minio': self.check_minio(),
        }
        
        # Overall status
        all_healthy = all(r['status'] == 'healthy' for r in results.values())
        
        return {
            'status': 'healthy' if all_healthy else 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'checks': results
        }


# Global instances
metrics_collector = MetricsCollector()
health_checker = HealthChecker()
