# Knowledge Assertions - Descriptor Contract - Phase 6.4
# =========================================================

"""
Assertion Descriptor: Metadata providing information about assertions.

Descriptors provide metadata independently of proposition content, enabling
efficient querying and governance without parsing full assertions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# ASSERTION KINDS - Classification of assertion types
# =============================================================================


class AssertionKind(Enum):
    """Kinds of assertions based on semantic content."""
    
    FACTUAL = "factual"            # Describes facts about the world
    DEFINITIONAL = "definitional"  # Defines concepts and relationships
    OBSERVATIONAL = "observational"  # Reports observations
    CAUSAL = "causal"              # States cause-effect relationships
    TEMPORAL = "temporal"          # Describes temporal ordering
    SPATIAL = "spatial"            # Describes spatial relationships
    FUNCTIONAL = "functional"      # Describes functions and capabilities
    SOCIAL = "social"              # Social normative claims
    MATHEMATICAL = "mathematical"  # Mathematical truths
    NORMATIVE = "normative"        # Normative/ethical claims
    PROCEDURAL = "procedural"      # Procedure/instruction claims
    UNKNOWN = "unknown"            # Kind indeterminate


# =============================================================================
# ASSERTION LIFECYCLE STATES
# =============================================================================


class AssertionLifecycleState(Enum):
    """States of assertion lifecycle."""
    
    DRAFT = "draft"              # Newly created, awaiting validation
    VALIDATING = "validating"    # Currently being validated
    ACTIVE = "active"            # Valid and currently accepted
    SUPERSEDED = "superseded"    # Replaced by newer revision
    REVISED = "revised"          # Revised version exists
    ARCHIVED = "archived"        # No longer active but preserved
    INVALID = "invalid"          # Failed validation


# =============================================================================
# ASSERTION DESCRIPTOR - Metadata independent of proposition content
# =============================================================================


@dataclass(frozen=True)
class AssertionDescriptor:
    """
    Descriptor providing metadata for an assertion.
    
    Descriptors provide metadata independently of proposition content,
    enabling efficient querying and governance without parsing full assertions.
    
    Fields:
        assertion_identity:     Unique identifier for this assertion
        semantic_identity:      Immutable semantic identity (persists across revisions)
        assertion_kind:         The kind of assertion (FACTUAL, DEFINITIONAL, etc.)
        lifecycle_state:        Current lifecycle state (DRAFT, ACTIVE, etc.)
        compatibility_revision: Maximum compatible revision number
        publication_status:     Publication status
        provenance:             Origin tracking information
    
    CONTRACT REQUIREMENTS:
        ASSERTION-LAW-001: Every Assertion possesses one immutable Semantic Identity
        ASSERTION-LAW-002: Assertions represent semantic propositions only
        ASSERTION-LAW-003: Assertions remain independent from Beliefs
        ASSERTION-LAW-004: Assertions preserve provenance
        ASSERTION-LAW-005: Assertions preserve revision lineage
        ASSERTION-LAW-006: Assertions remain independently inspectable
        ASSERTION-LAW-007: Assertions remain deterministic
        ASSERTION-LAW-008: Published Assertions remain immutable
    """
    
    assertion_identity: str
    semantic_identity: str
    assertion_kind: AssertionKind = AssertionKind.UNKNOWN
    lifecycle_state: AssertionLifecycleState = AssertionLifecycleState.DRAFT
    compatibility_revision: int = 1
    publication_status: bool = False
    provenance: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        """Check if assertion is currently active."""
        return self.lifecycle_state == AssertionLifecycleState.ACTIVE

    @property
    def is_published(self) -> bool:
        """Check if assertion is published (immutable)."""
        return self.publication_status

    @property
    def is_draft(self) -> bool:
        """Check if assertion is in draft state."""
        return self.lifecycle_state == AssertionLifecycleState.DRAFT

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert descriptor to dictionary for serialization.
        
        Deterministic serialization ensures equivalent descriptors compare identically.
        PROPOSITION-LAW-008: Proposition serialization shall remain deterministic.
        """
        return {
            "assertion_identity": self.assertion_identity,
            "semantic_identity": self.semantic_identity,
            "assertion_kind": self.assertion_kind.value,
            "lifecycle_state": self.lifecycle_state.value,
            "compatibility_revision": self.compatibility_revision,
            "publication_status": self.publication_status,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssertionDescriptor:
        """
        Create descriptor from dictionary.
        
        PROPOSITION-LAW-008: Deterministic deserialization.
        """
        return cls(
            assertion_identity=data.get("assertion_identity", ""),
            semantic_identity=data.get("semantic_identity", ""),
            assertion_kind=AssertionKind(data.get("assertion_kind", "unknown")),
            lifecycle_state=AssertionLifecycleState(data.get("lifecycle_state", "draft")),
            compatibility_revision=int(data.get("compatibility_revision", 1)),
            publication_status=bool(data.get("publication_status", False)),
            provenance=dict(data.get("provenance", {})),
        )

    @classmethod
    def create(
        cls,
        assertion_id: str,
        semantic_id: str = "",
        kind: AssertionKind = AssertionKind.UNKNOWN,
    ) -> AssertionDescriptor:
        """
        Create a new descriptor.
        
        ASSERTION-LAW-004: Preserves provenance with creation timestamp.
        """
        return cls(
            assertion_identity=assertion_id,
            semantic_identity=semantic_id or assertion_id,
            assertion_kind=kind,
            lifecycle_state=AssertionLifecycleState.DRAFT,
            compatibility_revision=1,
            publication_status=False,
            provenance={"created_at_utc": time.time()},
        )

    def update_lifecycle(self, new_state: AssertionLifecycleState) -> AssertionDescriptor:
        """
        Update the lifecycle state.
        
        REVISION-LAW-001: Assertion revisions preserve Semantic Identity.
        REVISION-LAW-002: Historical revisions remain immutable.
        """
        return AssertionDescriptor(
            assertion_identity=self.assertion_identity,
            semantic_identity=self.semantic_identity,
            assertion_kind=self.assertion_kind,
            lifecycle_state=new_state,
            compatibility_revision=self.compatibility_revision,
            publication_status=self.publication_status,
            provenance={
                **self.provenance,
                "state_updated_at_utc": time.time(),
                "previous_state": self.lifecycle_state.value,
            },
        )

    def publish(self) -> AssertionDescriptor:
        """
        Publish the assertion (make immutable).
        
        ASSERTION-LAW-008: Published Assertions remain immutable.
        """
        return AssertionDescriptor(
            assertion_identity=self.assertion_identity,
            semantic_identity=self.semantic_identity,
            assertion_kind=self.assertion_kind,
            lifecycle_state=AssertionLifecycleState.ACTIVE,
            compatibility_revision=self.compatibility_revision,
            publication_status=True,
            provenance={
                **self.provenance,
                "published_at_utc": time.time(),
                "previous_state": self.lifecycle_state.value,
            },
        )

    def bump_compatibility(self) -> AssertionDescriptor:
        """
        Bump the compatibility revision number.
        
        PROPOSITION-LAW-006: Proposition revisions shall preserve lineage.
        """
        return AssertionDescriptor(
            assertion_identity=self.assertion_identity,
            semantic_identity=self.semantic_identity,
            assertion_kind=self.assertion_kind,
            lifecycle_state=self.lifecycle_state,
            compatibility_revision=self.compatibility_revision + 1,
            publication_status=self.publication_status,
            provenance={
                **self.provenance,
                "compatibility_bumped_at_utc": time.time(),
                "previous_compatibility_revision": self.compatibility_revision,
            },
        )