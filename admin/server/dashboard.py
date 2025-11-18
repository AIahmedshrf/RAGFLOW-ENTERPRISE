"""
Dashboard API endpoints for RAGFlow Admin
Provides metrics, analytics, and activity data
"""
from datetime import datetime, timedelta
from flask import request
from admin.server import app
from admin.server.services import UserMgr, ServiceMgr
from api.db.services.knowledgebase_service import KnowledgebaseService
from api.db.services.dialog_service import DialogService
from api.db.services.document_service import DocumentService
from api.db.services.task_service import TaskService
from api.utils.api_utils import server_error_response, get_json_result
from functools import wraps
import traceback


def admin_auth_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Simple token validation - enhance as needed
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return get_json_result(data=False, code=401, message='Unauthorized')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/api/admin/dashboard/metrics', methods=['GET'])
@admin_auth_required
def get_dashboard_metrics():
    """Get comprehensive dashboard metrics"""
    try:
        # User metrics
        total_users = UserMgr.get_total_user_count()
        active_users_7d = UserMgr.get_active_user_count(days=7)
        
        # Knowledge base metrics
        kb_service = KnowledgebaseService()
        total_kbs = kb_service.get_total_count()
        
        # Conversation metrics
        dialog_service = DialogService()
        total_conversations = dialog_service.get_total_count()
        active_conversations_7d = dialog_service.get_active_count(days=7)
        
        # Document metrics
        doc_service = DocumentService()
        total_documents = doc_service.get_total_count()
        documents_processed_7d = doc_service.get_processed_count(days=7)
        
        # Agent metrics
        from agent.component import component_class
        active_agents = len(component_class)
        
        # Service metrics
        services = ServiceMgr.get_all_services()
        active_services = sum(1 for s in services if s.get('status') == 'running')
        total_services = len(services)
        
        # User activity trend (last 7 days)
        user_activity = []
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            count = UserMgr.get_daily_active_users(date)
            user_activity.append({'date': date, 'count': count})
        
        # API usage trend (last 7 days)
        api_usage = []
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            requests = TaskService.get_daily_request_count(date)
            api_usage.append({'date': date, 'requests': requests})
        
        # Storage usage breakdown
        storage_usage = [
            {'category': 'Documents', 'value': doc_service.get_storage_usage()},
            {'category': 'Embeddings', 'value': kb_service.get_embedding_storage()},
            {'category': 'Chat History', 'value': dialog_service.get_storage_usage()},
            {'category': 'Temp Files', 'value': TaskService.get_temp_storage()},
        ]
        
        # Recent activities
        recent_activities = UserMgr.get_recent_activities(limit=10)
        
        metrics = {
            'totalUsers': total_users,
            'activeUsers7d': active_users_7d,
            'totalKnowledgeBases': total_kbs,
            'totalConversations': total_conversations,
            'activeConversations7d': active_conversations_7d,
            'totalDocuments': total_documents,
            'documentsProcessed7d': documents_processed_7d,
            'activeAgents': active_agents,
            'activeServices': active_services,
            'totalServices': total_services,
            'userActivity': user_activity,
            'apiUsage': api_usage,
            'storageUsage': storage_usage,
            'recentActivities': recent_activities,
        }
        
        return get_json_result(data=metrics)
        
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@app.route('/api/admin/dashboard/stats/users', methods=['GET'])
@admin_auth_required
def get_user_stats():
    """Get detailed user statistics"""
    try:
        days = request.args.get('days', 30, type=int)
        
        stats = {
            'total': UserMgr.get_total_user_count(),
            'active': UserMgr.get_active_user_count(days=days),
            'new': UserMgr.get_new_user_count(days=days),
            'byRole': UserMgr.get_users_by_role(),
            'topActiveUsers': UserMgr.get_top_active_users(limit=10, days=days),
        }
        
        return get_json_result(data=stats)
        
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)


@app.route('/api/admin/dashboard/stats/system', methods=['GET'])
@admin_auth_required
def get_system_stats():
    """Get system resource statistics"""
    try:
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        stats = {
            'cpu': {
                'percent': cpu_percent,
                'count': psutil.cpu_count(),
            },
            'memory': {
                'total': memory.total,
                'available': memory.available,
                'percent': memory.percent,
                'used': memory.used,
            },
            'disk': {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percent': disk.percent,
            },
            'network': {
                'connections': len(psutil.net_connections()),
            }
        }
        
        return get_json_result(data=stats)
        
    except Exception as e:
        traceback.print_exc()
        return server_error_response(e)
