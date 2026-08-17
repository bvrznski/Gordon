# Gordon Phase 5.7.1-I: Consciousness Types
# ===============================================================================

"""
Canonical type definitions for the Consciousness capability.

This module defines immutable, hashable types for:
    - Contribution and Projection identifiers
    - Transition identifiers
    - Correlation and causation chains
    - Privacy and trust classifications
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any, Optional


# =============================================================================
# IDENTIFIER TYPES (frozen for determinism)
# =============================================================================

@dataclass(frozen=True)
class ContributionId:
    """
    Unique identifier for a contribution.
    
    Contributions are proposals submitted to Consciousness for consideration.
    Each contribution has a unique ID that persists across retries and
    resubmissions of the same proposal content.
    """
    
    value: str = field(default_factory=lambda: f"contrib-{_generate_uuid()}")
    """Unique identifier value."""
    
    @classmethod
    def from_value(cls, value: str) -> "ContributionId":
        """Create a ContributionId from an existing string value."""
        return cls(value=value)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ProjectionId:
    """
    Unique identifier for a projection.
    
    Projections expose bounded views from canonical external owners.
    Each projection has a unique ID that identifies its source and version.
    """
    
    value: str = field(default_factory=lambda: f"proj-{_generate_uuid()}")
    """Unique identifier value."""
    
    @classmethod
    def from_value(cls, value: str) -> "ProjectionId":
        """Create a ProjectionId from an existing string value."""
        return cls(value=value)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class TransitionId:
    """
    Unique identifier for a context transition.
    
    Transitions represent atomic commits of new current-context generations.
    Each transition has a unique ID that can be used to track and correlate
    transition operations across the system.
    """
    
    value: str = field(default_factory=lambda: f"transition-{_generate_uuid()}")
    """Unique identifier value."""
    
    @classmethod
    def from_value(cls, value: str) -> "TransitionId":
        """Create a TransitionId from an existing string value."""
        return cls(value=value)
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# CORRELATION TYPES (for tracing and debugging)
# =============================================================================

@dataclass(frozen=True)
class CorrelationId:
    """
    Identifier for grouping related operations.
    
    Correlation IDs trace the flow of work across subsystems,
    enabling debugging and observability across process boundaries.
    """
    
    value: str = field(default_factory=lambda: f"corr-{_generate_uuid()}")
    """Unique identifier value."""
    
    @classmethod
    def from_value(cls, value: str) -> "CorrelationId":
        """Create a CorrelationId from an existing string value."""
        return cls(value=value)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CausationId:
    """
    Identifier for causal relationships.
    
    Causation IDs track the chain of cause-and-effect across subsystems,
    enabling reconstruction of decision histories and failure root causes.
    """
    
    value: str = field(default_factory=lambda: f"caus-{_generate_uuid()}")
    """Unique identifier value."""
    
    @classmethod
    def from_value(cls, value: str) -> "CausationId":
        """Create a CausationId from an existing string value."""
        return cls(value=value)
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# PRIVACY CLASSIFICATION
# =============================================================================

class PrivacyClassification:
    """
    Canonical privacy classification for context elements.
    
    Privacy classifications determine how data is handled, stored,
    and exposed to consumers. Higher classifications require more
    restrictive handling.
    """
    
    # Classification levels (increasing sensitivity)
    PUBLIC = "public"
    """Public information with no privacy restrictions."""
    
    INTERNAL = "internal"
    """Internal use only, not for external disclosure."""
    
    CONFIDENTIAL = "confidential"
    """Confidential information requiring access controls."""
    
    RESTRICTED = "restricted"
    """Restricted information with strict access controls."""
    
    SECRET = "secret"
    """Secret information requiring highest protection."""
    
    # Valid classifications in order
    VALID_CLASSIFICATIONS: Tuple[str, ...] = (
        PUBLIC,
        INTERNAL,
        CONFIDENTIAL,
        RESTRICTED,
        SECRET,
    )
    
    @classmethod
    def is_valid(cls, classification: str) -> bool:
        """Check if a classification string is valid."""
        return classification in cls.VALID_CLASSIFICATIONS
    
    @classmethod
    def validate(cls, classification: str) -> str:
        """Validate and normalize a classification string."""
        if not cls.is_valid(classification):
            raise ValueError(
                f"Invalid privacy classification: {classification}. "
                f"Valid values: {cls.VALID_CLASSIFICATIONS}"
            )
        return classification
    
    @classmethod
    def requires_protection(cls, classification: str) -> bool:
        """Check if a classification requires protection."""
        return classification in (cls.CONFIDENTIAL, cls.RESTRICTED, cls.SECRET)
    
    @classmethod
    def is_public(cls, classification: str) -> bool:
        """Check if a classification is public."""
        return classification == cls.PUBLIC


# =============================================================================
# TRUST CLASSIFICATION
# =============================================================================

class TrustClassification:
    """
    Canonical trust classification for context elements.
    
    Trust classifications determine how data is evaluated and weighted.
    Higher trust levels may receive preferential treatment in reasoning,
    but never imply truth or validity.
    """
    
    # Classification levels (increasing trust)
    UNTRUSTED = "untrusted"
    """Untrusted source, verify all claims."""
    
    LOW = "low"
    """Low confidence source, treat with skepticism."""
    
    MEDIUM = "medium"
    """Medium confidence source, reasonable evaluation."""
    
    HIGH = "high"
    """High confidence source, weighted heavily in reasoning."""
    
    VERIFIED = "verified"
    """Verified source, maximum trust within bounds."""
    
    # Valid classifications in order
    VALID_CLASSIFICATIONS: Tuple[str, ...] = (
        UNTRUSTED,
        LOW,
        MEDIUM,
        HIGH,
        VERIFIED,
    )
    
    @classmethod
    def is_valid(cls, classification: str) -> bool:
        """Check if a classification string is valid."""
        return classification in cls.VALID_CLASSIFICATIONS
    
    @classmethod
    def validate(cls, classification: str) -> str:
        """Validate and normalize a classification string."""
        if not cls.is_valid(classification):
            raise ValueError(
                f"Invalid trust classification: {classification}. "
                f"Valid values: {cls.VALID_CLASSIFICATIONS}"
            )
        return classification
    
    @classmethod
    def can_be_used(cls, classification: str) -> bool:
        """Check if a classification can be used in reasoning."""
        # Untrusted content may still be used but with reduced confidence
        return True


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _generate_uuid() -> str:
    """Generate a short UUID-like identifier."""
    import uuid
    # Generate a random UUID and take first 8 chars for compactness
    return uuid.uuid4().hex[:8]


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ContributionId",
    "ProjectionId",
    "TransitionId",
    "CorrelationId",
    "CausationId",
    "PrivacyClassification",
    "TrustClassification",
)