# Gordon Phase 5.7.2-I: Experiential Field Types
# ===============================================================================
#
# Type definitions for the experiential field builder.
#

"""
Type and Class Definitions for Experiential Field Builder.

This module defines core types used throughout the experiential field:
    - ExperientialFieldId: Unique identifier for a field instance
    - ExperientialFieldGeneration: Monotonically increasing generation number
    - TransitionId: Unique identifier for transitions
    - ContentId: Unique identifier for content items within the field
    - ContributionId: Unique identifier for contribution submissions
    - RelationId: Unique identifier for relations between contents

All IDs are immutable and support equality comparison.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


def _generate_uuid() -> str:
    """Generate a short UUID-like identifier."""
    return uuid.uuid4().hex[:8]


# =============================================================================
# FIELD IDENTITIES
# =============================================================================

@dataclass(frozen=True)
class ExperientialFieldId:
    """
    Immutable unique identifier for an experiential field instance.
    
    The field ID persists across generations while the generation number
    increases with each transition. This allows tracking of a logical
    field's evolution over time.
    """
    
    value: str = field(default_factory=lambda: f"field-{_generate_uuid()}")
    """The string representation of this field ID."""
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_string(cls, s: str) -> "ExperientialFieldId":
        """Create a FieldId from a string representation."""
        return cls(value=s)


@dataclass(frozen=True)
class ExperientialFieldGeneration:
    """
    Immutable generation number for an experiential field.
    
    Generations are strictly monotonic - each transition produces
    a new generation exactly one higher than the previous.
    """
    
    value: int = 0
    """The numeric generation value."""
    
    def __str__(self) -> str:
        return f"gen-{self.value}"
    
    def next(self) -> "ExperientialFieldGeneration":
        """Return the next generation number."""
        return ExperientialFieldGeneration(value=self.value + 1)
    
    @classmethod
    def initial(cls) -> "ExperientialFieldGeneration":
        """Create an initial (zero) generation."""
        return cls(value=0)


@dataclass(frozen=True)
class TransitionId:
    """
    Unique identifier for a transition operation.
    
    Each field transition gets its own ID, allowing tracking of
    the exact sequence of state changes across generations.
    """
    
    value: str = field(default_factory=lambda: f"transition-{_generate_uuid()}")
    """The string representation of this transition ID."""
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_string(cls, s: str) -> "TransitionId":
        """Create a TransitionId from a string."""
        return cls(value=s)


# =============================================================================
# CONTENT IDENTITIES
# =============================================================================

@dataclass(frozen=True)
class ContentId:
    """
    Unique identifier for a content item within the field.
    
    Content IDs persist across generations when the same logical
    content appears in multiple snapshots, enabling provenance
    tracking across field evolution.
    """
    
    value: str = field(default_factory=lambda: f"content-{_generate_uuid()}")
    """The string representation of this content ID."""
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_string(cls, s: str) -> "ContentId":
        """Create a ContentId from a string."""
        return cls(value=s)


@dataclass(frozen=True)
class ContributionId:
    """
    Unique identifier for a contribution submission.
    
    Each contribution gets its own ID, allowing tracking of
    which proposals were submitted and how they were handled.
    """
    
    value: str = field(default_factory=lambda: f"contrib-{_generate_uuid()}")
    """The string representation of this contribution ID."""
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_string(cls, s: str) -> "ContributionId":
        """Create a ContributionId from a string."""
        return cls(value=s)


@dataclass(frozen=True)
class RelationId:
    """
    Unique identifier for a field relation.
    
    Relations between content items are tracked with their own IDs
    to support provenance and auditing of field structure evolution.
    """
    
    value: str = field(default_factory=lambda: f"relation-{_generate_uuid()}")
    """The string representation of this relation ID."""
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_string(cls, s: str) -> "RelationId":
        """Create a RelationId from a string."""
        return cls(value=s)


# =============================================================================
# SOURCE IDENTITIES
# =============================================================================

@dataclass(frozen=True)
class SourceId:
    """
    Unique identifier for a contribution source.
    
    Sources are external subsystems that submit contributions to the field.
    Each source has a stable identity across its lifetime.
    """
    
    value: str
    """The string representation of this source ID."""
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_string(cls, s: str) -> "SourceId":
        """Create a SourceId from a string."""
        return cls(value=s)


# =============================================================================
# CORRELATION IDENTITIES (for tracing)
# =============================================================================

@dataclass(frozen=True)
class CorrelationId:
    """
    Identifier for correlating related events across system boundaries.
    
    Used to trace the path of a logical request or event through
    multiple subsystems and transitions.
    """
    
    value: str = field(default_factory=lambda: f"corr-{_generate_uuid()}")
    """The string representation of this correlation ID."""
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_string(cls, s: str) -> "CorrelationId":
        """Create a CorrelationId from a string."""
        return cls(value=s)


@dataclass(frozen=True)
class CausationId:
    """
    Identifier for causation chains.
    
    Used to track cause-and-effect relationships between events,
    distinct from correlation which is about temporal association.
    """
    
    value: str = field(default_factory=lambda: f"caus-{_generate_uuid()}")
    """The string representation of this causation ID."""
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def from_string(cls, s: str) -> "CausationId":
        """Create a CausationId from a string."""
        return cls(value=s)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: tuple[str, ...] = (
    "ExperientialFieldId",
    "ExperientialFieldGeneration",
    "TransitionId",
    "ContentId",
    "ContributionId",
    "RelationId",
    "SourceId",
    "CorrelationId",
    "CausationId",
)