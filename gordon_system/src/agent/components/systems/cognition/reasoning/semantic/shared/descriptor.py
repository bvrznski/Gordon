# Semantic Reasoning Descriptor - Phase 7.10
# =============================================

"""
Canonical Semantic Reasoning Descriptor.

A descriptor exposes semantic reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class SemanticMode(Enum):
    """Semantic reasoning modes."""
    
    CONCEPTUAL_ANALYSIS = "conceptual_analysis"       # Analyze concept structure
    ONTOLOGY_REASONING = "ontology_reasoning"         # Ontology-based reasoning
    RELATION_DISCOVERY = "relation_discovery"         # Discover semantic relations
    HIERARCHY_REASONING = "hierarchy_reasoning"       # Inheritance and hierarchy
    COMPOSITION_ANALYSIS = "composition_analysis"     # Concept composition
    EQUIVALENCE_ANALYSIS = "equivalence_analysis"     # Semantic equivalence
    VALIDATION = "validation"                         # Consistency validation
    GOVERNANCE = "governance"                         # Governance evaluation


class SemanticState(Enum):
    """Semantic reasoning session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    CONCEPT_EXTRACTION = "concept_extraction"
    ONTOLOGY_RESOLUTION = "ontology_resolution"
    RELATION_ANALYSIS = "relation_analysis"
    HIERARCHY_REASONING = "hierarchy_reasoning"
    COMPOSITION_ANALYSIS = "composition_analysis"
    EQUIVALENCE_ANALYSIS = "equivalence_analysis"
    VALIDATION = "validation"
    GOVERNANCE = "governance"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class SemanticDescriptor:
    """
    Descriptor exposing semantic reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Reasoning goal
        - Semantic mode
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what semantic reasoning occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                      # Unique descriptor identifier
    semantic_identity: str                  # Semantic identity (stable across runs)
    
    # Reasoning goal
    reasoning_goal: str                     # What are we reasoning about?
    
    # Semantic mode
    semantic_mode: SemanticMode = SemanticMode.CONCEPTUAL_ANALYSIS
    
    # Lifecycle state
    lifecycle_state: SemanticState = SemanticState.CREATED
    
    # Compatibility
    compatibility_revision: int = 1         # For schema evolution tracking
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did reasoning originate?
    
    @property
    def duration_seconds(self) -> float:
        """Calculate duration if completed."""
        if self.started_at_utc and self.completed_at_utc:
            return self.completed_at_utc - self.started_at_utc
        if self.started_at_utc:
            return time.time() - self.started_at_utc
        return 0.0
    
    @property
    def is_completed(self) -> bool:
        """Check if reasoning completed."""
        return self.lifecycle_state == SemanticState.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if reasoning failed."""
        return self.lifecycle_state == SemanticState.FAILED
    
    @property
    def is_archived(self) -> bool:
        """Check if reasoning is archived."""
        return self.lifecycle_state == SemanticState.ARCHIVED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_goal: str,
        semantic_mode: SemanticMode = SemanticMode.CONCEPTUAL_ANALYSIS,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
    ) -> SemanticDescriptor:
        """Create a new semantic descriptor."""
        return cls(
            descriptor_id=f"semantic_descriptor:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_goal=reasoning_goal,
            semantic_mode=semantic_mode,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: SemanticState) -> SemanticDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == SemanticState.COMPLETED else None,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SemanticDescriptor",
    "SemanticMode",
    "SemanticState",
]