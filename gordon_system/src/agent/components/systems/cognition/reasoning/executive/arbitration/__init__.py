# Executive Arbitration - Phase 7.30
# ===================================

"""
Executive Arbitration Management.

Arbitration evaluates:
    - Goal conflicts between subsystems
    - Resource conflicts (CPU, memory, bandwidth)
    - Priority conflicts (which should run first?)
    - Execution conflicts (mutual exclusions needed)
    - Attention conflicts (limited attention resources)

Arbitration remains explicit and policy-driven.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any

from .shared import (
    ExecutiveSet,
    SubsystemType,
    ConflictKind,
    ResolutionKind,
    ArbitrationManagement,
)


@dataclass(frozen=True)
class ArbitrationRequest:
    """
    A request for arbitration when conflicts arise.
    
    An arbitration request specifies:
        - What conflict exists
        - Which subsystems are involved
        - Available resolution options
        - Policy constraints
    """
    
    # Identity
    request_id: str                             # Unique identifier
    
    # Conflict details
    conflict_kind: ConflictKind                 # Type of conflict
    affected_subsystems: Tuple[str, ...]        # Which subsystems?
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)  # Additional info
    
    # Resolution options (subsystem-chosen options)
    resolution_options: Tuple[Dict[str, Any], ...] = ()
    
    # Policy constraints
    priority_weights: Dict[str, int] = field(default_factory=dict)
    
    # Timing
    requested_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        conflict_kind: ConflictKind,
        affected_subsystems: List[str],
    ) -> "ArbitrationRequest":
        """Create a new arbitration request."""
        return cls(
            request_id=f"arbitration_request:{uuid.uuid4().hex[:16]}",
            conflict_kind=conflict_kind,
            affected_subsystems=tuple(affected_subsystems),
        )


@dataclass(frozen=True)
class ArbitrationDecision:
    """
    An explicit arbitration decision.
    
    A decision specifies:
        - Which resolution was selected
        - Rationale for the choice
        - How to implement it
    """
    
    # Identity
    decision_id: str                            # Unique identifier
    
    # Request being decided
    request_id: str                             # Original request
    
    # Selected resolution
    selected_resolution: ResolutionKind         # Which strategy?
    resolution_details: Dict[str, Any] = field(default_factory=dict)
    
    # Rationale (why this choice?)
    rationale: str                              # Human-readable explanation
    
    # Implementation instructions
    implementation_steps: Tuple[Dict[str, Any], ...] = ()
    
    # Timing
    decided_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        request_id: str,
        selected_resolution: ResolutionKind,
        rationale: str,
    ) -> "ArbitrationDecision":
        """Create a new arbitration decision."""
        return cls(
            decision_id=f"arbitration_decision:{uuid.uuid4().hex[:16]}",
            request_id=request_id,
            selected_resolution=selected_resolution,
            rationale=rationale,
        )


@dataclass(frozen=True)
class Arbitrator:
    """
    Global executive arbitrator that resolves conflicts.
    
    The arbitrator ensures that subsystem conflicts are resolved
    according to explicit policies without bias or ambiguity.
    """
    
    # Identity
    arbitrator_id: str                          # Unique identifier
    
    # Policy
    arbitration_policy: str                     # Policy name
    
    # Available subsystems
    available_subsystems: Tuple[SubsystemType, ...]
    
    # Resource constraints
    resource_constraints: Dict[str, float] = field(default_factory=dict)
    
    # Decision history (for learning)
    decision_history: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    # Metrics
    decisions_made: int = 0
    decisions_correct: int = 0
    
    @classmethod
    def create(
        cls,
        policy: str = "priority_based",
        subsystems: Optional[List[SubsystemType]] = None,
    ) -> "Arbitrator":
        """Create a new arbitrator."""
        return cls(
            arbitrator_id=f"arbitrator:{uuid.uuid4().hex[:16]}",
            arbitration_policy=policy,
            available_subsystems=tuple(subsystems or []),
        )
    
    def record_decision(self, decision: Dict[str, Any], was_correct: bool) -> "Arbitrator":
        """Record a decision and its outcome."""
        return dataclass_replace(
            self,
            decision_history=self.decision_history + (decision,),
            decisions_made=self.decisions_made + 1,
            decisions_correct=self.decisions_correct + (1 if was_correct else 0),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ArbitrationRequest",
    "ArbitrationDecision",
    "Arbitrator",
]