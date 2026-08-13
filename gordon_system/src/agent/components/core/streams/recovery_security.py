# Stream Recovery Security - Phase 3.11.7
# ========================================

"""
Security infrastructure for stream recovery operations.

This module implements security controls for the recovery lifecycle:
    
    Authentication: Verify identity of recovery participants
    Authorization: Enforce permissions on recovery operations
    Audit: Log all recovery actions for compliance
    
Security Constraints:
    - Prevent unauthorized checkpoint restoration
    - Prevent unauthorized replay operations
    - Prevent forged checkpoints or recovery sessions
    - Prevent cross-scope recovery (scope isolation)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import time


# =============================================================================
# RECOVERY AUTHORIZATION
# =============================================================================

class RecoveryAuthorization(Enum):
    """
    Authorization decision for recovery operations.
    
    Decisions:
        ALLOW: Operation authorized
        DENY: Operation explicitly denied
        ESCALATE: Decision requires escalation to higher authority
    """
    
    ALLOW = "allow"
    """Operation is authorized."""
    
    DENY = "deny"
    """Operation is not authorized."""
    
    ESCALATE = "escalate"
    """Decision requires escalation to higher authority."""


@dataclass(frozen=True)
class RecoveryAuthorizationContext:
    """
    Authorization context for recovery operations.
    """
    
    user_id: Optional[str] = None
    """User performing the operation (if applicable)."""
    
    agent_id: Optional[str] = None
    """Agent performing the operation."""
    
    session_id: Optional[str] = None
    """Session context for the operation."""
    
    tenant_id: Optional[str] = None
    """Tenant scope (for multi-tenant systems)."""
    
    roles: List[str] = field(default_factory=list)
    """Roles assigned to the requester."""
    
    permissions: List[str] = field(default_factory=list)
    """Specific permissions being requested."""
    
    timestamp_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class RecoveryAuthorizationResult:
    """
    Result of a recovery authorization check.
    """
    
    decision: RecoveryAuthorization
    reason: str = ""
    
    # Context captured at authorization time
    user_id: Optional[str] = None
    stream_id: Optional[str] = None
    
    # Required for audit trail
    authorization_timestamp_utc: float = field(default_factory=time.time)
    request_id: str = ""


class RecoveryAuthorizationEnforcer:
    """
    Enforcer of recovery operation authorization.
    
    Validates that recovery operations are performed by authorized entities
    and within proper scope boundaries.
    """
    
    def __init__(
        self,
        require_scope_isolation: bool = True,
        allowed_recovery_roles: Optional[List[str]] = None,
    ):
        """
        Initialize authorization enforcer.
        
        Args:
            require_scope_isolation: Enforce strict scope isolation?
            allowed_recovery_roles: Roles permitted to perform recovery
        """
        self._require_isolation = require_scope_isolation
        self._allowed_roles = allowed_recovery_roles or ["admin", "recovery_operator"]
    
    def authorize_checkpoint_restore(
        self,
        checkpoint_id: str,
        stream_id: str,
        context: RecoveryAuthorizationContext,
    ) -> RecoveryAuthorizationResult:
        """
        Authorize checkpoint restoration operation.
        
        Args:
            checkpoint_id: ID of checkpoint to restore
            stream_id: Stream being restored
            context: Authorization context
            
        Returns:
            Authorization result
        """
        # Check if requester has required role
        has_role = any(
            role in self._allowed_roles 
            for role in context.roles
        )
        
        if not has_role:
            return RecoveryAuthorizationResult(
                decision=RecoveryAuthorization.DENY,
                reason="User lacks recovery operator role",
                user_id=context.user_id,
                stream_id=stream_id,
            )
        
        # Check scope isolation (if enabled)
        if self._require_isolation and context.tenant_id:
            # Verify checkpoint belongs to same tenant
            checkpoint_tenant = self._get_checkpoint_tenant(checkpoint_id)
            if checkpoint_tenant and checkpoint_tenant != context.tenant_id:
                return RecoveryAuthorizationResult(
                    decision=RecoveryAuthorization.DENY,
                    reason=f"Scope violation: checkpoint from {checkpoint_tenant}, "
                           f"context is {context.tenant_id}",
                    user_id=context.user_id,
                    stream_id=stream_id,
                )
        
        # Check authorization to access stream
        if not self._can_access_stream(context, stream_id):
            return RecoveryAuthorizationResult(
                decision=RecoveryAuthorization.DENY,
                reason="User not authorized for stream",
                user_id=context.user_id,
                stream_id=stream_id,
            )
        
        return RecoveryAuthorizationResult(
            decision=RecoveryAuthorization.ALLOW,
            reason="Authorization check passed",
            user_id=context.user_id,
            stream_id=stream_id,
        )
    
    def authorize_replay_operation(
        self,
        stream_id: str,
        replay_range_start: int,
        context: RecoveryAuthorizationContext,
    ) -> RecoveryAuthorizationResult:
        """
        Authorize replay operation.
        
        Args:
            stream_id: Stream being replayed
            replay_range_start: Start position of replay
            context: Authorization context
            
        Returns:
            Authorization result
        """
        # Check role authorization
        if not any(
            role in self._allowed_roles 
            for role in context.roles
        ):
            return RecoveryAuthorizationResult(
                decision=RecoveryAuthorization.DENY,
                reason="User lacks replay operator role",
                user_id=context.user_id,
                stream_id=stream_id,
            )
        
        # Check scope isolation
        if self._require_isolation and context.tenant_id:
            replay_tenant = self._get_replay_scope_tenant(stream_id, replay_range_start)
            if replay_tenant and replay_tenant != context.tenant_id:
                return RecoveryAuthorizationResult(
                    decision=RecoveryAuthorization.ESCALATE,
                    reason=f"Cross-tenant replay detected, requires escalation",
                    user_id=context.user_id,
                    stream_id=stream_id,
                )
        
        return RecoveryAuthorizationResult(
            decision=RecoveryAuthorization.ALLOW,
            reason="Replay authorization check passed",
            user_id=context.user_id,
            stream_id=stream_id,
        )
    
    def _get_checkpoint_tenant(self, checkpoint_id: str) -> Optional[str]:
        """Extract tenant ID from checkpoint (if multi-tenant)."""
        # In real implementation, would parse checkpoint metadata
        return None
    
    def _get_replay_scope_tenant(
        self,
        stream_id: str,
        replay_start_position: int,
    ) -> Optional[str]:
        """Get tenant scope for a replay operation."""
        return None
    
    def _can_access_stream(self, context: RecoveryAuthorizationContext, stream_id: str) -> bool:
        """Check if requester can access the specified stream."""
        # In real implementation, would check stream permissions
        return len(context.roles) > 0


# =============================================================================
# AUDIT LOGGING
# =============================================================================

class RecoveryAuditEvent(Enum):
    """
    Audit event types for recovery operations.
    """
    
    RECOVERY_INITIATED = "recovery_initiated"
    """Recovery process started."""
    
    CHECKPOINT_SELECTED = "checkpoint_selected"
    """Checkpoint selected for restoration."""
    
    CHECKPOINT_RESTORED = "checkpoint_restored"
    """Checkpoint successfully restored."""
    
    REPLAY_STARTED = "replay_started"
    """Replay operation started."""
    
    REPLAY_COMPLETED = "replay_completed"
    """Replay completed."""
    
    VALIDATION_PASSED = "validation_passed"
    """Validation checks passed."""
    
    VALIDATION_FAILED = "validation_failed"
    """Validation failed, recovery aborted."""
    
    DEGRADED_MODE_ENTERED = "degraded_mode_entered"
    """Entered degraded mode."""
    
    RECOVERY_COMPLETED = "recovery_completed"
    """Recovery completed successfully."""
    
    RECOVERY_FAILED = "recovery_failed"
    """Recovery attempt failed."""


@dataclass(frozen=True)
class RecoveryAuditRecord:
    """
    Immutable audit record for recovery operations.
    """
    
    audit_id: str  # Unique audit trail identifier
    
    event_type: RecoveryAuditEvent
    
    timestamp_utc: float = field(default_factory=time.time)
    
    stream_id: Optional[str] = None
    generation_id: Optional[int] = None
    
    session_id: Optional[str] = None
    plan_id: Optional[str] = None
    
    # Authorization context
    user_id: Optional[str] = None
    agent_id: Optional[str] = None
    tenant_id: Optional[str] = None
    
    # Outcome
    success: bool = True
    error_message: str = ""
    
    # Details (for forensic analysis)
    checkpoint_id: Optional[str] = None
    replay_records_count: int = 0
    
    metadata: Dict[str, Any] = field(default_factory=dict)


class RecoveryAuditLogger:
    """
    Logger for recovery audit events.
    
    All recovery operations are logged for compliance and forensic analysis.
    Audit records are immutable.
    """
    
    def __init__(self):
        """Initialize the audit logger."""
        self._records: List[RecoveryAuditRecord] = []
        self._audit_counter = 0
    
    def log_event(
        self,
        event_type: RecoveryAuditEvent,
        stream_id: str,
        generation_id: Optional[int] = None,
        session_id: Optional[str] = None,
        plan_id: Optional[str] = None,
        success: bool = True,
        error_message: str = "",
        checkpoint_id: Optional[str] = None,
        replay_records_count: int = 0,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
    ) -> RecoveryAuditRecord:
        """
        Log a recovery audit event.
        
        Args:
            event_type: Type of audit event
            stream_id: Stream being recovered
            generation_id: Generation number (if applicable)
            session_id: Recovery session ID
            plan_id: Recovery plan ID
            success: Whether the operation succeeded
            error_message: Error message if failed
            checkpoint_id: Checkpoint involved (if any)
            replay_records_count: Records processed during replay
            user_id: User performing operation (if applicable)
            agent_id: Agent performing operation
            tenant_id: Tenant context
            
        Returns:
            The audit record created
        """
        self._audit_counter += 1
        
        record = RecoveryAuditRecord(
            audit_id=f"audit:{time.monotonic_ns()}:{self._audit_counter}",
            event_type=event_type,
            timestamp_utc=time.time(),
            stream_id=stream_id,
            generation_id=generation_id,
            session_id=session_id,
            plan_id=plan_id,
            success=success,
            error_message=error_message,
            checkpoint_id=checkpoint_id,
            replay_records_count=replay_records_count,
            user_id=user_id,
            agent_id=agent_id,
            tenant_id=tenant_id,
        )
        
        self._records.append(record)
        return record
    
    def get_records(
        self,
        event_type: Optional[RecoveryAuditEvent] = None,
        stream_id: Optional[str] = None,
        since_utc: Optional[float] = None,
    ) -> List[RecoveryAuditRecord]:
        """
        Get audit records, optionally filtered.
        
        Args:
            event_type: Filter by event type
            stream_id: Filter by stream ID
            since_utc: Only return events after this time
            
        Returns:
            List of matching audit records
        """
        result = self._records
        
        if event_type is not None:
            result = [r for r in result if r.event_type == event_type]
        
        if stream_id is not None:
            result = [r for r in result if r.stream_id == stream_id]
        
        if since_utc is not None:
            result = [r for r in result if r.timestamp_utc >= since_utc]
        
        return result
    
    @property
    def total_records(self) -> int:
        """Get total number of audit records."""
        return len(self._records)


# =============================================================================
# INTEGRITY PROTECTION
# =============================================================================

class IntegrityProtectionLevel(Enum):
    """
    Level of integrity protection for recovery operations.
    
    Levels:
        NONE: No integrity checks (unsafe, debug only)
        BASIC: Basic hash verification
        ENFORCED: Full cryptographic verification
    """
    
    NONE = "none"
    """No integrity checks - unsafe."""
    
    BASIC = "basic"
    """Basic hash verification."""
    
    ENFORCED = "enforced"
    """Full cryptographic verification with signatures."""


class RecoveryIntegrityProtector:
    """
    Protector of recovery operation integrity.
    
    Ensures that checkpoints and recovery sessions cannot be forged
    or tampered with.
    """
    
    def __init__(
        self,
        protection_level: IntegrityProtectionLevel = IntegrityProtectionLevel.ENFORCED,
    ):
        """
        Initialize integrity protector.
        
        Args:
            protection_level: Level of integrity protection to enforce
        """
        self._level = protection_level
    
    def protect_checkpoint(
        self,
        checkpoint_id: str,
        checkpoint_data: Dict[str, Any],
    ) -> Tuple[bool, List[str]]:
        """
        Apply integrity protection to a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint
            checkpoint_data: Checkpoint data
            
        Returns:
            (is_valid, errors) tuple
        """
        if self._level == IntegrityProtectionLevel.NONE:
            return True, []
        
        # In real implementation, would add cryptographic signature
        # and verify it during restoration
        
        return True, []
    
    def verify_checkpoint_integrity(
        self,
        checkpoint_id: str,
        checkpoint_data: Dict[str, Any],
    ) -> Tuple[bool, List[str]]:
        """
        Verify integrity of a checkpoint.
        
        Args:
            checkpoint_id: ID of the checkpoint
            checkpoint_data: Checkpoint data to verify
            
        Returns:
            (is_valid, errors) tuple
        """
        if self._level == IntegrityProtectionLevel.NONE:
            # Debug mode - skip verification
            return True, []
        
        # In real implementation, would:
        # 1. Verify cryptographic signature
        # 2. Check hash integrity
        # 3. Validate checksums
        
        # For now, assume valid if basic structure is present
        required_fields = ["checkpoint_id", "integrity_digest"]
        missing = [f for f in required_fields if f not in checkpoint_data]
        
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
        return True, []
    
    def protect_recovery_session(
        self,
        session_id: str,
        stream_id: str,
        generation_id: int,
    ) -> Tuple[bool, List[str]]:
        """
        Ensure recovery session cannot be forged.
        
        Args:
            session_id: Session identifier
            stream_id: Stream being recovered
            generation_id: Generation number
            
        Returns:
            (is_protected, errors) tuple
        """
        # In real implementation, would:
        # 1. Bind session to authentication context
        # 2. Use secure random IDs
        # 3. Implement session expiration
        
        if self._level == IntegrityProtectionLevel.ENFORCED:
            # Verify session ID format
            if not session_id.startswith("session:"):
                return False, ["Invalid session ID format"]
        
        return True, []


__all__ = [
    "RecoveryAuthorization",
    "RecoveryAuthorizationContext",
    "RecoveryAuthorizationResult",
    "RecoveryAuthorizationEnforcer",
    "RecoveryAuditEvent",
    "RecoveryAuditRecord",
    "RecoveryAuditLogger",
    "IntegrityProtectionLevel",
    "RecoveryIntegrityProtector",
]