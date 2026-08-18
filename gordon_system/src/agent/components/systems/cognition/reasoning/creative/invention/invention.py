# Creative Invention Management - Phase 7.33
# =========================================

"""
Canonical Creative Invention.

Invention determines new mechanisms, architectures, abstractions, workflows,
representations, and cognitive structures.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class InventionStrategy(Enum):
    """Strategies for creative invention."""
    
    MECHANISM_INVENTION = "mechanism_invention"      # New mechanisms
    ARCHITECTURE_INVENTION = "architecture_invention"  # New architectures
    ABSTRACTION_INVENTION = "abstraction_invention"  # New abstractions
    WORKFLOW_INVENTION = "workflow_invention"        # New workflows
    REPRESENTATION_INVENTION = "representation_invention"  # New representations


@dataclass(frozen=True)
class CreativeInvention:
    """
    Represents a creative invention.
    
    An invention includes:
        - Invention strategy used
        - Resulting new mechanism/architecture/etc.
        - Expected value estimates
        - Provenance tracking
    
    Inventions remain explicit for traceability and evaluation.
    """
    
    # Identity
    invention_id: str                       # Unique invention identifier
    semantic_identity: str                  # Semantic identity
    
    # Invention strategy
    strategy: InventionStrategy = InventionStrategy.MECHANISM_INVENTION
    
    # Result
    invented_entity_type: str = ""          # e.g., "algorithm", "data structure"
    invented_entity_description: str = ""   # Description of invention
    
    # Value estimates
    expected_value: float = 0.0             # Expected practical value (0-1)
    expected_novelty: float = 0.0           # Expected novelty level (0-1)
    
    # Source concepts (what this was derived from)
    source_concept_ids: List[str] = field(default_factory=list)
    
    # Provenance
    provenance_id: Optional[str] = None     # ID of creative session
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_innovative(self) -> bool:
        """Check if invention meets novelty threshold."""
        return self.expected_novelty >= 0.5
    
    @property
    def is_valuable(self) -> bool:
        """Check if invention meets value threshold."""
        return self.expected_value >= 0.5
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        invented_entity_type: str,
        invented_entity_description: str = "",
        strategy: InventionStrategy = InventionStrategy.MECHANISM_INVENTION,
        source_concept_ids: Optional[List[str]] = None,
        provenance_id: Optional[str] = None,
    ) -> CreativeInvention:
        """Create a new creative invention."""
        return cls(
            invention_id=f"invention:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            strategy=strategy,
            invented_entity_type=invented_entity_type,
            invented_entity_description=invented_entity_description,
            source_concept_ids=source_concept_ids or [],
            provenance_id=provenance_id,
            created_at_utc=time.time(),
        )
    
    def with_value(self, value: float) -> CreativeInvention:
        """Return a copy with updated expected value."""
        return dataclass_replace(
            self,
            expected_value=max(0.0, min(1.0, value)),
        )
    
    def with_novelty(self, novelty: float) -> CreativeInvention:
        """Return a copy with updated expected novelty."""
        return dataclass_replace(
            self,
            expected_novelty=max(0.0, min(1.0, novelty)),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CreativeInvention",
    "InventionStrategy",
]