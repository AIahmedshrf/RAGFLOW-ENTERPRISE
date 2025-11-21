#!/usr/bin/env python3
"""
Fix missing tenant for users
"""

from api.db.db_models import DB, User, Tenant, UserTenant
from api.db import StatusEnum
from common.misc_utils import get_uuid

def fix_user_tenant(email):
    """Fix tenant for a specific user"""
    with DB.connection_context():
        try:
            user = User.get(User.email == email)
            print(f"✓ Found user: {user.email}")
            
            # Check user_tenant
            user_tenants = list(UserTenant.select().where(UserTenant.user_id == user.id))
            if not user_tenants:
                print(f"✗ No user_tenant found for {email}")
                return False
            
            user_tenant = user_tenants[0]
            print(f"✓ User tenant_id: {user_tenant.tenant_id}, role: {user_tenant.role}")
            
            # Check if tenant exists
            try:
                tenant = Tenant.get(Tenant.id == user_tenant.tenant_id)
                print(f"✓ Tenant exists: {tenant.name}")
                return True
            except:
                print(f"✗ Tenant {user_tenant.tenant_id} NOT FOUND")
                print(f"Creating tenant...")
                
                # Create tenant
                tenant = Tenant(
                    id=user_tenant.tenant_id,
                    name=f"{user.nickname}'s Workspace" if user.nickname else "Default Workspace",
                    llm_id="deepseek_chat",
                    embd_id="BAAI/bge-large-zh-v1.5",
                    asr_id="openai/whisper-large", 
                    img2txt_id="Qwen/Qwen-VL",
                    rerank_id="BAAI/bge-reranker-v2-m3",
                    parser_ids="naive:raptor",
                    status=StatusEnum.VALID.value,
                    credit=0
                )
                tenant.save(force_insert=True)
                print(f"✓ Created tenant: {tenant.name}")
                return True
                
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    print("=== Fixing Tenant Issues ===\n")
    
    # Fix for all users
    with DB.connection_context():
        users = list(User.select())
        print(f"Found {len(users)} users\n")
        
        for user in users:
            print(f"Checking {user.email}...")
            fix_user_tenant(user.email)
            print()
    
    print("=== Done ===")
