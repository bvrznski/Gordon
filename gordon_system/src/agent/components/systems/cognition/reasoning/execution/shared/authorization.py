# Execution Reasoning Authorization - Phase 7.21
# ===============================================

"""
Canonical Execution Authorization for Phase 7.21.

Authorization evaluates execution permissions, policy compliance,
resource ownership, and security constraints.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class AuthorizationPolicy(Enum):
    """Authorization policy types."""
    
    STRICT = "strict"               # All constraints must pass
    PERMISSIVE = "permissive"       # Some constraints may be relaxed
    MONITORING = "monitoring"       # Only monitor, no blocking
    RISK_BASED = "risk_based"       # Policy adapts based on risk assessment


class AuthorizationState(Enum):
    """Authorization decision states."""
    
    PENDING = "pending"
    EVALUATING = "evaluating"
    AUTHORIZED = "authorized"
    DENIED = "denied"
    EXPIRED = "expired"


@dataclass(frozen=True)
class ExecutionAuthorization:
    """
    Execution Authorization governs which commands can execute.
    
    Authorization evaluates:
        - Execution permissions
        - Policy compliance  
        - Resource ownership
        - Security constraints
        - Execution readiness
        - Risk acceptance
    
    Authorization remains explicit and inspectable.
    """
    
    # Identity
    authorization_identity: str                 # Unique auth identifier
    
    # Authorized commands
    authorized_commands: Tuple[ExecutionCommand, ...]
    
    # Authorization policy
    authorization_policy: AuthorizationPolicy
    
    # Authorization state
    authorization_state: AuthorizationState = AuthorizationState.PENDING
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    evaluated_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate evaluation time."""
        if self.evaluated_at_utc:
            return self.evaluated_at_utc - self.created_at_utc
        return 0.0
    
    @property
    def is_authorized(self) -> bool:
        """Check if authorized."""
        return self.authorization_state == AuthorizationState.AUTHORIZED
    
    @property
    def is_denied(self) -> bool:
        """Check if denied."""
        return self.authorization_state == AuthorizationState.DENIED
    
    @classmethod
    def create(
        cls,
        authorized_commands: Tuple[ExecutionCommand, ...],
        authorization_policy: AuthorizationPolicy = AuthorizationPolicy.STRICT,
    ) -> ExecutionAuthorization:
        """Create a new execution authorization."""
        return cls(
            authorization_identity=f"auth:{uuid.uuid4().hex[:16]}",
            authorized_commands=authorized_commands,
            authorization_policy=authorization_policy,
            evaluated_at_utc=time.time(),
        )
    
    def to_state(self, new_state: AuthorizationState) -> ExecutionAuthorization:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            authorization_state=new_state,
        )


@dataclass(frozen=True)
class AuthorizationTrace:
    """
    Trace of authorization evaluation for inspection.
    """
    
    # Identity
    trace_identity: str
    
    # Evaluation steps
    evaluation_steps: Tuple[AuthorizationStep, ...]
    
    # Final decision
    final_decision: AuthorizationState
    
    @classmethod
    def create(
        cls,
        evaluation_steps: Tuple[AuthorizationStep, ...],
        final_decision: AuthorizationState,
    ) -> AuthorizationTrace:
        """Create a new authorization trace."""
        return cls(
            trace_identity=f"auth_trace:{uuid.uuid4().hex[:16]}",
            evaluation_steps=evaluation_steps,
            final_decision=final_decision,
        )


@dataclass(frozen=True)
class AuthorizationStep:
    """
    A single step in authorization evaluation.
    """
    
    # Identity
    step_identity: str
    
    # Check name
    check_name: str                             # e.g., "resource_permission", "policy_check"
    
    # Result
    result: bool                                # Pass/fail
    diagnostic_message: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        check_name: str,
        result: bool,
        diagnostic_message: Optional[str] = None,
    ) -> AuthorizationStep:
        """Create a new authorization step."""
        return cls(
            step_identity=f"auth_step:{uuid.uuid4().hex[:16]}",
            check_name=check_name,
            result=result,
            diagnostic_message=diagnostic_message,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ExecutionAuthorization",
    "AuthorizationPolicy",
    "AuthorizationState",
    "AuthorizationTrace",
    "AuthorizationStep",
]