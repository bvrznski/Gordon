# Executive State Serialization Types
# ====================================

"""
Serialization utilities for executive state and context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any


@dataclass(frozen=True)
class ExecutiveStateSerialization:
    """
    Serialization results for executive state.
    
    Ensures that serialization preserves all necessary information while
    removing any runtime objects or live references.
    """
    
    valid: bool = True
    """Whether the state can be serialized."""
    
    type_discriminators_preserved: bool = True
    """Whether type discriminators are preserved in output."""
    
    schema_version_preserved: bool = True
    """Whether schema version is preserved in output."""
    
    entity_ids_preserved: bool = True
    """Whether all entity IDs are preserved."""
    
    revisions_preserved: bool = True
    """Whether revision numbers are preserved."""
    
    semantic_modes_preserved: bool = True
    """Whether semantic modes are preserved."""
    
    references_preserved: bool = True
    """Whether all references (to other entities) are preserved as IDs."""
    
    factuality_markers_preserved: bool = True
    """Whether factuality markers are preserved."""
    
    privacy_classifications_preserved: bool = True
    """Whether privacy classifications are preserved."""
    
    authority_metadata_preserved: bool = True
    """Whether authority metadata is preserved."""
    
    confidence_scores_preserved: bool = True
    """Whether confidence scores are preserved."""
    
    completeness_markers_preserved: bool = True
    """Whether completeness markers are preserved."""
    
    consistency_markers_preserved: bool = True
    """Whether consistency markers are preserved."""
    
    coherence_markers_preserved: bool = True
    """Whether coherence markers are preserved."""
    
    runtime_objects_rejected: Tuple[str, ...] = field(default_factory=tuple)
    """List of runtime objects that were rejected (if any)."""
    
    @classmethod
    def valid(cls) -> ExecutiveStateSerialization:
        return cls(valid=True)
    
    @classmethod
    def invalid(
        cls,
        errors: Tuple[str, ...],
        runtime_objects_rejected: Tuple[str, ...] = (),
    ) -> ExecutiveStateSerialization:
        return cls(
            valid=False,
            runtime_objects_rejected=runtime_objects_rejected,
        )


@dataclass(frozen=True)
class ExecutiveContextSerialization:
    """
    Serialization results for executive context.
    """
    
    valid: bool = True
    """Whether the context can be serialized."""
    
    type_discriminators_preserved: bool = True
    schema_version_preserved: bool = True
    entity_ids_preserved: bool = True
    revisions_preserved: bool = True
    purpose_preserved: bool = True
    subject_preserved: bool = True
    
    references_preserved: bool = True
    projections_as_references_or_summaries: bool = True
    
    runtime_objects_rejected: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def valid(cls) -> ExecutiveContextSerialization:
        return cls(valid=True)


__all__: Tuple[str, ...] = (
    "ExecutiveStateSerialization",
    "ExecutiveContextSerialization",
)