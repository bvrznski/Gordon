# Schema Extraction - Phase 7.4
# ============================

"""
Canonical Schema Extraction Contract.

Schema extraction identifies reusable relational structures from cases.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class RelationalSchema:
    """
    A reusable relational structure extracted from cases.
    
    Schemas describe:
        - Feedback loops (self-regulating systems)
        - Producer-consumer relationships (resource flow)
        - Hierarchies (part-whole relations)
        - Pipelines (sequential processing)
        - Resource allocation (distribution mechanisms)
        - And more...
    
    Schemas remain explicit; they are not implicit assumptions.
    """
    
    # Identity
    schema_id: str                            # Unique identifier
    
    # Schema structure
    schema_name: str                          # Name of the pattern
    schema_type: str = "relational"           # e.g., "feedback_loop", "pipeline"
    
    # Participating relations
    participating_relations: Tuple[str, ...] = ()  # What's involved?
    
    # Abstraction level
    abstraction_level: int = 1                # Higher = more abstract
    
    # Applicability conditions
    applicability_conditions: Tuple[str, ...] = ()
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def relation_count(self) -> int:
        """Number of relations in schema."""
        return len(self.participating_relations)
    
    @classmethod
    def create(
        cls,
        schema_name: str,
        schema_type: str = "relational",
        relations: Optional[List[str]] = None,
        abstraction_level: int = 1,
    ) -> RelationalSchema:
        """Create a new relational schema."""
        return cls(
            schema_id=f"relational_schema:{uuid.uuid4().hex[:16]}",
            schema_name=schema_name,
            schema_type=schema_type,
            participating_relations=tuple(relations or []),
            abstraction_level=abstraction_level,
        )


@dataclass(frozen=True)
class SchemaExtraction:
    """
    Result of extracting a schema from case structures.
    
    Extraction identifies:
        - Reusable patterns
        - Abstraction levels
        - Applicability domains
        - Structural constraints
    
    Extracted schemas remain explicit; they don't replace original structures.
    """
    
    # Identity
    extraction_id: str                        # Unique identifier
    
    # Source cases
    source_case_ids: Tuple[str, ...] = ()     # Where was this extracted from?
    
    # Extracted schema
    extracted_schema: RelationalSchema        # The resulting schema
    
    # Extraction quality
    confidence: float = 0.0                   # How confident in extraction?
    
    # Applicability
    applicable_domains: Tuple[str, ...] = ()  # Which domains can use this?
    
    # Metadata
    extracted_at_utc: float = field(default_factory=time.time)
    
    @property
    def source_count(self) -> int:
        """Number of source cases."""
        return len(self.source_case_ids)
    
    @classmethod
    def create(
        cls,
        schema: RelationalSchema,
        source_cases: Optional[List[str]] = None,
        confidence: float = 0.5,
    ) -> SchemaExtraction:
        """Create a new schema extraction result."""
        return cls(
            extraction_id=f"schema_extraction:{uuid.uuid4().hex[:16]}",
            extracted_schema=schema,
            source_case_ids=tuple(source_cases or []),
            confidence=confidence,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "RelationalSchema",
    "SchemaExtraction",
]