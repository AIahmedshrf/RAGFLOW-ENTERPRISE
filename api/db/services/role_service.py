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
Enterprise RBAC Service
Manages Roles and Permissions for Role-Based Access Control
"""

from api.db.db_models import Role, RolePermission, DB
from api.db import StatusEnum
from api.utils import get_uuid


class RoleService:
    model = Role
    
    @classmethod
    @DB.connection_context()
    def get_by_name(cls, role_name):
        try:
            return cls.model.get(cls.model.role_name == role_name, cls.model.status == StatusEnum.VALID.value)
        except Exception:
            return None
    
    @classmethod
    @DB.connection_context()
    def get_by_id(cls, role_id):
        try:
            return cls.model.get(cls.model.id == role_id, cls.model.status == StatusEnum.VALID.value)
        except Exception:
            return None
    
    @classmethod
    @DB.connection_context()
    def get_all(cls):
        """Get all active roles"""
        return list(cls.model.select().where(cls.model.status == StatusEnum.VALID.value))
    
    @classmethod
    @DB.connection_context()
    def create_role(cls, role_name, description=None):
        """Create a new role"""
        role_id = get_uuid()
        role = cls.model(
            id=role_id,
            role_name=role_name,
            description=description,
            status=StatusEnum.VALID.value
        )
        role.save(force_insert=True)
        return role
    
    @classmethod
    @DB.connection_context()
    def update_description(cls, role_name, description):
        """Update role description"""
        role = cls.get_by_name(role_name)
        if not role:
            return False
        role.description = description
        role.save()
        return True
    
    @classmethod
    @DB.connection_context()
    def delete_role(cls, role_name):
        """Soft delete a role"""
        role = cls.get_by_name(role_name)
        if not role:
            return False
        role.status = StatusEnum.INVALID.value
        role.save()
        # Also delete all permissions for this role
        RolePermissionService.delete_by_role(role.id)
        return True


class RolePermissionService:
    model = RolePermission
    
    @classmethod
    @DB.connection_context()
    def get_permissions(cls, role_id):
        """Get all permissions for a role"""
        return list(cls.model.select().where(cls.model.role_id == role_id))
    
    @classmethod
    @DB.connection_context()
    def get_permission(cls, role_id, resource_type):
        """Get specific permission for role and resource"""
        try:
            return cls.model.get(
                cls.model.role_id == role_id,
                cls.model.resource_type == resource_type
            )
        except Exception:
            return None
    
    @classmethod
    @DB.connection_context()
    def set_permission(cls, role_id, resource_type, enable=None, read=None, write=None, share=None):
        """Set permissions for a role on a resource"""
        perm = cls.get_permission(role_id, resource_type)
        
        if perm:
            # Update existing permission
            if enable is not None:
                perm.enable = enable
            if read is not None:
                perm.read = read
            if write is not None:
                perm.write = write
            if share is not None:
                perm.share = share
            perm.save()
        else:
            # Create new permission
            perm = cls.model(
                id=get_uuid(),
                role_id=role_id,
                resource_type=resource_type,
                enable=enable if enable is not None else False,
                read=read if read is not None else False,
                write=write if write is not None else False,
                share=share if share is not None else False
            )
            perm.save(force_insert=True)
        
        return perm
    
    @classmethod
    @DB.connection_context()
    def delete_permission(cls, role_id, resource_type):
        """Delete specific permission"""
        perm = cls.get_permission(role_id, resource_type)
        if perm:
            perm.delete_instance()
            return True
        return False
    
    @classmethod
    @DB.connection_context()
    def delete_by_role(cls, role_id):
        """Delete all permissions for a role"""
        cls.model.delete().where(cls.model.role_id == role_id).execute()


# Import DB after defining services
from api.db.db_models import DB
