# Core Authority System
# =====================
"""
Core runtime authority management.

Provides:
- Authority grants and revocation
- Delegation with constraints
- Policy evaluation
- Access control validation

Phase 3.7: Runtime third-stage expansion - Authority subsystem.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Callable, Any
from enum import Enum
import time


# =============================================================================
# Authority Types
# =============================================================================

class AuthorityType(Enum):
    """
    Types of authorities in the runtime system.
    
    Each authority governs a specific domain:
        - LIFECYCLE: Entity lifecycle transitions
        - EXECUTION: Task execution and scheduling
        - STATE: State read/write operations
        - REGISTRY: Entity registration and lookup
        - SCHEDULING: Task scheduling decisions
        - OBSERVABILITY: Event emission and logging
        - INTEGRITY: Validation and verification operations
    """
    
    LIFECYCLE = "lifecycle"
    EXECUTION = "execution"
    STATE = "state"
    REGISTRY = "registry"
    SCHEDULING = "scheduling"
    OBSERVABILITY = "observability"
    INTEGRITY = "integrity"


@dataclass(frozen=True)
class AuthorityId:
    """
    Unique identifier for an authority.
    
    Format: <domain>/<authority_name>
    Example: lifecycle/stop_entity
    """
    
    domain: str
    name: str
    
    @classmethod
    def from_string(cls, s: str) -> "AuthorityId":
        """Parse authority ID from string."""
        parts = s.split("/", 1)
        if len(parts) == 2:
            return cls(domain=parts[0], name=parts[1])
        return cls(domain="unknown", name=s)
    
    def __str__(self) -> str:
        return f"{self.domain}/{self.name}"


# =============================================================================
# Authority Grant
# =============================================================================

@dataclass(frozen=True)
class AuthorityGrant:
    """
    A grant of authority from an issuer to a subject.
    
    Grants are time-bound and can be revoked.
    
    Usage:
        grant = AuthorityGrant(
            issuer=EntityId("authority_system"),
            subject=EntityId("my_service"),
            authority_id=AuthorityId("lifecycle", "start_entity"),
            conditions={"max_duration": 3600}
        )
        
        # Check if grant is still valid
        if grant.is_valid():
            # Authorize the action
            pass
    """
    
    grant_id: str
    
    issuer: Any  # EntityId or similar identifier
    subject: Any  # Who receives the authority
    
    authority_id: AuthorityId
    
    # Time bounds
    granted_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    
    # Constraints
    max_uses: Optional[int] = None
    uses_remaining: Optional[int] = None
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_valid(self) -> bool:
        """Check if grant is still valid (not expired)."""
        if self.expires_at is not None and time.time() > self.expires_at:
            return False
        if self.uses_remaining is not None and self.uses_remaining <= 0:
            return False
        return True
    
    @property
    def duration_seconds(self) -> Optional[float]:
        """Return grant duration if time-bounded."""
        if self.expires_at is None:
            return None
        return self.expires_at - self.granted_at
    
    def consume_use(self) -> "AuthorityGrant":
        """Return a copy with one use consumed."""
        if self.uses_remaining is None:
            return self
        
        return AuthorityGrant(
            grant_id=self.grant_id,
            issuer=self.issuer,
            subject=self.subject,
            authority_id=self.authority_id,
            granted_at=self.granted_at,
            expires_at=self.expires_at,
            max_uses=self.max_uses,
            uses_remaining=max(0, self.uses_remaining - 1),
            conditions=dict(self.conditions)
        )


# =============================================================================
# Delegation Chain
# =============================================================================

@dataclass(frozen=True)
class Delegation:
    """
    A delegation of authority from one entity to another.
    
    Delegations form chains: issuer -> delegate -> sub-delegate
    
    Usage:
        delegation = Delegation(
            delegator=EntityId("service_a"),
            delegate=EntityId("service_b"),
            authority_id=AuthorityId("state", "read_state")
        )
        
        # Check if a chain is valid
        if delegation_chain.is_valid():
            pass
    """
    
    delegation_id: str
    
    delegator: Any  # Original authority holder
    delegate: Any   # Who receives delegated authority
    
    authority_id: AuthorityId
    
    granted_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    
    # Chain depth (for bounded delegation)
    max_depth: int = 1
    current_depth: int = 0
    
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def can_delegate_further(self) -> bool:
        """Check if this delegate can further delegate."""
        return self.current_depth < self.max_depth
    
    @property
    def is_valid(self) -> bool:
        """Check if delegation is still valid."""
        if self.expires_at is not None and time.time() > self.expires_at:
            return False
        return True


# =============================================================================
# Authority Manager
# =============================================================================

class AuthorityManager:
    """
    Manages authority grants, delegations, and revocations.
    
    Provides:
        - Grant issuance with constraints
        - Delegation tracking with depth limits
        - Revocation of all grants for a subject
        - Authorization checks
    
    Usage:
        manager = AuthorityManager()
        
        # Issue a grant
        grant = manager.grant_authority(
            issuer=system_entity,
            subject=service_id,
            authority_id=AuthorityId("lifecycle", "start")
        )
        
        # Check authorization
        if manager.authorized(subject, authority_id):
            pass
        
        # Revoke all grants for a subject
        revoked = manager.revoke_authority(subject)
    """
    
    def __init__(self) -> None:
        self._grants: Dict[str, AuthorityGrant] = {}
        self._delegations: List[Delegation] = []
        self._revocations: Set[str] = set()
        self._lock = __import__("threading").Lock()
    
    def grant_authority(
        self,
        issuer: Any,
        subject: Any,
        authority_id: AuthorityId,
        expires_at: Optional[float] = None,
        max_uses: Optional[int] = None,
        **conditions
    ) -> AuthorityGrant:
        """
        Grant authority to a subject.
        
        Args:
            issuer: The authority issuing the grant
            subject: Who receives the authority
            authority_id: What authority is granted
            expires_at: When grant expires (optional)
            max_uses: Maximum uses allowed (optional)
            **conditions: Additional constraint key-value pairs
            
        Returns:
            The issued AuthorityGrant
        """
        import uuid
        
        with self._lock:
            grant = AuthorityGrant(
                grant_id=f"grant_{uuid.uuid4().hex[:8]}",
                issuer=issuer,
                subject=subject,
                authority_id=authority_id,
                expires_at=expires_at,
                max_uses=max_uses,
                uses_remaining=max_uses,
                conditions=dict(conditions)
            )
            
            self._grants[grant.grant_id] = grant
            return grant
    
    def delegate_authority(
        self,
        delegator: Any,
        delegate: Any,
        authority_id: AuthorityId,
        max_depth: int = 1,
        **conditions
    ) -> Delegation:
        """
        Create a delegation of authority.
        
        Args:
            delegator: Current authority holder
            delegate: Who receives the delegated authority
            authority_id: What authority is delegated
            max_depth: Maximum chain depth allowed
            **conditions: Additional constraints
            
        Returns:
            The created Delegation
        """
        import uuid
        
        delegation = Delegation(
            delegation_id=f"deleg_{uuid.uuid4().hex[:8]}",
            delegator=delegator,
            delegate=delegate,
            authority_id=authority_id,
            max_depth=max_depth,
            current_depth=0,
            conditions=dict(conditions)
        )
        
        with self._lock:
            self._delegations.append(delegation)
        
        return delegation
    
    def authorized(self, subject: Any, authority_id: AuthorityId) -> bool:
        """
        Check if a subject has authority for an operation.
        
        Checks:
            - Direct grants to subject
            - Delegation chains leading to subject
        
        Args:
            subject: Who is requesting authority
            authority_id: What authority is needed
            
        Returns:
            True if authorized, False otherwise
        """
        with self._lock:
            # Check direct grants
            for grant in self._grants.values():
                if (grant.subject == subject and 
                    grant.authority_id == authority_id and
                    grant.is_valid):
                    return True
            
            # Check delegations
            for delegation in self._delegations:
                if (delegation.delegate == subject and
                    delegation.authority_id == authority_id and
                    delegation.is_valid):
                    return True
            
            return False
    
    def revoke_authority(self, subject: Any) -> List[str]:
        """
        Revoke all grants to a subject.
        
        Args:
            subject: Who loses authority
            
        Returns:
            List of revoked grant IDs
        """
        revoked = []
        
        with self._lock:
            to_remove = [
                grant_id for grant_id, grant in self._grants.items()
                if grant.subject == subject
            ]
            
            for grant_id in to_remove:
                del self._grants[grant_id]
                self._revocations.add(grant_id)
                revoked.append(grant_id)
        
        return revoked
    
    def revoke_authority_by_id(self, grant_id: str) -> bool:
        """Revoke a specific grant by ID."""
        with self._lock:
            if grant_id in self._grants:
                del self._grants[grant_id]
                self._revocations.add(grant_id)
                return True
            return False
    
    def get_grants_for(self, subject: Any) -> List[AuthorityGrant]:
        """Get all grants for a subject."""
        with self._lock:
            return [
                grant for grant in self._grants.values()
                if grant.subject == subject and grant.is_valid
            ]
    
    @property
    def active_grants(self) -> int:
        """Return count of active (non-revoked) grants."""
        with self._lock:
            return len(self._grants)
    
    @property
    def total_revocations(self) -> int:
        """Return total number of revocations."""
        return len(self._revocations)


__all__ = [
    # Authority types
    "AuthorityType",
    "AuthorityId",
    
    # Grants and delegation
    "AuthorityGrant",
    "Delegation",
    
    # Manager
    "AuthorityManager",
]