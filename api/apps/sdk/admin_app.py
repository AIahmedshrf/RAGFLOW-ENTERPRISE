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
Admin API endpoints - Enterprise Edition
"""

import logging
from flask import request, jsonify
from flask_login import login_required, current_user
from api.utils.api_utils import get_json_result, server_error_response
from api.common.exceptions import AdminException

# Override page_name to prevent double /admin prefix
page_name = ""

# Import admin functions
try:
    import sys
    from pathlib import Path
    admin_path = Path(__file__).parent.parent.parent.parent / "admin" / "server"
    if str(admin_path) not in sys.path:
        sys.path.insert(0, str(admin_path))
    
    from admin.server.services import UserMgr, ServiceMgr
    from admin.server.auth import check_admin_auth
    from admin.server.config import SERVICE_CONFIGS, load_configurations
    from admin.server.roles import RoleMgr, RESOURCE_TYPES
    from common.constants import SERVICE_CONF
    
    # Load service configurations on startup
    SERVICE_CONFIGS.configs = load_configurations(SERVICE_CONF)
    logging.info(f"Admin modules imported successfully, loaded {len(SERVICE_CONFIGS.configs)} services")
except ImportError as e:
    logging.error(f"Failed to import admin modules: {e}")
    UserMgr = None
    ServiceMgr = None
    RoleMgr = None
    RESOURCE_TYPES = []
    check_admin_auth = lambda f: f


@manager.route('/admin/dashboard/metrics', methods=['GET'])  # noqa: F821
# @login_required  # Temporarily disabled for testing
def get_dashboard_metrics():
    """Get comprehensive dashboard metrics"""
    try:
        logging.info("=== get_dashboard_metrics called ===")
        if not UserMgr:
            logging.error("UserMgr is None")
            return server_error_response("Admin module not available")
        
        logging.info("Getting user stats...")
        # Get user stats
        total_users = UserMgr.get_total_user_count()
        logging.info(f"Total users: {total_users}")
        active_users_7d = UserMgr.get_active_user_count(days=7)
        logging.info(f"Active users 7d: {active_users_7d}")
        active_users_1d = UserMgr.get_active_user_count(days=1)
        new_users_30d = UserMgr.get_new_user_count(days=30)
        
        logging.info("Getting service stats...")
        # Get service stats
        services = ServiceMgr.get_all_services() if ServiceMgr else []
        active_services = len([s for s in services if s.get('status') == 'running'])
        total_services = len(services)
        
        logging.info("Getting recent activities...")
        # Get recent activities
        recent_activities = UserMgr.get_recent_activities(limit=10)
        
        metrics = {
            'totalUsers': total_users,
            'activeUsers24h': active_users_1d,
            'activeUsers7d': active_users_7d,
            'newUsers30d': new_users_30d,
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
            'recentActivities': recent_activities,
        }
        
        logging.info(f"Returning metrics: {metrics}")
        return get_json_result(data=metrics)
        
    except Exception as e:
        logging.error(f"get_dashboard_metrics error: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return server_error_response(str(e))


@manager.route('/admin/users', methods=['GET'])  # noqa: F821
# @login_required  # Temporarily disabled for testing
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


@manager.route('/admin/users', methods=['POST'])  # noqa: F821
# @login_required  # Temporarily disabled for testing
def create_user():
    """Create a new user"""
    try:
        if not UserMgr:
            return server_error_response("Admin module not available")
        
        data = request.json
        username = data.get('username')
        password = data.get('password')
        role = data.get('role', 'user')
        
        if not username or not password:
            return get_json_result(code=400, message="Username and password are required")
        
        from api.common.exceptions import AdminException
        try:
            res = UserMgr.create_user(username, password, role)
            if res.get("success"):
                user_info = res.get("user_info", {})
                user_info.pop("password", None)  # Don't return password
                return get_json_result(data=user_info)
            else:
                return get_json_result(code=400, message=res.get("message", "Create user failed"))
        except AdminException as e:
            return get_json_result(code=e.code, message=str(e))
    except Exception as e:
        logging.error(f"create_user error: {e}")
        return server_error_response(str(e))


@manager.route('/admin/users/<username>', methods=['GET'])  # noqa: F821
@login_required
def get_user_details(username):
    """Get user details"""
    try:
        if not UserMgr:
            return server_error_response("Admin module not available")
        
        from api.common.exceptions import AdminException
        try:
            user_details = UserMgr.get_user_details(username)
            return get_json_result(data=user_details)
        except AdminException as e:
            return get_json_result(code=e.code, message=str(e))
    except Exception as e:
        logging.error(f"get_user_details error: {e}")
        return server_error_response(str(e))


@manager.route('/admin/users/<username>', methods=['PUT'])  # noqa: F821
@login_required
def update_user(username):
    """Update user information"""
    try:
        if not UserMgr:
            return server_error_response("Admin module not available")
        
        data = request.json
        role = data.get('role')
        
        if not role:
            return get_json_result(code=400, message="Role is required")
        
        from api.common.exceptions import AdminException
        try:
            result = RoleMgr.update_user_role(username, role)
            return get_json_result(data=result)
        except AdminException as e:
            return get_json_result(code=e.code, message=str(e))
    except Exception as e:
        logging.error(f"update_user error: {e}")
        return server_error_response(str(e))


@manager.route('/admin/users/<username>', methods=['DELETE'])  # noqa: F821
@login_required
def delete_user(username):
    """Delete a user"""
    try:
        if not UserMgr:
            return server_error_response("Admin module not available")
        
        from api.common.exceptions import AdminException
        try:
            res = UserMgr.delete_user(username)
            if res.get("success"):
                return get_json_result(data=None, message=res.get("message", "User deleted"))
            else:
                return get_json_result(code=400, message=res.get("message", "Delete user failed"))
        except AdminException as e:
            return get_json_result(code=e.code, message=str(e))
    except Exception as e:
        logging.error(f"delete_user error: {e}")
        return server_error_response(str(e))


@manager.route('/admin/services', methods=['GET'])  # noqa: F821
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


@manager.route('/admin/system/version', methods=['GET'])  # noqa: F821
def get_system_version():
    """Get system version - no auth required"""
    try:
        from api.versions import get_ragflow_version
        return get_json_result(data={'version': get_ragflow_version()})
    except Exception as e:
        logging.error(f"get_system_version error: {e}")
        return server_error_response(str(e))


# ============ Role Management Endpoints ============

@manager.route('/admin/roles/resource', methods=['GET'])  # noqa: F821
# @login_required  # Disabled for testing
def list_resource_types():
    """Get available resource types"""
    try:
        return get_json_result(data={'resource_types': RESOURCE_TYPES})
    except Exception as e:
        logging.error(f"list_resource_types error: {e}")
        return server_error_response(str(e))


@manager.route('/admin/roles', methods=['POST'])  # noqa: F821
# @login_required  # Disabled for testing
def create_role():
    """Create a new role"""
    try:
        data = request.json
        role_name = data.get('role_name')
        description = data.get('description', '')
        
        if not role_name:
            return get_json_result(code=400, message="role_name is required")
        
        result = RoleMgr.create_role(role_name, description)
        return get_json_result(data=result)
    except Exception as e:
        logging.error(f"create_role error: {e}")
        return server_error_response(str(e))


@manager.route('/admin/roles', methods=['GET'])  # noqa: F821
# @login_required  # Disabled for testing
def list_roles():
    """List all roles"""
    try:
        roles = RoleMgr.list_roles()
        return get_json_result(data=roles)
    except Exception as e:
        logging.error(f"list_roles error: {e}")
        return server_error_response(str(e))


@manager.route('/admin/roles_with_permission', methods=['GET'])  # noqa: F821
# @login_required  # Disabled for testing
def list_roles_with_permission():
    """List all roles with their permissions"""
    try:
        roles_data = RoleMgr.list_roles()
        roles_list = roles_data.get('roles', [])
        
        result = []
        for role in roles_list:
            permissions_data = RoleMgr.get_role_permission(role['role_name'])
            role_with_perms = {
                "id": role['id'],
                "role_name": role['role_name'],
                "description": role['description'],
                "create_date": role['create_date'],
                "update_date": role['update_date'],
                "permissions": permissions_data.get('permissions', {})
            }
            result.append(role_with_perms)
        
        return get_json_result(data={"roles": result, "total": len(result)})
    except AdminException as e:
        return get_json_result(code=e.code, message=str(e))
    except Exception as e:
        logging.error(f"list_roles_with_permission error: {e}")
        return server_error_response(str(e))


@manager.route('/admin/roles/<role_name>', methods=['PUT'])  # noqa: F821
@login_required
def update_role(role_name):
    """Update role description"""
    try:
        data = request.json
        description = data.get('description', '')
        
        result = RoleMgr.update_role_description(role_name, description)
        return get_json_result(data=result)
    except Exception as e:
        logging.error(f"update_role error: {e}")
        return server_error_response(str(e))


@manager.route('/admin/roles/<role_name>', methods=['DELETE'])  # noqa: F821
@login_required
def delete_role(role_name):
    """Delete a role"""
    try:
        result = RoleMgr.delete_role(role_name)
        return get_json_result(data=result)
    except Exception as e:
        logging.error(f"delete_role error: {e}")
        return server_error_response(str(e))


@manager.route('/admin/roles/<role_name>/permission', methods=['GET'])  # noqa: F821
# @login_required  # Disabled for testing
def get_role_permission(role_name):
    """Get role permissions"""
    try:
        permissions = RoleMgr.get_role_permission(role_name)
        return get_json_result(data=permissions)
    except Exception as e:
        logging.error(f"get_role_permission error: {e}")
        return server_error_response(str(e))


@manager.route('/admin/roles/<role_name>/permission', methods=['POST'])  # noqa: F821
# @login_required  # Disabled for testing
def grant_role_permission(role_name):
    """Grant permissions to a role"""
    try:
        data = request.json
        resource = data.get('resource')
        actions = data.get('actions', [])
        
        if not resource:
            return get_json_result(code=400, message="resource is required")
        
        if not actions or not isinstance(actions, list):
            return get_json_result(code=400, message="actions must be a non-empty list")
        
        result = RoleMgr.grant_role_permission(role_name, actions, resource)
        return get_json_result(data=result)
    except AdminException as e:
        return get_json_result(code=e.code, message=str(e))
    except Exception as e:
        logging.error(f"grant_role_permission error: {e}")
        return server_error_response(str(e))


@manager.route('/admin/roles/<role_name>/permission', methods=['DELETE'])  # noqa: F821
@login_required
def revoke_role_permission(role_name):
    """Revoke permissions from a role"""
    try:
        resource = request.args.get('resource')
        actions_str = request.args.get('actions', '')
        actions = [a.strip() for a in actions_str.split(',') if a.strip()]
        
        if not resource:
            return get_json_result(code=400, message="resource is required")
        
        if not actions:
            return get_json_result(code=400, message="actions is required")
        
        result = RoleMgr.revoke_role_permission(role_name, actions, resource)
        return get_json_result(data=result)
    except AdminException as e:
        return get_json_result(code=e.code, message=str(e))
    except Exception as e:
        logging.error(f"revoke_role_permission error: {e}")
        return server_error_response(str(e))
