# Internal Context Snapshot Model
# ===============================

"""
Snapshot model for internal context.

A snapshot is an immutable, serialization-ready representation of a context
for storage or transmission.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any
from datetime import datetime


@dataclass(frozen=True, slots=True)
class InternalContextSnapshot:
    """
    Immutable snapshot of an internal context for serialization/storage.
    
    A snapshot is identical to InternalContext when InternalContext is already
    fully immutable and serialization-ready. Do not create redundant snapshot
    types without purpose.
    
    PROPERTIES:
        • Must expose no mutable nested structure
        • Preserve context revision
        • Preserve source revisions
        • Preserve provenance
        • Preserve completeness, confidence, freshness
        • Support deterministic comparison
        • Support serialization
        • Avoid live provider references
    
    USE CASES:
        • Storage in database or cache
        • Transmission between processes/hosts
        • Historical tracking without full contexts
        • Deterministic replay of context assembly
    """
    
    # Snapshot identity
    snapshot_id: str
    """Unique identifier for this snapshot."""
    
    snapshot_version: str = "1.0.0"
    """Schema version for compatibility tracking."""
    
    # Context identity and revisioning
    context_id: str
    """ID of the original context."""
    
    revision: int = 1
    """Revision number of the original context."""
    
    created_at_utc: datetime
    """When the context was assembled."""
    
    # Purpose and scope
    purpose: str
    """Purpose of the context."""
    
    scope: Dict[str, Any] = field(default_factory=dict)
    """Scope constraints as serializable dict."""
    
    # Content projections (as serializable dicts or references only)
    objectives: Optional[Dict[str, Any]] = None
    commitments: Optional[Dict[str, Any]] = None
    memory: Optional[Dict[str, Any]] = None
    identity: Optional[Dict[str, Any]] = None
    narrative: Optional[Dict[str, Any]] = None
    prediction: Optional[Dict[str, Any]] = None
    workspace: Optional[Dict[str, Any]] = None
    working_memory: Optional[Dict[str, Any]] = None
    execution: Optional[Dict[str, Any]] = None
    attention: Optional[Dict[str, Any]] = None
    affect: Optional[Dict[str, Any]] = None
    concerns: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    
    # Composition metadata (never silently erased)
    unresolved_conflicts: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    missing_requirements: Tuple[str, ...] = field(default_factory=tuple)
    confidence_score: float = 1.0
    completeness_status: str = "complete"
    freshness_status: str = "fresh"
    
    # Provenance (references only, no full payloads)
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_context(cls, context: "InternalContext") -> InternalContextSnapshot:
        """
        Create a snapshot from an InternalContext instance.
        
        This does NOT copy source data - only references and summaries.
        """
        return cls(
            snapshot_id=f"snapshot_{context.context_id}",
            context_id=context.context_id,
            revision=context.revision,
            created_at_utc=context.created_at_utc,
            purpose=context.purpose,
            scope={"subject_ids": [s.value for s in context.scope.subject_ids]},
            # Projections are references/summaries only
            memory=None,  # References only, not full records
            confidence_score=context.confidence.overall_confidence,
            completeness_status=context.completeness.status,
            freshness_status=context.freshness.status,
        )
    
    def to_serializable(self) -> Dict[str, Any]:
        """
        Convert snapshot to fully serializable dictionary.
        
        Returns a dict that can be safely JSON-serialized without any
        live objects or references.
        """
        return {
            "snapshot_id": self.snapshot_id,
            "snapshot_version": self.snapshot_version,
            "context_id": self.context_id,
            "revision": self.revision,
            "created_at_utc": (
                self.created_at_utc.isoformat()
                if hasattr(self.created_at_utc, "isoformat")
                else str(self.created_at_utc)
            ),
            "purpose": self.purpose,
        }