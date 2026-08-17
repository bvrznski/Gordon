# Knowledge Assertions - Assertion Dependency Contract - Phase 6.4
# =================================================================

"""
Assertion Dependencies: Explicit dependencies between assertions and other artifacts.

Dependencies remain explicit as required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# DEPENDENCY KINDS
# =============================================================================


class AssertionDependencyKind(Enum):
    """Kinds of assertion dependencies."""
    
    CONCEPT_DEPENDENCY = "concept_dependency"       # Depends on concept definitions
    ASSERTION_DEPENDENCY = "assertion_dependency"   # Depends on other assertions
    RELATION_DEPENDENCY = "relation_dependency"     # Depends on relations
    MODEL_DEPENDENCY = "model_dependency"           # Depends on model structure
    DEFINITION_DEPENDENCY = "definition_dependency" # Depends on definitions


# =============================================================================
# ASSERTION DEPENDENCY
# =============================================================================


@dataclass(frozen=True)
class AssertionDependency:
    """
    Dependency of one assertion on another artifact.
    
    Dependencies remain explicit and are tracked for reasoning purposes.
    
    Fields:
        dependency_identity:  Unique identifier for this dependency
        source_assertion:     The asserting that has the dependency
        target_artifact:      The artifact being depended upon
        dependency_kind:      Type of dependency
        justification:        Why this dependency exists
        provenance:           Origin tracking information
    
    CONTRACT REQUIREMENTS:
        ASSERTION-LAW-004: Provenance preserved
        ASSERTION-LAW-007: Deterministic behavior
    """
    
    dependency_identity: str
    source_assertion: str  # Assertion ID with the dependency
    target_artifact: str   # Artifact being depended upon (concept, assertion, etc.)
    dependency_kind: AssertionDependencyKind = AssertionDependencyKind.ASSERTION_DEPENDENCY
    justification: str = ""  # Reason for dependency
    provenance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for deterministic serialization."""
        return {
            "dependency_identity": self.dependency_identity,
            "source_assertion": self.source_assertion,
            "target_artifact": self.target_artifact,
            "dependency_kind": self.dependency_kind.value,
            "justification": self.justification,
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssertionDependency:
        """Create from dictionary (deterministic)."""
        return cls(
            dependency_identity=data.get("dependency_identity", ""),
            source_assertion=data.get("source_assertion", ""),
            target_artifact=data.get("target_artifact", ""),
            dependency_kind=AssertionDependencyKind(data.get("dependency_kind", "assertion_dependency")),
            justification=data.get("justification", ""),
            provenance=dict(data.get("provenance", {})),
        )

    @classmethod
    def concept_dependency(
        cls,
        assertion_id: str,
        concept_id: str,
        justification: str = "",
    ) -> AssertionDependency:
        """Create a concept dependency."""
        return cls(
            dependency_identity=f"dependency:{uuid.uuid4().hex[:16]}",
            source_assertion=assertion_id,
            target_artifact=concept_id,
            dependency_kind=AssertionDependencyKind.CONCEPT_DEPENDENCY,
            justification=justification or f"Depends on concept {concept_id}",
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def assertion_dependency(
        cls,
        source_id: str,
        target_id: str,
        justification: str = "",
    ) -> AssertionDependency:
        """Create an assertion dependency."""
        return cls(
            dependency_identity=f"dependency:{uuid.uuid4().hex[:16]}",
            source_assertion=source_id,
            target_artifact=target_id,
            dependency_kind=AssertionDependencyKind.ASSERTION_DEPENDENCY,
            justification=justification or f"Depends on assertion {target_id}",
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def relation_dependency(
        cls,
        assertion_id: str,
        relation_id: str,
        justification: str = "",
    ) -> AssertionDependency:
        """Create a relation dependency."""
        return cls(
            dependency_identity=f"dependency:{uuid.uuid4().hex[:16]}",
            source_assertion=assertion_id,
            target_artifact=relation_id,
            dependency_kind=AssertionDependencyKind.RELATION_DEPENDENCY,
            justification=justification or f"Depends on relation {relation_id}",
            provenance={"created_at_utc": time.time()},
        )

    @classmethod
    def definition_dependency(
        cls,
        assertion_id: str,
        definition_id: str,
        justification: str = "",
    ) -> AssertionDependency:
        """Create a definition dependency."""
        return cls(
            dependency_identity=f"dependency:{uuid.uuid4().hex[:16]}",
            source_assertion=assertion_id,
            target_artifact=definition_id,
            dependency_kind=AssertionDependencyKind.DEFINITION_DEPENDENCY,
            justification=justification or f"Depends on definition {definition_id}",
            provenance={"created_at_utc": time.time()},
        )

    def is_satisfied(self, available_artifacts: Tuple[str, ...]) -> bool:
        """Check if the dependency can be satisfied with available artifacts."""
        return self.target_artifact in available_artifacts