# Execution Reasoning Rollback - Phase 7.21
# ==========================================

"""
Canonical Rollback Management for Phase 7.21.

Rollback management defines rollback boundaries, restoration checkpoints,
compensation actions, partial rollback, and complete rollback.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class RollbackScope(Enum):
    """Rollback scope types."""
    
    COMMAND_LEVEL = "command_level"             # Rollback single command
    GROUP_LEVEL = "group_level"                 # Rollback group of commands
    SESSION_LEVEL = "session_level"             # Rollback entire session
    PARTIAL_SESSION = "partial_session"         # Rollback partial session


@dataclass(frozen=True)
class RecoveryCheckpoint:
    """
    A recovery checkpoint for rollback.
    
    Contains the state needed to restore execution after a failure.
    """
    
    # Identity
    checkpoint_identity: str                    # Unique checkpoint identifier
    
    # State captured
    command_states: Dict[str, str]              # Command ID -> state mapping
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        command_states: Dict[str, str],
    ) -> RecoveryCheckpoint:
        """Create a new recovery checkpoint."""
        return cls(
            checkpoint_identity=f"checkpoint:{uuid.uuid4().hex[:16]}",
            command_states=command_states,
        )


@dataclass(frozen=True)
class RollbackPlan:
    """
    A rollback plan for restoring execution.
    
    Defines how to recover from failures.
    """
    
    # Identity
    rollback_identity: str                      # Unique rollback identifier
    
    # Checkpoint reference
    checkpoint_reference: str                   # ID of the checkpoint to restore
    
    # Rollback scope
    rollback_scope: RollbackScope               # What to rollback?
    
    # Recovery strategy
    recovery_strategy: str                      # e.g., "restore", "compensate"
    
    @classmethod
    def create(
        cls,
        checkpoint_reference: str,
        rollback_scope: RollbackScope = RollbackScope.GROUP_LEVEL,
        recovery_strategy: str = "restore",
    ) -> RollbackPlan:
        """Create a new rollback plan."""
        return cls(
            rollback_identity=f"rollback:{uuid.uuid4().hex[:16]}",
            checkpoint_reference=checkpoint_reference,
            rollback_scope=rollback_scope,
            recovery_strategy=recovery_strategy,
        )


@dataclass(frozen=True)
class RollbackManagement:
    """
    Management of rollback operations.
    
    Evaluates:
        - Checkpoint validity
        - Rollback scope
        - Compensation actions
        - Partial restoration
        - Transaction integrity
    
    Rollback remains explicit and inspectable.
    """
    
    # Identity
    management_identity: str                    # Unique management identifier
    
    # Rollback plans
    rollback_plans: Tuple[RollbackPlan, ...]
    
    # Valid checkpoints
    valid_checkpoints: Tuple[RecoveryCheckpoint, ...] = ()
    
    @classmethod
    def create(
        cls,
        rollback_plans: Tuple[RollbackPlan, ...],
        valid_checkpoints: Tuple[RecoveryCheckpoint, ...] = (),
    ) -> RollbackManagement:
        """Create a new rollback management instance."""
        return cls(
            management_identity=f"rollback_mgmt:{uuid.uuid4().hex[:16]}",
            rollback_plans=rollback_plans,
            valid_checkpoints=valid_checkpoints,
        )
    
    def get_plan(self, plan_id: str) -> Optional[RollbackPlan]:
        """Get a specific rollback plan."""
        for plan in self.rollback_plans:
            if plan.rollback_identity == plan_id:
                return plan
        return None
    
    def add_checkpoint(self, checkpoint: RecoveryCheckpoint) -> RollbackManagement:
        """Return a new instance with the checkpoint added."""
        return dataclass_replace(
            self,
            valid_checkpoints=self.valid_checkpoints + (checkpoint,),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "RollbackManagement",
    "RollbackScope",
    "RecoveryCheckpoint",
    "RollbackPlan",
]