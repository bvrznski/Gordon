# Admission Eligibility - Phase 5.3
# ==================================

"""
Admission Eligibility: Evaluates if an observation candidate is eligible for
Memory admission.

Eligibility does not decide:

* persistence
* retention  
* consolidation
* forgetting

Those remain Memory responsibilities. Integration merely evaluates eligibility.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time


# =============================================================================
# ADMISSION ELIGIBILITY STATUS
# =============================================================================


class AdmissionEligibilityStatus:
    """
    Status of admission eligibility evaluation.
    
    Every candidate shall have an explicit eligibility status that indicates
    whether it's suitable for Memory submission.
    """
    
    ELIGIBLE = "eligible"                   # Candidate is eligible for admission
    PARTIALLY_ELIGIBLE = "partially_eligible"  # Eligible with limitations
    INELIGIBLE_SOURCE_INVALID = "ineligible_source_invalid"  # Source invalid
    INELIGIBLE_PROVENANCE_INCOMPLETE = "ineligible_provenance_incomplete"  # Missing provenance
    INELIGIBLE_CONFIDENCE_LOW = "ineligible_confidence_low"  # Confidence below threshold
    INELIGIBLE_AUTHORIZATION_DENIED = "ineligible_authorization_denied"  # No permission


# =============================================================================
# ADMISSION ELIGIBILITY RESULT
# =============================================================================


@dataclass(frozen=True)
class AdmissionEligibilityResult:
    """
    Result of admission eligibility evaluation.
    
    Every candidate shall undergo eligibility evaluation before candidate
    packaging. Eligibility does not imply Memory acceptance.
    """
    
    # Identity and target
    result_identity: str                    # Unique ID for this evaluation
    
    candidate_reference: str                # Reference to the candidate being evaluated
    
    # Overall status (required)
    is_eligible: bool                       # Is candidate eligible?
    status: AdmissionEligibilityStatus      # Detailed status
    
    # Evaluation details
    source_validity_passed: bool = True     # Source projection is valid
    provenance_complete: bool = True        # Full provenance chain exists
    confidence_available: bool = True       # Confidence metric available
    uncertainty_available: bool = True      # Uncertainty metric available
    
    # Quality metrics (required)
    confidence: float = 1.0                 # Overall eligibility confidence
    uncertainty: float = 0.0                # Uncertainty about eligibility
    
    # Limitations and findings
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    findings: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    
    @classmethod
    def eligible(
        cls,
        result_identity: str,
        candidate_ref: str,
        confidence: float = 1.0,
    ) -> "AdmissionEligibilityResult":
        """Create an eligible evaluation."""
        return cls(
            result_identity=result_identity,
            candidate_reference=candidate_ref,
            is_eligible=True,
            status=AdmissionEligibilityStatus.ELIGIBLE,
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    @classmethod
    def partially_eligible(
        cls,
        result_identity: str,
        candidate_ref: str,
        limitations: Tuple[str, ...] = (),
        confidence: float = 0.75,
    ) -> "AdmissionEligibilityResult":
        """Create a partial eligibility evaluation."""
        return cls(
            result_identity=result_identity,
            candidate_reference=candidate_ref,
            is_eligible=True,
            status=AdmissionEligibilityStatus.PARTIALLY_ELIGIBLE,
            limitations=limitations,
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    @classmethod
    def ineligible(
        cls,
        result_identity: str,
        candidate_ref: str,
        reason: str,
        status: AdmissionEligibilityStatus,
        confidence: float = 0.0,
    ) -> "AdmissionEligibilityResult":
        """Create an ineligible evaluation."""
        return cls(
            result_identity=result_identity,
            candidate_reference=candidate_ref,
            is_eligible=False,
            status=status,
            limitations=(reason,),
            confidence=confidence,
            uncertainty=1.0 - confidence,
        )
    
    @classmethod
    def ineligible_source_invalid(
        cls,
        result_identity: str,
        candidate_ref: str,
    ) -> "AdmissionEligibilityResult":
        """Create an ineligible evaluation for invalid source."""
        return cls(
            result_identity=result_identity,
            candidate_reference=candidate_ref,
            is_eligible=False,
            status=AdmissionEligibilityStatus.INELIGIBLE_SOURCE_INVALID,
            limitations=("Source projection is invalid",),
            confidence=0.0,
            uncertainty=1.0,
        )
    
    @classmethod
    def ineligible_provenance_incomplete(
        cls,
        result_identity: str,
        candidate_ref: str,
    ) -> "AdmissionEligibilityResult":
        """Create an ineligible evaluation for incomplete provenance."""
        return cls(
            result_identity=result_identity,
            candidate_reference=candidate_ref,
            is_eligible=False,
            status=AdmissionEligibilityStatus.INELIGIBLE_PROVENANCE_INCOMPLETE,
            limitations=("Provenance chain is incomplete",),
            confidence=0.3,
            uncertainty=0.7,
        )
    
    @classmethod
    def ineligible_confidence_low(
        cls,
        result_identity: str,
        candidate_ref: str,
        threshold: float = 0.5,
    ) -> "AdmissionEligibilityResult":
        """Create an ineligible evaluation for low confidence."""
        return cls(
            result_identity=result_identity,
            candidate_reference=candidate_ref,
            is_eligible=False,
            status=AdmissionEligibilityStatus.INELIGIBLE_CONFIDENCE_LOW,
            limitations=(f"Confidence below threshold {threshold}",),
            confidence=0.0,
            uncertainty=1.0,
        )
    
    @classmethod
    def ineligible_authorization_denied(
        cls,
        result_identity: str,
        candidate_ref: str,
    ) -> "AdmissionEligibilityResult":
        """Create an ineligible evaluation for authorization failure."""
        return cls(
            result_identity=result_identity,
            candidate_reference=candidate_ref,
            is_eligible=False,
            status=AdmissionEligibilityStatus.INELIGIBLE_AUTHORIZATION_DENIED,
            limitations=("Authorization denied",),
            confidence=0.0,
            uncertainty=1.0,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "result_identity": self.result_identity,
            "candidate_reference": self.candidate_reference,
            "is_eligible": self.is_eligible,
            "status": self.status,
            "source_validity_passed": self.source_validity_passed,
            "provenance_complete": self.provenance_complete,
            "confidence_available": self.confidence_available,
            "uncertainty_available": self.uncertainty_available,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "limitations": list(self.limitations),
            "findings": list(self.findings),
        }


# =============================================================================
# ADMISSION ELIGIBILITY VALIDATOR
# =============================================================================


class AdmissionEligibilityValidator:
    """
    Validates admission eligibility for candidates.
    
    Evaluates whether a candidate meets all eligibility requirements before
    packaging it for Memory submission.
    """
    
    def __init__(
        self,
        minimum_confidence: float = 0.5,
    ):
        """
        Initialize the validator.
        
        Args:
            minimum_confidence: Minimum confidence threshold (0.0-1.0)
        """
        self._minimum_confidence = minimum_confidence
    
    @property
    def minimum_confidence(self) -> float:
        """Minimum confidence threshold."""
        return self._minimum_confidence
    
    def evaluate(
        self,
        candidate_identity: str,
        source_projection_valid: bool,
        provenance_data: Optional[Dict[str, Any]],
        confidence: float,
        authorization_context: Optional[Dict[str, Any]] = None,
    ) -> AdmissionEligibilityResult:
        """
        Evaluate a candidate's eligibility for admission.
        
        Args:
            candidate_identity: ID of the candidate being evaluated
            source_projection_valid: Is source projection valid?
            provenance_data: Provenance information (optional)
            confidence: Confidence in the observation (0.0-1.0)
            authorization_context: Authorization context (optional)
            
        Returns:
            Eligibility result for this candidate
        """
        result_id = f"eligibility:{hash(str(candidate_identity)) % 10000:04x}"
        
        # Track issues
        findings = []
        limitations = []
        
        # Rule 1: Source projection must be valid
        if not source_projection_valid:
            return AdmissionEligibilityResult(
                result_identity=result_id,
                candidate_reference=candidate_identity,
                is_eligible=False,
                status=AdmissionEligibilityStatus.INELIGIBLE_SOURCE_INVALID,
                confidence=0.0,
                uncertainty=1.0,
                findings=[{"rule": "source_validity", "passed": False}],
            )
        
        # Rule 2: Provenance must be available
        if provenance_data is None:
            limitations.append("provenance_missing")
        
        # Rule 3: Confidence must meet threshold
        if confidence < self._minimum_confidence:
            return AdmissionEligibilityResult(
                result_identity=result_id,
                candidate_reference=candidate_identity,
                is_eligible=False,
                status=AdmissionEligibilityStatus.INELIGIBLE_CONFIDENCE_LOW,
                limitations=(f"Confidence {confidence} below threshold {self._minimum_confidence}",),
                confidence=0.0,
                uncertainty=1.0,
            )
        
        # Rule 4: Authorization must allow submission
        if authorization_context is not None:
            if authorization_context.get("deny_admission"):
                return AdmissionEligibilityResult(
                    result_identity=result_id,
                    candidate_reference=candidate_identity,
                    is_eligible=False,
                    status=AdmissionEligibilityStatus.INELIGIBLE_AUTHORIZATION_DENIED,
                    limitations=("Authorization denied admission",),
                    confidence=0.0,
                    uncertainty=1.0,
                )
        
        # All rules passed
        return AdmissionEligibilityResult(
            result_identity=result_id,
            candidate_reference=candidate_identity,
            is_eligible=True,
            status=AdmissionEligibilityStatus.ELIGIBLE,
            source_validity_passed=True,
            provenance_complete=provenance_data is not None,
            confidence_available=True,
            uncertainty_available=True,
            confidence=confidence,
            uncertainty=1.0 - confidence,
            findings=[
                {"rule": "source_validity", "passed": True},
                {"rule": "confident_threshold", "passed": True, "value": confidence},
            ],
        )
    
    def evaluate_bundle(
        self,
        candidate_identity: str,
        evidence_bundle_data: Dict[str, Any],
        context_bundle_data: Dict[str, Any],
    ) -> Tuple[bool, List[str]]:
        """
        Evaluate evidence and context bundle completeness.
        
        Args:
            candidate_identity: ID of the candidate
            evidence_bundle_data: Evidence bundle data
            context_bundle_data: Context bundle data
            
        Returns:
            (is_complete, list_of_missing_items)
        """
        missing = []
        
        # Check evidence bundle has source observations
        if "source_observations" not in evidence_bundle_data:
            missing.append("source_observations")
        
        # Check context bundle has identity context
        if "identity_context" not in context_bundle_data:
            missing.append("identity_context")
        
        return len(missing) == 0, missing


__all__ = [
    "AdmissionEligibilityStatus",
    "AdmissionEligibilityResult",
    "AdmissionEligibilityValidator",
]