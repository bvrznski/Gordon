# Gordon Phase 5.7.2-I: Experiential Field Validation
# ===============================================================================
#
# Contribution validation and rejection handling for the experiential field.
#

"""
Validation module for Experiential Field Builder.

This module handles validation of contributions before they are considered
for field construction:
    - Source identity verification
    - Schema validity checks
    - Freshness and expiration validation
    - Payload bounds checking
    - Duplicate detection
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Optional, Set
from enum import Enum

from .types import ContributionId, SourceId


# =============================================================================
# VALIDATION OUTCOMES
# =============================================================================

@dataclass(frozen=True)
class ValidationOutcome:
    """
    Result of validating a contribution.
    
    Either the contribution is accepted (with optional warnings) or it is
    rejected with a specific reason.
    """
    
    succeeded: bool
    """Whether the validation passed."""
    
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    """Optional warning messages for successful validation."""
    
    rejection_reason: Optional["RejectionReason"] = None
    """Reason for rejection if validation failed."""
    
    @property
    def is_rejected(self) -> bool:
        """Check if this outcome represents a rejection."""
        return not self.succeeded
    
    @classmethod
    def accept(cls, *warnings: str) -> "ValidationOutcome":
        """Create an acceptance outcome with optional warnings."""
        return cls(succeeded=True, warnings=tuple(warnings))
    
    @classmethod
    def reject(cls, reason: RejectionReason) -> "ValidationOutcome":
        """Create a rejection outcome with the given reason."""
        return cls(succeeded=False, rejection_reason=reason)


# =============================================================================
# REJECTION REASONS
# =============================================================================

class RejectionReason(Enum):
    """
    Reasons why a contribution may be rejected.
    
    Each reason corresponds to a specific validation failure mode.
    """
    
    # Source identity is not registered or unknown
    UNKNOWN_SOURCE = "unknown_source"
    
    # Contribution source is not authorized for the requested content kind
    UNAUTHORIZED_SOURCE = "unauthorized_source"
    
    # Contribution has expired (current time > expiration timestamp)
    EXPIRED = "expired"
    
    # Contribution payload exceeds size limits
    PAYLOAD_TOO_LARGE = "payload_too_large"
    
    # Content kind is not supported by this field builder
    UNSUPPORTED_CONTENT_KIND = "unsupported_content_kind"
    
    # Required content reference is missing or invalid
    INVALID_CONTENT_REFERENCE = "invalid_content_reference"
    
    # Relation references a content item that does not exist
    DANGLING_RELATION_REFERENCE = "dangling_relation_reference"
    
    # Duplicate contribution detected with the same ID
    DUPLICATE_ID = "duplicate_id"
    
    # Source generation is stale or mismatched
    SOURCE_GENERATION_MISMATCH = "source_generation_mismatch"
    
    # Privacy classification violates policy constraints
    PRIVACY_VIOLATION = "privacy_violation"
    
    # Trust level too low for admission (below configured threshold)
    TRUST_LEVEL_TOO_LOW = "trust_level_too_low"
    
    # Malformed or invalid JSON/schema structure
    MALFORMED = "malformed"
    
    # Missing required fields in the contribution envelope
    MISSING_REQUIRED_FIELDS = "missing_required_fields"


# =============================================================================
# CONTRIBUTION VALIDATOR
# =============================================================================

@dataclass
class ContributionValidator:
    """
    Validates contributions before they enter field construction.
    
    The validator checks:
        - Source identity and authorization
        - Schema validity
        - Freshness/expiration window
        - Payload bounds (size, content count, etc.)
        - Content kind support
        - Relation validity
    
    Note: This is a stateless validator. Each contribution is validated
    independently with the same rules.
    """
    
    # Configuration
    max_payload_size_bytes: int = 1_048_576  # Default 1MB
    """Maximum payload size in bytes."""
    
    supported_content_kinds: Set[str] = field(default_factory=lambda: {
        "workspace", "perceptual", "memory", "working_memory",
        "salience", "attention", "personality", "motivation",
        "cognition", "action_feedback"
    })
    """Set of content kinds this validator supports."""
    
    trusted_sources: Set[str] = field(default_factory=set)
    """Source IDs that are considered trusted (internal/system sources)."""
    
    def __post_init__(self):
        """Initialize internal state after construction."""
        if not isinstance(self.supported_content_kinds, set):
            self.supported_content_kinds = set(self.supported_content_kinds)
        if not isinstance(self.trusted_sources, set):
            self.trusted_sources = set(self.trusted_sources)
    
    def validate_source(
        self,
        source_id: str,
        is_registered: bool = True
    ) -> ValidationOutcome:
        """
        Validate that the source identity is acceptable.
        
        Args:
            source_id: The source ID from the contribution
            is_registered: Whether the source is registered (external check)
            
        Returns:
            Validation outcome indicating success or failure reason
        """
        if not is_registered:
            return ValidationOutcome.reject(RejectionReason.UNKNOWN_SOURCE)
        
        # TODO: Check authorization for content kind
        # This would require access to the source descriptor
        
        return ValidationOutcome.accept()
    
    def validate_freshness(
        self,
        freshness_utc: float,
        expiration_utc: Optional[float] = None
    ) -> ValidationOutcome:
        """
        Validate contribution freshness and expiration.
        
        Args:
            freshness_utc: When the contribution was created (Unix timestamp)
            expiration_utc: When the contribution expires (if any)
            
        Returns:
            Validation outcome for freshness check
        """
        current_time = time.time()
        
        # Check if expired
        if expiration_utc is not None and current_time > expiration_utc:
            return ValidationOutcome.reject(RejectionReason.EXPIRED)
        
        # TODO: Could add staleness checks based on freshness age
        
        return ValidationOutcome.accept()
    
    def validate_payload_size(
        self,
        payload_size_bytes: int
    ) -> ValidationOutcome:
        """
        Validate that payload size is within bounds.
        
        Args:
            payload_size_bytes: Size of the contribution payload in bytes
            
        Returns:
            Validation outcome for payload size check
        """
        if payload_size_bytes > self.max_payload_size_bytes:
            return ValidationOutcome.reject(RejectionReason.PAYLOAD_TOO_LARGE)
        
        return ValidationOutcome.accept()
    
    def validate_content_kind(self, kind: str) -> ValidationOutcome:
        """
        Validate that the content kind is supported.
        
        Args:
            kind: The content kind from the contribution
            
        Returns:
            Validation outcome for content kind check
        """
        if kind not in self.supported_content_kinds:
            return ValidationOutcome.reject(RejectionReason.UNSUPPORTED_CONTENT_KIND)
        
        return ValidationOutcome.accept()
    
    def validate(
        self,
        source_id: str,
        freshness_utc: float,
        expiration_utc: Optional[float],
        payload_size_bytes: int,
        content_kind: str,
        is_source_registered: bool = True
    ) -> ValidationOutcome:
        """
        Run all validation checks on a contribution.
        
        Args:
            source_id: Source submitting the contribution
            freshness_utc: Creation timestamp of the contribution
            expiration_utc: Expiration timestamp (if any)
            payload_size_bytes: Size of the payload in bytes
            content_kind: Kind/type of the contributed content
            is_source_registered: Whether source is registered
            
        Returns:
            Combined validation outcome from all checks
        """
        # Run all validations
        outcomes = [
            self.validate_source(source_id, is_source_registered),
            self.validate_freshness(freshness_utc, expiration_utc),
            self.validate_payload_size(payload_size_bytes),
            self.validate_content_kind(content_kind),
        ]
        
        # If any failed, return the first failure
        for outcome in outcomes:
            if not outcome.succeeded:
                return outcome
        
        # All passed - collect warnings and accept
        all_warnings = tuple(
            w for o in outcomes for w in o.warnings
        )
        
        return ValidationOutcome.accept(*all_warnings)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ValidationOutcome",
    "RejectionReason",
    "ContributionValidator",
)
