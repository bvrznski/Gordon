# Gordon Executive Decision Artifacts - Phase 4.4.10A
# ======================================================

"""
Executive Artifact Base Classes.

This module defines the foundational artifact types from which all
Executive semantic artifacts derive.


EXECUTIVE SEMANTIC OBJECT HIERARCHY
===================================

    SemanticObject
           |
           v
    ExecutiveSemanticObject
           |
           v
    ExecutiveArtifact
           |
     +-------+--------+
     |       |        |
     v       v        v
Decision Recommendation Commitment
     |
     v
DecisionRevision


ARTIFACT INHERITANCE RULES
==========================

1. Every artifact must have:
   - Immutable identity
   - Ownership reference
   - Authority constraints
   - Provenance tracking

2. Artifacts never contain runtime state.

3. All artifacts are serializable without execution context.


ARCHITECTURAL LAWS
==================

E-007: Identity survives revisions.
E-008: Revisions never overwrite history.
E-009: Authority shall never imply ownership.
E-010: Ownership shall never imply authority.
E-011: Every decision shall possess complete provenance.
E-012: Every decision shall possess immutable lineage.
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Tuple
from datetime import datetime, timezone


# =============================================================================
# SEMANTIC OBJECT BASE - Root of all semantic objects
# =============================================================================

@dataclass(frozen=True)
class SemanticObject:
    """
    Root semantic object type.
    
    This is the conceptual base for all semantic artifacts in Gordon.
    It provides no runtime behavior; it exists purely to establish
    type relationships.
    
    Runtime-neutral: Yes
    Executable: No
    """
    pass


# =============================================================================
# EXECUTIVE SEMANTIC OBJECT BASE - Executive domain root
# =============================================================================

@dataclass(frozen=True)
class ExecutiveSemanticObject(SemanticObject):
    """
    Base class for all Executive Network semantic objects.
    
    This is the canonical root for all Executive artifacts. All Executive
    semantic types derive from this.
    
    Runtime-neutral: Yes
    Executable: No
    """
    pass


# =============================================================================
# EXECUTIVE ARTIFACT - Core artifact base
# =============================================================================

@dataclass(frozen=True)
class ExecutiveArtifact(ExecutiveSemanticObject):
    """
    Base class for all Executive semantic artifacts.
    
    Every artifact shares these fundamental properties:
    
        IDENTITY
            A persistent identifier that survives revisions and context changes.
        
        OWNERSHIP
            The subsystem responsible for maintaining semantic correctness.
        
        AUTHORITY
            Constraints on who may create, modify, or terminate the artifact.
        
        PROVENANCE
            Complete lineage describing origin and evolution.
        
        SERIALIZABILITY
            Must be serializable without runtime state.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    artifact_id: str = field(default="")  # Set by subclasses
    
    @property
    def is_artifact(self) -> bool:
        """Return True for all artifacts."""
        return True


# =============================================================================
# DECISION ARTIFACT - Decision system root
# =============================================================================

@dataclass(frozen=True)
class DecisionArtifact(ExecutiveArtifact):
    """
    Base class for all Executive Decision artifacts.
    
    This is the canonical base for decisions, recommendations, commitments,
    and revisions.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # All decision artifacts reference their identity through a common interface
    
    @property
    def decision_id(self) -> str:
        """Return the decision identity this artifact belongs to."""
        return self.artifact_id
    
    @property
    def is_decision_artifact(self) -> bool:
        """Return True for all decision artifacts."""
        return True


# =============================================================================
# REFERENCE TYPES - Immutable references to artifacts
# =============================================================================

@dataclass(frozen=True)
class ArtifactReference:
    """
    Immutable reference to an Executive artifact.
    
    References are used instead of direct ownership to maintain loose coupling.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    artifact_id: str
    """The identity of the referenced artifact."""
    
    reference_type: str = "artifact"
    """Type classification for the reference."""
    
    @classmethod
    def for_artifact(cls, artifact_id: str) -> "ArtifactReference":
        """Create a reference to an artifact by its ID."""
        return cls(artifact_id=artifact_id)