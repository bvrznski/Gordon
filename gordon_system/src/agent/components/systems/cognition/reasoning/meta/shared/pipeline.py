# Meta-Reasoning Pipeline - Phase 7.27 Part 3
# =============================================

"""
Canonical Meta-Reasoning Pipeline definition.

This module implements the canonical pipeline for meta-reasoning as specified
in Part 3 of Phase 7.27:

    Reasoning Observation
         ↓
    Strategy Selection
         ↓
    Reasoning Regulation
         ↓
    Reasoner Coordination  
         ↓
    Escalation Analysis
         ↓
    Termination Analysis
         ↓
    Validation
         ↓
    Publication

Every stage remains independently observable.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class MetaReasoningState(Enum):
    """Meta-Reasoning session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    OBSERVING = "observing"              # Reasoning observation phase
    SELECTING = "selecting"              # Strategy selection phase
    REGULATING = "regulating"            # Regulation phase
    COORDINATING = "coordinating"        # Coordination phase
    ESCALATING = "escalating"            # Escalation analysis phase
    TERMINATING = "terminating"          # Termination analysis phase  
    VALIDATING = "validating"            # Validation phase
    PUBLISHING = "publishing"            # Publication phase
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class ReasoningObservation:
    """
    Observation of active reasoning processes.
    
    Captures the current state of reasoning for meta-level evaluation.
    """
    
    observation_id: str                   # Unique identifier
    timestamp_utc: float                  # When observed
    
    # Reasoner states
    active_reasoners: List[str]           # Which reasoners are active?
    pending_tasks: List[str]              # Tasks waiting execution
    completed_tasks: List[str]            # Completed tasks
    
    # Performance metrics
    current_latency_seconds: float        # Current processing latency
    resource_utilization: Dict[str, float]  # CPU, memory, etc.
    
    # Quality indicators
    confidence_estimate: float = 0.0      # Estimate of reasoning quality
    uncertainty_estimate: float = 0.0     # Estimate of reasoning uncertainty
    
    @classmethod
    def create(cls) -> ReasoningObservation:
        """Create a new observation with current state."""
        return cls(
            observation_id=f"observation:{uuid.uuid4().hex[:16]}",
            timestamp_utc=time.time(),
            active_reasoners=[],
            pending_tasks=[],
            completed_tasks=[],
            current_latency_seconds=0.0,
            resource_utilization={},
            confidence_estimate=0.0,
            uncertainty_estimate=0.0,
        )


@dataclass(frozen=True)
class StrategySelectionResult:
    """
    Result of strategy selection process.
    
    Specifies which reasoning strategies should be employed and why.
    """
    
    selection_id: str                     # Unique identifier
    selected_strategies: List[str]        # Selected reasoning strategies
    selection_rationale: Dict[str, Any]   # Why these strategies?
    
    # Strategy metadata
    expected_cost: float = 0.0            # Expected computational cost
    expected_quality: float = 0.0         # Expected quality outcome
    
    # Applicability
    applicable_context: str = ""          # Context where this applies
    confidence: float = 0.0               # Confidence in selection
    
    @classmethod
    def create(
        cls,
        selected_strategies: List[str],
        selection_rationale: Dict[str, Any],
    ) -> StrategySelectionResult:
        """Create a new strategy selection result."""
        return cls(
            selection_id=f"strategy_selection:{uuid.uuid4().hex[:16]}",
            selected_strategies=selected_strategies,
            selection_rationale=selection_rationale,
            expected_cost=0.0,
            expected_quality=0.0,
            applicable_context="",
            confidence=0.0,
        )


@dataclass(frozen=True)
class ReasoningRegulation:
    """
    Regulation of reasoning processes.
    
    Controls depth, breadth, latency, and resource allocation.
    """
    
    regulation_id: str                    # Unique identifier
    regulated_reasoners: List[str]        # Which reasoners are regulated?
    
    # Regulation policies
    max_depth: Optional[int] = None       # Maximum reasoning depth
    max_breadth: Optional[int] = None     # Maximum parallel branches
    max_latency_seconds: Optional[float] = None  # Time limit
    
    # Resource constraints
    resource_limits: Dict[str, float] = field(default_factory=dict)  # CPU, memory limits
    
    # Metrics
    current_depth: int = 0                # Current reasoning depth
    current_breadth: int = 0              # Current parallelism level
    
    # Policy
    policy_name: str = "default"          # Regulation policy name
    
    @classmethod
    def create(
        cls,
        regulated_reasoners: List[str],
        max_depth: Optional[int] = None,
        max_breadth: Optional[int] = None,
        resource_limits: Optional[Dict[str, float]] = None,
    ) -> ReasoningRegulation:
        """Create a new reasoning regulation."""
        return cls(
            regulation_id=f"regulation:{uuid.uuid4().hex[:16]}",
            regulated_reasoners=regulated_reasoners,
            max_depth=max_depth,
            max_breadth=max_breadth,
            resource_limits=resource_limits or {},
        )


@dataclass(frozen=True)
class ReasonerCoordination:
    """
    Coordination of reasoning processes.
    
    Determines parallel execution, sequencing, and dependency management.
    """
    
    coordination_id: str                  # Unique identifier
    participating_reasoners: List[str]    # Which reasoners participate?
    
    # Coordination strategy
    coordination_strategy: str = "sequential"  # How to coordinate?
    
    # Dependencies
    dependencies: Dict[str, List[str]] = field(default_factory=dict)  # reasoner -> prerequisites
    
    # Topology
    execution_topology: str = "linear"    # Linear, tree, mesh, etc.
    
    # Synchronization
    requires_consensus: bool = False      # Need consensus among reasoners?
    
    @classmethod
    def create(
        cls,
        participating_reasoners: List[str],
        coordination_strategy: str = "sequential",
        dependencies: Optional[Dict[str, List[str]]] = None,
    ) -> ReasonerCoordination:
        """Create a new reasoning coordination."""
        return cls(
            coordination_id=f"coordination:{uuid.uuid4().hex[:16]}",
            participating_reasoners=participating_reasoners,
            coordination_strategy=coordination_strategy,
            dependencies=dependencies or {},
        )


@dataclass(frozen=True)
class EscalationDecision:
    """
    Decision about escalating reasoning efforts.
    
    Determines when and how to increase reasoning resources.
    """
    
    escalation_id: str                    # Unique identifier
    escalation_trigger: str               # What triggered escalation?
    
    # Escalation action
    selected_strategy: Optional[str] = None  # New strategy to try
    
    # Expected improvement
    expected_improvement: float = 0.0     # Expected quality increase
    expected_time_seconds: float = 0.0    # Expected additional time
    
    # Resources
    additional_resources: Dict[str, float] = field(default_factory=dict)
    
    # Justification
    justification: str = ""               # Why escalate?
    
    @classmethod
    def create(
        cls,
        escalation_trigger: str,
        expected_improvement: float,
        justification: str = "",
    ) -> EscalationDecision:
        """Create a new escalation decision."""
        return cls(
            escalation_id=f"escalation:{uuid.uuid4().hex[:16]}",
            escalation_trigger=escalation_trigger,
            expected_improvement=expected_improvement,
            justification=justification,
        )


@dataclass(frozen=True)
class TerminationDecision:
    """
    Decision about terminating reasoning.
    
    Determines when reasoning has reached sufficient confidence or
    resource limits have been exhausted.
    """
    
    termination_id: str                   # Unique identifier
    
    # Termination conditions met
    termination_conditions: List[str]     # Which conditions triggered?
    
    # Quality metrics at termination
    final_confidence: float = 0.0         # Confidence achieved
    estimated_quality: float = 0.0        # Estimated quality of output
    
    # Rationale
    termination_rationale: str = ""       # Why terminate?
    
    @classmethod
    def create(
        cls,
        termination_conditions: List[str],
        final_confidence: float,
        termination_rationale: str = "",
    ) -> TerminationDecision:
        """Create a new termination decision."""
        return cls(
            termination_id=f"termination:{uuid.uuid4().hex[:16]}",
            termination_conditions=termination_conditions,
            final_confidence=final_confidence,
            termination_rationale=termination_rationale,
        )


@dataclass(frozen=True)
class MetaReasoningPipelineResult:
    """
    Result of the complete meta-reasoning pipeline.
    
    Represents the canonical output of a full meta-reasoning session
    following the pipeline: Observation → Selection → Regulation → 
    Coordination → Escalation → Termination → Validation → Publication
    """
    
    # Identity
    pipeline_id: str                      # Unique pipeline identifier
    semantic_identity: str                # Semantic identity (stable)
    
    # Pipeline state
    lifecycle_state: MetaReasoningState = MetaReasoningState.CREATED
    
    # Pipeline stages
    observation: Optional[ReasoningObservation] = None
    strategy_selection: Optional[StrategySelectionResult] = None
    regulation: Optional[ReasoningRegulation] = None
    coordination: Optional[ReasonerCoordination] = None
    escalation_decision: Optional[EscalationDecision] = None
    termination_decision: Optional[TerminationDecision] = None
    
    # Validation
    validation_passed: bool = False       # Did validation pass?
    validation_findings: List[str] = field(default_factory=list)
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate total pipeline duration."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0
    
    @property
    def is_completed(self) -> bool:
        """Check if pipeline completed."""
        return self.lifecycle_state == MetaReasoningState.COMPLETED
    
    def to_completed(self) -> MetaReasoningPipelineResult:
        """Mark pipeline as completed."""
        return dataclass_replace(
            self,
            lifecycle_state=MetaReasoningState.COMPLETED,
            completed_at_utc=time.time(),
        )
    
    def to_failed(self, failure_reason: str = "") -> MetaReasoningPipelineResult:
        """Mark pipeline as failed."""
        findings = list(self.validation_findings) + [f"FAILED: {failure_reason}"]
        return dataclass_replace(
            self,
            lifecycle_state=MetaReasoningState.FAILED,
            completed_at_utc=time.time(),
            validation_passed=False,
            validation_findings=findings,
        )
    
    @classmethod
    def create(cls, semantic_identity: str) -> MetaReasoningPipelineResult:
        """Create a new meta-reasoning pipeline."""
        return cls(
            pipeline_id=f"meta_pipeline:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            lifecycle_state=MetaReasoningState.CREATED,
            started_at_utc=time.time(),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "MetaReasoningPipelineResult",
    "MetaReasoningState",
    "ReasoningObservation",
    "StrategySelectionResult", 
    "ReasoningRegulation",
    "ReasonerCoordination",
    "EscalationDecision",
    "TerminationDecision",
]