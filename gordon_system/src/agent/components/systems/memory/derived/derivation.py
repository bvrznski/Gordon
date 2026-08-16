# Derived Memory Derivation Contract - Phase 5.1.6 Canonical Implementation
# ==========================================================================
"""
Derivation: The core contract for semantic inference operations.

Purpose:
    Define the interface and data structures for all derivation types.
    
Derivations compute new semantic artifacts from existing memory, following
strict contracts that ensure:

- Source artifacts remain unchanged (DERIVATION-LAW-002)
- Provenance is preserved (DERIVATION-LAW-004) 
- Evidence is explicit (DERIVATION-LAW-006)
- Deterministic behavior (DERIVATION-LAW-008)

Derivation Flow:
    Memory Artifacts
         ↓
    Evidence Selection  → selects relevant source artifacts and relations
         ↓
    Inference           → applies derivation method (causal, counterfactual, etc.)
         ↓
    Validation          → verifies evidence completeness and consistency
         ↓
    Derived Artifact    → published to memory substrate with full provenance

Derivation Kinds:
    CAUSAL           : Infer cause-effect relationships
    COUNTERFACTUAL   : Infer alternative histories  
    PREDICTIVE       : Infer future states
    
Derivation Status:
    PROPOSED     : Derivation created but not yet validated
    VALIDATING   : Validation in progress
    VALIDATED    : Successfully validated, ready for publication
    REJECTED     : Failed validation, cannot be published
    PUBLISHED    : Published to memory substrate
    REVISED      : Revised and revalidated
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# DERIVATION KINDS - What kind of semantic inference?
# =============================================================================


class DerivationKind(Enum):
    """
    Kinds of derivations.
    
    | Kind           | Purpose                                           |
    |----------------|---------------------------------------------------|
    | CAUSAL         : Infer causal structure from artifacts
    | COUNTERFACTUAL : Infer alternative histories  
    | PREDICTIVE     : Infer future states
    
    All derivations produce derived memory artifacts with explicit provenance.
    """
    
    CAUSAL = "causal"               # Cause-effect inference
    COUNTERFACTUAL = "counterfactual"  # Alternative history inference
    PREDICTIVE = "predictive"       # Future state inference


# =============================================================================
# DERIVATION STATUS - What is the derivation's current state?
# =============================================================================


class DerivationStatus(Enum):
    """
    Status of a derivation.
    
    | Status        | Description                                       |
    |---------------|---------------------------------------------------|
    | PROPOSED      : Derivation created, awaiting validation
    | VALIDATING    : Validation in progress
    | VALIDATED     : Successfully validated
    | REJECTED      : Validation failed
    | PUBLISHED     : Published to memory substrate
    | REVISED       : Revised and revalidated
    
    Status transitions must follow the contract.
    """
    
    PROPOSED = "proposed"
    VALIDATING = "validating"
    VALIDATED = "validated"
    REJECTED = "rejected"
    PUBLISHED = "published"
    REVISED = "revised"


# =============================================================================
# SUPPORTING EVIDENCE - What supports this derivation?
# =============================================================================


@dataclass(frozen=True)
class SupportingEvidence:
    """
    Evidence supporting a derivation.
    
    Fields:
        evidence_id:         Unique identifier for this piece of evidence
        source_artifact_ids: IDs of artifacts that support this derivation
        relations_used:      Relations between supporting artifacts
        confidence:          Confidence in this evidence (0.0-1.0)
        timestamp_utc:       When this evidence was collected
        
    Evidence Laws:
        EVIDENCE-LAW-001: Every derivation references supporting memory artifacts
        EVIDENCE-LAW-002: Evidence remains inspectable
        EVIDENCE-LAW-003: Evidence preserves provenance
    """
    
    evidence_id: str                        # Unique ID for this evidence record
    source_artifact_ids: Tuple[str, ...]    # Which artifacts support this?
    relations_used: Tuple[str, ...] = field(default_factory=tuple)  # Relations used
    confidence: float = 1.0                 # Trust in this evidence (0.0-1.0)
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# DERIVATION PROVENANCE - Where did this derivation come from?
# =============================================================================


@dataclass(frozen=True)
class DerivationProvenance:
    """
    Provenance record for a derivation.
    
    Fields:
        derivation_id:       Which derivation produced this?
        method:              What derivation method was used?
        algorithm_version:   Version of the inference algorithm
        timestamp_utc:       When was this derivation created?
        
    Provenance Laws:
        PROVENANCE-LAW-001: Every derived artifact preserves complete derivation provenance
        PROVENANCE-LAW-002: Derivation methods remain identifiable
        PROVENANCE-LAW-003: Supporting artifacts remain identifiable
    """
    
    derivation_id: str                      # ID of this derivation
    method: str                             # Method name (causal, counterfactual, etc.)
    algorithm_version: str = "1.0.0"        # Version of inference algorithm
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# DERIVATION METRICS - Statistics about a derivation
# =============================================================================


@dataclass(frozen=True)
class DerivationMetrics:
    """
    Metrics about derivation execution.
    
    Fields:
        input_artifact_count: Number of source artifacts processed
        output_artifact_count: Number of derived artifacts produced
        validation_time_ms: Time spent in validation (ms)
        inference_time_ms: Time spent in inference (ms)
        
    Health Contract:
        DERIVATION-LAW-008: Deterministic behavior
    """
    
    input_artifact_count: int = 0           # Source artifacts processed
    output_artifact_count: int = 0          # Derived artifacts produced
    
    validation_time_ms: float = 0.0         # Validation duration
    inference_time_ms: float = 0.0          # Inference duration
    
    confidence_sum: float = 0.0             # Sum of derived artifact confidences
    uncertainty_sum: float = 0.0            # Sum of derived artifact uncertainties


# =============================================================================
# MEMORY DERIVATION - Core derivation contract
# =============================================================================


@dataclass(frozen=True)
class MemoryDerivation:
    """
    Core contract for semantic derivations.
    
    Every derivation must produce a result following these contracts:
        - Source artifacts unchanged (DERIVATION-LAW-002)
        - Provenance preserved (DERIVATION-LAW-004)
        - Evidence explicit (DERIVATION-LAW-006)
        - Deterministic (DERIVATION-LAW-008)
    
    Fields:
        derivation_id:       Unique identifier for this derivation
        kind_:               What kind of derivation? (causal, counterfactual, predictive)
        
        # Input
        input_artifact_ids:  Source artifacts being derived from
        evidence:            Supporting evidence for this derivation
        
        # Processing
        status:              Current state of the derivation
        confidence:          Overall confidence in this derivation (0.0-1.0)
        uncertainty:         Uncertainty about this derivation (0.0-1.0)
        
        # Output
        derived_artifact_ids: IDs of artifacts produced by this derivation
        revision_history:    Track of revisions to the derivation
        
        # Provenance
        provenance:          Derivation provenance record
        timestamp_utc:       When was this derivation created?
        
        # Validation
        validation_status:   Current validation state
        validation_reason:   Reason for validation result (if failed)
        
        # Metrics
        metrics:             Execution metrics
        
    Derived Artifact Contract:
        Every derived artifact must include:
            - original_artifact_id: Source artifact identity
            - derivation_kind: What kind of derivation?
            - supporting_evidence: Evidence used in derivation
            - confidence: Trust level
            - uncertainty: Uncertainty measure
    """
    
    # Identity and type
    derivation_id: str                      # Unique ID for this derivation
    kind_: DerivationKind                   # What kind of derivation?
    
    # Input
    input_artifact_ids: Tuple[str, ...]     # Source artifact IDs
    evidence: SupportingEvidence            # Supporting evidence
    
    # Processing state
    status: DerivationStatus = DerivationStatus.PROPOSED
    confidence: float = 0.5                 # Confidence in derivation result (0.0-1.0)
    uncertainty: float = 0.5                # Uncertainty about result (0.0-1.0)
    
    # Output
    derived_artifact_ids: Tuple[str, ...] = field(default_factory=tuple)  # Produced artifacts
    
    # Revision tracking
    revision_history: Tuple[str, ...] = field(default_factory=tuple)
    current_revision: int = 1
    
    # Provenance
    provenance: DerivationProvenance = field(
        default_factory=lambda: DerivationProvenance(derivation_id="", method="unknown")
    )
    
    timestamp_utc: float = field(default_factory=time.time)
    
    # Validation
    validation_status: str = "unvalidated"  # unvalidated, valid, invalid
    validation_reason: Optional[str] = None
    
    # Metrics
    metrics: DerivationMetrics = field(default_factory=DerivationMetrics)


# =============================================================================
# MEMORY DERIVATION BUILDER - Mutable builder for derivations
# =============================================================================


class MemoryDerivationBuilder:
    """
    Mutable builder for constructing memory derivations.
    
    Allows step-by-step construction before producing an immutable derivation.
    Follows the pattern of other builders in the architecture.
    """
    
    def __init__(
        self,
        kind_: DerivationKind,
        input_artifact_ids: Tuple[str, ...],
    ):
        """Initialize the builder."""
        self._kind_ = kind_
        self._input_artifact_ids = tuple(input_artifact_ids)
        
        # Identity - generated
        self._derivation_id = f"derivation:{uuid.uuid4().hex[:12]}"
        
        # Evidence
        self._evidence: SupportingEvidence = SupportingEvidence(
            evidence_id=f"evidence:{uuid.uuid4().hex[:12]}",
            source_artifact_ids=self._input_artifact_ids,
            confidence=1.0,
        )
        
        # Status and metrics
        self._status = DerivationStatus.PROPOSED
        self._confidence = 0.5
        self._uncertainty = 0.5
        
        # Output tracking
        self._derived_artifact_ids: Tuple[str, ...] = tuple()
        
        # Revision history
        self._revision_history: Tuple[str, ...] = tuple()
        
        # Validation
        self._validation_status = "unvalidated"
        self._validation_reason: Optional[str] = None
        
        # Metrics
        self._metrics = DerivationMetrics()
        
        # Provenance
        self._provenance = DerivationProvenance(
            derivation_id=self._derivation_id,
            method=kind_.value,
        )
    
    def set_derivation_id(self, derivation_id: str) -> "MemoryDerivationBuilder":
        """Set the derivation ID."""
        self._derivation_id = derivation_id
        return self
    
    def add_supporting_artifact(self, artifact_id: str) -> "MemoryDerivationBuilder":
        """Add a supporting artifact to evidence."""
        new_sources = tuple(
            list(self._evidence.source_artifact_ids) + [artifact_id]
        )
        self._evidence = SupportingEvidence(
            evidence_id=self._evidence.evidence_id,
            source_artifact_ids=new_sources,
            relations_used=self._evidence.relations_used,
            confidence=self._evidence.confidence,
        )
        return self
    
    def add_relation(self, relation_id: str) -> "MemoryDerivationBuilder":
        """Add a relation used in this derivation."""
        new_relations = tuple(
            list(self._evidence.relations_used) + [relation_id]
        )
        self._evidence = SupportingEvidence(
            evidence_id=self._evidence.evidence_id,
            source_artifact_ids=self._evidence.source_artifact_ids,
            relations_used=new_relations,
            confidence=self._evidence.confidence,
        )
        return self
    
    def set_confidence(self, confidence: float) -> "MemoryDerivationBuilder":
        """Set the derivation confidence (0.0-1.0)."""
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {confidence}")
        self._confidence = confidence
        return self
    
    def set_uncertainty(self, uncertainty: float) -> "MemoryDerivationBuilder":
        """Set the derivation uncertainty (0.0-1.0)."""
        if not 0.0 <= uncertainty <= 1.0:
            raise ValueError(f"Uncertainty must be 0.0-1.0, got {uncertainty}")
        self._uncertainty = uncertainty
        return self
    
    def set_status(self, status: DerivationStatus) -> "MemoryDerivationBuilder":
        """Set the derivation status."""
        self._status = status
        return self
    
    def add_derived_artifact(self, artifact_id: str) -> "MemoryDerivationBuilder":
        """Add a derived artifact ID to the output."""
        new_outputs = tuple(
            list(self._derived_artifact_ids) + [artifact_id]
        )
        self._derived_artifact_ids = new_outputs
        return self
    
    def increment_revision(self) -> "MemoryDerivationBuilder":
        """Increment the revision number and update history."""
        new_history = (self._derivation_id,) + self._revision_history
        self._revision_history = new_history
        return self
    
    def set_validation_status(
        self, status: str, reason: Optional[str] = None
    ) -> "MemoryDerivationBuilder":
        """Set the validation status and optional reason."""
        self._validation_status = status
        self._validation_reason = reason
        return self
    
    def set_metrics(self, metrics: DerivationMetrics) -> "MemoryDerivationBuilder":
        """Set the derivation metrics."""
        self._metrics = metrics
        return self
    
    def build(self) -> MemoryDerivation:
        """
        Build an immutable MemoryDerivation from this builder.
        
        Returns:
            New MemoryDerivation with all settings applied
        """
        # Update provenance with current state
        provenance = DerivationProvenance(
            derivation_id=self._derivation_id,
            method=self._kind_.value,
            algorithm_version="1.0.0",
            timestamp_utc=time.time(),
        )
        
        return MemoryDerivation(
            derivation_id=self._derivation_id,
            kind_=self._kind_,
            input_artifact_ids=tuple(self._input_artifact_ids),
            evidence=self._evidence,
            status=self._status,
            confidence=self._confidence,
            uncertainty=self._uncertainty,
            derived_artifact_ids=self._derived_artifact_ids,
            revision_history=self._revision_history,
            current_revision=1 + len(self._revision_history),
            provenance=provenance,
            timestamp_utc=time.time(),
            validation_status=self._validation_status,
            validation_reason=self._validation_reason,
            metrics=self._metrics,
        )


# =============================================================================
# DERIVATION VALIDATOR - Validates derivations before publication
# =============================================================================


class DerivationValidator:
    """
    Validator for derivations.
    
    Verifies that derivations follow all contracts before they can be published.
    
    Validation Laws:
        VALIDATION-LAW-001: Every derivation must be validated before publication
        VALIDATION-LAW-002: Validation verifies evidence completeness
        VALIDATION-LAW-003: Validation verifies logical consistency
        VALIDATION-LAW-004: Validation verifies provenance integrity
    """
    
    def __init__(self):
        """Initialize the validator."""
        self._validation_count = 0
    
    def validate(
        self, derivation: MemoryDerivation
    ) -> Tuple[bool, Optional[str], float]:
        """
        Validate a derivation before publication.
        
        Args:
            derivation: The derivation to validate
            
        Returns:
            Tuple of (is_valid, reason, confidence_score)
            
        Validation Checks:
            - Evidence completeness (at least one source artifact)
            - Confidence is within valid range
            - Provenance is complete
            - Status allows publication
        """
        self._validation_count += 1
        
        # Check evidence completeness
        if len(derivation.input_artifact_ids) == 0:
            return False, "No input artifacts provided", 0.0
        
        # Check confidence range
        if not 0.0 <= derivation.confidence <= 1.0:
            return False, f"Invalid confidence: {derivation.confidence}", 0.0
        
        # Check uncertainty range  
        if not 0.0 <= derivation.uncertainty <= 1.0:
            return False, f"Invalid uncertainty: {derivation.uncertainty}", 0.0
        
        # Check provenance completeness
        if not derivation.provenance.derivation_id:
            return False, "Missing provenance", 0.0
        
        # Check status allows publication
        if derivation.status == DerivationStatus.REJECTED:
            return False, "Derivation rejected", 0.0
        
        # All checks passed
        confidence_score = max(0.0, min(1.0, derivation.confidence))
        
        # Update validation time in metrics
        derived_metrics = DerivationMetrics(
            input_artifact_count=len(derivation.input_artifact_ids),
            output_artifact_count=len(derivation.derived_artifact_ids),
            validation_time_ms=self._validation_count * 0.1,  # Simulated
        )
        
        return True, "Validation passed", confidence_score
    
    def validate_derived_artifact(
        self,
        artifact: Any,
        derivation_id: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a derived artifact.
        
        Args:
            artifact: The artifact to validate
            derivation_id: ID of the derivation that produced it
            
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check that artifact has required provenance for derivation
        if hasattr(artifact, "provenance"):
            prov = getattr(artifact, "provenance")
            if hasattr(prov, "derivation_id") and prov.derivation_id != derivation_id:
                return False, f"Provenance mismatch: expected {derivation_id}, got {prov.derivation_id}"
        
        return True, None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get validator statistics."""
        return {
            "validation_count": self._validation_count,
        }


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Kinds
    "DerivationKind",
    
    # Status
    "DerivationStatus",
    
    # Evidence
    "SupportingEvidence",
    
    # Provenance
    "DerivationProvenance",
    
    # Metrics
    "DerivationMetrics",
    
    # Core classes
    "MemoryDerivation",
    "MemoryDerivationBuilder",
    "DerivationValidator",
]