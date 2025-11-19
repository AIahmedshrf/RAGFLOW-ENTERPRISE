"""
Advanced Security System for RAGFlow Enterprise
Includes API key management, rate limiting, IP whitelisting, and encryption
"""
from typing import List, Dict, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
import hashlib
import secrets
import hmac
import time
from functools import wraps
from flask import request, g
from collections import defaultdict


class APIKeyManager:
    """Manages API keys for tenants and users"""
    
    def __init__(self):
        self.api_keys: Dict[str, Dict[str, Any]] = {}
        self.key_by_hash: Dict[str, str] = {}
    
    def generate_key(
        self,
        tenant_id: str,
        user_id: str,
        name: str,
        permissions: List[str],
        expires_in_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a new API key"""
        # Generate secure random key
        key = f"rsk_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        
        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)
        
        key_data = {
            'key_id': f"key_{len(self.api_keys) + 1}",
            'key_hash': key_hash,
            'tenant_id': tenant_id,
            'user_id': user_id,
            'name': name,
            'permissions': permissions,
            'created_at': datetime.now().isoformat(),
            'expires_at': expires_at.isoformat() if expires_at else None,
            'last_used_at': None,
            'usage_count': 0,
            'is_active': True,
        }
        
        self.api_keys[key_data['key_id']] = key_data
        self.key_by_hash[key_hash] = key_data['key_id']
        
        # Return key only once
        return {
            **key_data,
            'key': key,  # Only returned at creation
        }
    
    def validate_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Validate an API key"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        key_id = self.key_by_hash.get(key_hash)
        
        if not key_id:
            return None
        
        key_data = self.api_keys.get(key_id)
        if not key_data or not key_data['is_active']:
            return None
        
        # Check expiration
        if key_data['expires_at']:
            expires_at = datetime.fromisoformat(key_data['expires_at'])
            if datetime.now() > expires_at:
                key_data['is_active'] = False
                return None
        
        # Update usage
        key_data['last_used_at'] = datetime.now().isoformat()
        key_data['usage_count'] += 1
        
        return key_data
    
    def revoke_key(self, key_id: str) -> bool:
        """Revoke an API key"""
        key_data = self.api_keys.get(key_id)
        if not key_data:
            return False
        
        key_data['is_active'] = False
        return True
    
    def list_keys(
        self,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List API keys"""
        keys = list(self.api_keys.values())
        
        if tenant_id:
            keys = [k for k in keys if k['tenant_id'] == tenant_id]
        
        if user_id:
            keys = [k for k in keys if k['user_id'] == user_id]
        
        # Remove sensitive data
        return [
            {k: v for k, v in key.items() if k != 'key_hash'}
            for key in keys
        ]


class RateLimiter:
    """Rate limiting for API requests"""
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.limits = {
            'default': (100, 60),  # 100 requests per 60 seconds
            'free': (10, 60),      # 10 requests per 60 seconds
            'basic': (100, 60),
            'professional': (1000, 60),
            'enterprise': (10000, 60),
        }
    
    def check_rate_limit(
        self,
        identifier: str,
        tier: str = 'default'
    ) -> tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limit"""
        limit, window = self.limits.get(tier, self.limits['default'])
        current_time = time.time()
        
        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < window
        ]
        
        # Check limit
        current_count = len(self.requests[identifier])
        allowed = current_count < limit
        
        if allowed:
            self.requests[identifier].append(current_time)
        
        # Calculate reset time
        if self.requests[identifier]:
            oldest_request = min(self.requests[identifier])
            reset_at = oldest_request + window
        else:
            reset_at = current_time + window
        
        info = {
            'allowed': allowed,
            'limit': limit,
            'remaining': max(0, limit - current_count - (1 if allowed else 0)),
            'reset_at': reset_at,
            'retry_after': max(0, reset_at - current_time) if not allowed else 0,
        }
        
        return allowed, info
    
    def reset_limit(self, identifier: str):
        """Reset rate limit for an identifier"""
        if identifier in self.requests:
            del self.requests[identifier]


class IPWhitelist:
    """IP address whitelisting"""
    
    def __init__(self):
        self.whitelist: Dict[str, List[str]] = defaultdict(list)
        self.blacklist: set = set()
    
    def add_to_whitelist(self, tenant_id: str, ip_address: str):
        """Add IP to tenant whitelist"""
        if ip_address not in self.whitelist[tenant_id]:
            self.whitelist[tenant_id].append(ip_address)
    
    def remove_from_whitelist(self, tenant_id: str, ip_address: str):
        """Remove IP from tenant whitelist"""
        if ip_address in self.whitelist[tenant_id]:
            self.whitelist[tenant_id].remove(ip_address)
    
    def add_to_blacklist(self, ip_address: str):
        """Add IP to global blacklist"""
        self.blacklist.add(ip_address)
    
    def remove_from_blacklist(self, ip_address: str):
        """Remove IP from blacklist"""
        self.blacklist.discard(ip_address)
    
    def is_allowed(self, tenant_id: str, ip_address: str) -> bool:
        """Check if IP is allowed for tenant"""
        # Check blacklist first
        if ip_address in self.blacklist:
            return False
        
        # If whitelist is empty, allow all
        if not self.whitelist[tenant_id]:
            return True
        
        # Check whitelist
        return ip_address in self.whitelist[tenant_id]
    
    def get_whitelist(self, tenant_id: str) -> List[str]:
        """Get tenant whitelist"""
        return self.whitelist[tenant_id].copy()
    
    def get_blacklist(self) -> List[str]:
        """Get global blacklist"""
        return list(self.blacklist)


class DataEncryption:
    """Data encryption utilities"""
    
    @staticmethod
    def encrypt_field(data: str, key: str) -> str:
        """Encrypt sensitive data"""
        # Simplified encryption (use proper encryption in production like Fernet)
        import base64
        
        # Create HMAC
        signature = hmac.new(
            key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Combine data and signature
        combined = f"{data}:{signature}"
        
        # Base64 encode
        encrypted = base64.b64encode(combined.encode()).decode()
        
        return encrypted
    
    @staticmethod
    def decrypt_field(encrypted_data: str, key: str) -> Optional[str]:
        """Decrypt sensitive data"""
        try:
            import base64
            
            # Base64 decode
            combined = base64.b64decode(encrypted_data.encode()).decode()
            
            # Split data and signature
            data, signature = combined.rsplit(':', 1)
            
            # Verify signature
            expected_signature = hmac.new(
                key.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if hmac.compare_digest(signature, expected_signature):
                return data
            
            return None
        except Exception:
            return None
    
    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """Hash password with salt"""
        if not salt:
            salt = secrets.token_hex(16)
        
        pwd_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000
        ).hex()
        
        return pwd_hash, salt
    
    @staticmethod
    def verify_password(password: str, pwd_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        new_hash, _ = DataEncryption.hash_password(password, salt)
        return hmac.compare_digest(new_hash, pwd_hash)


# Security decorators
def require_api_key(f):
    """Decorator to require valid API key"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not api_key:
            return {'error': 'API key required', 'code': 401}, 401
        
        key_data = api_key_manager.validate_key(api_key)
        if not key_data:
            return {'error': 'Invalid or expired API key', 'code': 401}, 401
        
        # Store key data in request context
        g.api_key_data = key_data
        
        return f(*args, **kwargs)
    
    return decorated


def rate_limit(tier: str = 'default'):
    """Decorator for rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get identifier (IP or API key)
            identifier = request.remote_addr
            if hasattr(g, 'api_key_data'):
                identifier = g.api_key_data['key_id']
            
            allowed, info = rate_limiter.check_rate_limit(identifier, tier)
            
            if not allowed:
                return {
                    'error': 'Rate limit exceeded',
                    'retry_after': info['retry_after'],
                    'limit': info['limit'],
                    'code': 429
                }, 429
            
            # Add rate limit headers to response
            response = f(*args, **kwargs)
            
            if isinstance(response, tuple):
                data, status = response
            else:
                data, status = response, 200
            
            headers = {
                'X-RateLimit-Limit': str(info['limit']),
                'X-RateLimit-Remaining': str(info['remaining']),
                'X-RateLimit-Reset': str(int(info['reset_at'])),
            }
            
            return data, status, headers
        
        return decorated
    return decorator


def check_ip_whitelist(f):
    """Decorator to check IP whitelist"""
    @wraps(f)
    def decorated(*args, **kwargs):
        ip_address = request.remote_addr
        tenant_id = getattr(g, 'tenant_id', 'default')
        
        if not ip_whitelist.is_allowed(tenant_id, ip_address):
            return {'error': 'IP address not whitelisted', 'code': 403}, 403
        
        return f(*args, **kwargs)
    
    return decorated


# Global instances
api_key_manager = APIKeyManager()
rate_limiter = RateLimiter()
ip_whitelist = IPWhitelist()
