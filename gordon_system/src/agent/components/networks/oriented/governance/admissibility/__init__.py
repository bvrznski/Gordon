# Oriented Network Admissibility Model - Phase 4.7.11
# ===================================================

"""
Admissibility Framework for Oriented Network Governance

This module establishes the admissibility models that determine whether an
orientation is semantically valid within the governance framework.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Deterministic operations
    - Repository-independent

ADMISSIBILITY TYPES:

    AdmissibleOrientation           - Orientation that passes all checks
    ConditionallyAdmissibleOrientation - Orientation with conditions
    RejectedOrientation             - Orientation that failed basic checks
    ForbiddenOrientation            - Orientation explicitly forbidden
    UndefinedOrientation            - Orientation without sufficient information

ADMISSIBILITY LAWS (ORIENTED-ADMISSIBILITY-LAW-XXX):

    ORIENTED-ADMISSIBILITY-LAW-001: Admissibility is semantic
    ORIENTED-ADMISSIBILITY-LAW-002: Admissibility never implies execution
    ORIENTED-ADMISSIBILITY-LAW-003: Admissibility remains deterministic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# BASE ADMISSIBILITY MODEL
# =============================================================================

@dataclass(frozen=True)
class OrientationAdmissibility:
    """
    Base class for orientation admissibility.
    
    INVARIANTS:
        OA-INV-001: Admissibility is immutable
        OA-INV-002: Admissibility never executes runtime logic
        OA-INV-003: Admissibility remains deterministically verifiable
    """
    
    orientation_id: str
    """Orientation identifier being assessed"""
    
    admissibility_id: str = ""
    """Unique admissibility assessment ID"""
    
    reason: Optional[str] = None
    """Reason for the admissibility determination"""
    
    @property
    def is_admissible(self) -> bool:
        """
        Check if orientation is admissible.
        
        Returns:
            True if admissible, False otherwise
        """
        return self._is_admissible_impl()
    
    @property
    def status(self) -> str:
        """
        Get the admissibility status string.
        
        Returns:
            Status string (admissible, conditionally_admissible, 
                          rejected, forbidden, undefined)
        """
        return self._status_impl()
    
    def _is_admissible_impl(self) -> bool:
        """Implementation of admissibility check."""
        raise NotImplementedError
    
    def _status_impl(self) -> str:
        """Implementation of status getter."""
        raise NotImplementedError


# =============================================================================
# ADMISSIBILITY TYPES
# =============================================================================

@dataclass(frozen=True)
class AdmissibleOrientation(OrientationAdmissibility):
    """
    Orientation that passes all admissibility checks.
    
    SEMANTIC ROLE:
        - Represents an orientation that is fully admissible
        - No conditions or restrictions apply
    
    INVARIANTS:
        AO-INV-001: Orientation is admissible without conditions
        AO-INV-002: Admissibility determination is immutable
    """
    
    def _is_admissible_impl(self) -> bool:
        return True
    
    def _status_impl(self) -> str:
        return "admissible"


@dataclass(frozen=True)
class ConditionallyAdmissibleOrientation(OrientationAdmissibility):
    """
    Orientation that passes admissibility checks with conditions.
    
    SEMANTIC ROLE:
        - Represents an orientation that is conditionally admissible
        - Conditions must be satisfied before execution
    
    INVARIANTS:
        CAO-INV-001: Orientation is admissible only when conditions are met
        CAO-INV-002: Conditions are explicitly documented
    """
    
    conditions: Tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be satisfied"""
    
    def _is_admissible_impl(self) -> bool:
        # Conditionally admissible is only fully admissible if all conditions are met
        return len(self.conditions) == 0
    
    def _status_impl(self) -> str:
        return "conditionally_admissible"
    
    @property
    def condition_count(self) -> int:
        """Get the number of conditions."""
        return len(self.conditions)


@dataclass(frozen=True)
class RejectedOrientation(OrientationAdmissibility):
    """
    Orientation that failed basic admissibility checks.
    
    SEMANTIC ROLE:
        - Represents an orientation that was rejected
        - May have minor issues that can be fixed
    
    INVARIANTS:
        RO-INV-001: Orientation failed admissibility checks
        RO-INV-002: Rejection reason is explicitly documented
    """
    
    rejection_reasons: Tuple[str, ...] = field(default_factory=tuple)
    """Reasons for rejection"""
    
    def _is_admissible_impl(self) -> bool:
        return False
    
    def _status_impl(self) -> str:
        return "rejected"


@dataclass(frozen=True)
class ForbiddenOrientation(OrientationAdmissibility):
    """
    Orientation that is explicitly forbidden.
    
    SEMANTIC ROLE:
        - Represents an orientation that violates governance rules
        - Cannot be made admissible through conditions
    
    INVARIANTS:
        FO-INV-001: Orientation is explicitly forbidden
        FO-INV-002: Forbidden status cannot be overridden
    """
    
    prohibition: Optional[str] = None
    """The specific prohibition that applies"""
    
    def _is_admissible_impl(self) -> bool:
        return False
    
    def _status_impl(self) -> str:
        return "forbidden"


@dataclass(frozen=True)
class UndefinedOrientation(OrientationAdmissibility):
    """
    Orientation without sufficient information for assessment.
    
    SEMANTIC ROLE:
        - Represents an orientation with insufficient information
        - Cannot be assessed until more details are available
    
    INVARIANTS:
        UO-INV-001: Orientation cannot be assessed due to missing information
        UO-INV-002: Assessment can be repeated when more information is available
    """
    
    missing_information: Tuple[str, ...] = field(default_factory=tuple)
    """Information that would allow assessment"""
    
    def _is_admissible_impl(self) -> bool:
        return False
    
    def _status_impl(self) -> str:
        return "undefined"
    
    @property
    def has_sufficient_info(self) -> bool:
        """Check if sufficient information is available."""
        return len(self.missing_information) == 0


# =============================================================================
# ADMISSIBILITY ASSESSMENT RESULT
# =============================================================================

@dataclass(frozen=True)
class AdmissibilityAssessment:
    """
    Result of an admissibility assessment.
    
    INVARIANTS:
        AA-INV-001: Assessment is immutable
        AA-INV-002: Assessment never executes runtime logic
    """
    
    orientation_id: str
    """Orientation identifier"""
    
    assessment_id: str = ""
    """Unique assessment ID"""
    
    result: OrientationAdmissibility = field(
        default_factory=lambda: UndefinedOrientation(orientation_id="")
    )
    """Admissibility determination"""
    
    @property
    def is_admissible(self) -> bool:
        """
        Check if orientation is admissible.
        
        Returns:
            True if admissible, False otherwise
        """
        return self.result.is_admissible
    
    @property
    def status(self) -> str:
        """
        Get the admissibility status string.
        
        Returns:
            Status string from result
        """
        return self.result.status


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base model
    "OrientationAdmissibility",
    
    # Admissibility types
    "AdmissibleOrientation",
    "ConditionallyAdmissibleOrientation",
    "RejectedOrientation",
    "ForbiddenOrientation",
    "UndefinedOrientation",
    
    # Assessment result
    "AdmissibilityAssessment",
]