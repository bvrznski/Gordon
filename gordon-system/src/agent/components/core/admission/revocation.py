# Admission Revocation - Propagation and Coordination
# ====================================================

"""
Admission revocation coordination with readiness state.

This module provides:
- Readiness-revocation-to-admission propagation
- State version synchronization
- Receipt invalidation on revocation
- Multi-runtime isolation for revocations

When readiness is revoked, admission must close or restrict to prevent
new work from entering a runtime that is no longer ready.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
import time


# =============================================================================
# REVOCATION TYPES
# =============================================================================

class RevocationScope(Enum):
    """Scope of a revocation."""
    READINESS = "readiness"           # Readiness revoked
    ADMISSION = "admission"           # Admission revoked
    OPERATIONAL = "operational"       # Operational state changed


@dataclass(frozen=True)
class RevocationReason:
    """Reason for revocation."""
    reason_type: str  # e.g., "health_failure", "dependency_lost"
    description: str
    severity: "Severity"  # From integrity module
    recoverable: bool = True
    
    def is_critical(self) -> bool:
        return self.severity in ("ERROR", "CRITICAL") if isinstance(self.severity, str) else False


class Severity(Enum):
    """Revocation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


# =============================================================================
# REVOCATION REQUEST
# =============================================================================

@dataclass(frozen=True)
class RevocationRequest:
    """
    Request to revoke admission authority.
    
    This is the INPUT - the caller requests revocation with a reason.
    The AdmissionController decides whether and how to revoke.
    """
    runtime_id: str
    boot_session_id: str
    
    scope: RevocationScope
    reason: RevocationReason
    
    requested_at_utc: float = field(default_factory=time.time)
    
    # Context for decision making
    readiness_status_before: Optional[str] = None
    operational_state_before: Optional[str] = None


# =============================================================================
# REVOCATION DECISION
# =============================================================================

class RevocationAction(Enum):
    """Actions to take when revoking."""
    CLOSE_ADMISSION = "close_admission"             # Close admission completely
    RESTRICT_ADMISSION = "restrict_admission"       # Restrict to certain work classes
    DRAIN_ONLY = "drain_only"                       # Don't accept new work, drain existing


@dataclass(frozen=True)
class RevocationDecision:
    """
    Decision about revocation.
    
    This is the OUTPUT - the controller decides what action to take.
    """
    runtime_id: str
    request_id: str
    
    request: RevocationRequest
    
    action: RevocationAction
    restrictions_applied: Tuple[str, ...] = field(default_factory=tuple)
    
    # State at time of decision
    state_version_before: int
    state_version_after: int
    
    effectiveness_seconds: float = 0.0  # How long until effect is complete
    
    evaluated_at_utc: float = field(default_factory=time.time)


# =============================================================================
# REVOCATION RESULT
# =============================================================================

@dataclass(frozen=True)
class RevocationResult:
    """
    Result of applying a revocation.
    
    This records what actually happened - not just the decision.
    """
    runtime_id: str
    
    decision: Optional[RevocationDecision] = None
    
    admission_status_before: str
    admission_status_after: str
    
    # Receipts affected (invalidated)
    invalidated_receipt_ids: Tuple[str, ...] = field(default_factory=tuple)
    
    active_tasks_notified: int = 0
    
    evaluated_at_utc: float = field(default_factory=time.time)


# =============================================================================
# REVOCATION CONTROLLER
# =============================================================================

class RevocationController:
    """
    Coordinates revocation across readiness, admission, and operational state.
    
    This is NOT the authority for any individual domain. Instead, it:
        - Listens to revocation requests
        - Evaluates the scope and severity
        - Decides on appropriate action
        - Propagates changes to affected systems
    
    Invariants:
        1. Readiness revocation → admission closes or restricts
        2. Operational state change → admission adjusts accordingly
        3. Revocation is idempotent (re-revoking same reason has no effect)
        4. Revocations are runtime-scoped (never affect other runtimes)
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._boot_session_id = str(__import__('uuid').uuid4())
        
        # State tracking
        self._lock = __import__('threading').RLock()
        self._state_version = 0
        
        # Revocation records (for idempotency)
        self._active_revocations: Dict[str, RevocationDecision] = {}
        
        # Integration points
        self._readiness_callback: Optional[callable] = None
        self._admission_callback: Optional[callable] = None
    
    def set_readiness_callback(self, callback: callable) -> None:
        """Set callback for readiness state changes."""
        self._readiness_callback = callback
    
    def set_admission_callback(self, callback: callable) -> None:
        """Set callback for admission state changes."""
        self._admission_callback = callback
    
    # -------------------------------------------------------------------------
    # Revocation Request Handling
    # -------------------------------------------------------------------------
    
    async def handle_revocation_request(
        self,
        request: RevocationRequest
    ) -> Optional[RevocationDecision]:
        """
        Handle a revocation request.
        
        This evaluates the request and decides on appropriate action.
        
        Args:
            request: The revocation request to process
            
        Returns:
            Decision if revocation should proceed, None otherwise
        """
        with self._lock:
            # Check idempotency - same reason already revoked?
            reason_key = f"{request.scope.value}:{request.reason.reason_type}"
            if reason_key in self._active_revocations:
                return None  # Already handling this
            
            # Evaluate scope and decide action
            decision = await self._evaluate_revocation(request)
            
            if decision:
                self._active_revocations[reason_key] = decision
                self._state_version += 1
                
                # Apply revocation to admission
                if self._admission_callback:
                    try:
                        await self._admission_callback(decision.action, decision.restrictions_applied)
                    except Exception:
                        pass  # Don't let callback errors affect revocation
            
            return decision
    
    async def _evaluate_revocation(
        self,
        request: RevocationRequest
    ) -> Optional[RevocationDecision]:
        """
        Evaluate a revocation request and decide on action.
        
        This is the core logic - it determines what should happen based on:
            - Scope of revocation (readiness, admission, operational)
            - Severity of reason
            - Current state
        """
        # Default: close admission for readiness/operational revocations
        if request.scope in (
            RevocationScope.READINESS,
            RevocationScope.OPERATIONAL
        ):
            action = RevocationAction.CLOSE_ADMISSION
            
            if not request.reason.is_critical():
                # Non-critical may allow restricted instead of full closure
                if "degraded" in request.reason.description.lower():
                    action = RevocationAction.RESTRICT_ADMISSION
        else:
            action = RevocationAction.CLOSE_ADMISSION
        
        return RevocationDecision(
            runtime_id=self._runtime_id,
            request_id=str(__import__('uuid').uuid4()),
            request=request,
            action=action,
            restrictions_applied=tuple(
                r for r in ["readiness_revoked", request.reason.reason_type]
                if r
            ),
            state_version_before=self._state_version,
            state_version_after=self._state_version + 1,
            evaluated_at_utc=time.time()
        )
    
    # -------------------------------------------------------------------------
    # State Management
    # -------------------------------------------------------------------------
    
    def get_state_snapshot(self) -> Dict[str, Any]:
        """Get current revocation controller state."""
        with self._lock:
            return {
                "runtime_id": self._runtime_id,
                "boot_session_id": self._boot_session_id,
                "state_version": self._state_version,
                "active_revocations_count": len(self._active_revocations),
                "active_reasons": list(self._active_revocations.keys())
            }
    
    def clear_revocation(
        self,
        reason_type: str
    ) -> bool:
        """
        Clear a specific revocation.
        
        Use when the condition that caused revocation has been resolved.
        
        Args:
            reason_type: The type of revocation to clear
            
        Returns:
            True if revocation was cleared, False if not found
        """
        with self._lock:
            key = f"readiness:{reason_type}"
            if key in self._active_revocations:
                del self._active_revocations[key]
                self._state_version += 1
                return True
            
            # Also try admission key
            key = f"admission:{reason_type}"
            if key in self._active_revocations:
                del self._active_revocations[key]
                self._state_version += 1
                return True
            
            return False
    
    def is_revoked(self) -> bool:
        """Check if any revocation is currently active."""
        with self._lock:
            return len(self._active_revocations) > 0


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Types
    "RevocationScope",
    "Severity",
    
    # Models
    "RevocationReason",
    "RevocationRequest",
    "RevocationDecision",
    "RevocationResult",
    
    # Action
    "RevocationAction",
    
    # Controller
    "RevocationController",
]