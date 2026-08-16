# Executive State Metadata Types
# ==============================

"""
Metadata types for executive state privacy and provenance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any


# =============================================================================
# PRIVACY CLASSIFICATIONS
# =============================================================================


@dataclass(frozen=True)
class ExecutiveStatePrivacy:
    """
    Privacy classification for executive state.
    
    Defines who may access the state and under what conditions.
    """
    
    class Classification:
        INTERNAL = "internal"
        """Internal to the Executive Network only."""
        
        INTERNAL_RESTRICTED = "internal_restricted"
        """Internal but with additional access controls."""
        
        THREAD_SCOPED = "thread_scoped"
        """Available only within a specific execution thread."""
        
        TASK_SCOPED = "task_scoped"
        """Available only for a specific task context."""
        
        PARTICIPANT_SCOPED = "participant_scoped"
        """Available only to identified participants."""
        
        IDENTITY_SENSITIVE = "identity_sensitive"
        """Contains identity-sensitive information."""
        
        MEMORY_SENSITIVE = "memory_sensitive"
        """Contains memory-sensitive information."""
        
        SECURITY_SENSITIVE = "security_sensitive"
        """Contains security-sensitive information."""
        
        POLICY_SENSITIVE = "policy_sensitive"
        """Contains policy-sensitive information."""
        
        CONFIDENTIAL = "confidential"
        """Confidential - requires explicit authorization."""
        
        NON_DISCLOSABLE = "non_disclosable"
        """Must never be disclosed outside the Executive Network."""
        
        UNKNOWN = "unknown"
        """Privacy classification is unknown."""
    
    classification: str = Classification.INTERNAL
    """Privacy classification level."""
    
    access_rules: Tuple[str, ...] = field(default_factory=tuple)
    """Rules governing who may access this state."""
    
    disclosure_limitations: Tuple[str, ...] = field(default_factory=tuple)
    """Explicit limitations on disclosure."""
    
    @classmethod
    def internal(cls) -> ExecutiveStatePrivacy:
        """Create an internal-only classification."""
        return cls(classification=cls.Classification.INTERNAL)
    
    @classmethod
    def non_disclosable(cls) -> ExecutiveStatePrivacy:
        """Create a non-disclosable classification."""
        return cls(classification=cls.Classification.NON_DISCLOSABLE)


@dataclass(frozen=True)
class ExecutiveStateProvenance:
    """
    Provenance information for executive state.
    
    Tracks the origin and history of state elements.
    """
    
    created_by: str = "executive_network"
    """Who or what system created this state."""
    
    created_at_utc: float = 0.0
    """When the state was created (seconds since epoch)."""
    
    revision_history: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of prior revisions in lineage."""
    
    origin_transition: Optional[str] = None
    """Transition that produced this state (if applicable)."""
    
    source_provenance: Tuple[str, ...] = field(default_factory=tuple)
    """Provenance of source projections used to create this state."""
    
    @classmethod
    def initial(cls) -> ExecutiveStateProvenance:
        """Create provenance for an initial state."""
        return cls(created_by="executive_network")


@dataclass(frozen=True)
class ExecutiveContextPrivacy:
    """
    Privacy classification for executive context.
    
    Context is composed from external projections - this preserves their
    privacy classifications.
    """
    
    class Classification:
        INTERNAL = "internal"
        """Internal to the Executive Network."""
        
        THREAD_SCOPED = "thread_scoped"
        """Available only within a specific execution thread."""
        
        TASK_SCOPED = "task_scoped"
        """Available only for a specific task context."""
        
        PARTICIPANT_SCOPED = "participant_scoped"
        """Available only to identified participants."""
        
        CONFIDENTIAL = "confidential"
        """Confidential - requires explicit authorization."""
        
        UNKNOWN = "unknown"
        """Privacy classification is unknown."""
    
    classification: str = Classification.UNKNOWN
    """Privacy classification level."""
    
    most_restrictive_source_class: Optional[str] = None
    """The most restrictive source privacy class in this context."""
    
    access_rules: Tuple[str, ...] = field(default_factory=tuple)
    """Rules governing who may access this context."""
    
    @classmethod
    def internal(cls) -> ExecutiveContextPrivacy:
        """Create an internal-only classification."""
        return cls(classification=cls.Classification.INTERNAL)


@dataclass(frozen=True)
class ExecutiveContextProvenance:
    """
    Provenance information for executive context.
    
    Tracks the origin of each projection in the context.
    """
    
    assembled_by: str = "executive_context_assembler"
    """Who or what system assembled this context."""
    
    assembled_at_utc: float = 0.0
    """When the context was assembled (seconds since epoch)."""
    
    source_provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    """Provenance information for each source projection."""
    
    assembly_reason: Optional[str] = None
    """Reason for assembling this context (e.g., 'task_set_review')."""
    
    @classmethod
    def initial(cls) -> ExecutiveContextProvenance:
        """Create provenance for an initial context."""
        return cls(assembled_by="executive_context_assembler")


# =============================================================================
# EXPORTS
# =============================================================================

__all__: Tuple[str, ...] = (
    "ExecutiveStatePrivacy",
    "ExecutiveStateProvenance",
    "ExecutiveContextPrivacy",
    "ExecutiveContextProvenance",
)