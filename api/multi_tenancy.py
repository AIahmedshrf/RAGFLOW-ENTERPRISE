"""
Multi-Tenancy System for RAGFlow Enterprise
Provides tenant isolation, resource quotas, and management
"""
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json


class TenantStatus(Enum):
    """Tenant status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"


class SubscriptionPlan(Enum):
    """Subscription plans"""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


@dataclass
class ResourceQuota:
    """Resource quotas for a tenant"""
    max_users: int = 5
    max_knowledge_bases: int = 10
    max_documents: int = 1000
    max_conversations: int = 100
    max_agents: int = 5
    max_storage_gb: int = 10
    max_api_calls_per_day: int = 10000
    max_concurrent_requests: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'max_users': self.max_users,
            'max_knowledge_bases': self.max_knowledge_bases,
            'max_documents': self.max_documents,
            'max_conversations': self.max_conversations,
            'max_agents': self.max_agents,
            'max_storage_gb': self.max_storage_gb,
            'max_api_calls_per_day': self.max_api_calls_per_day,
            'max_concurrent_requests': self.max_concurrent_requests,
        }
    
    @staticmethod
    def from_plan(plan: SubscriptionPlan) -> 'ResourceQuota':
        """Get quotas based on subscription plan"""
        quotas = {
            SubscriptionPlan.FREE: ResourceQuota(
                max_users=2,
                max_knowledge_bases=2,
                max_documents=100,
                max_conversations=50,
                max_agents=1,
                max_storage_gb=1,
                max_api_calls_per_day=1000,
                max_concurrent_requests=2
            ),
            SubscriptionPlan.BASIC: ResourceQuota(
                max_users=10,
                max_knowledge_bases=20,
                max_documents=5000,
                max_conversations=500,
                max_agents=5,
                max_storage_gb=50,
                max_api_calls_per_day=50000,
                max_concurrent_requests=10
            ),
            SubscriptionPlan.PROFESSIONAL: ResourceQuota(
                max_users=50,
                max_knowledge_bases=100,
                max_documents=50000,
                max_conversations=5000,
                max_agents=20,
                max_storage_gb=500,
                max_api_calls_per_day=500000,
                max_concurrent_requests=50
            ),
            SubscriptionPlan.ENTERPRISE: ResourceQuota(
                max_users=1000,
                max_knowledge_bases=1000,
                max_documents=1000000,
                max_conversations=100000,
                max_agents=100,
                max_storage_gb=5000,
                max_api_calls_per_day=5000000,
                max_concurrent_requests=200
            ),
        }
        return quotas.get(plan, ResourceQuota())


@dataclass
class ResourceUsage:
    """Current resource usage for a tenant"""
    users_count: int = 0
    knowledge_bases_count: int = 0
    documents_count: int = 0
    conversations_count: int = 0
    agents_count: int = 0
    storage_used_gb: float = 0
    api_calls_today: int = 0
    current_concurrent_requests: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'users_count': self.users_count,
            'knowledge_bases_count': self.knowledge_bases_count,
            'documents_count': self.documents_count,
            'conversations_count': self.conversations_count,
            'agents_count': self.agents_count,
            'storage_used_gb': self.storage_used_gb,
            'api_calls_today': self.api_calls_today,
            'current_concurrent_requests': self.current_concurrent_requests,
        }


class Tenant:
    """Tenant entity"""
    
    def __init__(
        self,
        tenant_id: str,
        name: str,
        plan: SubscriptionPlan,
        admin_email: str,
        company: Optional[str] = None,
        domain: Optional[str] = None
    ):
        self.tenant_id = tenant_id
        self.name = name
        self.plan = plan
        self.admin_email = admin_email
        self.company = company
        self.domain = domain
        self.status = TenantStatus.ACTIVE
        self.quota = ResourceQuota.from_plan(plan)
        self.usage = ResourceUsage()
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.subscription_expires_at = datetime.now() + timedelta(days=365)
        self.metadata = {}
    
    def check_quota(self, resource: str, requested: int = 1) -> bool:
        """Check if tenant has quota for resource"""
        quota_map = {
            'users': (self.usage.users_count, self.quota.max_users),
            'knowledge_bases': (self.usage.knowledge_bases_count, self.quota.max_knowledge_bases),
            'documents': (self.usage.documents_count, self.quota.max_documents),
            'conversations': (self.usage.conversations_count, self.quota.max_conversations),
            'agents': (self.usage.agents_count, self.quota.max_agents),
            'api_calls': (self.usage.api_calls_today, self.quota.max_api_calls_per_day),
            'concurrent_requests': (self.usage.current_concurrent_requests, self.quota.max_concurrent_requests),
        }
        
        if resource not in quota_map:
            return True
        
        current, maximum = quota_map[resource]
        return (current + requested) <= maximum
    
    def increment_usage(self, resource: str, amount: int = 1):
        """Increment resource usage"""
        if resource == 'users':
            self.usage.users_count += amount
        elif resource == 'knowledge_bases':
            self.usage.knowledge_bases_count += amount
        elif resource == 'documents':
            self.usage.documents_count += amount
        elif resource == 'conversations':
            self.usage.conversations_count += amount
        elif resource == 'agents':
            self.usage.agents_count += amount
        elif resource == 'api_calls':
            self.usage.api_calls_today += amount
        elif resource == 'concurrent_requests':
            self.usage.current_concurrent_requests += amount
        
        self.updated_at = datetime.now()
    
    def decrement_usage(self, resource: str, amount: int = 1):
        """Decrement resource usage"""
        self.increment_usage(resource, -amount)
    
    def reset_daily_usage(self):
        """Reset daily usage counters"""
        self.usage.api_calls_today = 0
        self.updated_at = datetime.now()
    
    def upgrade_plan(self, new_plan: SubscriptionPlan):
        """Upgrade subscription plan"""
        self.plan = new_plan
        self.quota = ResourceQuota.from_plan(new_plan)
        self.updated_at = datetime.now()
    
    def is_active(self) -> bool:
        """Check if tenant is active"""
        if self.status != TenantStatus.ACTIVE:
            return False
        if datetime.now() > self.subscription_expires_at:
            self.status = TenantStatus.EXPIRED
            return False
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tenant to dictionary"""
        return {
            'tenant_id': self.tenant_id,
            'name': self.name,
            'plan': self.plan.value,
            'status': self.status.value,
            'admin_email': self.admin_email,
            'company': self.company,
            'domain': self.domain,
            'quota': self.quota.to_dict(),
            'usage': self.usage.to_dict(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'subscription_expires_at': self.subscription_expires_at.isoformat(),
            'metadata': self.metadata,
        }


class TenantManager:
    """Manages multiple tenants"""
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.tenant_by_domain: Dict[str, str] = {}
    
    def create_tenant(
        self,
        name: str,
        plan: SubscriptionPlan,
        admin_email: str,
        company: Optional[str] = None,
        domain: Optional[str] = None
    ) -> Tenant:
        """Create a new tenant"""
        tenant_id = f"tenant_{len(self.tenants) + 1}"
        
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            plan=plan,
            admin_email=admin_email,
            company=company,
            domain=domain
        )
        
        self.tenants[tenant_id] = tenant
        
        if domain:
            self.tenant_by_domain[domain] = tenant_id
        
        return tenant
    
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID"""
        return self.tenants.get(tenant_id)
    
    def get_tenant_by_domain(self, domain: str) -> Optional[Tenant]:
        """Get tenant by domain"""
        tenant_id = self.tenant_by_domain.get(domain)
        return self.tenants.get(tenant_id) if tenant_id else None
    
    def list_tenants(
        self,
        status: Optional[TenantStatus] = None,
        plan: Optional[SubscriptionPlan] = None
    ) -> List[Tenant]:
        """List all tenants with optional filters"""
        tenants = list(self.tenants.values())
        
        if status:
            tenants = [t for t in tenants if t.status == status]
        
        if plan:
            tenants = [t for t in tenants if t.plan == plan]
        
        return tenants
    
    def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> Optional[Tenant]:
        """Update tenant"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return None
        
        if 'name' in updates:
            tenant.name = updates['name']
        if 'company' in updates:
            tenant.company = updates['company']
        if 'status' in updates:
            tenant.status = TenantStatus(updates['status'])
        if 'plan' in updates:
            tenant.upgrade_plan(SubscriptionPlan(updates['plan']))
        
        tenant.updated_at = datetime.now()
        
        return tenant
    
    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete a tenant"""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
        
        # Remove domain mapping
        if tenant.domain and tenant.domain in self.tenant_by_domain:
            del self.tenant_by_domain[tenant.domain]
        
        del self.tenants[tenant_id]
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get tenant statistics"""
        total_tenants = len(self.tenants)
        
        stats = {
            'total_tenants': total_tenants,
            'by_status': {},
            'by_plan': {},
            'active_tenants': sum(1 for t in self.tenants.values() if t.is_active()),
        }
        
        for tenant in self.tenants.values():
            # Count by status
            status = tenant.status.value
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # Count by plan
            plan = tenant.plan.value
            stats['by_plan'][plan] = stats['by_plan'].get(plan, 0) + 1
        
        return stats


# Global tenant manager
tenant_manager = TenantManager()
