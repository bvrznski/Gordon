# Normative Reasoning - Shared Contracts
# ======================================

"""
Canonical Normative contracts for moral & normative reasoning.

This package contains the core contract classes for:
    - Normative sessions and session management
    - Value analysis and evaluation
    - Principle application and precedence
    - Obligation assessment
    - Permission analysis
    - Prohibition checks
    - Conflict resolution
    - Judgment formation
    - Validation and governance

All contracts preserve provenance and remain inspectable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# LIFECYCLE STATES
# =============================================================================

class NormativeState(Enum):
    """Normative session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    CONTEXT_ANALYSIS = "context_analysis"
    VALUE_ANALYSIS = "value_analysis"
    PRINCIPLE_APPLICATION = "principle_application"
    CONFLICT_DETECTION = "conflict_detection"
    NORMATIVE_JUDGMENT = "normative_judgment"
    VALIDATION = "validation"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


# =============================================================================
# NORMATIVE DESCRIPTOR
# =============================================================================

@dataclass(frozen=True)
class NormativeDescriptor:
    """
    Descriptor exposing normative reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Reasoning goal
        - Inference mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what normative reasoning occurred without
    needing to execute the full process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Reasoning goal
    reasoning_goal: str                     # What are we evaluating?
    
    # Inference mode
    inference_mode: str = "normative"       # e.g., "normative", "ethical"
    
    # Lifecycle state
    lifecycle_state: NormativeState = NormativeState.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did normative reasoning originate?
    
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
        """Check if normative reasoning completed."""
        return self.lifecycle_state == NormativeState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if normative reasoning failed."""
        return self.lifecycle_state == NormativeState.FAILED
    
    @property
    def is_archived(self) -> bool:
        """Check if normative reasoning is archived."""
        return self.lifecycle_state == NormativeState.ARCHIVED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_goal: str,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> NormativeDescriptor:
        """Create a new normative descriptor."""
        return cls(
            descriptor_id=f"normative_descriptor:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_goal=reasoning_goal,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: NormativeState) -> NormativeDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == NormativeState.COMPLETED else None,
        )


# =============================================================================
# NORMATIVE OBJECT
# =============================================================================

@dataclass(frozen=True)
class NormativeObject:
    """
    A normative object (value, principle, rule, obligation, etc.).
    
    Normative Objects remain explicit and inspectable.
    """
    
    # Identity
    object_id: str                          # Unique identifier
    object_type: str                        # e.g., "value", "principle", "obligation"
    
    # Normative role
    normative_role: str                     # The role this object plays
    
    # Applicability
    applicable_contexts: Tuple[str, ...] = ()  # In which contexts does this apply?
    
    # Supporting rationale
    supporting_rationale: str               # Why is this a norm?
    
    # Priority (higher = stronger)
    priority: float = 1.0                   # Relative priority
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    effective_from_utc: Optional[float] = None
    effective_until_utc: Optional[float] = None
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_active(self) -> bool:
        """Check if this normative object is currently active."""
        now = time.time()
        if self.effective_from_utc and now < self.effective_from_utc:
            return False
        if self.effective_until_utc and now > self.effective_until_utc:
            return False
        return True
    
    @classmethod
    def create(
        cls,
        object_type: str,
        normative_role: str,
        supporting_rationale: str,
        priority: float = 1.0,
        applicable_contexts: Optional[List[str]] = None,
        provenance: Optional[Dict[str, str]] = None,
    ) -> NormativeObject:
        """Create a new normative object."""
        return cls(
            object_id=f"normative_object:{uuid.uuid4().hex[:16]}",
            object_type=object_type,
            normative_role=normative_role,
            supporting_rationale=supporting_rationale,
            priority=priority,
            applicable_contexts=tuple(applicable_contexts or []),
            provenance=provenance or {},
        )


# =============================================================================
# NORMATIVE SET
# =============================================================================

@dataclass(frozen=True)
class NormativeSet:
    """
    A normative set defines all constraints for a single reasoning session.
    
    Normative Sets are immutable during reasoning and define:
        - Applicable values
        - Applicable principles
        - Candidate actions to evaluate
        - Context
        - Organizational policies
    
    Normative Sets remain explicit throughout the reasoning process.
    """
    
    # Identity
    normative_set_id: str                   # Unique identifier
    
    # Evaluated context
    evaluated_context: Dict[str, Any]       # The context being evaluated
    
    # Candidate actions
    candidate_actions: Tuple[str, ...]      # Actions to evaluate
    
    # Normative constraints
    values: Tuple[NormativeObject, ...] = ()
    principles: Tuple[NormativeObject, ...] = ()
    obligations: Tuple[NormativeObject, ...] = ()
    permissions: Tuple[NormativeObject, ...] = ()
    prohibitions: Tuple[NormativeObject, ...] = ()
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        evaluated_context: Dict[str, Any],
        candidate_actions: List[str],
        values: Optional[List[NormativeObject]] = None,
        principles: Optional[List[NormativeObject]] = None,
        obligations: Optional[List[NormativeObject]] = None,
        permissions: Optional[List[NormativeObject]] = None,
        prohibitions: Optional[List[NormativeObject]] = None,
    ) -> NormativeSet:
        """Create a new normative set."""
        return cls(
            normative_set_id=f"normative_set:{uuid.uuid4().hex[:16]}",
            evaluated_context=evaluated_context,
            candidate_actions=tuple(candidate_actions),
            values=tuple(values or []),
            principles=tuple(principles or []),
            obligations=tuple(obligations or []),
            permissions=tuple(permissions or []),
            prohibitions=tuple(prohibitions or []),
        )


# =============================================================================
# VALUE ANALYSIS
# =============================================================================

@dataclass(frozen=True)
class ValueAnalysis:
    """
    Analysis of how values apply to a specific situation.
    
    Value analysis evaluates:
        - Which values are relevant
        - How each value is affected
        - Trade-offs between conflicting values
        - Confidence in the assessment
    
    Values remain explicit throughout analysis.
    """
    
    # Identity
    analysis_id: str                        # Unique identifier
    
    # Evaluated values
    evaluated_values: Tuple[str, ...]       # IDs of values analyzed
    
    # Assessment for each value
    value_assessments: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Overall confidence
    confidence: float = 0.0                 # 0.0 to 1.0
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def assessed_value_count(self) -> int:
        """Count of values that were assessed."""
        return len(self.evaluated_values)
    
    @classmethod
    def create(
        cls,
        evaluated_values: List[str],
        confidence: float = 0.0,
        value_assessments: Optional[Dict[str, Dict[str, Any]]] = None,
        provenance: Optional[Dict[str, str]] = None,
    ) -> ValueAnalysis:
        """Create a new value analysis."""
        return cls(
            analysis_id=f"value_analysis:{uuid.uuid4().hex[:16]}",
            evaluated_values=tuple(evaluated_values),
            confidence=confidence,
            value_assessments=value_assessments or {},
            provenance=provenance or {},
        )


# =============================================================================
# PRINCIPLE APPLICATION
# =============================================================================

@dataclass(frozen=True)
class PrincipleApplication:
    """
    Application of principles to a specific situation.
    
    Principle application evaluates:
        - Which principles are applicable
        - Principle precedence (order of priority)
        - Principle conflicts
        - Context sensitivity
        - Exceptions
    
    Principles remain explicit throughout application.
    """
    
    # Identity
    application_id: str                     # Unique identifier
    
    # Applicable principles
    applicable_principles: Tuple[str, ...]  # IDs of principles applied
    
    # Precedence ordering (index = priority)
    principle_ordering: Tuple[str, ...] = ()
    
    # Resulting constraints
    resulting_constraints: Tuple[str, ...] = ()  # Constraints derived
    
    # Confidence in application
    confidence: float = 0.0                 # 0.0 to 1.0
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        applicable_principles: List[str],
        principle_ordering: Optional[List[str]] = None,
        resulting_constraints: Optional[List[str]] = None,
        confidence: float = 0.0,
        provenance: Optional[Dict[str, str]] = None,
    ) -> PrincipleApplication:
        """Create a new principle application."""
        return cls(
            application_id=f"principle_application:{uuid.uuid4().hex[:16]}",
            applicable_principles=tuple(applicable_principles),
            principle_ordering=tuple(principle_ordering or []),
            resulting_constraints=tuple(resulting_constraints or []),
            confidence=confidence,
            provenance=provenance or {},
        )


# =============================================================================
# OBLIGATION MANAGEMENT
# =============================================================================

@dataclass(frozen=True)
class ObligationManagement:
    """
    Management of obligations in a normative context.
    
    Obligation management evaluates:
        - Required behaviors (obligations)
        - Optional behaviors
        - Forbidden behaviors (prohibitions)
        - Conditional obligations
        - Expired obligations
    
    Obligations remain explicit throughout management.
    """
    
    # Identity
    obligation_id: str                      # Unique identifier
    
    # All obligations
    obligations: Tuple[Dict[str, Any], ...] = ()
    
    # Current state of each obligation
    obligation_states: Dict[str, str] = field(default_factory=dict)  # e.g., "active", "expired", "conditional"
    
    # Priority ordering
    priority_ordering: Tuple[str, ...] = ()
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        obligations: Optional[List[Dict[str, Any]]] = None,
        obligation_states: Optional[Dict[str, str]] = None,
        priority_ordering: Optional[List[str]] = None,
        provenance: Optional[Dict[str, str]] = None,
    ) -> ObligationManagement:
        """Create a new obligation management."""
        return cls(
            obligation_id=f"obligation_management:{uuid.uuid4().hex[:16]}",
            obligations=tuple(obligations or []),
            obligation_states=obligation_states or {},
            priority_ordering=tuple(priority_ordering or []),
            provenance=provenance or {},
        )


# =============================================================================
# NORMATIVE CONFLICT
# =============================================================================

@dataclass(frozen=True)
class NormativeConflict:
    """
    A normative conflict between constraints.
    
    Conflict analysis determines:
        - Which constraints are in conflict
        - Candidate resolutions
        - Resolution rationale
    
    Conflicts remain explicit and inspectable.
    """
    
    # Identity
    conflict_id: str                        # Unique identifier
    
    # Conflicting elements
    conflicting_elements: Tuple[str, ...]   # IDs of conflicting items
    
    # Conflict type
    conflict_type: str                      # e.g., "value_conflict", "principle_conflict"
    
    # Candidate resolutions
    candidate_resolutions: Tuple[Dict[str, Any], ...] = ()
    
    # Resolved (if any)
    resolved: bool = False
    resolution: Optional[Dict[str, Any]] = None
    
    # Confidence in conflict identification
    confidence: float = 0.0                 # 0.0 to 1.0
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def resolution_count(self) -> int:
        """Count of candidate resolutions."""
        return len(self.candidate_resolutions)
    
    @classmethod
    def create(
        cls,
        conflicting_elements: List[str],
        conflict_type: str,
        candidate_resolutions: Optional[List[Dict[str, Any]]] = None,
        confidence: float = 0.0,
        provenance: Optional[Dict[str, str]] = None,
    ) -> NormativeConflict:
        """Create a new normative conflict."""
        return cls(
            conflict_id=f"normative_conflict:{uuid.uuid4().hex[:16]}",
            conflicting_elements=tuple(conflicting_elements),
            conflict_type=conflict_type,
            candidate_resolutions=tuple(candidate_resolutions or []),
            confidence=confidence,
            provenance=provenance or {},
        )


# =============================================================================
# NORMATIVE JUDGMENT
# =============================================================================

@dataclass(frozen=True)
class NormativeJudgment:
    """
    A normative judgment about candidate actions.
    
    Normative judgments determine:
        - Which actions are permitted
        - Which actions are forbidden
        - Which actions are required
        - Which actions are recommended/discouraged
        - Remaining uncertainty
    
    Judgments remain explicit and justified.
    """
    
    # Identity
    judgment_id: str                        # Unique identifier
    
    # Evaluated actions
    evaluated_actions: Tuple[str, ...]      # Actions that were judged
    
    # Normative status for each action
    action_status: Dict[str, str] = field(default_factory=dict)  # e.g., "permitted", "forbidden", "required"
    
    # Supporting rationale (why this judgment?)
    supporting_rationale: Tuple[Dict[str, Any], ...] = ()
    
    # Confidence in each judgment
    confidence: float = 0.0                 # Overall confidence
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        evaluated_actions: List[str],
        action_status: Optional[Dict[str, str]] = None,
        supporting_rationale: Optional[List[Dict[str, Any]]] = None,
        confidence: float = 0.0,
        provenance: Optional[Dict[str, str]] = None,
    ) -> NormativeJudgment:
        """Create a new normative judgment."""
        return cls(
            judgment_id=f"normative_judgment:{uuid.uuid4().hex[:16]}",
            evaluated_actions=tuple(evaluated_actions),
            action_status=action_status or {},
            supporting_rationale=tuple(supporting_rationale or []),
            confidence=confidence,
            provenance=provenance or {},
        )
    
    def is_action_permitted(self, action: str) -> bool:
        """Check if an action is permitted."""
        return self.action_status.get(action) == "permitted"
    
    def is_action_forbidden(self, action: str) -> bool:
        """Check if an action is forbidden."""
        return self.action_status.get(action) == "forbidden"
    
    def is_action_required(self, action: str) -> bool:
        """Check if an action is required."""
        return self.action_status.get(action) == "required"


# =============================================================================
# NORMATIVE TRACE
# =============================================================================

@dataclass(frozen=True)
class NormativeTrace:
    """
    Complete trace of a normative reasoning session.
    
    Trace contains:
        - All value analyses
        - Principle applications
        - Conflict identifications
        - Normative judgments
        - Validation results
        - Diagnostics
    
    Trace remains inspectable for audit purposes.
    """
    
    # Identity
    trace_id: str                           # Unique identifier
    
    # Normative session identity
    session_identity: str                   # The session this traces
    
    # Reasoning steps (in order)
    normative_history: Tuple[Dict[str, Any], ...] = ()
    
    # Graph of reasoning relationships
    normative_graph: Dict[str, List[str]] = field(default_factory=dict)  # node -> [dependencies]
    
    # Diagnostics
    diagnostics: Tuple[Dict[str, Any], ...] = ()
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        session_identity: str,
        normative_history: Optional[List[Dict[str, Any]]] = None,
        normative_graph: Optional[Dict[str, List[str]]] = None,
        diagnostics: Optional[List[Dict[str, Any]]] = None,
        provenance: Optional[Dict[str, str]] = None,
    ) -> NormativeTrace:
        """Create a new normative trace."""
        return cls(
            trace_id=f"normative_trace:{uuid.uuid4().hex[:16]}",
            session_identity=session_identity,
            normative_history=tuple(normative_history or []),
            normative_graph=normative_graph or {},
            diagnostics=tuple(diagnostics or []),
            provenance=provenance or {},
        )


# =============================================================================
# NORMATIVE SESSION
# =============================================================================

@dataclass(frozen=True)
class NormativeSession:
    """
    A complete normative reasoning session.
    
    Every normative reasoning process occurs inside a Normative Session.
    The session defines:
        - normative objective
        - context
        - candidate actions
        - applicable principles
        - termination conditions
    
    Sessions are independently versioned and maintain provenance.
    """
    
    # Identity
    session_id: str                         # Unique session identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Session configuration
    normative_goal: str                     # What are we trying to judge?
    evaluated_context: Dict[str, Any]       # The context being evaluated
    
    # Evaluation inputs
    candidate_actions: Tuple[str, ...]      # Actions to evaluate
    applicable_principles: Tuple[NormativeObject, ...] = ()
    
    # Session lifecycle state
    lifecycle_state: NormativeState = NormativeState.CREATED
    
    # Results
    value_analyses: Tuple[ValueAnalysis, ...] = ()
    principle_applications: Tuple[PrincipleApplication, ...] = ()
    normative_conflicts: Tuple[NormativeConflict, ...] = ()
    normative_judgments: Tuple[NormativeJudgment, ...] = ()
    
    # Trace
    trace_id: Optional[str] = None
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_completed(self) -> bool:
        """Check if session completed."""
        return self.lifecycle_state in (NormativeState.COMPLETED, NormativeState.ARCHIVED)
    
    @property
    def judgment_count(self) -> int:
        """Count of judgments made."""
        return len(self.normative_judgments)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        normative_goal: str,
        evaluated_context: Dict[str, Any],
        candidate_actions: List[str],
        applicable_principles: Optional[List[NormativeObject]] = None,
        provenance: Optional[Dict[str, str]] = None,
    ) -> NormativeSession:
        """Create a new normative session."""
        return cls(
            session_id=f"normative_session:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            normative_goal=normative_goal,
            evaluated_context=evaluated_context,
            candidate_actions=tuple(candidate_actions),
            applicable_principles=tuple(applicable_principles or []),
            started_at_utc=time.time(),
            provenance=provenance or {},
        )
    
    def to_state(self, new_state: NormativeState) -> "NormativeSession":
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == NormativeState.COMPLETED else None,
        )


# =============================================================================
# NORMATIVE PIPELINE
# =============================================================================

@dataclass(frozen=True)
class NormativePipeline:
    """
    A normative reasoning pipeline.
    
    Canonical pipeline:
        Context Analysis
        ↓
        Value Analysis
        ↓
        Principle Application
        ↓
        Conflict Detection
        ↓
        Normative Judgment
        ↓
        Validation
        ↓
        Publication
    
    Every stage remains independently observable.
    """
    
    # Identity
    pipeline_id: str                        # Unique identifier
    
    # Pipeline strategy (configures execution)
    normative_strategy: Dict[str, Any] = field(default_factory=dict)  # e.g., "strict", "balanced"
    
    # Results from each stage
    context_analysis: Optional[Dict[str, Any]] = None
    value_analyses: Tuple[ValueAnalysis, ...] = ()
    principle_applications: Tuple[PrincipleApplication, ...] = ()
    normative_conflicts: Tuple[NormativeConflict, ...] = ()
    normative_judgments: Tuple[NormativeJudgment, ...] = ()
    
    # Validation
    validation_result: Optional[Dict[str, Any]] = None
    
    # Diagnostics
    diagnostics: Tuple[Dict[str, Any], ...] = ()
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_completed(self) -> bool:
        """Check if pipeline completed."""
        return self.completed_at_utc is not None
    
    @classmethod
    def create(
        cls,
        normative_strategy: Optional[Dict[str, Any]] = None,
        provenance: Optional[Dict[str, str]] = None,
    ) -> NormativePipeline:
        """Create a new normative pipeline."""
        return cls(
            pipeline_id=f"normative_pipeline:{uuid.uuid4().hex[:16]}",
            normative_strategy=normative_strategy or {},
            started_at_utc=time.time(),
            provenance=provenance or {},
        )
    
    def record_step(self, step_name: str, result: Dict[str, Any]) -> "NormativePipeline":
        """Record the result of a pipeline step."""
        new_diagnostics = list(self.diagnostics)
        new_diagnostics.append({
            "step": step_name,
            "result": result,
            "timestamp_utc": time.time(),
        })
        
        return dataclass_replace(
            self,
            diagnostics=tuple(new_diagnostics),
        )


# =============================================================================
# NORMATIVE FAILURE
# =============================================================================

@dataclass(frozen=True)
class NormativeFailure:
    """
    A normative failure with diagnostic information.
    
    Failures may include:
        - Missing principles
        - Conflicting obligations
        - Policy ambiguity
        - Incomplete context
        - Unsupported judgment
    
    Failures remain explicit; they don't silently terminate sessions.
    """
    
    # Identity
    failure_id: str                         # Unique identifier
    
    # Failure details
    failure_kind: str                       # What type of failure?
    affected_session: str                   # Which session failed?
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None     # Human-readable description
    
    # Recovery options
    recovery_options: Tuple[str, ...] = ()  # How might this be recovered?
    
    # Timing
    occurred_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_recoverable(self) -> bool:
        """Check if recovery is possible."""
        return len(self.recovery_options) > 0
    
    @classmethod
    def create(
        cls,
        failure_kind: str,
        affected_session: str,
        diagnostics: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        recovery_options: Optional[List[str]] = None,
        provenance: Optional[Dict[str, str]] = None,
    ) -> NormativeFailure:
        """Create a new failure record."""
        return cls(
            failure_id=f"normative_failure:{uuid.uuid4().hex[:16]}",
            failure_kind=failure_kind,
            affected_session=affected_session,
            diagnostics=diagnostics or {},
            error_message=error_message,
            recovery_options=tuple(recovery_options or []),
            occurred_at_utc=time.time(),
            provenance=provenance or {},
        )
    
    def with_diagnostic(self, key: str, value: Any) -> "NormativeFailure":
        """Return a copy with an additional diagnostic."""
        new_diagnostics = dict(self.diagnostics)
        new_diagnostics[key] = value
        return dataclass_replace(
            self,
            diagnostics=new_diagnostics,
        )


# =============================================================================
# NORMATIVE EVOLUTION
# =============================================================================

@dataclass(frozen=True)
class NormativeEvolution:
    """
    Evolution of normative reasoning over time.
    
    Normative reasoning evolves through:
        - Policy revisions
        - Value revisions
        - New regulations
        - Organizational updates
        - Ethical refinement
    
    Identity remains stable while constraints evolve.
    """
    
    # Identity (stable across evolutions)
    evolution_id: str                       # Unique evolution identifier
    normative_identity: str                 # The evolving normative identity
    
    # Evolution history
    evolution_history: Tuple[Dict[str, Any], ...] = ()  # Changes over time
    
    # Triggering events
    triggering_events: Tuple[str, ...] = ()  # What caused this evolution?
    
    # Resulting constraints after evolution
    resulting_constraints: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    evolved_from_version: int = 1           # Previous version
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def evolution_count(self) -> int:
        """Count of recorded evolutions."""
        return len(self.evolution_history)
    
    @classmethod
    def create(
        cls,
        normative_identity: str,
        triggering_events: Optional[List[str]] = None,
        provenance: Optional[Dict[str, str]] = None,
    ) -> NormativeEvolution:
        """Create a new evolution record."""
        return cls(
            evolution_id=f"normative_evolution:{uuid.uuid4().hex[:16]}",
            normative_identity=normative_identity,
            triggering_events=tuple(triggering_events or []),
            provenance=provenance or {},
            evolved_from_version=1,
        )
    
    def with_change(self, change: Dict[str, Any]) -> "NormativeEvolution":
        """Record a change in the evolution history."""
        new_history = self.evolution_history + (change,)
        return dataclass_replace(
            self,
            evolution_history=new_history,
            evolved_from_version=self.evolved_from_version + 1,
        )


# =============================================================================
# NORMATIVE GOVERNANCE
# =============================================================================

@dataclass(frozen=True)
class NormativeGovernance:
    """
    Governance evaluation of normative reasoning.
    
    Governance evaluates:
        - Value consistency
        - Principle consistency
        - Judgment quality
        - Conflict resolution
        - Policy compliance
        - Diagnostics
    
    Governance remains observational; it never modifies sessions directly.
    """
    
    # Identity
    governance_id: str                      # Unique identifier
    
    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...] = ()
    
    # Findings (positive observations)
    findings: Tuple[Dict[str, Any], ...] = ()
    
    # Violations (policy breaches)
    violations: Tuple[Dict[str, Any], ...] = ()
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()
    
    # Overall assessment
    is_compliant: bool = False              # Passed all governance checks?
    
    # Timing
    evaluated_at_utc: float = field(default_factory=time.time)
    
    @property
    def violation_count(self) -> int:
        """Count of governance violations."""
        return len(self.violations)
    
    @classmethod
    def create(
        cls,
        session_ids: Optional[List[str]] = None,
    ) -> NormativeGovernance:
        """Create a new governance evaluation."""
        return cls(
            governance_id=f"normative_governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple(session_ids or []),
        )
    
    def record_violation(self, violation: Dict[str, Any]) -> "NormativeGovernance":
        """Record a governance violation."""
        return dataclass_replace(
            self,
            violations=self.violations + (violation,),
        )
    
    def add_recommendation(self, recommendation: str) -> "NormativeGovernance":
        """Add a governance recommendation."""
        return dataclass_replace(
            self,
            recommendations=self.recommendations + (recommendation,),
        )


# =============================================================================
# NORMATIVE HEALTH
# =============================================================================

@dataclass(frozen=True)
class NormativeHealth:
    """
    Health metrics for normative reasoning.
    
    Metrics:
        - Value consistency
        - Principle consistency
        - Conflict resolution quality
        - Judgment transparency
        - Validation success
    
    Health remains descriptive, not prescriptive.
    """
    
    # Identity
    health_id: str                          # Unique identifier
    
    # Evaluated sessions
    evaluated_sessions: Tuple[str, ...] = ()
    
    # Metrics (0.0 to 1.0)
    value_consistency_score: float = 0.0
    principle_consistency_score: float = 0.0
    conflict_resolution_quality: float = 0.0
    judgment_transparency_score: float = 0.0
    validation_success_rate: float = 0.0
    
    # Overall health (average)
    overall_health_score: float = 0.0
    
    # Timing
    evaluated_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        session_ids: Optional[List[str]] = None,
    ) -> NormativeHealth:
        """Create a new health assessment."""
        return cls(
            health_id=f"normative_health:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple(session_ids or []),
        )


# =============================================================================
# NORMATIVE VALIDATION
# =============================================================================

@dataclass(frozen=True)
class NormativeValidation:
    """
    Validation of normative reasoning results.
    
    Validation is observational - it never modifies norms directly.
    
    Validates:
        - Value law compliance (VALUE-LAW-001 through VALUE-LAW-008)
        - Principle law compliance (PRINCIPLE-LAW-001 through PRINCIPLE-LAW-008)
        - Obligation law compliance (OBLIGATION-LAW-001 through OBLIGATION-LAW-008)
        - Conflict law compliance (CONFLICT-LAW-001 through CONFLICT-LAW-008)
        - Global invariants
    
    Validation results remain immutable and inspectable.
    """
    
    # Identity
    validation_id: str                      # Unique identifier
    
    # Evaluated session
    evaluated_session: str                  # Session ID being validated
    
    # Validation findings
    passed_checks: Tuple[Dict[str, Any], ...] = ()
    failed_checks: Tuple[Dict[str, Any], ...] = ()
    
    # Overall validation status
    is_valid: bool = False                  # Passed all checks?
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    validated_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def passed_count(self) -> int:
        """Count of passed checks."""
        return len(self.passed_checks)
    
    @property
    def failed_count(self) -> int:
        """Count of failed checks."""
        return len(self.failed_checks)
    
    @classmethod
    def create(
        cls,
        evaluated_session: str,
        provenance: Optional[Dict[str, str]] = None,
    ) -> NormativeValidation:
        """Create a new validation record."""
        return cls(
            validation_id=f"normative_validation:{uuid.uuid4().hex[:16]}",
            evaluated_session=evaluated_session,
            provenance=provenance or {},
        )
    
    def with_passed_check(self, check: Dict[str, Any]) -> "NormativeValidation":
        """Record a passed validation check."""
        return dataclass_replace(
            self,
            passed_checks=self.passed_checks + (check,),
        )
    
    def with_failed_check(self, check: Dict[str, Any]) -> "NormativeValidation":
        """Record a failed validation check."""
        return dataclass_replace(
            self,
            failed_checks=self.failed_checks + (check,),
            is_valid=False,
        )


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """
    Simple dataclass replace helper for frozen instances.
    
    For Python 3.12+, use dataclasses.replace instead.
    This is a compatibility implementation.
    """
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    # States
    "NormativeState",
    # Contracts
    "NormativeDescriptor",
    "NormativeObject",
    "NormativeSet",
    "ValueAnalysis",
    "PrincipleApplication",
    "ObligationManagement",
    "NormativeConflict",
    "NormativeJudgment",
    "NormativeTrace",
    "NormativeSession",
    "NormativePipeline",
    "NormativeFailure",
    "NormativeEvolution",
    "NormativeGovernance",
    "NormativeHealth",
    "NormativeValidation",
    # Helpers
    "dataclass_replace",
]