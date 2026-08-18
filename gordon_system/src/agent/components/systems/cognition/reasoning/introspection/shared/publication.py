# Self-State Publication - Phase 7.29
# ====================================

"""
Self-State Publication manages introspection result publication.

Publication determines:
    - Self summaries
    - Confidence summaries
    - Cognitive summaries
    - Resource summaries
    - Health summaries
    
Publication remains explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class SelfStatePublication:
    """
    Publication of introspection results.
    
    A publication contains:
        - Explicit identity
        - Published state (self model summaries, awareness, diagnostics, etc.)
        - Publication scope (what is published where)
        - Publication policy
        - Provenance tracking
    
    Publications remain independently inspectable.
    """
    
    # Identity
    publication_id: str                       # Unique identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Published state
    self_model_summary: Optional[Dict[str, Any]] = None   # Self model summary
    awareness_summary: Optional[Dict[str, Any]] = None    # Awareness summary
    consistency_summary: Optional[Dict[str, Any]] = None  # Consistency summary
    diagnostic_summary: Optional[Dict[str, Any]] = None   # Diagnostic summary
    
    # Publication scope
    publication_scope: str = "internal"       # internal, monitoring, diagnostic, persistent
    
    # Publication policy
    publication_policy: str = "default"       # Policy for this publication
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_introspection_id: Optional[str] = None   # Which introspection?
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        scope: str = "internal",
        policy: str = "default",
    ) -> SelfStatePublication:
        """Create a new self-state publication."""
        return cls(
            publication_id=f"publication:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            publication_scope=scope,
            publication_policy=policy,
        )
    
    def with_summary(self, summary_type: str, summary_data: Dict[str, Any]) -> SelfStatePublication:
        """Return a copy with a summary added."""
        attr_map = {
            "self_model": "self_model_summary",
            "awareness": "awareness_summary",
            "consistency": "consistency_summary",
            "diagnostic": "diagnostic_summary",
        }
        
        attr = attr_map.get(summary_type, None)
        if attr:
            return dataclass_replace(
                self,
                **{attr: summary_data}
            )
        
        return self


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "SelfStatePublication",
]