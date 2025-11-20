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
import logging

from typing import Dict, Any, List

from api.common.exceptions import AdminException
from api.db.services.role_service import RoleService, RolePermissionService
from api.db.services.user_service import UserService


# Define available resource types
RESOURCE_TYPES = ["dataset", "agent", "chat", "user", "file"]


class RoleMgr:
    @staticmethod
    def create_role(role_name: str, description: str) -> Dict[str, Any]:
        """Create a new role"""
        try:
            # Check if role already exists
            existing = RoleService.get_by_name(role_name)
            if existing:
                raise AdminException(f"Role '{role_name}' already exists", 400)
            
            role = RoleService.create_role(role_name, description)
            return {
                "id": role.id,
                "role_name": role.role_name,
                "description": role.description,
                "create_date": role.create_date
            }
        except AdminException:
            raise
        except Exception as e:
            logging.error(f"create_role error: {e}")
            raise AdminException(f"Failed to create role: {e}", 500)

    @staticmethod
    def update_role_description(role_name: str, description: str) -> Dict[str, Any]:
        """Update role description"""
        try:
            role = RoleService.get_by_name(role_name)
            if not role:
                raise AdminException(f"Role '{role_name}' not found", 404)
            
            success = RoleService.update_description(role_name, description)
            if not success:
                raise AdminException(f"Failed to update role '{role_name}'", 500)
            
            return {"role_name": role_name, "description": description}
        except AdminException:
            raise
        except Exception as e:
            logging.error(f"update_role_description error: {e}")
            raise AdminException(f"Failed to update role: {e}", 500)

    @staticmethod
    def delete_role(role_name: str) -> Dict[str, Any]:
        """Delete a role (soft delete)"""
        try:
            # Prevent deletion of system roles
            if role_name.lower() in ['admin', 'user', 'viewer']:
                raise AdminException(f"Cannot delete system role '{role_name}'", 403)
            
            role = RoleService.get_by_name(role_name)
            if not role:
                raise AdminException(f"Role '{role_name}' not found", 404)
            
            success = RoleService.delete_role(role_name)
            if not success:
                raise AdminException(f"Failed to delete role '{role_name}'", 500)
            
            return {"role_name": role_name, "deleted": True}
        except AdminException:
            raise
        except Exception as e:
            logging.error(f"delete_role error: {e}")
            raise AdminException(f"Failed to delete role: {e}", 500)

    @staticmethod
    def list_roles() -> Dict[str, Any]:
        """List all active roles"""
        try:
            roles = RoleService.get_all()
            role_list = []
            for role in roles:
                role_list.append({
                    "id": role.id,
                    "role_name": role.role_name,
                    "description": role.description or "",
                    "create_date": role.create_date,
                    "update_date": role.update_date
                })
            return {"roles": role_list, "total": len(role_list)}
        except Exception as e:
            logging.error(f"list_roles error: {e}")
            raise AdminException(f"Failed to list roles: {e}", 500)

    @staticmethod
    def get_role_permission(role_name: str) -> Dict[str, Any]:
        """Get all permissions for a role"""
        try:
            role = RoleService.get_by_name(role_name)
            if not role:
                raise AdminException(f"Role '{role_name}' not found", 404)
            
            permissions = RolePermissionService.get_permissions(role.id)
            perm_dict = {}
            for perm in permissions:
                perm_dict[perm.resource_type] = {
                    "enable": bool(perm.enable),
                    "read": bool(perm.read),
                    "write": bool(perm.write),
                    "share": bool(perm.share)
                }
            
            return {
                "role": {
                    "id": role.id,
                    "name": role.role_name,
                    "description": role.description or ""
                },
                "permissions": perm_dict
            }
        except AdminException:
            raise
        except Exception as e:
            logging.error(f"get_role_permission error: {e}")
            raise AdminException(f"Failed to get role permissions: {e}", 500)

    @staticmethod
    def grant_role_permission(role_name: str, actions: list, resource: str) -> Dict[str, Any]:
        """Grant permissions to a role on a resource"""
        try:
            role = RoleService.get_by_name(role_name)
            if not role:
                raise AdminException(f"Role '{role_name}' not found", 404)
            
            if resource not in RESOURCE_TYPES:
                raise AdminException(f"Invalid resource type '{resource}'. Must be one of: {RESOURCE_TYPES}", 400)
            
            # Parse actions into permissions
            perms = {"enable": False, "read": False, "write": False, "share": False}
            for action in actions:
                action_lower = action.lower()
                if action_lower in perms:
                    perms[action_lower] = True
                else:
                    raise AdminException(f"Invalid action '{action}'. Must be one of: enable, read, write, share", 400)
            
            # Set permissions
            perm = RolePermissionService.set_permission(
                role.id, resource, **perms
            )
            
            return {
                "role_name": role_name,
                "resource": resource,
                "permissions": {
                    "enable": bool(perm.enable),
                    "read": bool(perm.read),
                    "write": bool(perm.write),
                    "share": bool(perm.share)
                }
            }
        except AdminException:
            raise
        except Exception as e:
            logging.error(f"grant_role_permission error: {e}")
            raise AdminException(f"Failed to grant permissions: {e}", 500)

    @staticmethod
    def revoke_role_permission(role_name: str, actions: list, resource: str) -> Dict[str, Any]:
        """Revoke permissions from a role on a resource"""
        try:
            role = RoleService.get_by_name(role_name)
            if not role:
                raise AdminException(f"Role '{role_name}' not found", 404)
            
            if resource not in RESOURCE_TYPES:
                raise AdminException(f"Invalid resource type '{resource}'", 400)
            
            # Get current permissions
            perm = RolePermissionService.get_permission(role.id, resource)
            if not perm:
                return {"role_name": role_name, "resource": resource, "message": "No permissions to revoke"}
            
            # Revoke specified actions
            updates = {}
            for action in actions:
                action_lower = action.lower()
                if action_lower in ["enable", "read", "write", "share"]:
                    updates[action_lower] = False
            
            if updates:
                perm = RolePermissionService.set_permission(role.id, resource, **updates)
            
            return {
                "role_name": role_name,
                "resource": resource,
                "permissions": {
                    "enable": bool(perm.enable),
                    "read": bool(perm.read),
                    "write": bool(perm.write),
                    "share": bool(perm.share)
                }
            }
        except AdminException:
            raise
        except Exception as e:
            logging.error(f"revoke_role_permission error: {e}")
            raise AdminException(f"Failed to revoke permissions: {e}", 500)

    @staticmethod
    def update_user_role(user_name: str, role_name: str) -> Dict[str, Any]:
        """Update user's role"""
        try:
            # Verify role exists
            role = RoleService.get_by_name(role_name)
            if not role:
                raise AdminException(f"Role '{role_name}' not found", 404)
            
            # Get user
            users = UserService.query(email=user_name)
            if not users:
                raise AdminException(f"User '{user_name}' not found", 404)
            
            user = users[0]
            # Update user role field (assuming user.role exists)
            # Note: This may need adjustment based on actual User model structure
            user.role = role_name
            user.save()
            
            return {"user_name": user_name, "role_name": role_name}
        except AdminException:
            raise
        except Exception as e:
            logging.error(f"update_user_role error: {e}")
            raise AdminException(f"Failed to update user role: {e}", 500)

    @staticmethod
    def get_user_permission(user_name: str) -> Dict[str, Any]:
        """Get user's permissions based on their role"""
        try:
            # Get user
            users = UserService.query(email=user_name)
            if not users:
                raise AdminException(f"User '{user_name}' not found", 404)
            
            user = users[0]
            role_name = getattr(user, 'role', 'user')  # Default to 'user' role
            
            if not role_name:
                return {
                    "user": {"id": user.id, "username": user_name, "role": "none"},
                    "role_permissions": {}
                }
            
            # Get role
            role = RoleService.get_by_name(role_name)
            if not role:
                return {
                    "user": {"id": user.id, "username": user_name, "role": role_name},
                    "role_permissions": {}
                }
            
            # Get permissions
            permissions = RolePermissionService.get_permissions(role.id)
            perm_dict = {}
            for perm in permissions:
                perm_dict[perm.resource_type] = {
                    "enable": bool(perm.enable),
                    "read": bool(perm.read),
                    "write": bool(perm.write),
                    "share": bool(perm.share)
                }
            
            return {
                "user": {
                    "id": user.id,
                    "username": user_name,
                    "role": role_name
                },
                "role_permissions": perm_dict
            }
        except AdminException:
            raise
        except Exception as e:
            logging.error(f"get_user_permission error: {e}")
            raise AdminException(f"Failed to get user permissions: {e}", 500)
