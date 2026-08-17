# Knowledge Artifact - Phase 6.1
# ===============================

"""
BaseKnowledgeArtifact: Universal semantic contract for all Gordon knowledge artifacts.

Every Knowledge artifact (Concept, Belief, Relation, Model, Hypothesis) shall derive
from this canonical base contract, inheriting:
    
    * Semantic Identity        - Unique identifier
    * Semantic Authority       - Source of ownership
    * Semantic Validity        - Truth and logical soundness
    * Semantic Scope           - Applicability boundaries
    * Semantic Provenance      - Origin and evolution history
    * Semantic Confidence      - Semantic certainty metrics
    * Semantic Uncertainty     - Semantic ambiguity metrics
    * Semantic Revision        - Version management
    * Semantic Compatibility   - Interaction with revisions
    * Semantic Certification   - Quality assurance state

This base contract enforces the Foundational Invariants:
    - Exactly one semantic identity
    - Exactly one current revision  
    - At least one provenance record
    - One authority
    - One validity state
    - One scope
    - Confidence value
    - Uncertainty value

Historical revisions remain immutable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# SEMANTIC LIFECYCLE STATES - Artifact maturity progression
# =============================================================================


class SemanticLifecycleState(Enum):
    """
    States of semantic artifact lifecycle progression.
    
    Defines the maturity states an artifact transitions through:
        CREATED     -> Initial creation (not yet validated)
        DRAFT       -> Work-in-progress state
        VALIDATING  -> Under validation review
        CERTIFIED   -> Passed validation, ready for publication
        ACTIVE      -> Published and in use
        REVISED     -> Has been superseded by newer revision
        SUPERSEDED  -> Replaced by another artifact
        DEPRECATED  -> Marked as outdated but still referenced
        ARCHIVED    -> Preserved for historical purposes
        INVALID     # Failed validation, not for use
    """
    
    CREATED = "created"
    DRAFT = "draft"
    VALIDATING = "validating"
    CERTIFIED = "certified"
    ACTIVE = "active"
    REVISED = "revised"
    SUPERSEDED = "superseded"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    INVALID = "invalid"


# =============================================================================
# SEMANTIC PUBLICATION STATUS - Availability states
# =============================================================================


class SemanticPublicationStatus(Enum):
    """
    Publication availability statuses.
    
    Defines the publication state of a semantic artifact:
        PRIVATE     -> Not available outside creator
        INTERNAL    -> Available within organization/system
        SHARED      -> Shared with selected external parties
        ACTIVE      -> Publicly available
        RESTRICTED  -> Available under specific conditions
        SUPERSEDED  -> Replaced by newer publication
    """
    
    PRIVATE = "private"
    INTERNAL = "internal"
    SHARED = "shared"
    ACTIVE = "active"
    RESTRICTED = "restricted"
    SUPERSEDED = "superseded"


# =============================================================================
# COMPATIBILITY KINDS - Revision interaction types
# =============================================================================


class SemanticCompatibilityKind(Enum):
    """
    Kinds of compatibility between revisions.
    
    Defines how two revisions may interact:
        FULLY_COMPATIBLE      -> Can be used interchangeably
        BACKWARD_COMPATIBLE   -> Newer works with older consumers
        FORWARD_COMPATIBLE    -> Older works with newer consumers
        PARTIALLY_COMPATIBLE  -> Some operations work, others don't
        MIGRATION_REQUIRED    -> Requires explicit migration process
        INCOMPATIBLE          -> Cannot interact without breaking
    """
    
    FULLY_COMPATIBLE = "fully_compatible"
    BACKWARD_COMPATIBLE = "backward_compatible"
    FORWARD_COMPATIBLE = "forward_compatible"
    PARTIALLY_COMPATIBLE = "partially_compatible"
    MIGRATION_REQUIRED = "migration_required"
    INCOMPATIBLE = "incompatible"


# =============================================================================
# CERTIFICATION LEVELS - Quality assurance grades
# =============================================================================


class SemanticCertificationLevel(Enum):
    """
    Levels of semantic certification quality.
    
    Defines the implementation quality grade:
        UNCERTIFIED   -> Not yet certified
        PARTIAL       -> Some checks passed
        CERTIFIED     -> Passed all required checks
        VERIFIED      -> Verified by independent assessment
        REFERENCE     -> Reference standard quality
    """
    
    UNCERTIFIED = "uncertified"
    PARTIAL = "partial"
    CERTIFIED = "certified"
    VERIFIED = "verified"
    REFERENCE = "reference"


# =============================================================================
# VALIDATION LEVELS - Check depth tiers
# =============================================================================


class SemanticValidationLevel(Enum):
    """
    Levels of validation depth.
    
    Defines how thorough the validation process is:
        BASIC       -> Syntax and structure only
        STRUCTURAL  -> Format and schema compliance
        SEMANTIC    -> Meaning and consistency checks
        ONTOLOGICAL -> Integration with ontology
        FULL        -> All possible checks performed
    """
    
    BASIC = "basic"
    STRUCTURAL = "structural"
    SEMANTIC = "semantic"
    ONTOLOGICAL = "ontological"
    FULL = "full"


# =============================================================================
# BASE KNOWLEDGE ARTIFACT - Canonical base contract
# =============================================================================


@dataclass(frozen=True)
class BaseKnowledgeArtifact:
    """
    Base class for all Gordon Knowledge artifacts.
    
    Every semantic artifact inherits this contract, which provides the
    foundational properties required throughout the artifact's lifecycle.
    
    This is the constitutional layer that ensures every Concept, Belief,
    Relation, Model, and Hypothesis shares identical guarantees for:
        - Identity: Unique, immutable reference
        - Authority: Explicit ownership tracking
        - Validity: Assessable truth state
        - Scope: Defined applicability boundaries
        - Provenance: Complete history preservation
        - Confidence/Uncertainty: Epistemic metrics
    
    The artifact evolves through revisions while preserving all foundational
    properties. Historical revisions remain immutable.
    
    Fields:
        semantic_identity:     Unique identifier for this artifact
        semantic_authority:    Source of ownership and responsibility
        semantic_validity:     Current validity assessment
        semantic_scope:        Applicability domain boundaries
        semantic_provenance:   Complete origin and evolution trail
        semantic_confidence:   Semantic certainty metrics
        semantic_uncertainty:  Semantic ambiguity metrics
        semantic_revision:     Current revision identifier
        semantic_compatibility: Revision compatibility state
        semantic_certification: Quality assurance status
        lifecycle_state:       Maturity progression state
    """
    
    # Core identity (required - immutable)
    semantic_identity: str                # Unique artifact identifier
    
    # Foundational properties (all required)
    semantic_authority: Dict[str, Any]    # Authority assessment data
    semantic_validity: Dict[str, Any]     # Validity state and evidence
    semantic_scope: Dict[str, Any]        # Applicability boundaries
    semantic_provenance: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)  # Provenance trail
    
    # Epistemic metrics (required - must follow same pattern)
    semantic_confidence: Dict[str, Any] = field(default_factory=dict)  # Confidence metrics
    semantic_uncertainty: Dict[str, Any] = field(default_factory=dict)  # Uncertainty metrics
    
    # Lifecycle tracking (required - with defaults for optional fields)
    semantic_revision: int = 1            # Current revision number
    semantic_compatibility: Dict[str, Any] = field(default_factory=dict)  # Compatibility data
    semantic_certification: Dict[str, Any] = field(default_factory=dict)  # Certification status
    
    lifecycle_state: SemanticLifecycleState = SemanticLifecycleState.CREATED
    
    # Timestamps
    created_at_utc: float = field(default_factory=time.time)
    updated_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_valid(self) -> bool:
        """Check if artifact has valid foundational data."""
        return (
            len(self.semantic_identity) > 0 and
            self.semantic_authority is not None and
            self.semantic_validity is not None and
            self.semantic_scope is not None and
            self.semantic_confidence is not None and
            self.semantic_uncertainty is not None
        )
    
    @property
    def has_provenance(self) -> bool:
        """Check if artifact has provenance records."""
        return len(self.semantic_provenance) > 0
    
    @classmethod
    def create_initial(
        cls,
        semantic_identity: str,
        semantic_authority: Dict[str, Any],
        semantic_validity: Dict[str, Any],
        semantic_scope: Dict[str, Any],
        semantic_confidence: Dict[str, Any],
        semantic_uncertainty: Dict[str, Any],
        provenance_context: Optional[Dict[str, Any]] = None,
    ) -> "BaseKnowledgeArtifact":
        """
        Create a new initial knowledge artifact.
        
        Args:
            semantic_identity: Unique identifier
            semantic_authority: Authority assessment data
            semantic_validity: Validity state and evidence
            semantic_scope: Applicability boundaries
            semantic_confidence: Confidence metrics
            semantic_uncertainty: Uncertainty metrics
            provenance_context: Initial provenance context (optional)
            
        Returns:
            New BaseKnowledgeArtifact in CREATED lifecycle state
        """
        initial_provenance = (
            {
                "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
                "originating_request": provenance_context.get("request", "") if provenance_context else "",
                "originating_system": provenance_context.get("system", "unknown") if provenance_context else "unknown",
                "originating_revision": 1,
                "evidence_references": [],
                "grounding_references": [],
                "revision_chain": [],
                "authority": semantic_authority.get("authority_identity", ""),
                "timestamp_utc": time.time(),
            },
        )
        
        return cls(
            semantic_identity=semantic_identity,
            semantic_authority=semantic_authority,
            semantic_validity=semantic_validity,
            semantic_scope=semantic_scope,
            semantic_provenance=initial_provenance,
            semantic_confidence=semantic_confidence,
            semantic_uncertainty=semantic_uncertainty,
            semantic_revision=1,
            lifecycle_state=SemanticLifecycleState.CREATED,
            created_at_utc=time.time(),
        )
    
    def with_revision(
        self,
        new_revision: int,
        change_summary: Optional[str] = None,
    ) -> "BaseKnowledgeArtifact":
        """
        Create a new revision of this artifact.
        
        Args:
            new_revision: The revision number
            change_summary: Brief description of changes (optional)
            
        Returns:
            New artifact instance with updated revision
        """
        # Preserve all provenance and update with new revision
        new_provenance = tuple(list(self.semantic_provenance) + [{
            "provenance_identity": f"provenance:{uuid.uuid4().hex[:16]}",
            "originating_request": f"Revision {new_revision}: {change_summary or 'unknown change'}",
            "originating_system": self.semantic_authority.get("originating_system", "system"),
            "originating_revision": new_revision,
            "evidence_references": [],
            "grounding_references": [],
            "revision_chain": [self.semantic_identity],
            "authority": self.semantic_authority.get("authority_identity", ""),
            "timestamp_utc": time.time(),
        }])
        
        return BaseKnowledgeArtifact(
            semantic_identity=self.semantic_identity,
            semantic_authority=self.semantic_authority,
            semantic_validity=self.semantic_validity,
            semantic_scope=self.semantic_scope,
            semantic_provenance=new_provenance,
            semantic_confidence=self.semantic_confidence,
            semantic_uncertainty=self.semantic_uncertainty,
            semantic_revision=new_revision,
            semantic_compatibility={
                "source_revision": self.semantic_revision,
                "target_revision": new_revision,
                "compatibility_kind": SemanticCompatibilityKind.BACKWARD_COMPATIBLE.value,
                "migration_requirements": change_summary or "",
                "limitations": [],
                "provenance_identity": f"compat:{uuid.uuid4().hex[:16]}",
            },
            semantic_certification=self.semantic_certification,
            lifecycle_state=SemanticLifecycleState.ACTIVE if self.lifecycle_state == SemanticLifecycleState.CREATED else self.lifecycle_state,
            created_at_utc=self.created_at_utc,
            updated_at_utc=time.time(),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert artifact to dictionary for serialization."""
        return {
            "semantic_identity": self.semantic_identity,
            "semantic_authority": self.semantic_authority,
            "semantic_validity": self.semantic_validity,
            "semantic_scope": self.semantic_scope,
            "semantic_provenance": [p for p in self.semantic_provenance],
            "semantic_confidence": self.semantic_confidence,
            "semantic_uncertainty": self.semantic_uncertainty,
            "semantic_revision": self.semantic_revision,
            "semantic_compatibility": self.semantic_compatibility,
            "semantic_certification": self.semantic_certification,
            "lifecycle_state": self.lifecycle_state.value,
            "created_at_utc": self.created_at_utc,
            "updated_at_utc": self.updated_at_utc,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseKnowledgeArtifact":
        """Create artifact from dictionary."""
        provenance = []
        for p_data in data.get("semantic_provenance", []):
            if isinstance(p_data, dict):
                provenance.append(p_data)
        
        return cls(
            semantic_identity=data.get("semantic_identity", str(uuid.uuid4())),
            semantic_authority=data.get("semantic_authority", {}),
            semantic_validity=data.get("semantic_validity", {}),
            semantic_scope=data.get("semantic_scope", {}),
            semantic_provenance=tuple(provenance),
            semantic_confidence=data.get("semantic_confidence", {}),
            semantic_uncertainty=data.get("semantic_uncertainty", {}),
            semantic_revision=int(data.get("semantic_revision", 1)),
            semantic_compatibility=data.get("semantic_compatibility", {}),
            semantic_certification=data.get("semantic_certification", {}),
            lifecycle_state=SemanticLifecycleState(data.get("lifecycle_state", "created")),
            created_at_utc=float(data.get("created_at_utc", time.time())),
            updated_at_utc=float(data.get("updated_at_utc", time.time())),
        )


__all__ = [
    # Lifecycle states
    "SemanticLifecycleState",
    # Publication statuses
    "SemanticPublicationStatus",
    # Compatibility kinds
    "SemanticCompatibilityKind",
    # Certification levels
    "SemanticCertificationLevel",
    # Validation levels
    "SemanticValidationLevel",
    # Base contract
    "BaseKnowledgeArtifact",
]