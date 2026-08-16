# Memory Lifecycle Contracts - Phase 5.1.4 State Transition Contracts
# ====================================================================
"""
Memory Lifecycle Contracts: The contracts governing lifecycle state transitions.

This module defines the contracts for:
    - Lifecycle ownership and responsibilities
    - State transition validation
    - Admission pipeline
    - Retention policies
    - Archival procedures
    - Supersession semantics
    - Failure handling
    - Recovery mechanisms

Contract Principles:
    CONTRACT-PRINCIPLE-001: Contracts define responsibilities, not implementation
    CONTRACT-PRINCIPLE-002: Contracts are enforced through validation
    CONTRACT-PRINCIPLE-003: Contract violations produce explicit diagnostics
    CONTRACT-PRINCIPLE-004: Contracts preserve history and provenance

Architectural Separation:
    
    Foundation (Memory Artifact)
        ↓ defines what exists
    
    Lifecycle (State Machine)
        ↓ owns state transitions
    
    Operations (Transformations)
        ↓ request transitions
    
    Access (Visibility)
        ↓ exposes resulting state

This separation ensures existence semantics remain independent of
transformation semantics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# LIFECYCLE CONTRACT TYPES
# =============================================================================


class ContractType(Enum):
    """
    Types of lifecycle contracts.
    
    | Type             | Description                                         |
    |------------------|-----------------------------------------------------|
    | ADMISSION        | Artifact admission into Memory Substrate           |
    | ACTIVATION       | Artifact activation for cognition                  |
    | RETENTION        | Long-term preservation decision                    |
    | ARCHIVAL         | Artifact archival (inactive but preserved)         |
    | SUPERSESSION     | Revision supersession (new replaces old)           |
    | FAILURE          | Failure detection and recording                    |
    | RECOVERY         | Recovery from failure state                        |
    """
    
    ADMISSION = "admission"        # Admission into substrate
    ACTIVATION = "activation"      # Activation for cognition
    RETENTION = "retention"        # Retention policy decision
    ARCHIVAL = "archival"          # Artifact archival
    SUPERSESSION = "supersession"  # New revision supersedes old
    FAILURE = "failure"            # Failure detection and recording
    RECOVERY = "recovery"          # Recovery from failure


# =============================================================================
# TRANSITION VALIDATION RESULT
# =============================================================================


@dataclass(frozen=True)
class TransitionValidationResult:
    """
    Result of transition validation.
    
    Fields:
        is_valid:           Was the transition valid?
        
        # If invalid, these are populated
        error_code:         Machine-readable error code
        error_message:      Human-readable error message
        
        # Provenance
        timestamp_utc:      When was validation performed?
    """
    
    is_valid: bool = True
    
    # Error information (populated if not valid)
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    
    # Provenance
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# ADMISSION CONTRACT
# =============================================================================


@dataclass(frozen=True)
class AdmissionResult:
    """
    Result of an admission attempt.
    
    Admission determines whether a candidate Memory Artifact becomes part
    of the Memory Substrate. Success means the artifact enters the ACTIVE state.
    
    Fields:
        is_admitted:       Was the artifact admitted?
        
        # If successful
        artifact_id:       The assigned artifact ID
        initial_state:     Initial lifecycle state (ACTIVE)
        
        # Validation details
        validation_passed: All validation checks passed?
        validation_rules:  Which rules were validated
        
        # Provenance
        timestamp_utc:     When was admission attempted?
        provenance:        Where did this artifact come from?
        
        # Diagnostics
        diagnostics:       Any diagnostic information
    """
    
    is_admitted: bool = False
    
    # Success fields
    artifact_id: Optional[str] = None
    initial_state: str = "active"
    
    # Validation details
    validation_passed: bool = True
    validation_rules: Tuple[str, ...] = field(default_factory=tuple)
    
    # Provenance
    timestamp_utc: float = field(default_factory=time.time)
    provenance: Dict[str, Any] = field(default_factory=lambda: {"origin": "system"})
    
    # Diagnostics
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)


class AdmissionContract:
    """
    Contract for Memory Artifact admission into the Memory Substrate.
    
    Responsibilities:
        - Validate candidate artifacts
        - Assign artifact IDs
        - Initialize revision tracking
        - Establish provenance
        - Record transition history
    
    Admission Laws:
        ADMISSION-LAW-001: Admission creates existence in substrate
        ADMISSION-LAW-002: Admission assigns stable identity
        ADMISSION-LAW-003: Admission initializes revision tracking
        ADMISSION-LAW-004: Admission establishes provenance
        ADMISSION-LAW-005: Admission records transition history
    
    Valid State Transition:
        CANDIDATE → ACTIVE (if validation passes)
    
    If validation fails, the artifact remains in CANDIDATE state (or is rejected).
    """
    
    def __init__(self):
        """Initialize the admission contract."""
        self._admission_count = 0
        self._failure_count = 0
    
    def validate_admission(
        self,
        artifact_id: str,
        provenance: Dict[str, Any],
        artifact_kind: Optional[str] = None,
        validation_rules: Tuple[str, ...] = (),
    ) -> TransitionValidationResult:
        """
        Validate an artifact for admission.
        
        Args:
            artifact_id: The proposed artifact ID
            provenance: Provenance information about the artifact
            artifact_kind: Type of artifact (optional)
            validation_rules: Additional rules to validate against
            
        Returns:
            Validation result with error details if invalid
        """
        # Basic validation
        if not artifact_id or len(artifact_id) == 0:
            return TransitionValidationResult(
                is_valid=False,
                error_code="MISSING_ID",
                error_message="Artifact ID is required for admission",
            )
        
        if provenance is None:
            return TransitionValidationResult(
                is_valid=False,
                error_code="MISSING_PROVENANCE",
                error_message="Provenance information is required for admission",
            )
        
        # Check for duplicate ID (if substrate supports it)
        # This would check the actual substrate in implementation
        
        self._admission_count += 1
        return TransitionValidationResult(is_valid=True)
    
    def execute_admission(
        self,
        artifact_id: str,
        provenance: Dict[str, Any],
        artifact_kind: Optional[str] = None,
        validation_rules: Tuple[str, ...] = (),
    ) -> AdmissionResult:
        """
        Execute the admission of an artifact into the substrate.
        
        This is a contract - actual implementation would be in MemoryLifecycle
        or similar.
        
        Args:
            artifact_id: The proposed artifact ID
            provenance: Provenance information about the artifact
            artifact_kind: Type of artifact (optional)
            validation_rules: Additional rules to validate against
            
        Returns:
            AdmissionResult with success/failure info
        """
        # Validate first
        validation = self.validate_admission(
            artifact_id=artifact_id,
            provenance=provenance,
            artifact_kind=artifact_kind,
            validation_rules=validation_rules,
        )
        
        if not validation.is_valid:
            return AdmissionResult(
                is_admitted=False,
                validation_passed=False,
                diagnostics=(f"Validation failed: {validation.error_message}",),
            )
        
        # Create provenance record
        final_provenance = dict(provenance)
        final_provenance["admission_time_utc"] = time.time()
        final_provenance["admitted_by"] = "lifecycle_system"
        
        self._admission_count += 1
        
        return AdmissionResult(
            is_admitted=True,
            artifact_id=artifact_id,
            initial_state="active",
            validation_passed=True,
            validation_rules=validation_rules + ("admission_validated",),
            provenance=final_provenance,
            diagnostics=("Artifact admitted successfully",),
        )
    
    @property
    def admission_count(self) -> int:
        """Total number of admission attempts."""
        return self._admission_count
    
    @property
    def failure_count(self) -> int:
        """Number of failed admissions."""
        return self._failure_count


# =============================================================================
# ACTIVATION CONTRACT
# =============================================================================


@dataclass(frozen=True)
class ActivationResult:
    """
    Result of an activation attempt.
    
    Activation determines whether an existing artifact participates in
    current cognition. It affects visibility, priority, and availability.
    
    Fields:
        is_activated:      Was the artifact successfully activated?
        
        # Artifact info
        artifact_id:       ID of the artifact
        previous_state:    State before activation
        new_state:         State after activation
        
        # Validation details
        validation_passed: All validation checks passed?
        
        # Provenance
        timestamp_utc:     When was activation attempted?
        provenance:        What triggered this activation?
        
        # Diagnostics
        diagnostics:       Any diagnostic information
    """
    
    is_activated: bool = False
    
    artifact_id: Optional[str] = None
    previous_state: str = "unknown"
    new_state: str = "unknown"
    
    validation_passed: bool = True
    
    timestamp_utc: float = field(default_factory=time.time)
    provenance: Dict[str, Any] = field(default_factory=lambda: {"origin": "system"})
    
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)


class ActivationContract:
    """
    Contract for Memory Artifact activation.
    
    Responsibilities:
        - Validate artifact exists and is accessible
        - Update visibility status
        - Record transition history
        - Preserve semantic identity
    
    Activation Laws:
        ACTIVATION-LAW-001: Activation affects lifecycle state only
        ACTIVATION-LAW-002: Activation never modifies semantic content
        ACTIVATION-LAW-003: Activation preserves identity
        ACTIVATION-LAW-004: Activation preserves provenance
        ACTIVATION-LAW-005: Activation history is inspectable
    
    Valid State Transitions:
        CANDIDATE → ACTIVE (admission completes)
        ACTIVE remains ACTIVE (refresh/keep-alive)
    
    Invalid Transitions:
        ARCHIVED → ACTIVE (must first unarchive)
        SUPERSEDED → ACTIVE (cannot reactivate superseded revisions)
        FAILED → ACTIVE (must recover first)
    """
    
    def __init__(self):
        """Initialize the activation contract."""
        self._activation_count = 0
    
    def validate_activation(
        self,
        artifact_id: str,
        current_state: str,
        requested_state: str = "active",
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if an artifact can be activated.
        
        Args:
            artifact_id: ID of the artifact
            current_state: Current lifecycle state
            requested_state: State being requested
            
        Returns:
            (is_valid, error_message) tuple
        """
        # Map string states to our state enum for validation
        from .states import LifecycleState
        
        try:
            current = LifecycleState(current_state)
            requested = LifecycleState(requested_state)
        except ValueError as e:
            return False, f"Invalid state: {e}"
        
        # Define valid transitions for activation
        if current == LifecycleState.CANDIDATE:
            if requested != LifecycleState.ACTIVE:
                return False, "CANDIDATE can only transition to ACTIVE"
        
        elif current == LifecycleState.ACTIVE:
            if requested != LifecycleState.ACTIVE:
                return False, "ACTIVE is already active (refresh only)"
        
        elif current == LifecycleState.FAILED:
            # Must recover first
            return False, "FAILED artifacts must be recovered before activation"
        
        else:
            return False, (
                f"Cannot activate from {current.value}. "
                f"Only CANDIDATE and ACTIVE can transition to ACTIVE"
            )
        
        self._activation_count += 1
        return True, None
    
    def execute_activation(
        self,
        artifact_id: str,
        current_state: str,
        previous_state: Optional[str] = None,
        trigger: str = "lifecycle_system",
    ) -> ActivationResult:
        """
        Execute the activation of an artifact.
        
        Args:
            artifact_id: ID of the artifact
            current_state: Current lifecycle state
            previous_state: State before this operation (if known)
            trigger: What triggered this activation?
            
        Returns:
            ActivationResult with success/failure info
        """
        is_valid, error = self.validate_activation(
            artifact_id=artifact_id,
            current_state=current_state,
            requested_state="active",
        )
        
        if not is_valid:
            return ActivationResult(
                is_activated=False,
                artifact_id=artifact_id,
                previous_state=current_state,
                new_state=current_state,
                validation_passed=False,
                provenance={"trigger": trigger},
                diagnostics=(f"Activation failed: {error}",),
            )
        
        new_state = "active"
        self._activation_count += 1
        
        return ActivationResult(
            is_activated=True,
            artifact_id=artifact_id,
            previous_state=current_state,
            new_state=new_state,
            validation_passed=True,
            provenance={"trigger": trigger, "timestamp_utc": time.time()},
            diagnostics=("Artifact activated successfully",),
        )
    
    @property
    def activation_count(self) -> int:
        """Total number of activations."""
        return self._activation_count


# =============================================================================
# RETENTION CONTRACT
# =============================================================================


@dataclass(frozen=True)
class RetentionDecision:
    """
    A retention policy decision for an artifact.
    
    Fields:
        artifact_id:       ID of the artifact
        is_retained:       Will this artifact be retained?
        
        # Evaluation results
        importance_score:  How important is this artifact?
        utility_score:     How useful is this artifact?
        stability_score:   How stable is this artifact's semantics?
        
        # Decision details
        retention_period:  For how long should it be retained (seconds)?
        decision_reason:   Why was this decision made?
        
        # Timestamps
        evaluated_at_utc:  When was this evaluated?
    """
    
    artifact_id: str
    is_retained: bool = True
    
    importance_score: float = 0.5       # 0.0-1.0
    utility_score: float = 0.5          # 0.0-1.0
    stability_score: float = 0.5        # 0.0-1.0
    
    retention_period: int = 86400       # Default: 24 hours (seconds)
    decision_reason: str = "default_retention"
    
    evaluated_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class RetentionResult:
    """
    Result of a retention policy evaluation.
    
    Fields:
        is_retained:       Was the artifact retained?
        
        # Artifact info
        artifact_id:       ID of the artifact
        previous_state:    State before evaluation
        new_state:         State after evaluation
        
        # Evaluation details
        decision:          RetentionDecision object
        scores:            Evaluation scores
        
        # Provenance
        timestamp_utc:     When was this evaluated?
        provenance:        What triggered this evaluation?
        
        # Diagnostics
        diagnostics:       Any diagnostic information
    """
    
    is_retained: bool = False
    
    artifact_id: Optional[str] = None
    previous_state: str = "unknown"
    new_state: str = "unknown"
    
    decision: RetentionDecision = field(default_factory=lambda: RetentionDecision(""))
    
    scores: Dict[str, float] = field(default_factory=dict)
    
    timestamp_utc: float = field(default_factory=time.time)
    provenance: Dict[str, Any] = field(default_factory=lambda: {"origin": "system"})
    
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)


class RetentionContract:
    """
    Contract for long-term artifact retention.
    
    Responsibilities:
        - Evaluate importance, utility, and stability
        - Make retention decisions
        - Determine retention period
        - Record evaluation results
    
    Retention Laws:
        RETENTION-LAW-001: Retention preserves Memory Artifacts
        RETENTION-LAW-002: Retention never redefines semantics
        RETENTION-LAW-003: Retention preserves provenance
        RETENTION-LAW-004: Retention preserves revision history
        RETENTION-LAW-005: Retention decisions are explicit
    
    Valid State Transitions:
        ACTIVE → RETAINED (if retention decision is positive)
        RETAINED remains RETAINED (extension of retention period)
    
    Invalid Transitions:
        ARCHIVED → RETAINED (must unarchive first)
        SUPERSEDED → RETAINED (superseded revisions follow their own rules)
    """
    
    def __init__(
        self,
        default_retention_period: int = 86400,  # 24 hours
        importance_threshold: float = 0.5,
        utility_threshold: float = 0.5,
        stability_threshold: float = 0.5,
    ):
        """
        Initialize the retention contract.
        
        Args:
            default_retention_period: Default period in seconds (default: 24h)
            importance_threshold: Minimum importance score to retain
            utility_threshold: Minimum utility score to retain
            stability_threshold: Minimum stability score to retain
        """
        self.default_retention_period = default_retention_period
        self.importance_threshold = importance_threshold
        self.utility_threshold = utility_threshold
        self.stability_threshold = stability_threshold
        self._evaluation_count = 0
    
    def evaluate_retention(
        self,
        artifact_id: str,
        current_state: str,
        semantic_content: Optional[Dict[str, Any]] = None,
        revision_history: Optional[Tuple[Any, ...]] = None,
        usage_patterns: Optional[Dict[str, float]] = None,
    ) -> RetentionDecision:
        """
        Evaluate whether an artifact should be retained.
        
        Args:
            artifact_id: ID of the artifact
            current_state: Current lifecycle state
            semantic_content: Content of the artifact (for importance eval)
            revision_history: History of revisions (for stability eval)
            usage_patterns: How has this been used? (for utility eval)
            
        Returns:
            RetentionDecision with evaluation results
        """
        self._evaluation_count += 1
        
        # Default values
        importance = 0.5
        utility = 0.5
        stability = 0.5
        
        # Evaluate importance from semantic content
        if semantic_content:
            # Simplified: count of content keys as proxy for importance
            importance = min(1.0, len(semantic_content) / 10.0)
        
        # Evaluate utility from usage patterns
        if usage_patterns and "access_count" in usage_patterns:
            access_count = usage_patterns.get("access_count", 0)
            # Logarithmic scaling for access count utility
            utility = min(1.0, (access_count / 100.0) + 0.1)
        
        # Evaluate stability from revision history
        if revision_history and len(revision_history) > 0:
            revisions = len(revision_history)
            if revisions < 3:
                stability = 0.8  # Few changes = stable
            elif revisions < 5:
                stability = 0.6  # Some changes
            else:
                stability = 0.4  # Many changes = less stable
        
        # Make decision based on thresholds
        is_retained = (
            importance >= self.importance_threshold and
            utility >= self.utility_threshold and
            stability >= self.stability_threshold
        )
        
        retention_period = (
            self.default_retention_period if is_retained else 0
        )
        
        reason = "retained" if is_retained else "not_retained"
        
        return RetentionDecision(
            artifact_id=artifact_id,
            is_retained=is_retained,
            importance_score=importance,
            utility_score=utility,
            stability_score=stability,
            retention_period=retention_period,
            decision_reason=f"{reason}: importance={importance:.2f}, "
                           f"utility={utility:.2f}, stability={stability:.2f}",
        )
    
    def execute_retention(
        self,
        artifact_id: str,
        current_state: str,
        previous_state: Optional[str] = None,
        retention_period: Optional[int] = None,
    ) -> RetentionResult:
        """
        Execute the retention decision.
        
        Args:
            artifact_id: ID of the artifact
            current_state: Current lifecycle state
            previous_state: State before evaluation
            retention_period: How long to retain (if different from default)
            
        Returns:
            RetentionResult with outcome
        """
        # Perform evaluation
        decision = self.evaluate_retention(artifact_id, current_state)
        
        if retention_period is not None:
            # Simple dataclass replacement without circular dependency
            from dataclasses import replace as dc_replace
            decision = dc_replace(decision, retention_period=retention_period)
        
        # Determine new state based on decision
        from .states import LifecycleState
        
        if decision.is_retained:
            new_state = "retained"
        else:
            # If not retained, might archive or fail depending on policy
            new_state = current_state  # Keep current state for now
        
        return RetentionResult(
            is_retained=decision.is_retained,
            artifact_id=artifact_id,
            previous_state=current_state,
            new_state=new_state,
            decision=decision,
            scores={
                "importance": decision.importance_score,
                "utility": decision.utility_score,
                "stability": decision.stability_score,
            },
            provenance={"timestamp_utc": time.time()},
            diagnostics=(f"Retention: {decision.decision_reason}",),
        )
    
    @property
    def evaluation_count(self) -> int:
        """Total number of retention evaluations."""
        return self._evaluation_count


# =============================================================================
# ARCHIVAL CONTRACT
# =============================================================================


@dataclass(frozen=True)
class ArchivalResult:
    """
    Result of an archival operation.
    
    Fields:
        is_archived:       Was the artifact archived?
        
        # Artifact info
        artifact_id:       ID of the artifact
        previous_state:    State before archival
        
        # Timestamps
        archived_at_utc:   When was this archived?
        retention_until:   When will it be eligible for removal?
        
        # Validation details
        validation_passed: All validation checks passed?
        
        # Provenance
        provenance:        What triggered this archival?
        
        # Diagnostics
        diagnostics:       Any diagnostic information
    """
    
    is_archived: bool = False
    
    artifact_id: Optional[str] = None
    previous_state: str = "unknown"
    
    archived_at_utc: float = field(default_factory=time.time)
    retention_until: Optional[float] = None
    
    validation_passed: bool = True
    
    provenance: Dict[str, Any] = field(default_factory=lambda: {"origin": "system"})
    
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)


class ArchivalContract:
    """
    Contract for artifact archival.
    
    Responsibilities:
        - Transition artifacts from ACTIVE/RETAINED to ARCHIVED state
        - Preserve all semantic content
        - Record provenance of archival decision
        - Enable queryability of archived artifacts
    
    Archival Laws:
        ARCHIVAL-LAW-001: Archival preserves complete semantic history
        ARCHIVAL-LAW-002: Archived artifacts remain queryable
        ARCHIVAL-LAW-003: Archival preserves provenance
        ARCHIVAL-LAW-004: Archival preserves revision lineage
        ARCHIVAL-LAW-005: Archival never destroys artifacts
    
    Valid State Transitions:
        ACTIVE → ARCHIVED (via retention policy)
        RETAINED → ARCHIVED (via retention policy)
    
    Invalid Transitions:
        CANDIDATE → ARCHIVED (must go through ACTIVE first)
        SUPERSEDED → ARCHIVED (superseded follows different rules)
        FAILED → ARCHIVED (must recover or be deleted)
    """
    
    def __init__(self):
        """Initialize the archival contract."""
        self._archival_count = 0
    
    def validate_archival(
        self,
        artifact_id: str,
        current_state: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if an artifact can be archived.
        
        Args:
            artifact_id: ID of the artifact
            current_state: Current lifecycle state
            
        Returns:
            (is_valid, error_message) tuple
        """
        from .states import LifecycleState
        
        try:
            current = LifecycleState(current_state)
        except ValueError as e:
            return False, f"Invalid state: {e}"
        
        # Only ACTIVE and RETAINED can be archived
        if current not in (LifecycleState.ACTIVE, LifecycleState.RETAINED):
            return False, (
                f"Cannot archive from {current.value}. "
                f"Only ACTIVE and RETAINED can be archived"
            )
        
        return True, None
    
    def execute_archival(
        self,
        artifact_id: str,
        current_state: str,
        previous_state: Optional[str] = None,
        retention_period_days: int = 365,
    ) -> ArchivalResult:
        """
        Execute the archival of an artifact.
        
        Args:
            artifact_id: ID of the artifact
            current_state: Current lifecycle state
            previous_state: State before archival (if known)
            retention_period_days: How long to retain in archive (days)
            
        Returns:
            ArchivalResult with success/failure info
        """
        is_valid, error = self.validate_archival(artifact_id, current_state)
        
        if not is_valid:
            return ArchivalResult(
                is_archived=False,
                artifact_id=artifact_id,
                previous_state=current_state,
                validation_passed=False,
                diagnostics=(f"Archival failed: {error}",),
            )
        
        new_state = "archived"
        self._archival_count += 1
        
        retention_until = time.time() + (retention_period_days * 86400)
        
        return ArchivalResult(
            is_archived=True,
            artifact_id=artifact_id,
            previous_state=current_state,
            archived_at_utc=time.time(),
            retention_until=retention_until,
            validation_passed=True,
            provenance={"timestamp_utc": time.time(), "retention_days": retention_period_days},
            diagnostics=(f"Artifact archived until {retention_until}",),
        )
    
    @property
    def archival_count(self) -> int:
        """Total number of archivals."""
        return self._archival_count


# =============================================================================
# SUPERSESSION CONTRACT
# =============================================================================


@dataclass(frozen=True)
class SupersessionResult:
    """
    Result of a supersession operation.
    
    Fields:
        is_superseded:     Was the artifact superseded?
        
        # Artifact info
        artifact_id:       ID of the artifact that was superseded
        new_artifact_id:   ID of the new revision (if different)
        previous_state:    State before supersession
        
        # Revision tracking
        old_revision:      Which revision was superseded
        new_revision:      What is the next revision number
        
        # Timestamps
        superseded_at_utc: When was this superseded?
        
        # Validation details
        validation_passed: All validation checks passed?
        
        # Provenance
        provenance:        What triggered this supersession?
        
        # Diagnostics
        diagnostics:       Any diagnostic information
    """
    
    is_superseded: bool = False
    
    artifact_id: Optional[str] = None
    new_artifact_id: Optional[str] = None
    previous_state: str = "unknown"
    
    old_revision: int = 1
    new_revision: int = 2
    
    superseded_at_utc: float = field(default_factory=time.time)
    
    validation_passed: bool = True
    
    provenance: Dict[str, Any] = field(default_factory=lambda: {"origin": "system"})
    
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)


class SupersessionContract:
    """
    Contract for artifact supersession (revision replacement).
    
    Responsibilities:
        - Create new revision with incremented version number
        - Mark old revision as SUPERSEDED
        - Preserve all semantic history
        - Link revisions via provenance
    
    Supersession Laws:
        SUPERSESSION-LAW-001: Supersession preserves previous revisions
        SUPERSESSION-LAW-002: Superseded artifacts remain inspectable
        SUPERSESSION-LAW-003: Supersession preserves provenance
        SUPERSESSION-LAW-004: Supersession preserves semantic identity
        SUPERSESSION-LAW-005: Supersession explicitly references successor
    
    Valid State Transitions:
        ACTIVE → SUPERSEDED (when new revision is created)
    
    Invalid Transitions:
        CANDIDATE → SUPERSEDED (must be active first)
        ARCHIVED → SUPERSEDED (unarchive first if needed)
        SUPERSEDED → SUPERSEDED (already superseded)
    """
    
    def __init__(self):
        """Initialize the supersession contract."""
        self._supersession_count = 0
    
    def validate_supersession(
        self,
        artifact_id: str,
        current_state: str,
        current_revision: int,
    ) -> Tuple[bool, Optional[str], int]:
        """
        Validate if an artifact can be superseded.
        
        Args:
            artifact_id: ID of the artifact
            current_state: Current lifecycle state
            current_revision: Current revision number
            
        Returns:
            (is_valid, error_message, new_revision) tuple
        """
        from .states import LifecycleState
        
        try:
            current = LifecycleState(current_state)
        except ValueError as e:
            return False, f"Invalid state: {e}", current_revision
        
        # Only ACTIVE can be superseded
        if current != LifecycleState.ACTIVE:
            return False, (
                f"Cannot supersede from {current.value}. "
                f"Only ACTIVE can be superseded"
            ), current_revision
        
        new_revision = current_revision + 1
        
        return True, None, new_revision
    
    def execute_supersession(
        self,
        artifact_id: str,
        current_state: str,
        current_revision: int,
        previous_state: Optional[str] = None,
    ) -> SupersessionResult:
        """
        Execute the supersession of an artifact (create new revision).
        
        Args:
            artifact_id: ID of the artifact
            current_state: Current lifecycle state
            current_revision: Current revision number
            previous_state: State before supersession (if known)
            
        Returns:
            SupersessionResult with success/failure info
        """
        is_valid, error, new_revision = self.validate_supersession(
            artifact_id, current_state, current_revision
        )
        
        if not is_valid:
            return SupersessionResult(
                is_superseded=False,
                artifact_id=artifact_id,
                previous_state=current_state,
                old_revision=current_revision,
                validation_passed=False,
                diagnostics=(f"Supersession failed: {error}",),
            )
        
        new_artifact_id = f"{artifact_id}:v{new_revision}"
        self._supersession_count += 1
        
        return SupersessionResult(
            is_superseded=True,
            artifact_id=artifact_id,
            new_artifact_id=new_artifact_id,
            previous_state=current_state,
            old_revision=current_revision,
            new_revision=new_revision,
            superseded_at_utc=time.time(),
            validation_passed=True,
            provenance={
                "timestamp_utc": time.time(),
                "previous_revision": current_revision,
                "new_revision": new_revision,
                "reason": "supersession",
            },
            diagnostics=(
                f"Revision {current_revision} superseded by revision {new_revision}",
            ),
        )
    
    @property
    def supersession_count(self) -> int:
        """Total number of supersessions."""
        return self._supersession_count


# =============================================================================
# FAILURE CONTRACT
# =============================================================================


@dataclass(frozen=True)
class FailureRecord:
    """
    Record of a lifecycle failure.
    
    Fields:
        failure_id:        Unique ID for this failure record
        artifact_id:       ID of the affected artifact
        
        # Failure details
        failure_type:      Type of failure (validation, integrity, etc.)
        severity:          0.0-1.0 severity level
        description:       Human-readable description
        
        # Detection
        detected_at_utc:   When was this detected?
        detected_by:       What/who detected it?
        
        # Recovery info
        recoverable:       Can this be recovered?
        recovery_suggestion: Suggested recovery action
    """
    
    failure_id: str = field(default_factory=lambda: f"fail:{uuid.uuid4().hex[:12]}")
    artifact_id: Optional[str] = None
    
    failure_type: str = "unknown"
    severity: float = 0.5  # 0.0-1.0
    description: str = "Unknown failure"
    
    detected_at_utc: float = field(default_factory=time.time)
    detected_by: str = "lifecycle_system"
    
    recoverable: bool = True
    recovery_suggestion: str = ""


@dataclass(frozen=True)
class FailureResult:
    """
    Result of a failure detection.
    
    Fields:
        is_failure:        Was a failure detected?
        
        # Artifact info
        artifact_id:       ID of the affected artifact
        previous_state:    State before failure
        
        # Failure details
        failure_record:    FailureRecord with full details
        
        # Provenance
        timestamp_utc:     When was failure recorded?
        
        # Diagnostics
        diagnostics:       Any diagnostic information
    """
    
    is_failure: bool = False
    
    artifact_id: Optional[str] = None
    previous_state: str = "unknown"
    
    failure_record: FailureRecord = field(
        default_factory=lambda: FailureRecord()
    )
    
    timestamp_utc: float = field(default_factory=time.time)
    
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)


class FailureContract:
    """
    Contract for lifecycle failure detection and recording.
    
    Responsibilities:
        - Detect lifecycle failures
        - Record failure with full provenance
        - Mark affected artifacts as FAILED
        - Determine recoverability
    
    Failure Laws:
        FAILURE-LAW-001: Failure never silently invalidates Memory
        FAILURE-LAW-002: Failure preserves diagnostics
        FAILURE-LAW-003: Failure preserves provenance
        FAILURE-LAW-004: Failure preserves revision history
        FAILURE-LAW-005: Failure severity is explicit
    
    Valid State Transitions:
        Any state → FAILED (when failure detected)
    
    Note: The artifact remains accessible for inspection but is excluded
    from active cognition.
    """
    
    def __init__(self):
        """Initialize the failure contract."""
        self._failure_count = 0
    
    def validate_failure(
        self,
        artifact_id: str,
        current_state: str,
        failure_type: str,
        severity: float,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if a failure should be recorded.
        
        Args:
            artifact_id: ID of the affected artifact
            current_state: Current lifecycle state
            failure_type: Type of failure (validation, integrity, etc.)
            severity: Severity level 0.0-1.0
            
        Returns:
            (is_valid, error_message) tuple
        """
        if not artifact_id:
            return False, "Artifact ID is required"
        
        if not failure_type or len(failure_type) == 0:
            return False, "Failure type must be specified"
        
        if not (0.0 <= severity <= 1.0):
            return False, f"Severity must be 0.0-1.0, got {severity}"
        
        return True, None
    
    def execute_failure(
        self,
        artifact_id: str,
        current_state: str,
        failure_type: str,
        severity: float = 0.5,
        description: str = "Lifecycle failure detected",
        recoverable: bool = True,
        detected_by: str = "lifecycle_system",
    ) -> FailureResult:
        """
        Execute the recording of a failure.
        
        Args:
            artifact_id: ID of the affected artifact
            current_state: Current lifecycle state
            failure_type: Type of failure
            severity: Severity level 0.0-1.0
            description: Human-readable description
            recoverable: Can this be recovered?
            detected_by: What/who detected it?
            
        Returns:
            FailureResult with full details
        """
        is_valid, error = self.validate_failure(
            artifact_id, current_state, failure_type, severity
        )
        
        if not is_valid:
            # Even validation failures can create records
            return FailureResult(
                is_failure=True,
                artifact_id=artifact_id,
                previous_state=current_state,
                timestamp_utc=time.time(),
                diagnostics=(f"Failure recording issue: {error}",),
            )
        
        failure_record = FailureRecord(
            artifact_id=artifact_id,
            failure_type=failure_type,
            severity=severity,
            description=description,
            recoverable=recoverable,
            recovery_suggestion=(
                f"Attempt RECOVERY transition from FAILED to RECOVERING"
            ),
            detected_by=detected_by,
        )
        
        self._failure_count += 1
        
        return FailureResult(
            is_failure=True,
            artifact_id=artifact_id,
            previous_state=current_state,
            failure_record=failure_record,
            timestamp_utc=time.time(),
            diagnostics=(f"Failure recorded: {description}",),
        )
    
    @property
    def failure_count(self) -> int:
        """Total number of failures recorded."""
        return self._failure_count


# =============================================================================
# RECOVERY CONTRACT
# =============================================================================


@dataclass(frozen=True)
class RecoveryResult:
    """
    Result of a recovery operation.
    
    Fields:
        is_recovered:      Was the artifact recovered?
        
        # Artifact info
        artifact_id:       ID of the artifact
        previous_state:    State before recovery
        
        # Recovery details
        recovery_method:   How was it recovered?
        recovery_actions:  What actions were taken?
        
        # Validation after recovery
        post_recovery_validation: Is the artifact valid now?
        
        # Timestamps
        recovered_at_utc:  When was this recovered?
        
        # Provenance
        provenance:        What triggered recovery?
        
        # Diagnostics
        diagnostics:       Any diagnostic information
    """
    
    is_recovered: bool = False
    
    artifact_id: Optional[str] = None
    previous_state: str = "unknown"
    
    recovery_method: str = ""
    recovery_actions: Tuple[str, ...] = field(default_factory=tuple)
    
    post_recovery_validation: bool = True
    
    recovered_at_utc: float = field(default_factory=time.time)
    
    provenance: Dict[str, Any] = field(default_factory=lambda: {"origin": "system"})
    
    diagnostics: Tuple[str, ...] = field(default_factory=tuple)


class RecoveryContract:
    """
    Contract for recovery from lifecycle failure.
    
    Responsibilities:
        - Attempt to restore lifecycle consistency
        - Revalidate artifact integrity
        - Repair transition metadata if possible
        - Restore accessibility if recovery succeeds
    
    Recovery Laws:
        RECOVERY-LAW-001: Recovery restores lifecycle consistency
        RECOVERY-LAW-002: Recovery never fabricates history
        RECOVERY-LAW-003: Recovery preserves provenance
        RECOVERY-LAW-004: Recovery preserves identity
        RECOVERY-LAW-005: Recovery preserves revision lineage
    
    Valid State Transitions:
        FAILED → RECOVERING (initiate recovery)
        RECOVERING → ACTIVE (recovery successful)
        RECOVERING → FAILED (recovery failed - give up)
    
    Invalid Transitions:
        Any non-FAILED state → RECOVERING
        RECOVERING directly to any state except ACTIVE or FAILED
    """
    
    def __init__(self):
        """Initialize the recovery contract."""
        self._recovery_attempts = 0
        self._successful_recoveries = 0
    
    def validate_recovery_initiation(
        self,
        artifact_id: str,
        current_state: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if recovery can be initiated.
        
        Args:
            artifact_id: ID of the artifact
            current_state: Current lifecycle state
            
        Returns:
            (is_valid, error_message) tuple
        """
        from .states import LifecycleState
        
        try:
            current = LifecycleState(current_state)
        except ValueError as e:
            return False, f"Invalid state: {e}"
        
        if current != LifecycleState.FAILED:
            return False, (
                f"Recovery can only be initiated for FAILED artifacts. "
                f"Current state: {current.value}"
            )
        
        self._recovery_attempts += 1
        return True, None
    
    def initiate_recovery(
        self,
        artifact_id: str,
        current_state: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Initiate recovery process for a FAILED artifact.
        
        Args:
            artifact_id: ID of the artifact
            current_state: Current lifecycle state
            
        Returns:
            (success, error_message) tuple
        """
        return self.validate_recovery_initiation(artifact_id, current_state)
    
    def execute_recovery(
        self,
        artifact_id: str,
        current_state: str,
        recovery_method: str = "manual",
        recovery_actions: Tuple[str, ...] = (),
    ) -> RecoveryResult:
        """
        Execute the recovery of a FAILED artifact.
        
        Args:
            artifact_id: ID of the artifact
            current_state: Current lifecycle state (should be RECOVERING)
            recovery_method: How is recovery being performed?
            recovery_actions: What actions were taken?
            
        Returns:
            RecoveryResult with success/failure info
        """
        # Validate we can recover from current state
        from .states import LifecycleState
        
        try:
            current = LifecycleState(current_state)
        except ValueError as e:
            return RecoveryResult(
                is_recovered=False,
                artifact_id=artifact_id,
                previous_state=current_state,
                diagnostics=(f"Invalid state: {e}",),
            )
        
        # Can recover from FAILED state (initiate) or RECOVERING state
        if current not in (LifecycleState.FAILED, LifecycleState.RECOVERING):
            return RecoveryResult(
                is_recovered=False,
                artifact_id=artifact_id,
                previous_state=current_state,
                diagnostics=(f"Can only recover from FAILED or RECOVERING state",),
            )
        
        # Simulate recovery process
        self._recovery_attempts += 1
        
        # In a real implementation, this would check if recovery is actually possible
        # For now, assume successful recovery with some probability
        
        # Check if we have enough information to recover
        has_sufficient_info = len(recovery_actions) > 0 or recovery_method != "manual"
        
        if has_sufficient_info:
            self._successful_recoveries += 1
            
            return RecoveryResult(
                is_recovered=True,
                artifact_id=artifact_id,
                previous_state=current_state,
                recovery_method=recovery_method,
                recovery_actions=recovery_actions,
                post_recovery_validation=True,
                recovered_at_utc=time.time(),
                provenance={
                    "timestamp_utc": time.time(),
                    "recovery_method": recovery_method,
                },
                diagnostics=(
                    f"Recovery successful via {recovery_method}: "
                    f"{', '.join(recovery_actions)}",
                ),
            )
        else:
            # Recovery failed
            return RecoveryResult(
                is_recovered=False,
                artifact_id=artifact_id,
                previous_state=current_state,
                recovery_method=recovery_method,
                recovery_actions=recovery_actions,
                post_recovery_validation=False,
                recovered_at_utc=time.time(),
                provenance={
                    "timestamp_utc": time.time(),
                    "recovery_method": recovery_method,
                },
                diagnostics=(f"Recovery failed: insufficient information",),
            )
    
    @property
    def recovery_attempts(self) -> int:
        """Total number of recovery attempts."""
        return self._recovery_attempts
    
    @property
    def recovery_success_rate(self) -> float:
        """Success rate of recoveries (0.0-1.0)."""
        if self._recovery_attempts == 0:
            return 1.0
        return self._successful_recoveries / self._recovery_attempts


# =============================================================================
# UTILITY: CONTRACT REGISTRY
# =============================================================================


CONTRACT_REGISTRY: Dict[ContractType, Any] = {
    ContractType.ADMISSION: AdmissionContract(),
    ContractType.ACTIVATION: ActivationContract(),
    ContractType.RETENTION: RetentionContract(),
    ContractType.ARCHIVAL: ArchivalContract(),
    ContractType.SUPERSESSION: SupersessionContract(),
    ContractType.FAILURE: FailureContract(),
    ContractType.RECOVERY: RecoveryContract(),
}


def get_contract(contract_type: ContractType) -> Any:
    """
    Get the contract instance for a given type.
    
    Args:
        contract_type: Type of contract needed
        
    Returns:
        Contract instance
    """
    return CONTRACT_REGISTRY.get(contract_type)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "ContractType",
    
    # Validation results
    "TransitionValidationResult",
    
    # Results
    "AdmissionResult",
    "ActivationResult",
    "RetentionDecision",
    "RetentionResult",
    "ArchivalResult",
    "SupersessionResult",
    "FailureRecord",
    "FailureResult",
    "RecoveryResult",
    
    # Contracts
    "AdmissionContract",
    "ActivationContract",
    "RetentionContract",
    "ArchivalContract",
    "SupersessionContract",
    "FailureContract",
    "RecoveryContract",
    
    # Registry
    "CONTRACT_REGISTRY",
    "get_contract",
]