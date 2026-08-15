# Executive Conflict Model
# =========================

"""
Canonical immutable ExecutiveConflict dataclass.

Executive conflict is a bounded, typed, evidence-backed representation of
incompatible, competing, contradictory, obstructive, ambiguous, or mutually
unsatisfied executive conditions that may impair or alter the current
Executive Program, Executive Task Set, decision process, or cognitive progression.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional

# =============================================================================
# IDENTITY TYPES
# =============================================================================


@dataclass(frozen=True)
class ExecutiveConflictId:
    """
    Unique identifier for an Executive Conflict instance.
    
    Every conflict must have a stable, deterministically generated ID.
    """
    
    value: str = field(default_factory=lambda: f"conf_{id(object()):x}")
    """Unique string identifier."""
    
    @classmethod
    def generate(cls) -> "ExecutiveConflictId":
        """Generate a new conflict ID."""
        return cls()
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ExecutiveConflictRevision:
    """
    Revision tracking for executive conflicts.
    
    Conflicts may be revised as new evidence is gathered or conditions change.
    Revisions preserve lineage for recurrence detection and history tracking.
    """
    
    number: int = 1
    """Revision number (strictly monotonic)."""
    
    source_id: Optional[str] = None
    """ID of the source conflict if this is a revision."""
    
    @classmethod
    def initial(cls) -> "ExecutiveConflictRevision":
        """Create an initial (first) revision."""
        return cls(number=1)
    
    @classmethod
    def from_source(cls, source_id: str, base_number: int = 1) -> "ExecutiveConflictRevision":
        """Create a revision referencing a source conflict."""
        return cls(number=base_number, source_id=source_id)


@dataclass(frozen=True)
class ExecutiveConflictSchemaVersion:
    """
    Schema version for executive conflicts.
    
    Enables versioning of the conflict model across implementations.
    """
    
    major: int = 1
    minor: int = 0
    patch: int = 0
    
    @property
    def value(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


# =============================================================================
# CONFLICT KIND ENUMERATION
# =============================================================================


class ExecutiveConflictKind:
    """
    Typed taxonomy of executive conflict kinds.
    
    Each kind represents a distinct semantic category of conflict that may
    require different assessment or resolution approaches.
    """
    
    # Goal and commitment conflicts
    GOAL_GOAL_CONFLICT = "goal_goal_conflict"
    """Two goals with mutually incompatible satisfaction conditions."""
    
    COMMITMENT_COMMITMENT_CONFLICT = "commitment_commitment_conflict"
    """Two commitments that cannot both be satisfied."""
    
    GOAL_COMMITMENT_CONFLICT = "goal_commitment_conflict"
    """A goal is obstructed by a binding commitment."""
    
    # Program and task-set conflicts
    PROGRAM_PROGRAM_CONFLICT = "program_program_conflict"
    """Multiple active programs with incompatible requirements."""
    
    TASK_SET_TASK_SET_CONFLICT = "task_set_task_set_conflict"
    """Multiple task sets with incompatible rules or constraints."""
    
    PROGRAM_TASK_SET_CONFLICT = "program_task_set_conflict"
    """An active program conflicts with its assigned task set."""
    
    # Priority and strategy conflicts
    PRIORITY_CONFLICT = "priority_conflict"
    """Priority ordering is inconsistent or contradictory."""
    
    STRATEGY_CONFLICT = "strategy_conflict"
    """Conflicting strategy requirements or recommendations."""
    
    # Rule, constraint, policy, security conflicts
    RULE_CONFLICT = "rule_conflict"
    """Multiple rules with incompatible applicability."""
    
    CONSTRAINT_CONFLICT = "constraint_conflict"
    """Constraints that cannot all be satisfied simultaneously."""
    
    POLICY_CONFLICT = "policy_conflict"
    """Policy requirements are contradictory or incompatible."""
    
    SECURITY_CONFLICT = "security_conflict"
    """Security constraints conflict with operational requirements."""
    
    # Authority and source conflicts
    AUTHORITY_CONFLICT = "authority_conflict"
    """Multiple authoritative sources provide contradictory guidance."""
    
    # Plan, reasoning, evidence conflicts
    PLAN_CONFLICT = "plan_conflict"
    """Different plans propose incompatible actions or sequences."""
    
    REASONING_CONFLICT = "reasoning_conflict"
    """Reasoning processes produce contradictory conclusions."""
    
    EVIDENCE_CONFLICT = "evidence_conflict"
    """Conflicting evidence from different sources."""
    
    INTERPRETATION_CONFLICT = "interpretation_conflict"
    """Different interpretations of the same evidence or situation."""
    
    # Prediction and outcome conflicts
    PREDICTION_OBSERVATION_CONFLICT = "prediction_observation_conflict"
    """An observed outcome contradicts a prediction."""
    
    EXPECTATION_OUTCOME_CONFLICT = "expectation_outcome_conflict"
    """Expected outcomes differ from actual outcomes."""
    
    # Decision and action conflicts
    DECISION_CANDIDATE_CONFLICT = "decision_candidate_conflict"
    """Multiple decision candidates are equally valid but incompatible."""
    
    ACTION_CANDIDATE_CONFLICT = "action_candidate_conflict"
    """Action candidates compete for selection with incompatible effects."""
    
    # Focus and attention conflicts
    FOCUS_TASK_SET_CONFLICT = "focus_task_set_conflict"
    """Current focus is misaligned with task set requirements."""
    
    # Motivation and resource conflicts
    MOTIVATION_COMMITMENT_CONFLICT = "motivation_commitment_conflict"
    """Motivational support is insufficient for binding commitment."""
    
    WORKING_MEMORY_REQUIREMENT_CONFLICT = "working_memory_requirement_conflict"
    """Working memory cannot maintain all required items simultaneously."""
    
    WORKSPACE_CONTENT_CONFLICT = "workspace_content_conflict"
    """Workspace content conflicts with task requirements."""
    
    CAPABILITY_REQUIREMENT_CONFLICT = "capability_requirement_conflict"
    """Required capabilities are unavailable or insufficient."""
    
    RESOURCE_CONSTRAINT_CONFLICT = "resource_constraint_conflict"
    """Resource constraints prevent required actions."""
    
    # Temporal and dependency conflicts
    TEMPORAL_CONFLICT = "temporal_conflict"
    """Conflicting temporal requirements (deadlines, ordering)."""
    
    DEPENDENCY_CONFLICT = "dependency_conflict"
    """Dependency requirements cannot be satisfied simultaneously."""
    
    # Completion and recovery conflicts
    COMPLETION_CRITERIA_CONFLICT = "completion_criteria_conflict"
    """Different completion criteria contradict each other."""
    
    RECOVERY_CONFLICT = "recovery_conflict"
    """Recovery options are mutually exclusive or conflicting."""
    
    # Communication and general conflicts
    COMMUNICATION_CONFLICT = "communication_conflict"
    """Communication requirements are contradictory."""
    
    GENERAL_EXECUTIVE_CONFLICT = "general_executive_conflict"
    """A conflict that doesn't fit other categories but is executive-relevant."""
    
    UNKNOWN = "unknown"
    """Unknown or unclassified conflict kind."""
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid conflict kinds as a tuple."""
        return (
            cls.GOAL_GOAL_CONFLICT,
            cls.COMMITMENT_COMMITMENT_CONFLICT,
            cls.GOAL_COMMITMENT_CONFLICT,
            cls.PROGRAM_PROGRAM_CONFLICT,
            cls.TASK_SET_TASK_SET_CONFLICT,
            cls.PROGRAM_TASK_SET_CONFLICT,
            cls.PRIORITY_CONFLICT,
            cls.STRATEGY_CONFLICT,
            cls.RULE_CONFLICT,
            cls.CONSTRAINT_CONFLICT,
            cls.POLICY_CONFLICT,
            cls.SECURITY_CONFLICT,
            cls.AUTHORITY_CONFLICT,
            cls.PLAN_CONFLICT,
            cls.REASONING_CONFLICT,
            cls.EVIDENCE_CONFLICT,
            cls.INTERPRETATION_CONFLICT,
            cls.PREDICTION_OBSERVATION_CONFLICT,
            cls.EXPECTATION_OUTCOME_CONFLICT,
            cls.DECISION_CANDIDATE_CONFLICT,
            cls.ACTION_CANDIDATE_CONFLICT,
            cls.FOCUS_TASK_SET_CONFLICT,
            cls.MOTIVATION_COMMITMENT_CONFLICT,
            cls.WORKING_MEMORY_REQUIREMENT_CONFLICT,
            cls.WORKSPACE_CONTENT_CONFLICT,
            cls.CAPABILITY_REQUIREMENT_CONFLICT,
            cls.RESOURCE_CONSTRAINT_CONFLICT,
            cls.TEMPORAL_CONFLICT,
            cls.DEPENDENCY_CONFLICT,
            cls.COMPLETION_CRITERIA_CONFLICT,
            cls.RECOVERY_CONFLICT,
            cls.COMMUNICATION_CONFLICT,
            cls.GENERAL_EXECUTIVE_CONFLICT,
            cls.UNKNOWN,
        )


# =============================================================================
# CONFLICT DIMENSION ENUMERATION
# =============================================================================


class ExecutiveConflictDimension:
    """
    Dimensions along which a conflict may be assessed.
    
    A single conflict may span multiple dimensions. Each dimension represents
    a different semantic aspect of the incompatibility or competition.
    """
    
    LOGICAL = "logical"
    """Logical inconsistency or contradiction."""
    
    SEMANTIC = "semantic"
    """Semantic incompatibility or misalignment."""
    
    FACTUAL = "factual"
    """Factual disagreement or evidence conflict."""
    
    TEMPORAL = "temporal"
    """Temporal ordering conflicts (deadlines, sequences)."""
    
    CAUSAL = "causal"
    """Causal relationship conflicts."""
    
    GOAL = "goal"
    """Goal incompatibility or competition."""
    
    COMMITMENT = "commitment"
    """Commitment conflict or breach risk."""
    
    PRIORITY = "priority"
    """Priority ordering conflict."""
    
    STRATEGIC = "strategic"
    """Strategy or approach conflict."""
    
    POLICY = "policy"
    """Policy applicability or requirement conflict."""
    
    SECURITY = "security"
    """Security constraint conflict."""
    
    AUTHORITY = "authority"
    """Authority assignment or decision conflict."""
    
    RESOURCE = "resource"
    """Resource allocation or availability conflict."""
    
    CAPABILITY = "capability"
    """Capability requirement or availability conflict."""
    
    ATTENTIONAL = "attentional"
    """Attention or focus allocation conflict."""
    
    MOTIVATIONAL = "motivational"
    """Motivational alignment conflict."""
    
    DECISIONAL = "decisional"
    """Decision-making process conflict."""
    
    BEHAVIORAL = "behavioral"
    """Behavioral requirement conflict."""
    
    COMMUNICATION = "communication"
    """Communication or information flow conflict."""
    
    PRIVACY = "privacy"
    """Privacy or confidentiality conflict."""
    
    DISCLOSURE = "disclosure"
    """Disclosure or transparency conflict."""
    
    COMPLETION = "completion"
    """Completion criteria or success condition conflict."""
    
    RECOVERY = "recovery"
    """Recovery path or strategy conflict."""
    
    DEPENDENCY = "dependency"
    """Dependency ordering or availability conflict."""
    
    UNKNOWN = "unknown"
    """Unknown or unclassified dimension."""
    
    @classmethod
    def all_dimensions(cls) -> Tuple[str, ...]:
        """Return all valid dimensions as a tuple."""
        return (
            cls.LOGICAL,
            cls.SEMANTIC,
            cls.FACTUAL,
            cls.TEMPORAL,
            cls.CAUSAL,
            cls.GOAL,
            cls.COMMITMENT,
            cls.PRIORITY,
            cls.STRATEGIC,
            cls.POLICY,
            cls.SECURITY,
            cls.AUTHORITY,
            cls.RESOURCE,
            cls.CAPABILITY,
            cls.ATTENTIONAL,
            cls.MOTIVATIONAL,
            cls.DECISIONAL,
            cls.BEHAVIORAL,
            cls.COMMUNICATION,
            cls.PRIVACY,
            cls.DISCLOSURE,
            cls.COMPLETION,
            cls.RECOVERY,
            cls.DEPENDENCY,
            cls.UNKNOWN,
        )


# =============================================================================
# CONFLICT STATUS ENUMERATION
# =============================================================================


class ExecutiveConflictStatus:
    """
    Semantic status of an executive conflict.
    
    Status reflects the current state in the conflict lifecycle, not a
    runtime job status or execution state.
    """
    
    DETECTED = "detected"
    """Initial detection, awaiting validation."""
    
    VALIDATING = "validating"
    """Evidence is being validated."""
    
    CONFIRMED = "confirmed"
    """Conflict is confirmed by evidence."""
    
    PARTIALLY_CONFIRMED = "partially_confirmed"
    """Some evidence supports, but not all conditions are met."""
    
    DISPUTED = "disputed"
    """The conflict is being contested or challenged."""
    
    UNRESOLVED = "unresolved"
    """Conflict remains active and unresolved."""
    
    UNDER_REVIEW = "under_review"
    """Under review by authority or monitoring systems."""
    
    WAITING_FOR_EVIDENCE = "waiting_for_evidence"
    """Awaiting additional evidence for assessment."""
    
    WAITING_FOR_AUTHORITY = "waiting_for_authority"
    """Awaiting authority decision for resolution."""
    
    MITIGATED = "mitigated"
    """Conflict severity has been reduced through mitigation."""
    
    RESOLVED = "resolved"
    """Conflict has been successfully resolved."""
    
    SUPERSEDED = "superseded"
    """A newer conflict has superseded this one."""
    
    DISMISSED = "dismissed"
    """Conflict was deemed insignificant or not actionable."""
    
    EXPIRED = "expired"
    """Conflict expired due to time bounds or other criteria."""
    
    INVALID = "invalid"
    """Conflict is no longer valid (e.g., source evidence invalidated)."""
    
    UNKNOWN = "unknown"
    """Status is unknown or unassessed."""
    
    @classmethod
    def terminal_statuses(cls) -> Tuple[str, ...]:
        """Return statuses that are considered final/terminal."""
        return (
            cls.RESOLVED,
            cls.SUPERSEDED,
            cls.DISMISSED,
            cls.EXPIRED,
            cls.INVALID,
        )


# =============================================================================
# CONFLICT SCOPE MODEL
# =============================================================================


@dataclass(frozen=True)
class ExecutiveConflictScope:
    """
    Bounded scope of an executive conflict.
    
    Defines the range of systems, programs, or structures that are involved
    in the conflict. A local conflict must not automatically be promoted
    to a global conflict without explicit justification.
    """
    
    program_scope: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Executive Programs affected by the conflict."""
    
    task_set_scope: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Executive Task Sets affected by the conflict."""
    
    goal_scope: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Goals involved in the conflict."""
    
    commitment_scope: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Commitments involved in the conflict."""
    
    thread_scope: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Execution Threads affected by the conflict."""
    
    decision_scope: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Decisions affected by the conflict."""
    
    temporal_scope_seconds: float = 0.0
    """Temporal scope in seconds (0 = no time-bound)."""
    
    authority_scope: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of authorities involved in the conflict."""
    
    @classmethod
    def local(cls) -> "ExecutiveConflictScope":
        """Create a local-scope conflict (single program/task set)."""
        return cls()
    
    @classmethod
    def global_scope(
        cls,
        program_ids: Tuple[str, ...] = (),
        task_set_ids: Tuple[str, ...] = (),
    ) -> "ExecutiveConflictScope":
        """Create a global-scope conflict affecting multiple systems."""
        return cls(program_scope=program_ids, task_set_scope=task_set_ids)
    
    @property
    def is_local(self) -> bool:
        """Check if the scope is local (single program/task set)."""
        return len(self.program_scope) <= 1 and len(self.task_set_scope) <= 1
    
    @property
    def is_global(self) -> bool:
        """Check if the scope is global (multiple programs or task sets)."""
        return not self.is_local


# =============================================================================
# EXECUTIVE CONFLICT - THE ROOT MODEL
# =============================================================================


@dataclass(frozen=True)
class ExecutiveConflict:
    """
    Immutable, bounded representation of an executive conflict.
    
    This is the canonical type for representing conflicts in Phase 4.4.5.
    Every conflict must be fully specified with all required fields.
    
    CONFIRMED INvariants:
        - EXEC-CONFLICT-INV-001: Conflict is semantic, not exception
        - EXEC-CONFLICT-INV-002: Detection distinct from resolution
        - EXEC-CONFLICT-INV-003: Detection does not grant resolution authority
        - EXEC-CONFLICT-INV-004-052: All other architectural invariants
    
    PROPERTIES:
        * Immutable: frozen=True dataclass
        * Bounded: all collections have capacity limits
        * Evidence-backed: evidence is mandatory, not optional
        * Typed: kind and dimensions explicitly specified
        * Authoritative: authority requirement is explicit
    """
    
    # Identity and revisioning
    conflict_id: ExecutiveConflictId
    """Unique identifier for this conflict instance."""
    
    revision: ExecutiveConflictRevision
    """Current revision of the conflict (for lineage tracking)."""
    
    schema_version: ExecutiveConflictSchemaVersion = field(
        default_factory=ExecutiveConflictSchemaVersion
    )
    """Schema version for compatibility tracking."""
    
    # Classification
    kind: str  # ExecutiveConflictKind value
    """The semantic category of the conflict."""
    
    status: str  # ExecutiveConflictStatus value
    """Current semantic status in the conflict lifecycle."""
    
    scope: ExecutiveConflictScope
    """Bounded scope of affected systems and structures."""
    
    # Subject references (external, not embedded)
    subjects: Tuple[str, ...] = field(default_factory=tuple)
    """References to conflicting executive subjects (programs, goals, etc.)."""
    
    sources: Tuple[str, ...] = field(default_factory=tuple)
    """References to source systems contributing to the conflict."""
    
    relations: Tuple[str, ...] = field(default_factory=tuple)
    """References to related conflicts via ExecutiveConflictRelation kinds."""
    
    # Dimensions
    dimensions: Tuple[str, ...] = field(default_factory=tuple)
    """Dimensions along which this conflict manifests (ExecutiveConflictDimension values)."""
    
    # Evidence (mandatory for any meaningful conflict)
    evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence items supporting the conflict assessment."""
    
    # Assessment metrics
    severity: str  # ExecutiveConflictSeverity value
    """Assessment of conflict severity."""
    
    persistence: str  # ExecutiveConflictPersistence value
    """Assessment of how persistent this conflict is."""
    
    recurrence: str = "none"
    """Recurrence classification (ExecutiveConflictRecurrence value)."""
    
    propagation: Tuple[str, ...] = field(default_factory=tuple)
    """Propagated effects to other systems."""
    
    interference: str = "none"
    """Interference assessment (ExecutiveInterferenceAssessment value)."""
    
    # Affected structures
    affected_programs: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Executive Programs affected by the conflict."""
    
    affected_task_sets: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Executive Task Sets affected by the conflict."""
    
    affected_goals: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Goals affected by the conflict."""
    
    affected_commitments: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Commitments affected by the conflict."""
    
    affected_decisions: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Decisions affected by the conflict."""
    
    affected_actions: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Action Candidates affected by the conflict."""
    
    # Authority and resolution
    resolution_authority: str = "executive_network_internal"
    """Authority required to resolve this conflict."""
    
    # Demand assessment (advisory only)
    demand_assessment: Optional[str] = None  # ExecutiveDemandAssessment reference
    """Reference to associated demand assessment (if any)."""
    
    # Quality metrics
    confidence_class: str = "unknown"
    """Classification of confidence in the conflict assessment."""
    
    completeness_class: str = "partial"
    """Classification of evidence completeness."""
    
    validity_class: str = "valid"
    """Classification of semantic validity."""
    
    privacy_classification: str = "internal"
    """Privacy classification of this conflict."""
    
    provenance_created_by: str = "executive_conflict_monitor"
    """Who/what created this conflict."""
    
    provenance_created_at_utc: float = 0.0
    """When conflict was created (seconds since epoch)."""
    
    provenance_validated_by: Optional[str] = None
    """Who validated this conflict (if any)."""
    
    provenance_validated_at_utc: Optional[float] = None
    """When conflict was validated (if at all)."""
    
    # =============================================================================
    # VALIDATION METHODS
    # =============================================================================
    
    def is_terminal(self) -> bool:
        """Check if the conflict is in a terminal status."""
        return self.status in ExecutiveConflictStatus.terminal_statuses()
    
    def has_required_evidence(self) -> bool:
        """Check if sufficient evidence is present (at least one item)."""
        return len(self.evidence) >= 1
    
    @classmethod
    def initial(
        cls,
        kind: str,
        severity: str = "negligible",
        status: str = "detected",
        confidence_class: str = "unknown",
    ) -> "ExecutiveConflict":
        """
        Create an initial conflict with minimal required fields.
        
        All other fields will have default values.
        """
        return cls(
            conflict_id=ExecutiveConflictId.generate(),
            revision=ExecutiveConflictRevision.initial(),
            kind=kind,
            status=status,
            severity=severity,
            confidence_class=confidence_class,
        )
    
    def revise(self, new_status: Optional[str] = None) -> "ExecutiveConflict":
        """
        Create a revised version of this conflict.
        
        Creates a new revision with incremented number and preserves lineage
        to the previous revision.
        """
        return ExecutiveConflict(
            conflict_id=self.conflict_id,
            revision=ExecutiveConflictRevision.from_source(
                source_id=str(self.conflict_id),
                base_number=self.revision.number + 1,
            ),
            schema_version=self.schema_version,
            kind=self.kind,
            status=new_status or self.status,
            scope=self.scope,
            subjects=self.subjects,
            sources=self.sources,
            relations=self.relations,
            dimensions=self.dimensions,
            evidence=self.evidence,
            severity=self.severity,
            persistence=self.persistence,
            recurrence=self.recurrence,
            propagation=self.propagation,
            interference=self.interference,
            affected_programs=self.affected_programs,
            affected_task_sets=self.affected_task_sets,
            affected_goals=self.affected_goals,
            affected_commitments=self.affected_commitments,
            affected_decisions=self.affected_decisions,
            affected_actions=self.affected_actions,
            resolution_authority=self.resolution_authority,
            demand_assessment=self.demand_assessment,
            confidence_class=self.confidence_class,
            completeness_class=self.completeness_class,
            validity_class=self.validity_class,
            privacy_classification=self.privacy_classification,
            provenance_created_by=self.provenance_created_by,
            provenance_created_at_utc=self.provenance_created_at_utc,
            provenance_validated_by=self.provenance_validated_by,
            provenance_validated_at_utc=self.provenance_validated_at_utc,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    # Identity types
    "ExecutiveConflictId",
    "ExecutiveConflictRevision",
    "ExecutiveConflictSchemaVersion",
    
    # Enumeration types
    "ExecutiveConflictKind",
    "ExecutiveConflictDimension",
    "ExecutiveConflictStatus",
    
    # Scope model
    "ExecutiveConflictScope",
    
    # Core conflict type
    "ExecutiveConflict",
)