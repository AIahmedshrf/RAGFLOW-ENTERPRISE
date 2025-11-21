"""
Whitelist Service - Database access layer for registration whitelist
"""
import logging
from typing import List, Optional, Dict, Any
from api.db.db_models import Whitelist
from api.db import StatusEnum


class WhitelistService:
    """Service for managing whitelist entries"""
    
    @staticmethod
    def get_all() -> List[Whitelist]:
        """Get all whitelist entries"""
        try:
            return list(Whitelist.select())
        except Exception as e:
            logging.error(f"get_all whitelist error: {e}")
            return []
    
    @staticmethod
    def get_by_id(entry_id: int) -> Optional[Whitelist]:
        """Get whitelist entry by ID"""
        try:
            return Whitelist.get_by_id(entry_id)
        except Exception as e:
            logging.error(f"get_by_id whitelist error: {e}")
            return None
    
    @staticmethod
    def get_by_email(email: str) -> Optional[Whitelist]:
        """Get whitelist entry by email"""
        try:
            return Whitelist.get(Whitelist.email == email)
        except Whitelist.DoesNotExist:
            return None
        except Exception as e:
            logging.error(f"get_by_email whitelist error: {e}")
            return None
    
    @staticmethod
    def exists(email: str) -> bool:
        """Check if email exists in whitelist"""
        return WhitelistService.get_by_email(email) is not None
    
    @staticmethod
    def create(email: str) -> Optional[Whitelist]:
        """Create new whitelist entry"""
        try:
            entry = Whitelist.create(email=email)
            return entry
        except Exception as e:
            logging.error(f"create whitelist error: {e}")
            return None
    
    @staticmethod
    def update_by_id(entry_id: int, email: str) -> bool:
        """Update whitelist entry by ID"""
        try:
            entry = WhitelistService.get_by_id(entry_id)
            if not entry:
                return False
            entry.email = email
            entry.save()
            return True
        except Exception as e:
            logging.error(f"update whitelist error: {e}")
            return False
    
    @staticmethod
    def delete_by_email(email: str) -> bool:
        """Delete whitelist entry by email"""
        try:
            entry = WhitelistService.get_by_email(email)
            if not entry:
                return False
            entry.delete_instance()
            return True
        except Exception as e:
            logging.error(f"delete whitelist error: {e}")
            return False
    
    @staticmethod
    def delete_by_id(entry_id: int) -> bool:
        """Delete whitelist entry by ID"""
        try:
            entry = WhitelistService.get_by_id(entry_id)
            if not entry:
                return False
            entry.delete_instance()
            return True
        except Exception as e:
            logging.error(f"delete whitelist error: {e}")
            return False
    
    @staticmethod
    def batch_create(emails: List[str]) -> Dict[str, Any]:
        """Batch create whitelist entries"""
        success_count = 0
        failed_emails = []
        
        for email in emails:
            if WhitelistService.exists(email):
                failed_emails.append({"email": email, "reason": "Already exists"})
                continue
            
            if WhitelistService.create(email):
                success_count += 1
            else:
                failed_emails.append({"email": email, "reason": "Creation failed"})
        
        return {
            "success_count": success_count,
            "failed_count": len(failed_emails),
            "failed_emails": failed_emails
        }
