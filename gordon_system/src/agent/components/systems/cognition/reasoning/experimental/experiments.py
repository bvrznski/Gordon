# Experimental Reasoning - Experiments
# =====================================

"""
Canonical Experiment contracts.

Experiments describe structured evidence acquisition procedures.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ExperimentIdentity:
    """
    Immutable identity for an experiment.
    
    Allows replay and verification of experimental results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    experiment_number: int = 1                # For repeated experiments
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, experiment_number: int = 1) -> ExperimentIdentity:
        """Create a new experiment identity."""
        return cls(
            semantic_identity=semantic_identity,
            experiment_number=experiment_number,
        )


class ExperimentLifecycle(Enum):
    """Experiment lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    DESIGNING = "designing"
    OPTIMIZING = "optimizing"
    VALIDATING = "validating"
    READY = "ready"
    EXECUTED = "executed"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class ExperimentDesign:
    """
    A complete experiment design for structured evidence acquisition.
    
    Experiments include:
        - Measurements
        - Interventions
        - Controls
        - Expected observations
        - Termination conditions
    
    Experiments remain explicit and independently inspectable.
    """
    
    # Identity
    experiment_id: str                        # Unique identifier
    semantic_identity: str                    # Stable identity across runs
    
    # Experiment classification
    experiment_name: Optional[str] = None     # Human-readable name
    
    # Tested hypothesis
    tested_hypothesis: Optional[str] = None   # What hypothesis is being tested?
    
    # Intervention plan
    intervention_plan: Tuple[str, ...] = ()   # Description of interventions to apply
    
    # Expected observations
    expected_observations: Dict[str, str] = field(default_factory=dict)  # variable -> expected outcome
    
    # Measurement plan reference
    measurement_plan_id: Optional[str] = None
    
    # Control condition references
    control_conditions: Tuple[str, ...] = ()
    
    # Termination conditions
    termination_conditions: Tuple[str, ...] = ()  # When to stop the experiment
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did experiment originate?
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration if completed."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0
    
    @property
    def is_completed(self) -> bool:
        """Check if experiment design completed."""
        return self.lifecycle_state == ExperimentLifecycle.COMPLETED
    
    @property
    def lifecycle_state(self) -> str:
        """Get current lifecycle state based on timestamps."""
        if self.completed_at_utc:
            return "completed"
        if self.started_at_utc:
            return "executed"
        return "created"
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        origin_context: str = "unknown",
        intervention_plan: Optional[List[str]] = None,
        expected_observations: Optional[Dict[str, str]] = None,
    ) -> ExperimentDesign:
        """Create a new experiment design."""
        return cls(
            experiment_id=f"experiment:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            intervention_plan=tuple(intervention_plan or []),
            expected_observations=expected_observations or {},
            origin_context=origin_context,
            started_at_utc=time.time(),
        )


@dataclass(frozen=True)
class ExperimentTrace:
    """
    Trace of an experiment session.
    
    Contains all reasoning steps, experiments, interventions, measurements,
    controls, validation results, and diagnostics from the session.
    
    Trace remains inspectable for audit and reproducibility.
    """
    
    # Identity
    trace_id: str                             # Unique identifier
    
    # Reasoning steps (in chronological order)
    reasoning_steps: Tuple[str, ...] = ()
    
    # Experiment graph (experiments and their relationships)
    experiment_graph: Dict[str, List[str]] = field(default_factory=dict)  # exp -> dependencies
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = ()         # Diagnostic records
    
    # Provenance
    session_identity: Optional[str] = None   # Session identity if available
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def step_count(self) -> int:
        """Get the number of reasoning steps."""
        return len(self.reasoning_steps)
    
    @classmethod
    def create(
        cls,
        session_identity: Optional[str] = None,
        origin_context: str = "unknown",
    ) -> ExperimentTrace:
        """Create a new experiment trace."""
        return cls(
            trace_id=f"trace:{uuid.uuid4().hex[:16]}",
            session_identity=session_identity,
            created_at_utc=time.time(),
        )


__all__ = [
    "ExperimentIdentity",
    "ExperimentLifecycle",
    "ExperimentDesign",
    "ExperimentTrace",
]