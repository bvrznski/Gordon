# Gordon Phase 5.7.6-I: Perspective Engine - Self-Reference
# ===============================================================================
"""
Canonical self-reference representation for the Perspective Engine.

Self-reference establishes bounded references to the current agent, executing
context, or internal actor within the first-person perspective frame.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace as dataclass_replace
from typing import Tuple, Optional


def _generate_uuid() -> str:
    """Generate a short UUID-like identifier."""
    import uuid
    return uuid.uuid4().hex[:8]


# =============================================================================
# SELF-REFERENCE KINDS
# =============================================================================

SELF_REFERENCE_KIND_AGENT = "agent"
"""Reference to the executing agent."""

SELF_REFERENCE_KIND_EXECUTING_CONTEXT = "executing_context"
"""Reference to the current execution context."""

SELF_REFERENCE_KIND_INTERNAL_ACTOR = "internal_actor"
"""Reference to internal actor within the system."""

VALID_SELF_REFERENCE_KINDS: Tuple[str, ...] = (
    SELF_REFERENCE_KIND_AGENT,
    SELF_REFERENCE_KIND_EXECUTING_CONTEXT,
    SELF_REFERENCE_KIND_INTERNAL_ACTOR,
)


# =============================================================================
# SELF-REFERENCE DATA
# =============================================================================

@dataclass(frozen=True)
class SelfReference:
    """
    Immutable self-reference within the perspective frame.
    
    Self-references establish bounded references to:
        - The current agent (this system)
        - The executing context
        - Internal actors
    
    Self-reference properties:
        - Immutable: Once created, never modified
        - Bounded: Does not include identity, personality, or history
        - Explicit: Reference format is clear and machine-readable
        - Contextual: References are valid within the current perspective
    
    NOT included (owned by external systems):
        - Identity construction (who am I?)
        - Personal narrative (my story)
        - Historical memory (past events)
        - Affective state (feelings about self)
    """
    
    # Identity
    self_ref_id: str = field(default_factory=lambda: f"self-{_generate_uuid()}")
    """Unique identifier for this self-reference."""
    
    kind: str = SELF_REFERENCE_KIND_AGENT
    """Type of self-reference."""
    
    agent_id: Optional[str] = None
    """Agent ID (if applicable)."""
    
    # Context
    perspective_frame_ref: Optional[str] = None
    """Reference to the perspective frame containing this reference."""
    
    context_generation: int = 0
    """Context generation when this reference was created."""
    
    timestamp_utc: float = field(default_factory=lambda: 0.0)
    """When this reference was created."""
    
    provenance: Optional[str] = None
    """Source that established this self-reference (if any)."""
    
    trust_level: str = "medium"
    """Trust level for self-references in this context."""
    
    privacy_level: str = "internal"
    """Privacy classification of this reference."""
    
    @classmethod
    def initial(cls) -> "SelfReference":
        """
        Create an initial self-reference.
        
        This creates a canonical self-reference at system start.
        """
        import time
        return cls(
            kind=SELF_REFERENCE_KIND_AGENT,
            perspective_frame_ref="frame-initial-001",
            context_generation=0,
            timestamp_utc=time.time(),
            trust_level="medium",
            privacy_level="internal",
        )
    
    @classmethod
    def from_context(cls, agent_id: str) -> "SelfReference":
        """
        Create a self-reference from an existing context.
        
        Args:
            agent_id: ID of the current agent
        """
        import time
        return cls(
            kind=SELF_REFERENCE_KIND_AGENT,
            agent_id=agent_id,
            perspective_frame_ref=f"frame-{_generate_uuid()}",
            context_generation=1,
            timestamp_utc=time.time(),
            trust_level="medium",
            privacy_level="internal",
        )
    
    @classmethod
    def as_executing_context(
        cls,
        context_id: str,
        generation: int = 0,
    ) -> "SelfReference":
        """
        Create a self-reference as the executing context.
        
        Args:
            context_id: ID of the execution context
            generation: Context generation
        """
        import time
        return cls(
            kind=SELF_REFERENCE_KIND_EXECUTING_CONTEXT,
            agent_id=context_id,
            perspective_frame_ref=f"frame-{_generate_uuid()}",
            context_generation=generation,
            timestamp_utc=time.time(),
            trust_level="high",
            privacy_level="internal",
        )
    
    @property
    def is_agent_reference(self) -> bool:
        """Check if this references the agent."""
        return self.kind == SELF_REFERENCE_KIND_AGENT
    
    @property
    def is_context_reference(self) -> bool:
        """Check if this references the executing context."""
        return self.kind == SELF_REFERENCE_KIND_EXECUTING_CONTEXT
    
    @property
    def is_actor_reference(self) -> bool:
        """Check if this references an internal actor."""
        return self.kind == SELF_REFERENCE_KIND_INTERNAL_ACTOR
    
    def to_identifier(self) -> str:
        """
        Get a string identifier for this self-reference.
        
        This provides a canonical string representation for use in
        conscious content organization.
        """
        parts = [self.kind]
        if self.agent_id:
            parts.append(self.agent_id)
        return ":".join(parts)


# =============================================================================
# SELF-REFERENCE VALIDATOR
# =============================================================================

@dataclass
class SelfReferenceValidator:
    """
    Validator for self-references.
    
    Ensures self-references are properly bounded and don't overstep into
    identity, personality, or memory territory.
    """
    
    max_self_ref_length: int = 64
    """Maximum length for self-reference identifiers."""
    
    require_context_generation: bool = True
    """Whether to require context generation in references."""
    
    def validate(self, self_ref: SelfReference) -> Tuple[bool, Optional[str]]:
        """
        Validate a self-reference.
        
        Args:
            self_ref: Self-reference to validate
            
        Returns:
            Tuple of (success, error_message if failed)
        """
        # Check kind
        if self_ref.kind not in VALID_SELF_REFERENCE_KINDS:
            return False, f"Invalid self-reference kind: {self_ref.kind}"
        
        # Check identifier length
        identifier = self_ref.to_identifier()
        if len(identifier) > self.max_self_ref_length:
            return False, f"Self-reference too long ({len(identifier)} > {self.max_self_ref_length})"
        
        # Check context generation if required
        if self.require_context_generation and self_ref.context_generation < 0:
            return False, "Context generation cannot be negative"
        
        # All checks passed
        return True, None
    
    @classmethod
    def default(cls) -> "SelfReferenceValidator":
        """Return a validator with default settings."""
        return cls()
    
    @classmethod
    def strict(cls) -> "SelfReferenceValidator":
        """Return a strict validator for production use."""
        return cls(max_self_ref_length=48, require_context_generation=True)


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    # Kinds
    "SELF_REFERENCE_KIND_AGENT",
    "SELF_REFERENCE_KIND_EXECUTING_CONTEXT",
    "SELF_REFERENCE_KIND_INTERNAL_ACTOR",
    "VALID_SELF_REFERENCE_KINDS",
    # Classes
    "SelfReference",
    "SelfReferenceValidator",
)