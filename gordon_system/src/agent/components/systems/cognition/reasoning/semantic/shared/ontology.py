# Semantic Ontology Reasoning - Phase 7.10
# =========================================

"""
Canonical Ontology Reasoning contracts.

Ontology reasoning operates over:
    - Concept collections
    - Ontology selection
    - Hierarchy analysis
    - Relation discovery
    - Consistency validation
    - Publication
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Set
from enum import Enum, auto


class OntologyReasoningState(Enum):
    """Ontology reasoning lifecycle states."""
    
    CREATED = "created"
    CONCEPT_COLLECTION = "concept_collection"
    ONTOLOGY_SELECTION = "ontology_selection"
    HIERARCHY_ANALYSIS = "hierarchy_analysis"
    RELATION_DISCOVERY = "relation_discovery"
    CONSISTENCY_VALIDATION = "consistency_validation"
    PUBLICATION = "publication"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class OntologyReasoning:
    """
    Ontology reasoning result.
    
    A OntologyReasoning contains:
        - Reasoning identity
        - Participating ontology
        - Inferred relations
        - Diagnostics
        - Provenance tracking
    """
    
    # Identity
    reasoning_id: str                       # Unique reasoning identifier
    
    # Reasoning goal
    reasoning_goal: str                     # What was the reasoning goal?
    
    # Ontology scope
    ontology_uri: Optional[str] = None      # Which ontology was used?
    ontology_version: Optional[str] = None  # Version of the ontology
    
    # Participating concepts
    participating_concepts: Tuple[str, ...] = ()
    
    # Inferred relations
    inferred_relations: Tuple[OntologyRelation, ...] = ()
    
    # Diagnostics
    diagnostics: Tuple[DiagnosticsRecord, ...] = ()
    
    # State
    reasoning_state: OntologyReasoningState = OntologyReasoningState.CREATED
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    @property
    def concept_count(self) -> int:
        """Count of participating concepts."""
        return len(self.participating_concepts)
    
    @property
    def relation_count(self) -> int:
        """Count of inferred relations."""
        return len(self.inferred_relations)
    
    @property
    def is_completed(self) -> bool:
        """Check if reasoning completed."""
        return self.reasoning_state == OntologyReasoningState.COMPLETED
    
    @classmethod
    def create(
        cls,
        reasoning_goal: str,
        ontology_uri: Optional[str] = None,
        participating_concepts: Optional[List[str]] = None,
    ) -> OntologyReasoning:
        """Create a new ontology reasoning record."""
        return cls(
            reasoning_id=f"ontology_reasoning:{uuid.uuid4().hex[:16]}",
            reasoning_goal=reasoning_goal,
            ontology_uri=ontology_uri,
            participating_concepts=tuple(participating_concepts or []),
        )
    
    def with_ontology(self, ontology_uri: str, version: Optional[str] = None) -> OntologyReasoning:
        """Return a copy with ontology assigned."""
        return dataclass_replace(
            self,
            ontology_uri=ontology_uri,
            ontology_version=version,
            reasoning_state=OntologyReasoningState.ONTOLOGY_SELECTION,
        )
    
    def add_concepts(self, concepts: List[str]) -> OntologyReasoning:
        """Return a copy with additional concepts."""
        new_concepts = set(self.participating_concepts) | set(concepts)
        return dataclass_replace(
            self,
            participating_concepts=tuple(sorted(new_concepts)),
            reasoning_state=OntologyReasoningState.CONCEPT_COLLECTION,
        )
    
    def add_relations(self, relations: List[OntologyRelation]) -> OntologyReasoning:
        """Return a copy with inferred relations."""
        new_relations = set(self.inferred_relations) | set(relations)
        return dataclass_replace(
            self,
            inferred_relations=tuple(sorted(new_relations)),
            reasoning_state=OntologyReasoningState.RELATION_DISCOVERY,
        )
    
    def with_diagnostics(self, diagnostics: List[DiagnosticsRecord]) -> OntologyReasoning:
        """Return a copy with diagnostics records."""
        new_diagnostics = set(self.diagnostics) | set(diagnostics)
        return dataclass_replace(
            self,
            diagnostics=tuple(sorted(new_diagnostics)),
        )
    
    def complete(self) -> OntologyReasoning:
        """Mark reasoning as completed."""
        return dataclass_replace(
            self,
            reasoning_state=OntologyReasoningState.COMPLETED,
            completed_at_utc=time.time(),
        )


@dataclass(frozen=True)
class OntologyRelation:
    """
    Semantic relation inferred from ontology.
    
    Relations include:
        - is-a
        - part-of
        - instance-of
        - causes
        - requires
        - contradicts
        - equivalent-to
        - depends-on
        - compatible-with
    """
    
    relation_id: str                        # Unique identifier
    source_concept: str                     # Source concept URI/name
    target_concept: str                     # Target concept URI/name
    relation_type: str                      # e.g., "is-a", "part-of"
    confidence: float = 1.0                 # Confidence level [0, 1]
    
    @classmethod
    def create_is_a(cls, child: str, parent: str) -> OntologyRelation:
        """Create an is-a relation."""
        return cls(
            relation_id=f"relation:{uuid.uuid4().hex[:16]}",
            source_concept=child,
            target_concept=parent,
            relation_type="is-a",
        )
    
    @classmethod
    def create_part_of(cls, part: str, whole: str) -> OntologyRelation:
        """Create a part-of relation."""
        return cls(
            relation_id=f"relation:{uuid.uuid4().hex[:16]}",
            source_concept=part,
            target_concept=whole,
            relation_type="part-of",
        )
    
    @classmethod
    def create_instance_of(cls, instance: str, class_: str) -> OntologyRelation:
        """Create an instance-of relation."""
        return cls(
            relation_id=f"relation:{uuid.uuid4().hex[:16]}",
            source_concept=instance,
            target_concept=class_,
            relation_type="instance-of",
        )


@dataclass(frozen=True)
class DiagnosticsRecord:
    """
    Diagnostic record from ontology reasoning.
    
    Diagnostics include:
        - Inconsistency findings
        - Missing concepts
        - Ambiguity detection
        - Performance metrics
    """
    
    diagnostic_id: str                      # Unique identifier
    diagnostic_type: str                    # e.g., "inconsistency", "missing"
    message: str                            # Diagnostic message
    severity: str = "info"                  # info, warning, error
    
    @classmethod
    def info(cls, message: str) -> DiagnosticsRecord:
        """Create an info diagnostic."""
        return cls(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:16]}",
            diagnostic_type="info",
            message=message,
        )
    
    @classmethod
    def warning(cls, message: str) -> DiagnosticsRecord:
        """Create a warning diagnostic."""
        return cls(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:16]}",
            diagnostic_type="warning",
            message=message,
            severity="warning",
        )
    
    @classmethod
    def error(cls, message: str) -> DiagnosticsRecord:
        """Create an error diagnostic."""
        return cls(
            diagnostic_id=f"diag:{uuid.uuid4().hex[:16]}",
            diagnostic_type="error",
            message=message,
            severity="error",
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "OntologyReasoning",
    "OntologyRelation",
    "DiagnosticsRecord",
    "OntologyReasoningState",
]