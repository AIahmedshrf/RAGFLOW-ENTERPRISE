"""
Tenant Management API Routes
Provides endpoints for tenant CRUD operations and resource management
"""
from flask import Blueprint, request
from api.multi_tenancy import tenant_manager, SubscriptionPlan
from api.security import require_api_key, rate_limit
from datetime import datetime


tenant_bp = Blueprint('tenant', __name__, url_prefix='/api/v1/tenants')


@tenant_bp.route('', methods=['POST'])
@rate_limit('professional')
def create_tenant():
    """Create a new tenant"""
    try:
        data = request.get_json()
        
        tenant = tenant_manager.create_tenant(
            name=data['name'],
            admin_email=data['admin_email'],
            plan=SubscriptionPlan[data.get('plan', 'FREE')],
            company=data.get('company'),
            domain=data.get('domain'),
        )
        
        return {
            'success': True,
            'tenant': {
                'tenant_id': tenant.tenant_id,
                'name': tenant.name,
                'plan': tenant.plan.value,
                'admin_email': tenant.admin_email,
                'company': tenant.company,
                'domain': tenant.domain,
                'status': tenant.status.value,
                'created_at': tenant.created_at,
                'subscription_expires_at': tenant.subscription_expires_at,
            }
        }, 201
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@tenant_bp.route('/<tenant_id>', methods=['GET'])
@require_api_key
@rate_limit('basic')
def get_tenant(tenant_id):
    """Get tenant details"""
    tenant = tenant_manager.get_tenant(tenant_id)
    
    if not tenant:
        return {'error': 'Tenant not found', 'code': 404}, 404
    
    return {
        'success': True,
        'tenant': {
            'tenant_id': tenant.tenant_id,
            'name': tenant.name,
            'plan': tenant.plan.value,
            'admin_email': tenant.admin_email,
            'company': tenant.company,
            'domain': tenant.domain,
            'status': tenant.status.value,
            'created_at': tenant.created_at,
            'subscription_expires_at': tenant.subscription_expires_at,
            'quota': {
                'max_users': tenant.quota.max_users,
                'max_knowledge_bases': tenant.quota.max_knowledge_bases,
                'max_documents': tenant.quota.max_documents,
                'max_conversations': tenant.quota.max_conversations,
                'max_agents': tenant.quota.max_agents,
                'max_storage_gb': tenant.quota.max_storage_gb,
                'max_api_calls_per_day': tenant.quota.max_api_calls_per_day,
                'max_concurrent_requests': tenant.quota.max_concurrent_requests,
            },
            'usage': {
                'users': tenant.usage.users,
                'knowledge_bases': tenant.usage.knowledge_bases,
                'documents': tenant.usage.documents,
                'conversations': tenant.usage.conversations,
                'agents': tenant.usage.agents,
                'storage_gb': tenant.usage.storage_gb,
                'api_calls_today': tenant.usage.api_calls_today,
                'concurrent_requests': tenant.usage.concurrent_requests,
            }
        }
    }


@tenant_bp.route('', methods=['GET'])
@require_api_key
@rate_limit('professional')
def list_tenants():
    """List all tenants"""
    status = request.args.get('status')
    plan = request.args.get('plan')
    search = request.args.get('search')
    
    filters = {}
    if status:
        filters['status'] = status
    if plan:
        filters['plan'] = plan
    if search:
        filters['search'] = search
    
    tenants = tenant_manager.list_tenants(**filters)
    
    return {
        'success': True,
        'tenants': [
            {
                'tenant_id': t.tenant_id,
                'name': t.name,
                'plan': t.plan.value,
                'admin_email': t.admin_email,
                'company': t.company,
                'domain': t.domain,
                'status': t.status.value,
                'created_at': t.created_at,
                'subscription_expires_at': t.subscription_expires_at,
            }
            for t in tenants
        ],
        'total': len(tenants)
    }


@tenant_bp.route('/<tenant_id>', methods=['PUT'])
@require_api_key
@rate_limit('basic')
def update_tenant(tenant_id):
    """Update tenant"""
    try:
        data = request.get_json()
        
        success = tenant_manager.update_tenant(tenant_id, **data)
        
        if not success:
            return {'error': 'Tenant not found', 'code': 404}, 404
        
        tenant = tenant_manager.get_tenant(tenant_id)
        
        return {
            'success': True,
            'tenant': {
                'tenant_id': tenant.tenant_id,
                'name': tenant.name,
                'plan': tenant.plan.value,
                'admin_email': tenant.admin_email,
                'company': tenant.company,
                'domain': tenant.domain,
                'status': tenant.status.value,
            }
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@tenant_bp.route('/<tenant_id>', methods=['DELETE'])
@require_api_key
@rate_limit('professional')
def delete_tenant(tenant_id):
    """Delete tenant"""
    success = tenant_manager.delete_tenant(tenant_id)
    
    if not success:
        return {'error': 'Tenant not found', 'code': 404}, 404
    
    return {'success': True, 'message': 'Tenant deleted successfully'}


@tenant_bp.route('/<tenant_id>/upgrade', methods=['POST'])
@require_api_key
@rate_limit('basic')
def upgrade_plan(tenant_id):
    """Upgrade tenant subscription plan"""
    try:
        data = request.get_json()
        new_plan = SubscriptionPlan[data['plan']]
        
        tenant = tenant_manager.get_tenant(tenant_id)
        if not tenant:
            return {'error': 'Tenant not found', 'code': 404}, 404
        
        tenant.upgrade_plan(new_plan)
        
        return {
            'success': True,
            'tenant': {
                'tenant_id': tenant.tenant_id,
                'plan': tenant.plan.value,
                'quota': {
                    'max_users': tenant.quota.max_users,
                    'max_knowledge_bases': tenant.quota.max_knowledge_bases,
                    'max_documents': tenant.quota.max_documents,
                    'max_storage_gb': tenant.quota.max_storage_gb,
                }
            }
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@tenant_bp.route('/<tenant_id>/usage', methods=['GET'])
@require_api_key
@rate_limit('basic')
def get_usage(tenant_id):
    """Get tenant resource usage"""
    tenant = tenant_manager.get_tenant(tenant_id)
    
    if not tenant:
        return {'error': 'Tenant not found', 'code': 404}, 404
    
    # Calculate usage percentages
    usage_percent = {
        'users': (tenant.usage.users / tenant.quota.max_users * 100) if tenant.quota.max_users else 0,
        'knowledge_bases': (tenant.usage.knowledge_bases / tenant.quota.max_knowledge_bases * 100) if tenant.quota.max_knowledge_bases else 0,
        'documents': (tenant.usage.documents / tenant.quota.max_documents * 100) if tenant.quota.max_documents else 0,
        'storage': (tenant.usage.storage_gb / tenant.quota.max_storage_gb * 100) if tenant.quota.max_storage_gb else 0,
        'api_calls': (tenant.usage.api_calls_today / tenant.quota.max_api_calls_per_day * 100) if tenant.quota.max_api_calls_per_day else 0,
    }
    
    return {
        'success': True,
        'usage': {
            'current': {
                'users': tenant.usage.users,
                'knowledge_bases': tenant.usage.knowledge_bases,
                'documents': tenant.usage.documents,
                'conversations': tenant.usage.conversations,
                'agents': tenant.usage.agents,
                'storage_gb': tenant.usage.storage_gb,
                'api_calls_today': tenant.usage.api_calls_today,
                'concurrent_requests': tenant.usage.concurrent_requests,
            },
            'quota': {
                'max_users': tenant.quota.max_users,
                'max_knowledge_bases': tenant.quota.max_knowledge_bases,
                'max_documents': tenant.quota.max_documents,
                'max_conversations': tenant.quota.max_conversations,
                'max_agents': tenant.quota.max_agents,
                'max_storage_gb': tenant.quota.max_storage_gb,
                'max_api_calls_per_day': tenant.quota.max_api_calls_per_day,
                'max_concurrent_requests': tenant.quota.max_concurrent_requests,
            },
            'percentage': usage_percent
        }
    }


@tenant_bp.route('/statistics', methods=['GET'])
@require_api_key
@rate_limit('professional')
def get_statistics():
    """Get tenant statistics"""
    stats = tenant_manager.get_statistics()
    
    return {
        'success': True,
        'statistics': stats
    }


@tenant_bp.route('/domain/<domain>', methods=['GET'])
@rate_limit('basic')
def get_tenant_by_domain(domain):
    """Get tenant by domain"""
    tenant = tenant_manager.get_tenant_by_domain(domain)
    
    if not tenant:
        return {'error': 'Tenant not found for domain', 'code': 404}, 404
    
    return {
        'success': True,
        'tenant': {
            'tenant_id': tenant.tenant_id,
            'name': tenant.name,
            'domain': tenant.domain,
            'status': tenant.status.value,
        }
    }
