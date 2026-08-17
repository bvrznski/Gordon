# Explanation Descriptor - Phase 7.14
# ======================================

"""
Canonical Explanatory Reasoning Descriptor.

A descriptor exposes explanation metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class ExplanationMode(Enum):
    """Modes of explanatory reasoning."""
    
    DIAGNOSTIC = "diagnostic"               # Identify causes from effects
    EXPLANATORY = "explanatory"             # Explain observations
    JUSTIFICATION = "justification"         # Justify decisions or actions
    CAUSAL_INFER = "causal_infer"           # Infer causal mechanisms
    NARRATIVE = "narrative"                 # Tell a story about what happened
    ALTERNATIVE_ANALYSIS = "alternative_analysis"  # Compare competing explanations


class ExplanationLifecycle(Enum):
    """Explanation session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    EVIDENCE_COLLECTION = "evidence_collection"
    CLAIM_ORGANIZATION = "claim_organization"
    JUSTIFICATION_CONSTRUCTION = "justification_construction"
    NARRATIVE_CONSTRUCTION = "narrative_construction"
    ALTERNATIVE_COMPARISON = "alternative_comparison"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class ExplanationDescriptor:
    """
    Descriptor exposing explanation metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Explanation mode and goal
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what explanation occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Reasoning classification
    explanation_mode: ExplanationMode         # What kind of explanatory reasoning?
    explanation_goal: str                     # What are we trying to explain?
    
    # Lifecycle state
    lifecycle_state: ExplanationLifecycle = ExplanationLifecycle.CREATED
    
    # Constraints and requirements
    confidence_threshold: float = 0.5         # Minimum confidence for accepting explanation
    min_evidence_required: int = 1            # Minimum evidence required
    max_alternatives: int = 5                 # Maximum alternative explanations to consider
    temporal_scope: Tuple[float, float] = (0.0, float('inf'))  # Time range
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None   # If this is a refinement
    origin_context: str = "unknown"              # Where did explanation originate?
    
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
        """Check if explanation completed."""
        return self.lifecycle_state == ExplanationLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if explanation failed."""
        return self.lifecycle_state == ExplanationLifecycle.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        explanation_goal: str,
        explanation_mode: ExplanationMode = ExplanationMode.DIAGNOSTIC,
        origin_context: str = "unknown",
        source_descriptor_id: Optional[str] = None,
        confidence_threshold: float = 0.5,
    ) -> ExplanationDescriptor:
        """Create a new explanation descriptor."""
        return cls(
            descriptor_id=f"explanation:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            explanation_goal=explanation_goal,
            explanation_mode=explanation_mode,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            confidence_threshold=confidence_threshold,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: ExplanationLifecycle) -> ExplanationDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == ExplanationLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class ExplanationSessionIdentity:
    """
    Immutable identity for an explanation session.
    
    Allows replay and verification of explanatory results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> ExplanationSessionIdentity:
        """Create a new session identity."""
        return cls(
            semantic_identity=semantic_identity,
            session_number=session_number,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "ExplanationDescriptor",
    "ExplanationSessionIdentity",
    "ExplanationMode",
    "ExplanationLifecycle",
]