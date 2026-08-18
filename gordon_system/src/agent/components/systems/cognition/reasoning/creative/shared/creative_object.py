# Creative Object Contract - Phase 7.33
# ====================================

"""
Canonical Creative Object.

A creative object represents a novel cognitive artifact generated through
creative reasoning processes.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class CreativeObject:
    """
    Represents a creative artifact generated through creative reasoning.
    
    A creative object includes:
        - Identity and provenance tracking
        - Novelty score (0-1 scale)
        - Usefulness estimate (0-1 scale)
        - Originating domains
        - Generative lineage
    
    Creative objects remain explicit and inspectable.
    """
    
    # Identity
    object_id: str                          # Unique identifier
    semantic_identity: str                  # Semantic identity
    
    # Content
    content_type: str                       # e.g., "design", "algorithm", "architecture"
    content: Any                            # The actual creative output (can be structured)
    
    # Originating domains (where knowledge came from)
    originating_domains: List[str] = field(default_factory=list)
    
    # Quality estimates
    novelty_score: float = 0.0              # 0-1 scale (novelty relative to existing knowledge)
    usefulness_estimate: float = 0.0        # 0-1 scale (estimated practical value)
    feasibility_estimate: float = 0.0       # 0-1 scale (likelihood of implementation)
    
    # Generative lineage
    provenance_id: Optional[str] = None     # ID of the creative process that generated this
    source_object_ids: List[str] = field(default_factory=list)  # Objects this was derived from
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_novel(self) -> bool:
        """Check if object has sufficient novelty."""
        return self.novelty_score >= 0.5
    
    @property
    def is_useful(self) -> bool:
        """Check if object has sufficient usefulness."""
        return self.usefulness_estimate >= 0.5
    
    @property
    def is_viable(self) -> bool:
        """Check if object meets basic viability thresholds."""
        return self.is_novel and self.is_useful and self.feasibility_estimate >= 0.3
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        content_type: str,
        content: Any,
        originating_domains: Optional[List[str]] = None,
        provenance_id: Optional[str] = None,
        source_object_ids: Optional[List[str]] = None,
    ) -> CreativeObject:
        """Create a new creative object."""
        return cls(
            object_id=f"creative_object:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            content_type=content_type,
            content=content,
            originating_domains=originating_domains or [],
            provenance_id=provenance_id,
            source_object_ids=source_object_ids or [],
            created_at_utc=time.time(),
        )
    
    def with_novelty(self, score: float) -> CreativeObject:
        """Return a copy with updated novelty score."""
        return dataclass_replace(
            self,
            novelty_score=max(0.0, min(1.0, score)),
        )
    
    def with_usefulness(self, score: float) -> CreativeObject:
        """Return a copy with updated usefulness estimate."""
        return dataclass_replace(
            self,
            usefulness_estimate=max(0.0, min(1.0, score)),
        )
    
    def with_feasibility(self, score: float) -> CreativeObject:
        """Return a copy with updated feasibility estimate."""
        return dataclass_replace(
            self,
            feasibility_estimate=max(0.0, min(1.0, score)),
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CreativeObject",
]