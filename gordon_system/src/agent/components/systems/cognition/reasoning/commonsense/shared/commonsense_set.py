# Commonsense Set - Phase 7.45
# ==============================

"""
Canonical Commonsense Set.

A Commonsense Set defines the context, observations, and constraints for
commonsense reasoning.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# OBSERVED ENTITY
# =============================================================================

@dataclass(frozen=True)
class ObservedEntity:
    """
    An entity observed in the current context.
    
    Each observed entity includes its type, properties, and relationships.
    """
    
    entity_id: str                            # Unique identifier for the entity
    entity_type: str                          # e.g., "person", "object", "location"
    name: Optional[str] = None                # Human-readable name if applicable
    properties: Dict[str, Any] = field(default_factory=dict)  # Entity attributes
    relationships: List[Tuple[str, str]] = field(default_factory=list)  # (relation_type, target_id)
    
    @classmethod
    def create(
        cls,
        entity_id: str,
        entity_type: str,
        name: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        relationships: Optional[List[Tuple[str, str]]] = None,
    ) -> ObservedEntity:
        """Create a new observed entity."""
        return cls(
            entity_id=entity_id,
            entity_type=entity_type,
            name=name,
            properties=properties or {},
            relationships=relationships or [],
        )


# =============================================================================
# OBSERVED CONTEXT
# =============================================================================

@dataclass(frozen=True)
class ObservedContext:
    """
    The observed context for commonsense reasoning.
    
    Context includes:
        - All observed entities and their states
        - Spatial relationships between entities
        - Temporal information about observations
        - Environmental constraints
    """
    
    context_id: str                           # Unique context identifier
    entities: Tuple[ObservedEntity, ...]      # All observed entities
    spatial_relationships: Dict[str, List[Tuple[str, str]]] = field(
        default_factory=dict
    )  # e.g., "above": [("book", "table")]
    temporal_info: Optional[Dict[str, Any]] = None  # Timestamps, durations, etc.
    environmental_constraints: List[str] = field(default_factory=list)  # e.g., "gravity_present"
    
    @classmethod
    def create(
        cls,
        context_id: str,
        entities: Tuple[ObservedEntity, ...],
        spatial_relationships: Optional[Dict[str, List[Tuple[str, str]]]] = None,
        temporal_info: Optional[Dict[str, Any]] = None,
        environmental_constraints: Optional[List[str]] = None,
    ) -> ObservedContext:
        """Create a new observed context."""
        return cls(
            context_id=context_id,
            entities=entities,
            spatial_relationships=spatial_relationships or {},
            temporal_info=temporal_info,
            environmental_constraints=environmental_constraints or [],
        )
    
    def get_entities_by_type(self, entity_type: str) -> Tuple[ObservedEntity, ...]:
        """Get all entities of a specific type."""
        return tuple(e for e in self.entities if e.entity_type == entity_type)
    
    def find_entity(self, entity_id: str) -> Optional[ObservedEntity]:
        """Find an entity by its ID."""
        for entity in self.entities:
            if entity.entity_id == entity_id:
                return entity
        return None


# =============================================================================
# MISSING INFORMATION
# =============================================================================

@dataclass(frozen=True)
class MissingInformation:
    """
    Information that is missing but could be inferred through commonsense.
    
    Each missing item includes:
        - What information is missing
        - Why it's likely inferable (based on context)
        - Confidence in the inference
    """
    
    missing_id: str                           # Unique identifier for this missing info
    description: str                          # What is missing?
    inference_basis: List[str] = field(default_factory=list)  # What supports inferring it?
    estimated_completeness: float = 0.5       # 0.0 to 1.0 estimate
    
    @classmethod
    def create(
        cls,
        missing_id: str,
        description: str,
        inference_basis: Optional[List[str]] = None,
        estimated_completeness: float = 0.5,
    ) -> MissingInformation:
        """Create a new missing information item."""
        return cls(
            missing_id=missing_id,
            description=description,
            inference_basis=inference_basis or [],
            estimated_completeness=estimated_completeness,
        )


# =============================================================================
# CONTEXTUAL CONSTRAINTS
# =============================================================================

@dataclass(frozen=True)
class ContextualConstraints:
    """
    Constraints on commonsense reasoning.
    
    These constraints define the boundaries within which commonsense
    inferences should be made.
    """
    
    constraint_id: str                        # Unique constraint identifier
    hard_constraints: List[str] = field(default_factory=list)  # Cannot violate these
    soft_constraints: List[str] = field(default_factory=list)  # Prefer not to violate
    
    @classmethod
    def create(
        cls,
        constraint_id: str,
        hard_constraints: Optional[List[str]] = None,
        soft_constraints: Optional[List[str]] = None,
    ) -> ContextualConstraints:
        """Create a new set of contextual constraints."""
        return cls(
            constraint_id=constraint_id,
            hard_constraints=hard_constraints or [],
            soft_constraints=soft_constraints or [],
        )


# =============================================================================
# COMMONSENSE SET
# =============================================================================

@dataclass(frozen=True)
class CommonsenseSet:
    """
    Complete set of information for commonsense reasoning.
    
    A Commonsense Set defines:
        - The observed context (what we've seen)
        - Missing information (what needs inference)
        - Contextual constraints (boundaries for reasoning)
    
    Commonsense Sets remain immutable during reasoning to ensure
    deterministic, reproducible results.
    """
    
    set_id: str                               # Unique set identifier
    semantic_identity: str                    # Semantic identity of the reasoning session
    observed_context: ObservedContext         # What has been observed
    missing_information: Tuple[MissingInformation, ...] = field(default_factory=tuple)  # What needs inference
    contextual_constraints: ContextualConstraints  # Reasoning constraints
    
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        observed_context: ObservedContext,
        missing_information: Optional[Tuple[MissingInformation, ...]] = None,
        contextual_constraints: Optional[ContextualConstraints] = None,
    ) -> CommonsenseSet:
        """Create a new commonsense set."""
        return cls(
            set_id=f"commonsense_set:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            observed_context=observed_context,
            missing_information=missing_information or (),
            contextual_constraints=contextual_constraints or ContextualConstraints.create("default"),
        )
    
    def get_missing_by_description(self, description: str) -> Optional[MissingInformation]:
        """Find missing information by its description."""
        for item in self.missing_information:
            if item.description == description:
                return item
        return None


__all__ = [
    "ObservedEntity",
    "ObservedContext",
    "MissingInformation",
    "ContextualConstraints",
    "CommonsenseSet",
]