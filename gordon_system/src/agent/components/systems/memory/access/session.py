# Memory Access Session - Phase 5.1.3 Canonical Access Context
# ===============================================================

"""
Memory Access Session: Context and state for memory access operations.

Every access interaction belongs to a session that maintains:
    - identity (session identifier)
    - requester (who/what is making the request)
    - permissions (what this requester may do)
    - visibility scope (which artifacts are visible in this context)
    - lifetime (when the session expires)
    - provenance (how this session was created)
    - statistics (metrics collected during session)

Session Laws:
    SESSION-LAW-001: Every access interaction belongs to a session
    SESSION-LAW-002: Sessions possess explicit identity
    SESSION-LAW-003: Sessions preserve requester identity
    SESSION-LAW-004: Sessions preserve authorization context
    SESSION-LAW-005: Sessions preserve publication history
    SESSION-LAW-006: Sessions remain observable
    SESSION-LAW-007: Session termination preserves diagnostics
    SESSION-LAW-008: Session behavior remains deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# SESSION TYPES - What kind of session?
# =============================================================================


class AccessSessionType(Enum):
    """
    Types of access sessions.
    
    | Type       | Description                                      |
    |------------|-------------------------------------------------|
    | INTERNAL   | Internal architecture access                     |
    | EXTERNAL   | External API/plugin access                       |
    | PERSISTENT | Long-term historical access                      |
    | TRANSIENT  | Temporary working memory access                  |
    """
    
    INTERNAL = "internal"
    EXTERNAL = "external"
    PERSISTENT = "persistent"
    TRANSIENT = "transient"


# =============================================================================
# SESSION PERMISSIONS - What may be done?
# =============================================================================


class AccessPermission(Enum):
    """
    Permissions that can be granted in a session.
    
    | Permission      | Description                                  |
    |-----------------|----------------------------------------------|
    | READ            | Read artifacts from memory                   |
    | QUERY           | Execute queries                              |
    | PROJECT         | Generate projections                         |
    | PUBLISH         | Publish projections to consumer              |
    | STATS           | Access statistics and diagnostics            |
    | AUTH_ADMIN      | Modify authorization policies (rare)         |
    """
    
    READ = "read"
    QUERY = "query"
    PROJECT = "project"
    PUBLISH = "publish"
    STATS = "stats"
    AUTH_ADMIN = "auth_admin"


# =============================================================================
# ACCESS SESSION - Context for memory access
# =============================================================================


@dataclass(frozen=True)
class MemoryAccessSession:
    """
    Context and state for a memory access interaction.
    
    Every access request must belong to a session. The session maintains
    the context needed to make authorization, visibility, and publication
    decisions.
    
    Fields:
        session_id:          Unique identifier for this session
        
        # Consumer identity
        requester_id:        Who/what is making requests?
        requester_type:      What kind of consumer? (reasoning, api, plugin, etc.)
        
        # Authorization context
        permissions:         Which permissions are granted?
        authorization_policy: Reference to policy used for decisions
        
        # Visibility scope
        visibility_scope:    Which artifacts may be visible?
        excluded_artifacts:  Which artifacts must be hidden?
        
        # Lifetime
        created_at_utc:      When was the session created?
        expires_at_utc:      When does it expire? (0 = never)
        max_duration_sec:    Maximum allowed duration
        
        # Statistics
        request_count:       Number of requests made
        publication_count:   Number of publications made
        last_request_at_utc: When was last request processed?
        
        # Provenance
        created_by:          Who/what created this session?
        purpose:             Why was it created?
        
        # Diagnostics
        status:              Active, expired, terminated, etc.
    """
    
    # Core identity (required)
    session_id: str
    
    # Consumer identity
    requester_id: str
    requester_type: str  # reasoning, planning, api, plugin, etc.
    
    # Authorization context
    permissions: Tuple[AccessPermission, ...]
    authorization_policy: Optional[str] = None  # Policy name/ID
    
    # Visibility scope (optional)
    visibility_scope: Dict[str, Any] = field(default_factory=dict)
    excluded_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    expires_at_utc: float = 0.0  # 0 = no expiration
    max_duration_sec: float = 3600.0  # Default: 1 hour
    
    # Statistics
    request_count: int = 0
    publication_count: int = 0
    last_request_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    created_by: Optional[str] = None  # Who created this session?
    purpose: Optional[str] = None     # Why was it created?
    
    # Diagnostics
    status: str = "active"  # active, expired, terminated
    
    @property
    def is_expired(self) -> bool:
        """Check if the session has expired."""
        if self.expires_at_utc <= 0.0:
            return False
        return time.time() > self.expires_at_utc
    
    @property
    def remaining_seconds(self) -> float:
        """Get remaining lifetime in seconds (0 or negative if expired)."""
        if self.expires_at_utc <= 0.0:
            return float('inf')
        return max(0.0, self.expires_at_utc - time.time())
    
    def has_permission(self, permission: AccessPermission) -> bool:
        """Check if this session has a specific permission."""
        return permission in self.permissions
    
    def record_request(self) -> "MemoryAccessSession":
        """Increment request count and update timestamp."""
        return dataclass_replace(
            self,
            request_count=self.request_count + 1,
            last_request_at_utc=time.time(),
        )
    
    def record_publication(self) -> "MemoryAccessSession":
        """Increment publication count and update timestamp."""
        return dataclass_replace(
            self,
            publication_count=self.publication_count + 1,
            last_request_at_utc=time.time(),
        )
    
    def with_expiration(self, duration_sec: float) -> "MemoryAccessSession":
        """Set expiration to now + duration seconds."""
        return dataclass_replace(
            self,
            expires_at_utc=time.time() + duration_sec,
        )
    
    @classmethod
    def create_internal(
        cls,
        requester_id: str,
        permissions: Tuple[AccessPermission, ...] = tuple(),
        purpose: Optional[str] = None,
    ) -> "MemoryAccessSession":
        """
        Create an internal access session.
        
        Args:
            requester_id: Which internal component is requesting?
            permissions: What operations are allowed (defaults to read/query/project)
            purpose: Why was this created? (optional)
            
        Returns:
            New MemoryAccessSession with internal context
        """
        if not permissions:
            permissions = (
                AccessPermission.READ,
                AccessPermission.QUERY,
                AccessPermission.PROJECT,
            )
        
        return cls(
            session_id=str(uuid.uuid4()),
            requester_id=requester_id,
            requester_type="internal",
            permissions=permissions,
            purpose=purpose or f"Internal access for {requester_id}",
            created_by="system",
        )
    
    @classmethod
    def create_external(
        cls,
        requester_id: str,
        consumer_type: str,
        permissions: Tuple[AccessPermission, ...] = tuple(),
        expires_in_sec: float = 3600.0,
        purpose: Optional[str] = None,
    ) -> "MemoryAccessSession":
        """
        Create an external access session.
        
        Args:
            requester_id: External identifier (user, API key, etc.)
            consumer_type: Type of external consumer
            permissions: What operations are allowed (defaults to read-only)
            expires_in_sec: How long until expiration? (default: 1 hour)
            purpose: Why was this created? (optional)
            
        Returns:
            New MemoryAccessSession with external context
        """
        if not permissions:
            permissions = (AccessPermission.READ,)
        
        session = cls(
            session_id=str(uuid.uuid4()),
            requester_id=requester_id,
            requester_type=consumer_type,
            permissions=permissions,
            purpose=purpose or f"External access for {requester_id}",
            created_by="system",
        )
        return session.with_expiration(expires_in_sec)
    
    def terminate(self, reason: Optional[str] = None) -> "MemoryAccessSession":
        """Terminate this session with a diagnostic note."""
        return dataclass_replace(
            self,
            status="terminated",
            excluded_artifacts=self.excluded_artifacts + (f"termination:{reason or 'unknown'}",),
        )


# =============================================================================
# SESSION BUILDER - Mutable builder for sessions
# =============================================================================


class MemoryAccessSessionFactory:
    """
    Mutable builder for constructing access sessions.
    
    Allows incremental configuration before producing an immutable session.
    """
    
    def __init__(self):
        self._session_id: Optional[str] = None
        self._requester_id: Optional[str] = None
        self._requester_type: str = "unknown"
        
        # Authorization context
        self._permissions: List[AccessPermission] = []
        self._authorization_policy: Optional[str] = None
        
        # Visibility scope
        self._visibility_scope: Dict[str, Any] = {}
        self._excluded_artifacts: List[str] = []
        
        # Timestamps
        self._created_at_utc: float = time.time()
        self._expires_at_utc: float = 0.0
        self._max_duration_sec: float = 3600.0
        
        # Statistics (start fresh)
        self._request_count: int = 0
        self._publication_count: int = 0
        
        # Provenance
        self._created_by: Optional[str] = None
        self._purpose: Optional[str] = None
    
    def set_session_id(self, session_id: str) -> "MemoryAccessSessionFactory":
        """Set the session ID."""
        self._session_id = session_id
        return self
    
    def set_requester_id(self, requester_id: str) -> "MemoryAccessSessionFactory":
        """Set the requester identifier."""
        self._requester_id = requester_id
        return self
    
    def set_requester_type(self, requester_type: str) -> "MemoryAccessSessionFactory":
        """Set the requester type (reasoning, api, plugin, etc.)."""
        self._requester_type = requester_type
        return self
    
    def add_permission(self, permission: AccessPermission) -> "MemoryAccessSessionFactory":
        """Add a permission to this session."""
        if permission not in self._permissions:
            self._permissions.append(permission)
        return self
    
    def set_permissions(self, permissions: Tuple[AccessPermission, ...]) -> "MemoryAccessSessionFactory":
        """Set all permissions at once."""
        self._permissions = list(permissions)
        return self
    
    def set_authorization_policy(self, policy_id: str) -> "MemoryAccessSessionFactory":
        """Set the authorization policy to use for decisions."""
        self._authorization_policy = policy_id
        return self
    
    def add_visibility_constraint(
        self,
        key: str,
        value: Any,
    ) -> "MemoryAccessSessionFactory":
        """Add a visibility constraint (e.g., 'artifact_kind': 'observation')."""
        self._visibility_scope[key] = value
        return self
    
    def exclude_artifact(self, artifact_id: str) -> "MemoryAccessSessionFactory":
        """Exclude an artifact from visibility in this session."""
        if artifact_id not in self._excluded_artifacts:
            self._excluded_artifacts.append(artifact_id)
        return self
    
    def set_expiration_seconds(self, duration_sec: float) -> "MemoryAccessSessionFactory":
        """Set expiration time relative to now."""
        self._expires_at_utc = time.time() + duration_sec
        return self
    
    def set_created_by(self, created_by: str) -> "MemoryAccessSessionFactory":
        """Set who/what created this session."""
        self._created_by = created_by
        return self
    
    def set_purpose(self, purpose: str) -> "MemoryAccessSessionFactory":
        """Set the purpose for creating this session."""
        self._purpose = purpose
        return self
    
    def build(self) -> MemoryAccessSession:
        """
        Build an immutable MemoryAccessSession.
        
        Returns:
            New MemoryAccessSession with all settings applied
            
        Raises:
            ValueError: If required fields are missing
        """
        if not self._session_id:
            self._session_id = str(uuid.uuid4())
        if not self._requester_id:
            raise ValueError("requester_id is required")
        
        return MemoryAccessSession(
            session_id=self._session_id,
            requester_id=self._requester_id,
            requester_type=self._requester_type,
            permissions=tuple(self._permissions),
            authorization_policy=self._authorization_policy,
            visibility_scope=dict(self._visibility_scope),
            excluded_artifacts=tuple(self._excluded_artifacts),
            created_at_utc=self._created_at_utc,
            expires_at_utc=self._expires_at_utc,
            max_duration_sec=self._max_duration_sec,
            request_count=self._request_count,
            publication_count=self._publication_count,
            last_request_at_utc=time.time(),
            created_by=self._created_by,
            purpose=self._purpose,
            status="active",
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def dataclass_replace(instance: MemoryAccessSession, **kwargs) -> MemoryAccessSession:
    """Replace fields in a frozen dataclass."""
    return MemoryAccessSession(
        session_id=instance.session_id,
        requester_id=kwargs.get("requester_id", instance.requester_id),
        requester_type=kwargs.get("requester_type", instance.requester_type),
        permissions=kwargs.get("permissions", instance.permissions),
        authorization_policy=kwargs.get("authorization_policy", instance.authorization_policy),
        visibility_scope=dict(instance.visibility_scope) if "visibility_scope" not in kwargs else kwargs["visibility_scope"],
        excluded_artifacts=kwargs.get("excluded_artifacts", instance.excluded_artifacts),
        created_at_utc=kwargs.get("created_at_utc", instance.created_at_utc),
        expires_at_utc=kwargs.get("expires_at_utc", instance.expires_at_utc),
        max_duration_sec=kwargs.get("max_duration_sec", instance.max_duration_sec),
        request_count=kwargs.get("request_count", instance.request_count),
        publication_count=kwargs.get("publication_count", instance.publication_count),
        last_request_at_utc=kwargs.get("last_request_at_utc", instance.last_request_at_utc),
        created_by=kwargs.get("created_by", instance.created_by),
        purpose=kwargs.get("purpose", instance.purpose),
        status=kwargs.get("status", instance.status),
    )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MemoryAccessSession",
    "AccessSessionType",
    "AccessPermission",
    "MemoryAccessSessionFactory",
    "dataclass_replace",
]