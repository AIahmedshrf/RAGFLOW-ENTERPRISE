"""
Security API Routes
Provides endpoints for API key management, rate limiting, and IP whitelisting
"""
from flask import Blueprint, request, g
from api.security import (
    api_key_manager,
    rate_limiter,
    ip_whitelist,
    require_api_key,
    rate_limit,
    DataEncryption
)


security_bp = Blueprint('security', __name__, url_prefix='/api/v1/security')


# API Key Management
@security_bp.route('/keys', methods=['POST'])
@require_api_key
@rate_limit('professional')
def generate_api_key():
    """Generate a new API key"""
    try:
        data = request.get_json()
        
        key_data = api_key_manager.generate_key(
            tenant_id=data['tenant_id'],
            user_id=data['user_id'],
            name=data['name'],
            permissions=data.get('permissions', ['read']),
            expires_in_days=data.get('expires_in_days')
        )
        
        return {
            'success': True,
            'key': key_data['key'],  # Only shown once
            'key_id': key_data['key_id'],
            'name': key_data['name'],
            'permissions': key_data['permissions'],
            'created_at': key_data['created_at'],
            'expires_at': key_data['expires_at'],
        }, 201
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@security_bp.route('/keys', methods=['GET'])
@require_api_key
@rate_limit('basic')
def list_api_keys():
    """List API keys"""
    tenant_id = request.args.get('tenant_id')
    user_id = request.args.get('user_id')
    
    keys = api_key_manager.list_keys(tenant_id, user_id)
    
    return {
        'success': True,
        'keys': keys,
        'total': len(keys)
    }


@security_bp.route('/keys/<key_id>', methods=['DELETE'])
@require_api_key
@rate_limit('basic')
def revoke_api_key(key_id):
    """Revoke an API key"""
    success = api_key_manager.revoke_key(key_id)
    
    if not success:
        return {'error': 'Key not found', 'code': 404}, 404
    
    return {'success': True, 'message': 'API key revoked'}


@security_bp.route('/keys/validate', methods=['POST'])
@rate_limit('basic')
def validate_api_key():
    """Validate an API key"""
    try:
        data = request.get_json()
        key = data.get('key')
        
        if not key:
            return {'error': 'Key required', 'code': 400}, 400
        
        key_data = api_key_manager.validate_key(key)
        
        if not key_data:
            return {
                'success': True,
                'valid': False,
                'message': 'Invalid or expired key'
            }
        
        return {
            'success': True,
            'valid': True,
            'key_id': key_data['key_id'],
            'tenant_id': key_data['tenant_id'],
            'user_id': key_data['user_id'],
            'permissions': key_data['permissions'],
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


# Rate Limiting
@security_bp.route('/rate-limit/check', methods=['POST'])
@require_api_key
def check_rate_limit():
    """Check rate limit for an identifier"""
    try:
        data = request.get_json()
        identifier = data.get('identifier', request.remote_addr)
        tier = data.get('tier', 'default')
        
        allowed, info = rate_limiter.check_rate_limit(identifier, tier)
        
        return {
            'success': True,
            'rate_limit': info
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@security_bp.route('/rate-limit/reset', methods=['POST'])
@require_api_key
@rate_limit('professional')
def reset_rate_limit():
    """Reset rate limit for an identifier"""
    try:
        data = request.get_json()
        identifier = data['identifier']
        
        rate_limiter.reset_limit(identifier)
        
        return {'success': True, 'message': 'Rate limit reset'}
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


# IP Whitelisting
@security_bp.route('/whitelist/<tenant_id>', methods=['GET'])
@require_api_key
@rate_limit('basic')
def get_whitelist(tenant_id):
    """Get IP whitelist for tenant"""
    ips = ip_whitelist.get_whitelist(tenant_id)
    
    return {
        'success': True,
        'tenant_id': tenant_id,
        'ips': ips,
        'total': len(ips)
    }


@security_bp.route('/whitelist/<tenant_id>', methods=['POST'])
@require_api_key
@rate_limit('basic')
def add_to_whitelist(tenant_id):
    """Add IP to whitelist"""
    try:
        data = request.get_json()
        ip_address = data['ip_address']
        
        ip_whitelist.add_to_whitelist(tenant_id, ip_address)
        
        return {
            'success': True,
            'message': f'IP {ip_address} added to whitelist'
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@security_bp.route('/whitelist/<tenant_id>/<ip_address>', methods=['DELETE'])
@require_api_key
@rate_limit('basic')
def remove_from_whitelist(tenant_id, ip_address):
    """Remove IP from whitelist"""
    ip_whitelist.remove_from_whitelist(tenant_id, ip_address)
    
    return {
        'success': True,
        'message': f'IP {ip_address} removed from whitelist'
    }


@security_bp.route('/blacklist', methods=['GET'])
@require_api_key
@rate_limit('professional')
def get_blacklist():
    """Get global IP blacklist"""
    ips = ip_whitelist.get_blacklist()
    
    return {
        'success': True,
        'ips': ips,
        'total': len(ips)
    }


@security_bp.route('/blacklist', methods=['POST'])
@require_api_key
@rate_limit('professional')
def add_to_blacklist():
    """Add IP to global blacklist"""
    try:
        data = request.get_json()
        ip_address = data['ip_address']
        
        ip_whitelist.add_to_blacklist(ip_address)
        
        return {
            'success': True,
            'message': f'IP {ip_address} added to blacklist'
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@security_bp.route('/blacklist/<ip_address>', methods=['DELETE'])
@require_api_key
@rate_limit('professional')
def remove_from_blacklist(ip_address):
    """Remove IP from blacklist"""
    ip_whitelist.remove_from_blacklist(ip_address)
    
    return {
        'success': True,
        'message': f'IP {ip_address} removed from blacklist'
    }


# Password Management
@security_bp.route('/password/hash', methods=['POST'])
@require_api_key
@rate_limit('basic')
def hash_password():
    """Hash a password"""
    try:
        data = request.get_json()
        password = data['password']
        
        pwd_hash, salt = DataEncryption.hash_password(password)
        
        return {
            'success': True,
            'hash': pwd_hash,
            'salt': salt
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@security_bp.route('/password/verify', methods=['POST'])
@require_api_key
@rate_limit('basic')
def verify_password():
    """Verify a password against hash"""
    try:
        data = request.get_json()
        password = data['password']
        pwd_hash = data['hash']
        salt = data['salt']
        
        valid = DataEncryption.verify_password(password, pwd_hash, salt)
        
        return {
            'success': True,
            'valid': valid
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


# Data Encryption
@security_bp.route('/encrypt', methods=['POST'])
@require_api_key
@rate_limit('basic')
def encrypt_data():
    """Encrypt sensitive data"""
    try:
        data = request.get_json()
        plaintext = data['data']
        key = data.get('key', 'default-encryption-key')  # Should use proper key management
        
        encrypted = DataEncryption.encrypt_field(plaintext, key)
        
        return {
            'success': True,
            'encrypted': encrypted
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400


@security_bp.route('/decrypt', methods=['POST'])
@require_api_key
@rate_limit('basic')
def decrypt_data():
    """Decrypt sensitive data"""
    try:
        data = request.get_json()
        encrypted = data['encrypted']
        key = data.get('key', 'default-encryption-key')
        
        plaintext = DataEncryption.decrypt_field(encrypted, key)
        
        if plaintext is None:
            return {'error': 'Decryption failed', 'code': 400}, 400
        
        return {
            'success': True,
            'data': plaintext
        }
    except Exception as e:
        return {'error': str(e), 'code': 400}, 400
