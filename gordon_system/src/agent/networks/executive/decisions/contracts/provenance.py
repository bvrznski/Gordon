# Gordon Executive Decision Provenance - Phase 4.4.10A
# ======================================================

"""
Decision Provenance and Lineage System.

This module defines the provenance tracking system for Executive Decisions.
Provenance records complete semantic lineage describing how a decision
originated, including its origin, reason, evidence, assumptions, dependencies,
and revision history.


PROVENANCE OVERVIEW
===================

    Observation
           |
           v
    Evidence
           |
           v
    Reasoning
           |
           v
    Recommendation
           |
           v
    Executive Decision
           |
           v
    Commitment

This graph is semantic. Not computational.

ARCHITECTURAL LAWS
==================

E-011: Every decision shall possess complete provenance.
E-012: Every decision shall possess immutable lineage.
E-038: Semantic artifacts shall never contain executable behavior.
"""

from dataclasses import dataclass, field
from typing import Tuple, Optional
from enum import Enum


# =============================================================================
# PROVENANCE SOURCES - Origin types for decisions
# =============================================================================

class ProvenanceSource(Enum):
    """
    Source categories for Executive Decisions.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    EXTERNAL_REQUEST = "external_request"
    """Decision initiated by external request."""
    
    INTERNAL_GENERATION = "internal_generation"
    """Decision generated internally by the system."""
    
    SYSTEM_RECOVERY = "system_recovery"
    """Decision generated during error recovery."""
    
    POLICY_DRIVEN = "policy_driven"
    """Decision required by policy constraints."""
    
    SECURITY_DRIVEN = "security_driven"
    """Decision required for security reasons."""
    
    LEARNING_DRIVEN = "learning_driven"
    """Decision driven by learning and adaptation."""


# =============================================================================
# PROVENANCE LINKS - Relationships between decisions
# =============================================================================

class ProvenanceLink(Enum):
    """
    Semantic relationships in decision provenance.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    PARENT = "parent"
    """This decision derives from a parent decision."""
    
    CHILD = "child"
    """This is a child of another decision."""
    
    DERIVED_FROM = "derived_from"
    """This decision is derived from another."""
    
    SUPPORTED_BY = "supported_by"
    """This decision is supported by another."""
    
    ALTERNATIVE_TO = "alternative_to"
    """This is an alternative to another decision."""
    
    REPLACEMENT_FOR = "replacement_for"
    """This replaces another decision."""


# =============================================================================
# DECISION PROVENANCE - Complete lineage record
# =============================================================================

@dataclass(frozen=True)
class DecisionProvenance:
    """
    Complete provenance record for an Executive Decision.
    
    Provenance records the complete semantic lineage describing how a
    decision originated, including its origin, reason, evidence,
    assumptions, dependencies, and revision history.
    
    Runtime-neutral: Yes
    Executable: No
    
    Key properties:
        - source: Originating subsystem or context
        - origin_id: ID of the originating event/request
        - supporting_evidence_ids: Evidence that supported this decision
        - made_assumptions: Assumptions accepted during formation
        - dependencies: Other decisions/contexts this depends on
        - author_id: Who authored this decision
        
    Example:
        >>> provenance = DecisionProvenance(
        ...     source=ProvenanceSource.EXTERNAL_REQUEST,
        ...     origin_id="request_abc123",
        ... )
    """
    
    source: ProvenanceSource = ProvenanceSource.INTERNAL_GENERATION
    """Originating subsystem or context."""
    
    origin_id: str = field(default="")
    """ID of the originating event or request."""
    
    supporting_evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of evidence that supported this decision."""
    
    made_assumptions: Tuple[str, ...] = field(default_factory=tuple)
    """Assumptions accepted during decision formation."""
    
    dependencies: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of decisions/contexts this depends on."""
    
    author_id: Optional[str] = None
    """ID of the subsystem that authored this decision."""
    
    @property
    def is_provenance(self) -> bool:
        """Return True for all provenance records."""
        return True
    
    def has_evidence(self, evidence_id: str) -> bool:
        """
        Check if a specific piece of evidence supports this decision.
        
        Runtime-neutral: Yes
        Executable: No
        """
        return evidence_id in self.supporting_evidence_ids
    
    @classmethod
    def from_origin(cls, source: ProvenanceSource, origin_id: str) -> "DecisionProvenance":
        """Create a provenance record with minimal information."""
        return cls(
            source=source,
            origin_id=origin_id,
        )


# =============================================================================
# DECISION LINEAGE - Relationships between decision instances
# =============================================================================

@dataclass(frozen=True)
class DecisionLineage:
    """
    Complete lineage of relationships for an Executive Decision.
    
    Lineage describes how decisions relate to each other: parent-child,
    derived-from, alternative-to, replacement-for, etc.
    
    Runtime-neutral: Yes
    Executable: No
    
    Invariants:
        - Acyclic (no circular dependencies)
        - Traceable (all relationships can be followed)
        - Serializable (can be stored without runtime state)
        - Deterministic (equal inputs produce equivalent lineage)
    """
    
    decision_id: str = field(default="")
    """The identity of the decision."""
    
    parent_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of parent decisions."""
    
    child_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of child decisions."""
    
    derived_from_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of decisions this was derived from."""
    
    supported_by_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of decisions that support this one."""
    
    alternative_to_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of decisions this is an alternative to."""
    
    replacement_for_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of decisions this replaces."""
    
    @property
    def is_lineage(self) -> bool:
        """Return True for all lineage records."""
        return True
    
    def has_parent(self, decision_id: str) -> bool:
        """
        Check if a decision is a parent.
        
        Runtime-neutral: Yes
        Executable: No
        """
        return decision_id in self.parent_ids
    
    @property
    def is_root(self) -> bool:
        """Check if this decision has no parents."""
        return len(self.parent_ids) == 0


# =============================================================================
# PROVENANCE TRACE - Complete audit trail
# =============================================================================

@dataclass(frozen=True)
class ProvenanceTrace:
    """
    Complete provenance trace from origin to current state.
    
    This records the complete history of how a decision came to be,
    including all supporting evidence, reasoning steps, and authority
    decisions.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    decision_id: str = field(default="")
    """The identity of the decision."""
    
    trace_path: Tuple[str, ...] = field(default_factory=tuple)
    """Ordered sequence of provenance events."""
    
    @property
    def is_provenance_trace(self) -> bool:
        """Return True for all provenance traces."""
        return True
    
    @property
    def length(self) -> int:
        """Return the number of steps in the trace."""
        return len(self.trace_path)
    
    @classmethod
    def initial(cls, decision_id: str) -> "ProvenanceTrace":
        """
        Create an initial provenance trace.
        
        Runtime-neutral: Yes
        Executable: No
        """
        return cls(decision_id=decision_id)


# =============================================================================
# PROVENANCE VALIDATION - Validation utilities
# =============================================================================

class ProvenanceValidation:
    """
    Static validation utilities for DecisionProvenance.
    
    Runtime-neutral: Yes
    Executable: No
    
    All methods are pure and deterministic.
    """
    
    @staticmethod
    def is_valid_source(source: ProvenanceSource) -> bool:
        """Validate that a provenance source is valid."""
        return isinstance(source, ProvenanceSource)
    
    @staticmethod
    def is_valid_link(link: ProvenanceLink) -> bool:
        """Validate that a provenance link is valid."""
        return isinstance(link, ProvenanceLink)


# No additional imports needed here
