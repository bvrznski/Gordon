# Gordon Cognitive Architecture - Phase 4.11.2
# ===========================================

"""
Coordination Validation Module
==============================

Canonical immutable validators for temporal coordination components.

VALIDATION OVERVIEW
-------------------
Validation ensures all coordination artifacts conform to their contracts.
Validators are pure functions that never mutate inputs and always return
deterministic results.

VALIDATION INVARIANTS:
- Validation is side-effect free
- Validation never mutates input models
- Validation findings remain typed
- Validation ordering is deterministic

VALIDATION PIPELINE:
1. Epoch validation -> 2. Cycle creation validation -> 3. Publication window validation
4. Projection acceptance validation -> 5. Snapshot validation -> 6. Barrier evaluation
7. Convergence validation -> 8. State publication validation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# =============================================================================
# VALIDATION FINDING MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class ValidationFinding:
    """
    Immutable validation finding.
    
    VALIDATION-FINDING-INV-001: Finding is immutable (deeply frozen)
    VALIDATION-FINDING-INV-002: Finding has no runtime references
    
    FINDING-LAW-011: Validation findings shall remain typed
    """
    finding_code: str = ""
    """Code identifying this finding type."""
    
    severity: str = "warning"
    """Severity level (warning, error, critical)."""
    
    subject_refs: tuple[str, ...] = ()
    """References to affected subjects."""
    
    message_params: tuple[str, ...] = ()
    """Parameters for the finding message."""
    
    blocking_status: str = "non_blocking"
    """Whether this finding blocks further processing."""
    
    owning_authority_ref: Optional[str] = None
    """Reference to authority that owns resolution."""
    
    provenance_ref: Optional[str] = None
    """Reference to finding provenance record."""


# =============================================================================
# VALIDATION RESULT MODEL
# =============================================================================

@dataclass(frozen=True, slots=True)
class ValidationResult:
    """
    Immutable validation result.
    
    VALIDATION-RESULT-INV-001: Result is immutable (deeply frozen)
    VALIDATION-RESULT-INV-002: Result has no runtime references
    
    VALIDATION-LAW-011: Validation findings shall remain typed
    """
    is_valid: bool = False
    """Whether validation passed."""
    
    subject_ref: Optional[str] = None
    """Reference to the validated subject."""
    
    findings: tuple[ValidationFinding, ...] = ()
    """Findings from validation."""
    
    limitations: tuple[str, ...] = ()
    """Limitations on this validation."""
    
    provenance_ref: Optional[str] = None
    """Reference to validation provenance record."""
    
    @classmethod
    def valid(
        cls,
        subject_ref: str,
    ) -> ValidationResult:
        """
        Create a valid validation result.
        
        Args:
            subject_ref: Reference to validated subject
            
        Returns:
            A new ValidationResult instance
        """
        return cls(
            is_valid=True,
            subject_ref=subject_ref,
        )
    
    @classmethod
    def invalid(
        cls,
        subject_ref: str,
        findings: tuple[ValidationFinding, ...],
    ) -> ValidationResult:
        """
        Create an invalid validation result.
        
        Args:
            subject_ref: Reference to validated subject
            findings: Validation findings
            
        Returns:
            A new ValidationResult instance
        """
        return cls(
            is_valid=False,
            subject_ref=subject_ref,
            findings=findings,
        )
    
    @classmethod
    def with_limitations(
        cls,
        subject_ref: str,
        findings: tuple[ValidationFinding, ...],
        limitations: tuple[str, ...],
    ) -> ValidationResult:
        """
        Create a validation result with known limitations.
        
        Args:
            subject_ref: Reference to validated subject
            findings: Validation findings
            limitations: Known limitations
            
        Returns:
            A new ValidationResult instance
        """
        return cls(
            is_valid=True,
            subject_ref=subject_ref,
            findings=findings,
            limitations=limitations,
        )


# =============================================================================
# EPOCH VALIDATOR
# =============================================================================

@dataclass(frozen=True, slots=True)
class EpochValidator:
    """
    Immutable validator for coordination epochs.
    
    EPOCH-VALIDATOR-INV-001: Validator is deterministic
    
    Inputs:
    - CoordinationEpoch model
    
    Output: ValidationResult
    """
    
    @classmethod
    def validate_epoch(
        cls,
        epoch_ref: str,
        status: str,
        cycle_references: tuple[str, ...],
        membership_revision: int,
        policy_revision: int,
    ) -> ValidationResult:
        """
        Validate a coordination epoch.
        
        Args:
            epoch_ref: Reference to the epoch
            status: Epoch status string
            cycle_references: References to cycles in the epoch
            membership_revision: Active membership revision
            policy_revision: Active policy revision
            
        Returns:
            A new ValidationResult instance
        """
        findings = []
        
        # Validate status is known
        valid_statuses = {"open", "active", "quiescent", "completing", "complete", "failed", "cancelled", "superseded"}
        if status not in valid_statuses:
            findings.append(
                ValidationFinding(
                    finding_code="invalid_epoch_status",
                    severity="error",
                    subject_refs=(epoch_ref,),
                    message_params=(status,),
                )
            )
        
        # Validate revision is positive
        if membership_revision < 1:
            findings.append(
                ValidationFinding(
                    finding_code="invalid_membership_revision",
                    severity="critical",
                    subject_refs=(epoch_ref,),
                    message_params=(str(membership_revision),),
                )
            )
        
        if policy_revision < 1:
            findings.append(
                ValidationFinding(
                    finding_code="invalid_policy_revision",
                    severity="critical",
                    subject_refs=(epoch_ref,),
                    message_params=(str(policy_revision),),
                )
            )
        
        return ValidationResult(
            is_valid=len(findings) == 0,
            subject_ref=epoch_ref,
            findings=tuple(findings),
        )


# =============================================================================
# CYCLE VALIDATOR
# =============================================================================

@dataclass(frozen=True, slots=True)
class CycleValidator:
    """
    Immutable validator for coordination cycles.
    
    CYCLE-VALIDATOR-INV-001: Validator is deterministic
    
    Inputs:
    - CoordinationCycle model
    
    Output: ValidationResult
    """
    
    @classmethod
    def validate_cycle(
        cls,
        cycle_ref: str,
        lifecycle_status: str,
        epoch_ref: Optional[str],
        state_reference: Optional[str],
    ) -> ValidationResult:
        """
        Validate a coordination cycle.
        
        Args:
            cycle_ref: Reference to the cycle
            lifecycle_status: Lifecycle status string
            epoch_ref: Parent epoch reference (optional)
            state_reference: Produced state reference (optional)
            
        Returns:
            A new ValidationResult instance
        """
        findings = []
        
        # Validate lifecycle status
        valid_statuses = {
            "created", "collecting", "validating", "waiting",
            "ready_to_synchronize", "synchronizing", "building_state",
            "ready_to_publish", "complete", "degraded", "failed", "superseded"
        }
        if lifecycle_status not in valid_statuses:
            findings.append(
                ValidationFinding(
                    finding_code="invalid_cycle_lifecycle_status",
                    severity="error",
                    subject_refs=(cycle_ref,),
                    message_params=(lifecycle_status,),
                )
            )
        
        # Validate state reference for completed cycles
        if lifecycle_status == "complete" and not state_reference:
            findings.append(
                ValidationFinding(
                    finding_code="missing_state_reference",
                    severity="critical",
                    subject_refs=(cycle_ref,),
                )
            )
        
        return ValidationResult(
            is_valid=len(findings) == 0,
            subject_ref=cycle_ref,
            findings=tuple(findings),
        )


# =============================================================================
# PUBLICATION WINDOW VALIDATOR
# =============================================================================

@dataclass(frozen=True, slots=True)
class PublicationWindowValidator:
    """
    Immutable validator for publication windows.
    
    WINDOW-VALIDATOR-INV-001: Validator is deterministic
    
    Inputs:
    - ProjectionPublicationWindow model
    
    Output: ValidationResult
    """
    
    @classmethod
    def validate_window(
        cls,
        window_ref: str,
        status: str,
        required_networks: tuple[str, ...],
        accepted_projections: tuple[str, ...],
    ) -> ValidationResult:
        """
        Validate a publication window.
        
        Args:
            window_ref: Reference to the window
            status: Window status string
            required_networks: Required network references
            accepted_projections: Accepted projection references
            
        Returns:
            A new ValidationResult instance
        """
        findings = []
        
        # Validate status
        valid_statuses = {"pending", "open", "closing", "closed", "invalid", "superseded"}
        if status not in valid_statuses:
            findings.append(
                ValidationFinding(
                    finding_code="invalid_window_status",
                    severity="error",
                    subject_refs=(window_ref,),
                    message_params=(status,),
                )
            )
        
        # Validate required networks have projections
        for network in required_networks:
            network_projections = [p for p in accepted_projections if network in p]
            if not network_projections and status == "closed":
                findings.append(
                    ValidationFinding(
                        finding_code="missing_required_projection",
                        severity="error",
                        subject_refs=(window_ref, network),
                    )
                )
        
        return ValidationResult(
            is_valid=len(findings) == 0,
            subject_ref=window_ref,
            findings=tuple(findings),
        )


# =============================================================================
# BARRIER VALIDATOR
# =============================================================================

@dataclass(frozen=True, slots=True)
class BarrierValidator:
    """
    Immutable validator for synchronization barriers.
    
    BARRIER-VALIDATOR-INV-001: Validator is deterministic
    
    Inputs:
    - CoordinationSynchronizationBarrier model
    
    Output: ValidationResult
    """
    
    @classmethod
    def validate_barrier(
        cls,
        barrier_ref: str,
        status: str,
        required_participants: tuple[str, ...],
        missing_projections: tuple[str, ...],
    ) -> ValidationResult:
        """
        Validate a synchronization barrier.
        
        Args:
            barrier_ref: Reference to the barrier
            status: Barrier status string
            required_participants: Required participant references
            missing_projections: Missing projection references
            
        Returns:
            A new ValidationResult instance
        """
        findings = []
        
        # Validate status
        valid_statuses = {"closed", "partially_satisfied", "open", "open_with_limitations", "blocked", "failed", "superseded"}
        if status not in valid_statuses:
            findings.append(
                ValidationFinding(
                    finding_code="invalid_barrier_status",
                    severity="error",
                    subject_refs=(barrier_ref,),
                    message_params=(status,),
                )
            )
        
        # Validate barrier is closed when required projections are missing
        if missing_projections and status == "open":
            findings.append(
                ValidationFinding(
                    finding_code="barrier_open_with_missing_projections",
                    severity="error",
                    subject_refs=(barrier_ref,) + tuple(missing_projections),
                )
            )
        
        return ValidationResult(
            is_valid=len(findings) == 0,
            subject_ref=barrier_ref,
            findings=tuple(findings),
        )


# =============================================================================
# CONVERGENCE VALIDATOR
# =============================================================================

@dataclass(frozen=True, slots=True)
class ConvergenceValidator:
    """
    Immutable validator for convergence assessments.
    
    CONVERGENCE-VALIDATOR-INV-001: Validator is deterministic
    
    Inputs:
    - CoordinationConvergence model
    
    Output: ValidationResult
    """
    
    @classmethod
    def validate_convergence(
        cls,
        convergence_ref: str,
        status: str,
        barrier_terminal: bool,
    ) -> ValidationResult:
        """
        Validate a convergence assessment.
        
        Args:
            convergence_ref: Reference to the convergence
            status: Convergence status string
            barrier_terminal: Whether barrier is in terminal state
            
        Returns:
            A new ValidationResult instance
        """
        findings = []
        
        # Validate status
        valid_statuses = {"not_evaluated", "changing", "stable", "stable_with_limitations", "blocked", "failed"}
        if status not in valid_statuses:
            findings.append(
                ValidationFinding(
                    finding_code="invalid_convergence_status",
                    severity="error",
                    subject_refs=(convergence_ref,),
                    message_params=(status,),
                )
            )
        
        # Validate stable convergence requires terminal barrier
        if status == "stable" and not barrier_terminal:
            findings.append(
                ValidationFinding(
                    finding_code="stable_convergence_without_terminal_barrier",
                    severity="critical",
                    subject_refs=(convergence_ref,),
                )
            )
        
        return ValidationResult(
            is_valid=len(findings) == 0,
            subject_ref=convergence_ref,
            findings=tuple(findings),
        )


# =============================================================================
# STATE VALIDATION
# =============================================================================

@dataclass(frozen=True, slots=True)
class StateValidator:
    """
    Immutable validator for coordination states.
    
    STATE-VALIDATOR-INV-001: Validator is deterministic
    
    Inputs:
    - CoordinationState model
    
    Output: ValidationResult
    """
    
    @classmethod
    def validate_state(
        cls,
        state_ref: str,
        cycle_ref: Optional[str],
        projections: tuple[str, ...],
        compatibility_status: str,
    ) -> ValidationResult:
        """
        Validate a coordination state.
        
        Args:
            state_ref: Reference to the state
            cycle_ref: Source cycle reference (optional)
            projections: State projections
            compatibility_status: Compatibility status
            
        Returns:
            A new ValidationResult instance
        """
        findings = []
        
        # Validate cycle reference
        if not cycle_ref:
            findings.append(
                ValidationFinding(
                    finding_code="missing_cycle_reference",
                    severity="critical",
                    subject_refs=(state_ref,),
                )
            )
        
        # Validate projections exist
        if not projections:
            findings.append(
                ValidationFinding(
                    finding_code="empty_projection_set",
                    severity="error",
                    subject_refs=(state_ref,),
                )
            )
        
        return ValidationResult(
            is_valid=len(findings) == 0,
            subject_ref=state_ref,
            findings=tuple(findings),
        )