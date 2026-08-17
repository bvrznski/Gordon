# Gordon Phase 5.7.1-I: Consciousness Identities
# ===============================================================================

"""
Canonical identity types for the Consciousness capability.

This module defines immutable identity classes for:
    - Capability instance identification
    - Context identity and generation tracking
    - Source registration identifiers
    - Extension registration identifiers
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple


# =============================================================================
# CANONICAL CAPABILITY IDENTITY
# =============================================================================

@dataclass(frozen=True)
class ConsciousnessCapabilityId:
    """
    Unique identifier for the Consciousness capability instance.
    
    Each Consciousness capability instance has exactly one stable identity
    that persists across restarts and transitions. This identity is used
    to distinguish this capability from others in the system.
    
    Identity properties:
        - Immutable: Once assigned, never changes
        - Stable: Persists across capability restarts
        - Unique: No two instances share the same ID
        - Canonical: Single source of truth for capability identification
    
    Usage:
        - Transition commits must include this capability's identity
        - Extension registrations reference this identity
        - Query results include this identity for provenance tracking
    """
    
    value: str = field(default_factory=lambda: "consciousness-001")
    """Unique identifier value."""
    
    @classmethod
    def default(cls) -> "ConsciousnessCapabilityId":
        """Return the canonical default capability ID."""
        return cls(value="consciousness-001")
    
    @classmethod
    def from_value(cls, value: str) -> "ConsciousnessCapabilityId":
        """Create a ConsciousnessCapabilityId from an existing string value."""
        if not value:
            raise ValueError("Consciousness capability ID cannot be empty")
        return cls(value=value)
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# CONTEXT IDENTITIES
# =============================================================================

@dataclass(frozen=True)
class ContextId:
    """
    Unique identifier for a current context.
    
    A context represents the agent-relative current experiential state at
    a point in time. The context ID persists across generations of the
    same conceptual context (e.g., ongoing conversation, active task).
    
    Identity properties:
        - Immutable: Context ID never changes during its lifetime
        - Stable: Persists across generations of the same context
        - Unique: Each distinct context has a unique ID
    
    Usage:
        - All snapshots for the same logical context share the same context_id
        - Transitions reference the current context_id
        - Consumer queries can filter by context_id
    """
    
    value: str = field(default_factory=lambda: f"context-{_generate_uuid()}")
    """Unique identifier value."""
    
    @classmethod
    def initial(cls) -> "ContextId":
        """Return an initial context ID for first use."""
        return cls(value="context-initial-001")
    
    @classmethod
    def from_value(cls, value: str) -> "ContextId":
        """Create a ContextId from an existing string value."""
        if not value:
            raise ValueError("Context ID cannot be empty")
        return cls(value=value)
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ContextGeneration:
    """
    Generation number for context snapshots.
    
    Each committed transition creates a new generation of the current
    context. Generations are strictly monotonic, ensuring consumers
    can detect stale state and maintain consistency.
    
    Generation properties:
        - Immutable: Once assigned, never changes
        - Monotonic: Each new generation has generation_number > previous
        - Bounded: Limited to prevent unbounded growth
    
    Usage:
        - Snapshot comparison detects stale context
        - Transition requests include expected generation for validation
        - Consumer queries can filter by minimum acceptable generation
    """
    
    value: int = field(default=0)
    """Generation number (strictly monotonic)."""
    
    @classmethod
    def initial(cls) -> "ContextGeneration":
        """Return the initial generation (0)."""
        return cls(value=0)
    
    @classmethod
    def next(cls, previous: "ContextGeneration") -> "ContextGeneration":
        """Return the next generation after the given one."""
        return cls(value=previous.value + 1)
    
    def __int__(self) -> int:
        return self.value
    
    def __lt__(self, other: "ContextGeneration") -> bool:
        return self.value < other.value
    
    def __le__(self, other: "ContextGeneration") -> bool:
        return self.value <= other.value
    
    def __gt__(self, other: "ContextGeneration") -> bool:
        return self.value > other.value
    
    def __ge__(self, other: "ContextGeneration") -> bool:
        return self.value >= other.value


# =============================================================================
# SOURCE IDENTITIES
# =============================================================================

@dataclass(frozen=True)
class SourceId:
    """
    Unique identifier for a contribution source.
    
    Each contributing system (Workspace, Perception, Working Memory, etc.)
    has a stable identity that persists across registrations. Sources
    submit contributions for consideration by Consciousness.
    
    Identity properties:
        - Immutable: Source ID never changes during its lifetime
        - Stable: Persists across capability restarts
        - Unique: No two sources share the same ID
        - Canonical: Single source of truth for source identification
    
    Usage:
        - All contributions include their source_id
        - Projections reference their source_id
        - Queries can filter by source_id
    """
    
    value: str = field(default_factory=lambda: f"source-{_generate_uuid()}")
    """Unique identifier value."""
    
    @classmethod
    def from_value(cls, value: str) -> "SourceId":
        """Create a SourceId from an existing string value."""
        if not value:
            raise ValueError("Source ID cannot be empty")
        return cls(value=value)
    
    def __str__(self) -> str:
        return self.value


# =============================================================================
# EXTENSION IDENTITIES
# =============================================================================

@dataclass(frozen=True)
class ExtensionId:
    """
    Unique identifier for an extension registration.
    
    Extensions are Phase 5.7.2-5.7.8 subsystems that register with
    Consciousness to participate in the current context lifecycle.
    Each extension has a stable identity and versioned state.
    
    Identity properties:
        - Immutable: Extension ID never changes during its lifetime
        - Stable: Persists across capability restarts
        - Unique: No two extensions share the same ID
        - Canonical: Single source of truth for extension identification
    
    Usage:
        - Transitions reference extension snapshot references by extension_id
        - Dependency ordering uses extension identities
        - Queries can filter by extension_id
    """
    
    value: str = field(default_factory=lambda: f"extension-{_generate_uuid()}")
    """Unique identifier value."""
    
    @classmethod
    def from_value(cls, value: str) -> "ExtensionId":
        """Create an ExtensionId from an existing string value."""
        if not value:
            raise ValueError("Extension ID cannot be empty")
        return cls(value=value)
    
    def __str__(self) -> str:
        return self.value


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
    "ConsciousnessCapabilityId",
    "ContextId",
    "ContextGeneration",
    "SourceId",
    "ExtensionId",
)