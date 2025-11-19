#
#  Copyright 2025 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

"""
Admin API endpoints - Proxy to admin.server.routes
This file makes admin routes available in the main Flask app
"""

import logging
from flask import request, jsonify
from flask_login import login_required, current_user
from api.utils.api_utils import get_json_result, server_error_response

# Import admin functions
try:
    import sys
    from pathlib import Path
    admin_path = Path(__file__).parent.parent.parent / "admin" / "server"
    if str(admin_path) not in sys.path:
        sys.path.insert(0, str(admin_path))
    
    from admin.server.services import UserMgr, ServiceMgr
    from admin.server.auth import check_admin_auth
    logging.info("Admin modules imported successfully")
except ImportError as e:
    logging.error(f"Failed to import admin modules: {e}")
    UserMgr = None
    ServiceMgr = None
    check_admin_auth = lambda f: f


@manager.route('/admin/dashboard/metrics', methods=['GET'])
@login_required
def get_dashboard_metrics():
    """Get comprehensive dashboard metrics"""
    try:
        if not UserMgr:
            return server_error_response("Admin module not available")
        
        # Get user stats
        total_users = UserMgr.get_total_users()
        active_users_24h = UserMgr.get_active_users(hours=24)
        active_users_7d = UserMgr.get_active_users(days=7)
        
        # Get service stats
        services = ServiceMgr.get_all_services() if ServiceMgr else []
        active_services = len([s for s in services if s.get('status') == 'running'])
        total_services = len(services)
        
        metrics = {
            'totalUsers': total_users,
            'activeUsers24h': active_users_24h,
            'activeUsers7d': active_users_7d,
            'activeServices': active_services,
            'totalServices': total_services,
            'totalKnowledgeBases': 0,
            'totalConversations': 0,
            'activeConversations7d': 0,
            'totalDocuments': 0,
            'documentsProcessed7d': 0,
            'activeAgents': 0,
            'userActivity': [],
            'apiUsage': [],
            'storageUsage': [],
            'recentActivities': [],
        }
        
        return get_json_result(data=metrics)
        
    except Exception as e:
        logging.error(f"get_dashboard_metrics error: {e}")
        return server_error_response(str(e))


@manager.route('/admin/users', methods=['GET'])
@login_required
def list_users():
    """Get all users"""
    try:
        if not UserMgr:
            return server_error_response("Admin module not available")
        
        result = UserMgr.get_all_users()
        return get_json_result(data=result)
    except Exception as e:
        logging.error(f"list_users error: {e}")
        return server_error_response(str(e))


@manager.route('/admin/services', methods=['GET'])
@login_required
def get_services():
    """Get all services"""
    try:
        if not ServiceMgr:
            return server_error_response("Admin module not available")
        
        services = ServiceMgr.get_all_services()
        return get_json_result(data=services)
    except Exception as e:
        logging.error(f"get_services error: {e}")
        return server_error_response(str(e))


@manager.route('/admin/system/version', methods=['GET'])
def get_system_version():
    """Get system version - no auth required"""
    try:
        from api.versions import get_ragflow_version
        return get_json_result(data={'version': get_ragflow_version()})
    except Exception as e:
        logging.error(f"get_system_version error: {e}")
        return server_error_response(str(e))
