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


import re
from werkzeug.security import check_password_hash
from api.db import ActiveEnum
from api.db.services import UserService
from api.db.joint_services.user_account_service import create_new_user, delete_user_data
from api.db.services.canvas_service import UserCanvasService
from api.db.services.user_service import TenantService
from api.db.services.knowledgebase_service import KnowledgebaseService
from api.utils.crypt import decrypt
from api.utils import health_utils

from api.common.exceptions import AdminException, UserAlreadyExistsError, UserNotFoundError
from config import SERVICE_CONFIGS


class UserMgr:
    @staticmethod
    def get_all_users():
        from api.db.services.user_service import UserTenantService
        users = UserService.get_all_users()
        result = []
        for user in users:
            # Get user's role from user_tenant table
            user_tenants = UserTenantService.query(user_id=user.id)
            role = None
            if user_tenants:
                # Get the first tenant's role (most users have one tenant)
                role = user_tenants[0].role if hasattr(user_tenants[0], 'role') else None
            
            result.append({
                'email': user.email,
                'nickname': user.nickname,
                'role': role,  # Add role field
                'create_date': user.create_date,
                'is_active': user.is_active,
                'is_superuser': user.is_superuser,
            })
        return result
    
    @staticmethod
    def get_total_user_count():
        """Get total number of users"""
        return len(UserService.get_all_users())
    
    @staticmethod
    def get_active_user_count(days=7):
        """Get count of active users in last N days"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        users = UserService.get_all_users()
        active_count = sum(1 for u in users if u.last_login_time and u.last_login_time > cutoff_date)
        return active_count
    
    @staticmethod
    def get_new_user_count(days=30):
        """Get count of new users in last N days"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        users = UserService.get_all_users()
        new_count = sum(1 for u in users if u.create_date and u.create_date > cutoff_date)
        return new_count
    
    @staticmethod
    def get_users_by_role():
        """Get user count by role"""
        users = UserService.get_all_users()
        admins = sum(1 for u in users if u.is_superuser)
        regular = len(users) - admins
        return {'admin': admins, 'user': regular}
    
    @staticmethod
    def get_daily_active_users(date):
        """Get active user count for a specific date"""
        from datetime import datetime, timedelta
        target_date = datetime.strptime(date, '%Y-%m-%d')
        next_day = target_date + timedelta(days=1)
        users = UserService.get_all_users()
        count = sum(1 for u in users if u.last_login_time and 
                   target_date <= u.last_login_time < next_day)
        return count
    
    @staticmethod
    def get_top_active_users(limit=10, days=30):
        """Get most active users"""
        # This is a simplified implementation
        # In production, you'd track user activity in a separate table
        users = UserService.get_all_users()
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=days)
        
        active_users = []
        for user in users:
            if user.last_login_time and user.last_login_time > cutoff_date:
                active_users.append({
                    'email': user.email,
                    'nickname': user.nickname,
                    'last_login': user.last_login_time.isoformat() if user.last_login_time else None,
                })
        
        # Sort by last_login and limit
        active_users.sort(key=lambda x: x['last_login'] or '', reverse=True)
        return active_users[:limit]
    
    @staticmethod
    def get_recent_activities(limit=10):
        """Get recent user activities"""
        # Simplified implementation - returns recent user creations
        users = UserService.get_all_users()
        activities = []
        
        for user in sorted(users, key=lambda x: x.create_date or datetime.min, reverse=True)[:limit]:
            activities.append({
                'id': user.id,
                'type': 'user_created',
                'user': user.email,
                'description': f'User {user.email} was created',
                'timestamp': user.create_date.isoformat() if user.create_date else None,
            })
        
        return activities

    @staticmethod
    def get_user_details(username):
        # use email to query
        users = UserService.query_user_by_email(username)
        result = []
        for user in users:
            result.append({
                'email': user.email,
                'language': user.language,
                'last_login_time': user.last_login_time,
                'is_active': user.is_active,
                'is_anonymous': user.is_anonymous,
                'login_channel': user.login_channel,
                'status': user.status,
                'is_superuser': user.is_superuser,
                'create_date': user.create_date,
                'update_date': user.update_date
            })
        return result

    @staticmethod
    def create_user(username, password, role="user") -> dict:
        # Validate the email address
        if not re.match(r"^[\w\._-]+@([\w_-]+\.)+[\w-]{2,}$", username):
            raise AdminException(f"Invalid email address: {username}!")
        # Check if the email address is already used
        if UserService.query(email=username):
            raise UserAlreadyExistsError(username)
        # Construct user info data
        user_info_dict = {
            "email": username,
            "nickname": "",  # ask user to edit it manually in settings.
            "password": decrypt(password),
            "login_channel": "password",
            "is_superuser": role == "admin",
            "role": role,  # Pass role to create_new_user
        }
        return create_new_user(user_info_dict)

    @staticmethod
    def delete_user(username):
        # use email to delete
        user_list = UserService.query_user_by_email(username)
        if not user_list:
            raise UserNotFoundError(username)
        if len(user_list) > 1:
            raise AdminException(f"Exist more than 1 user: {username}!")
        usr = user_list[0]
        return delete_user_data(usr.id)

    @staticmethod
    def update_user_password(username, new_password) -> str:
        # use email to find user. check exist and unique.
        user_list = UserService.query_user_by_email(username)
        if not user_list:
            raise UserNotFoundError(username)
        elif len(user_list) > 1:
            raise AdminException(f"Exist more than 1 user: {username}!")
        # check new_password different from old.
        usr = user_list[0]
        psw = decrypt(new_password)
        if check_password_hash(usr.password, psw):
            return "Same password, no need to update!"
        # update password
        UserService.update_user_password(usr.id, psw)
        return "Password updated successfully!"

    @staticmethod
    def update_user_activate_status(username, activate_status: str):
        # use email to find user. check exist and unique.
        user_list = UserService.query_user_by_email(username)
        if not user_list:
            raise UserNotFoundError(username)
        elif len(user_list) > 1:
            raise AdminException(f"Exist more than 1 user: {username}!")
        # check activate status different from new
        usr = user_list[0]
        # format activate_status before handle
        _activate_status = activate_status.lower()
        target_status = {
            'on': ActiveEnum.ACTIVE.value,
            'off': ActiveEnum.INACTIVE.value,
        }.get(_activate_status)
        if not target_status:
            raise AdminException(f"Invalid activate_status: {activate_status}")
        if target_status == usr.is_active:
            return f"User activate status is already {_activate_status}!"
        # update is_active
        UserService.update_user(usr.id, {"is_active": target_status})
        return f"Turn {_activate_status} user activate status successfully!"


class UserServiceMgr:

    @staticmethod
    def get_user_datasets(username):
        # use email to find user.
        user_list = UserService.query_user_by_email(username)
        if not user_list:
            raise UserNotFoundError(username)
        elif len(user_list) > 1:
            raise AdminException(f"Exist more than 1 user: {username}!")
        # find tenants
        usr = user_list[0]
        tenants = TenantService.get_joined_tenants_by_user_id(usr.id)
        tenant_ids = [m["tenant_id"] for m in tenants]
        # filter permitted kb and owned kb
        return KnowledgebaseService.get_all_kb_by_tenant_ids(tenant_ids, usr.id)

    @staticmethod
    def get_user_agents(username):
        # use email to find user.
        user_list = UserService.query_user_by_email(username)
        if not user_list:
            raise UserNotFoundError(username)
        elif len(user_list) > 1:
            raise AdminException(f"Exist more than 1 user: {username}!")
        # find tenants
        usr = user_list[0]
        tenants = TenantService.get_joined_tenants_by_user_id(usr.id)
        tenant_ids = [m["tenant_id"] for m in tenants]
        # filter permitted agents and owned agents
        res = UserCanvasService.get_all_agents_by_tenant_ids(tenant_ids, usr.id)
        return [{
            'title': r['title'],
            'permission': r['permission'],
            'canvas_category': r['canvas_category'].split('_')[0]
        } for r in res]


class ServiceMgr:

    @staticmethod
    def get_all_services():
        result = []
        configs = SERVICE_CONFIGS.configs
        for service_id, config in enumerate(configs):
            config_dict = config.to_dict()
            try:
                service_detail = ServiceMgr.get_service_details(service_id)
                if "status" in service_detail:
                    config_dict['status'] = service_detail['status']
                else:
                    config_dict['status'] = 'timeout'
            except Exception:
                config_dict['status'] = 'timeout'
            result.append(config_dict)
        return result

    @staticmethod
    def get_services_by_type(service_type_str: str):
        raise AdminException("get_services_by_type: not implemented")

    @staticmethod
    def get_service_details(service_id: int):
        service_id = int(service_id)
        configs = SERVICE_CONFIGS.configs
        service_config_mapping = {
            c.id: {
                'name': c.name,
                'detail_func_name': c.detail_func_name
            } for c in configs
        }
        service_info = service_config_mapping.get(service_id, {})
        if not service_info:
            raise AdminException(f"invalid service_id: {service_id}")

        detail_func = getattr(health_utils, service_info.get('detail_func_name'))
        res = detail_func()
        res.update({'service_name': service_info.get('name')})
        return res

    @staticmethod
    def shutdown_service(service_id: int):
        raise AdminException("shutdown_service: not implemented")

    @staticmethod
    def restart_service(service_id: int):
        raise AdminException("restart_service: not implemented")
