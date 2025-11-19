"""
Monitoring API Routes
"""
from flask import Blueprint, Response
from devops.monitoring import metrics_collector, health_checker
from api.security import rate_limit


monitoring_bp = Blueprint('monitoring', __name__, url_prefix='/api/v1')


@monitoring_bp.route('/health', methods=['GET'])
@rate_limit('basic')
def health_check():
    """Health check endpoint"""
    health = health_checker.run_all_checks()
    
    status_code = 200 if health['status'] == 'healthy' else 503
    
    return health, status_code


@monitoring_bp.route('/metrics', methods=['GET'])
def prometheus_metrics():
    """Prometheus metrics endpoint"""
    metrics = metrics_collector.get_prometheus_metrics()
    
    return Response(metrics, mimetype='text/plain')


@monitoring_bp.route('/readiness', methods=['GET'])
def readiness_check():
    """Kubernetes readiness probe"""
    # Check if app is ready to accept traffic
    return {'status': 'ready'}, 200


@monitoring_bp.route('/liveness', methods=['GET'])
def liveness_check():
    """Kubernetes liveness probe"""
    # Check if app is alive
    return {'status': 'alive'}, 200
