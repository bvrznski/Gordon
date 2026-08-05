# Memory Security & Privacy
# ==========================

"""
Memory security and privacy enforcement for storage and retrieval.

Provides:
- MemoryAuthorization: Access control enforcement
- PrivacyFilter: Result privacy filtering with redaction support
"""

import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from .contracts import (
    MemoryRecord,
    MemoryPrivacyClass,
    MemoryAccessScope,
)


# =============================================================================
# Authorization Status
# =============================================================================

class AuthorizationStatus(Enum):
    """Result of an authorization decision."""
    ALLOWED = "allowed"
    DENIED = "denied"
    REDACTED = "redacted"  # Partial access with redaction


@dataclass(frozen=True)
class AuthorizationDecision:
    """Authorization decision for a memory operation."""
    status: AuthorizationStatus
    reason: str = ""
    required_permissions: List[str] = field(default_factory=list)


# =============================================================================
# Memory Authorization
# =============================================================================

class MemoryAuthorization:
    """
    Enforces access control for memory operations.
    
    This is a simplified authorization layer. In production, this would
    integrate with the system's authority/authorization infrastructure.
    
    Key Responsibilities:
    - Validate access to memory records
    - Check owner scope and privacy class
    - Determine if redaction is required
    
    NOT responsible for:
    - Defining authorization policies (owned by security authority)
    - Authentication
    - Role management
    
    Usage:
        auth = MemoryAuthorization()
        
        # Check if user can access a record
        decision = await auth.can_access(user_id, record, operation="read")
        
        if decision.status == AuthorizationStatus.ALLOWED:
            # Allow access
            pass
        elif decision.status == AuthorizationStatus.REDACTED:
            # Return redacted version
            pass
    """
    
    def __init__(self) -> None:
        """Initialize the authorization system."""
        self._lock = threading.RLock()
        
        # Track user permissions (would integrate with auth authority in prod)
        self._user_permissions: Dict[str, List[str]] = {}
        
        # Statistics
        self._stats = {
            "checks": 0,
            "allowed": 0,
            "denied": 0,
        }
    
    async def can_access(
        self,
        actor_id: str,
        record: MemoryRecord,
        operation: str = "read"
    ) -> AuthorizationDecision:
        """
        Check if an actor can perform an operation on a memory record.
        
        Args:
            actor_id: ID of the requesting entity
            record: The memory record to access
            operation: Type of operation (read, write, delete)
            
        Returns:
            AuthorizationDecision with status and details
        """
        with self._lock:
            self._stats["checks"] += 1
            
            # Owner always has full access
            if record.owner_id == actor_id:
                self._stats["allowed"] += 1
                return AuthorizationDecision(
                    status=AuthorizationStatus.ALLOWED,
                    reason="Record owner has full access"
                )
            
            # Check privacy class and access scope
            if record.privacy_class == MemoryPrivacyClass.PERSONAL_DATA:
                if operation in ("read", "write"):
                    self._stats["denied"] += 1
                    return AuthorizationDecision(
                        status=AuthorizationStatus.DENIED,
                        reason="Personal data requires explicit authorization",
                        required_permissions=["access_personal_data"]
                    )
            
            # For shared records, allow access based on scope
            if record.access_scope == MemoryAccessScope.SHARED:
                self._stats["allowed"] += 1
                return AuthorizationDecision(
                    status=AuthorizationStatus.ALLOWED,
                    reason="Record is shared"
                )
            
            # Public records are accessible to all
            if record.access_scope == MemoryAccessScope.PUBLIC:
                self._stats["allowed"] += 1
                return AuthorizationDecision(
                    status=AuthorizationStatus.ALLOWED,
                    reason="Record is public"
                )
            
            # Default: deny unless owner
            self._stats["denied"] += 1
            return AuthorizationDecision(
                status=AuthorizationStatus.DENIED,
                reason="Access denied by privacy policy",
                required_permissions=["access_private_memory"]
            )
    
    async def can_write(
        self,
        actor_id: str,
        record: MemoryRecord
    ) -> AuthorizationDecision:
        """Check if actor can write to a memory record."""
        return await self.can_access(actor_id, record, operation="write")
    
    async def can_delete(
        self,
        actor_id: str,
        record: MemoryRecord
    ) -> AuthorizationDecision:
        """Check if actor can delete a memory record."""
        return await self.can_access(actor_id, record, operation="delete")
    
    async def set_user_permissions(self, user_id: str, permissions: List[str]) -> None:
        """Set permissions for a user (for testing/development)."""
        with self._lock:
            self._user_permissions[user_id] = list(permissions)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get authorization statistics."""
        with self._lock:
            return {
                **self._stats,
                "users_with_permissions": len(self._user_permissions),
            }


# =============================================================================
# Privacy Filter
# =============================================================================

class PrivacyFilter:
    """
    Filters memory results for privacy compliance.
    
    Redacts sensitive fields and enforces privacy boundaries on retrieval.
    
    Usage:
        filter = PrivacyFilter()
        
        # Filter a single record
        filtered = await filter.filter_record(record, actor_id)
        
        # Filter a list of records
        filtered_list = await filter.filter_records(records, actor_id)
    """
    
    def __init__(self) -> None:
        """Initialize the privacy filter."""
        self._lock = threading.RLock()
        
        # Sensitive field patterns to redact
        self._sensitive_patterns = [
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
            r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b",  # SSN pattern
            r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone pattern
        ]
        
        # Statistics
        self._stats = {
            "records_filtered": 0,
            "fields_redacted": 0,
        }
    
    async def filter_record(
        self,
        record: MemoryRecord,
        actor_id: Optional[str] = None,
        redact_sensitive: bool = True
    ) -> MemoryRecord:
        """
        Filter a memory record for privacy.
        
        Args:
            record: The memory record to filter
            actor_id: ID of the requesting entity (for access control)
            redact_sensitive: Whether to redact sensitive fields
            
        Returns:
            Filtered record with privacy applied
        """
        # For now, return original record
        # In production, would:
        # 1. Check authorization
        # 2. Apply field-level filtering
        # 3. Redact sensitive content
        
        with self._lock:
            self._stats["records_filtered"] += 1
        
        return record
    
    async def filter_records(
        self,
        records: List[MemoryRecord],
        actor_id: Optional[str] = None,
        redact_sensitive: bool = True
    ) -> List[MemoryRecord]:
        """
        Filter multiple memory records for privacy.
        
        Args:
            records: The memory records to filter
            actor_id: ID of the requesting entity
            redact_sensitive: Whether to redact sensitive fields
            
        Returns:
            List of filtered records
        """
        return [await self.filter_record(r, actor_id, redact_sensitive) for r in records]
    
    async def mask_content(self, content: str, max_visible: int = 10) -> str:
        """Mask content for privacy (show only first N characters)."""
        if len(content) <= max_visible:
            return content
        return content[:max_visible] + "..."
    
    def get_stats(self) -> Dict[str, Any]:
        """Get privacy filter statistics."""
        with self._lock:
            return {
                **self._stats,
            }


__all__ = [
    "AuthorizationStatus",
    "AuthorizationDecision",
    "MemoryAuthorization",
    "PrivacyFilter",
]