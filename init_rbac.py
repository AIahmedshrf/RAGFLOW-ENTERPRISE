#!/usr/bin/env python3
"""
Initialize default RBAC roles for RAGFlow Enterprise
Creates: admin, user, viewer roles with appropriate permissions
"""

import requests
import json

BASE_URL = "http://localhost:8080/api/v1/admin"

# Note: In production, you'll need authentication token
# For now, testing without auth (temporarily disabled in code)

def create_role(role_name, description):
    """Create a role"""
    url = f"{BASE_URL}/roles"
    data = {"role_name": role_name, "description": description}
    response = requests.post(url, json=data)
    print(f"Create Role '{role_name}': {response.status_code}")
    print(f"  Response: {response.json()}")
    return response.json()

def grant_permissions(role_name, resource, actions):
    """Grant permissions to a role"""
    url = f"{BASE_URL}/roles/{role_name}/permission"
    data = {"resource": resource, "actions": actions}
    response = requests.post(url, json=data)
    print(f"Grant {role_name} on {resource}: {response.status_code}")
    return response.json()

def list_roles():
    """List all roles"""
    url = f"{BASE_URL}/roles"
    response = requests.get(url)
    print(f"\nList Roles: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def list_resources():
    """List available resources"""
    url = f"{BASE_URL}/roles/resource"
    response = requests.get(url)
    print(f"\nList Resources: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.json()

# Initialize default roles
print("=== Initializing RAGFlow Enterprise RBAC ===\n")

# 1. Create Roles
print("--- Creating Roles ---")
create_role("admin", "Full system access - can manage everything")
create_role("user", "Standard user - can create and manage own resources")
create_role("viewer", "Read-only access - can only view resources")

# 2. Grant Permissions
print("\n--- Granting Permissions ---")

# Admin: Full access to everything
for resource in ["dataset", "agent", "chat", "user", "file"]:
    grant_permissions("admin", resource, ["enable", "read", "write", "share"])

# User: Can manage own datasets, agents, chats, files (no user management)
for resource in ["dataset", "agent", "chat", "file"]:
    grant_permissions("user", resource, ["enable", "read", "write", "share"])

# Viewer: Read-only access
for resource in ["dataset", "agent", "chat", "file"]:
    grant_permissions("viewer", resource, ["read"])

# 3. List Results
print("\n--- Results ---")
list_resources()
list_roles()

print("\n✅ RBAC initialization complete!")
