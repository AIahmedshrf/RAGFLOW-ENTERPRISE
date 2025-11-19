"""
Audit logging system for admin actions
Tracks all administrative operations for security and compliance
"""
from datetime import datetime
from typing import Optional, Dict, Any
import json
from functools import wraps
from flask import request
from flask_login import current_user


class AuditLog:
    """In-memory audit log storage (should be moved to database in production)"""
    
    logs = []
    MAX_LOGS = 10000
    
    @classmethod
    def add_log(cls, action: str, resource_type: str, resource_id: str,
                details: Optional[Dict[str, Any]] = None, 
                user_email: Optional[str] = None,
                status: str = 'success'):
        """Add an audit log entry"""
        log_entry = {
            'id': len(cls.logs) + 1,
            'timestamp': datetime.now().isoformat(),
            'user': user_email or (current_user.email if current_user and hasattr(current_user, 'email') else 'system'),
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'status': status,
            'details': details or {},
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.user_agent.string if request and request.user_agent else None,
        }
        
        cls.logs.insert(0, log_entry)
        
        # Limit logs to MAX_LOGS
        if len(cls.logs) > cls.MAX_LOGS:
            cls.logs = cls.logs[:cls.MAX_LOGS]
        
        return log_entry
    
    @classmethod
    def get_logs(cls, limit: int = 100, offset: int = 0,
                 action: Optional[str] = None,
                 resource_type: Optional[str] = None,
                 user_email: Optional[str] = None,
                 start_date: Optional[str] = None,
                 end_date: Optional[str] = None):
        """Retrieve audit logs with filtering"""
        filtered_logs = cls.logs
        
        # Apply filters
        if action:
            filtered_logs = [log for log in filtered_logs if log['action'] == action]
        
        if resource_type:
            filtered_logs = [log for log in filtered_logs if log['resource_type'] == resource_type]
        
        if user_email:
            filtered_logs = [log for log in filtered_logs if log['user'] == user_email]
        
        if start_date:
            filtered_logs = [log for log in filtered_logs if log['timestamp'] >= start_date]
        
        if end_date:
            filtered_logs = [log for log in filtered_logs if log['timestamp'] <= end_date]
        
        # Apply pagination
        total = len(filtered_logs)
        paginated_logs = filtered_logs[offset:offset + limit]
        
        return {
            'logs': paginated_logs,
            'total': total,
            'limit': limit,
            'offset': offset,
        }
    
    @classmethod
    def get_stats(cls):
        """Get audit log statistics"""
        if not cls.logs:
            return {
                'total_actions': 0,
                'actions_by_type': {},
                'actions_by_user': {},
                'recent_activity': [],
            }
        
        actions_by_type = {}
        actions_by_user = {}
        
        for log in cls.logs:
            # Count by action type
            action = log['action']
            actions_by_type[action] = actions_by_type.get(action, 0) + 1
            
            # Count by user
            user = log['user']
            actions_by_user[user] = actions_by_user.get(user, 0) + 1
        
        return {
            'total_actions': len(cls.logs),
            'actions_by_type': actions_by_type,
            'actions_by_user': actions_by_user,
            'recent_activity': cls.logs[:10],
        }


def audit_log(action: str, resource_type: str):
    """Decorator to automatically log admin actions"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Extract resource_id from kwargs or args
            resource_id = kwargs.get('username') or kwargs.get('user_name') or \
                         kwargs.get('service_id') or kwargs.get('role_name') or 'unknown'
            
            try:
                result = f(*args, **kwargs)
                
                # Log successful action
                AuditLog.add_log(
                    action=action,
                    resource_type=resource_type,
                    resource_id=str(resource_id),
                    details={'args': str(args), 'kwargs': str(kwargs)},
                    status='success'
                )
                
                return result
                
            except Exception as e:
                # Log failed action
                AuditLog.add_log(
                    action=action,
                    resource_type=resource_type,
                    resource_id=str(resource_id),
                    details={'error': str(e), 'args': str(args), 'kwargs': str(kwargs)},
                    status='failed'
                )
                raise
        
        return wrapped
    return decorator


# Export decorator and class
__all__ = ['AuditLog', 'audit_log']
