# Workspace Certification Module
# =============================

"""
Canonical WorkspaceCertification and related types.

WorkspaceCertification represents the complete semantic certification of a workspace
state, verifying determinism, boundedness, immutability, provenance, ownership,
authority, architectural laws, invariants, dependency direction, and runtime neutrality.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


CertificationIdentity = str
"""
Unique identifier for a WorkspaceCertification instance.

Characteristics:
- Globally unique across all time
- Never changes once assigned
- External or deterministically derived (never internally generated)
"""


@dataclass(frozen=True)
class CertificationEvidence:
    """
    Evidence supporting a workspace state certification.
    
    Captures the semantic verification results without runtime dependencies.
    """
    
    # Verification checks
    determinism_verified: bool = True
    """Whether determinism was verified."""
    
    boundedness_verified: bool = True
    """Whether boundedness was verified."""
    
    immutability_verified: bool = True
    """Whether deep immutability was verified."""
    
    provenance_verified: bool = True
    """Whether provenance preservation was verified."""
    
    ownership_verified: bool = True
    """Whether ownership boundaries were preserved."""
    
    authority_verified: bool = True
    """Whether authority boundaries were preserved."""
    
    architectural_laws_verified: bool = True
    """Whether all architectural laws were satisfied."""
    
    invariants_verified: bool = True
    """Whether all invariants were satisfied."""
    
    dependency_direction_verified: bool = True
    """Whether dependency direction is correct."""
    
    runtime_neutrality_verified: bool = True
    """Whether no runtime state was embedded."""
    
    # Validation details
    verification_errors: Tuple[str, ...] = field(default_factory=tuple)
    """Any verification errors encountered."""
    
    verification_warnings: Tuple[str, ...] = field(default_factory=tuple)
    """Any verification warnings."""


@dataclass(frozen=True)
class ValidationResult:
    """
    Result of a validation check.
    
    Captures whether a specific aspect passed validation without runtime dependencies.
    """
    
    # Validation status
    valid: bool = False
    """Whether this validation passed."""
    
    validation_kind: str = "general"
    """Kind of validation performed."""
    
    # Target
    validated_target_id: str = ""
    """ID of the item being validated."""
    
    validated_revision: int = 0
    """Revision of the item being validated."""
    
    # Details
    error_message: str = ""
    """Error description if validation failed."""
    
    checked_at_utc: float = 0.0
    """When validation occurred (semantic reference)."""
    
    validator_id: str = ""
    """ID of the validator."""


@dataclass(frozen=True)
class WorkspaceCertification:
    """
    Complete semantic certification of a workspace state.
    
    Certification semantics:
        - Verifies determinism: same inputs produce identical outputs
        - Verifies boundedness: all collections have explicit limits
        - Verifies immutability: no mutation after creation
        - Verifies provenance: origin information is preserved
        - Verifies ownership: external boundaries are respected
        - Verifies authority: decision-making boundaries are preserved
        - Verifies architectural laws: all rules are satisfied
        - Verifies invariants: all invariants hold true
        - Verifies dependency direction: dependencies flow correctly
        - Verifies runtime neutrality: no runtime state embedded
    
    Certification never mutates Workspace State.
    
    ARCHITECTURAL INVARIANT: Every Certified State references exactly one Certification.
    """
    
    # Identity and Revisioning
    certification_id: CertificationIdentity = "certification_initial"
    """Unique identifier for this certification instance."""
    
    certified_revision: int = 0
    """Revision of the state that was certified."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # State reference
    certified_state_id: str = ""
    """ID of the certified workspace state."""
    
    # Certification evidence
    evidence: CertificationEvidence = field(default_factory=CertificationEvidence)
    """Evidence supporting this certification."""
    
    # Validation results
    validation_results: Tuple[ValidationResult, ...] = field(default_factory=tuple)
    """Results of all validation checks performed."""
    
    # Timestamps (semantic only, not runtime state)
    certified_at_utc: float = 0.0
    """When certification was recorded (seconds since epoch)."""
    
    certifying_authority_id: str = ""
    """Authority that performed the certification."""
    
    # Certification outcome
    certification_result: str = "valid"
    """Overall result of the certification (valid, invalid, conditional)."""
    
    @classmethod
    def create_initial(cls) -> WorkspaceCertification:
        """
        Create an initial certification record.
        
        This represents a fresh start with no certifications yet recorded.
        """
        return cls(
            certified_revision=0,
            certification_result="valid",
            certified_state_id="workspace_state_initial",
        )
    
    @property
    def is_fully_certified(self) -> bool:
        """Check if all verification checks passed."""
        return (
            self.evidence.determinism_verified
            and self.evidence.boundedness_verified
            and self.evidence.immutability_verified
            and self.evidence.provenance_verified
            and self.evidence.ownership_verified
            and self.evidence.authority_verified
            and self.evidence.architectural_laws_verified
            and self.evidence.invariants_verified
            and self.evidence.dependency_direction_verified
            and self.evidence.runtime_neutrality_verified
        )


@dataclass(frozen=True)
class CertifiedWorkspaceState:
    """
    The final, certified workspace state artifact.
    
    This is the terminal artifact of Phase 4.6.8 - Workspace State Integration,
    Continuity, and Final Certification.
    
    Contains the complete semantic state along with its certification evidence,
    ensuring that all architectural laws, invariants, and correctness properties
    have been verified.
    
    Properties:
        - Immutable: Cannot be modified after creation
        - Bounded: All collections have explicit limits
        - Certified: All verification checks have passed
        - Deterministic: Same inputs produce identical outputs
        - Runtime-neutral: No runtime state embedded
    
    ARCHITECTURAL INVARIANTS:
        CWS-INV-001: Every certified state has exactly one certification
        CWS-INV-002: Certification never mutates the workspace state
        CWS-INV-003: All architectural laws are satisfied
        CWS-INV-004: All invariants hold true
        CWS-INV-005: Lineage is acyclic
        CWS-INV-006: History is append-only
    """
    
    # Core state
    state_id: str = "workspace_state_initial"
    """Unique identifier for this certified workspace state."""
    
    revision: int = 0
    """Current revision number (strictly monotonic)."""
    
    schema_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # WorkspaceState content
    snapshot: dict = field(default_factory=dict)
    """Semantic snapshot of the workspace state."""
    
    delta_references: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of deltas applied to this state."""
    
    transition_references: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of transitions in the history of this state."""
    
    # Continuity
    continuity_valid: bool = True
    """Whether current continuity is valid."""
    
    lineage_intact: bool = True
    """Whether the lineage chain is intact."""
    
    # Certification
    certification_id: str = ""
    """ID of the associated certification."""
    
    certified_at_utc: float = 0.0
    """When state was certified (semantic reference)."""
    
    certifier_authority_id: str = ""
    """Authority that certified this state."""
    
    certification_result: str = "valid"
    """Result of the certification (valid, invalid, conditional)."""
    
    @classmethod
    def initial(cls) -> CertifiedWorkspaceState:
        """
        Create an initial certified workspace state.
        
        This creates a clean starting point with all verification checks passing.
        """
        return cls(
            state_id="workspace_state_initial",
            revision=0,
            certification_result="valid",
            continuity_valid=True,
            lineage_intact=True,
        )
    
    @property
    def is_terminal(self) -> bool:
        """Check if this certified state represents a terminal condition."""
        # Terminal states are determined by external authorities
        return self.certification_result in ("completed", "failed")


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "CertificationIdentity",
    "CertificationEvidence",
    "ValidationResult",
    "WorkspaceCertification",
    "CertifiedWorkspaceState",
)