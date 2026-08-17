# Analogical Reasoning Descriptor - Phase 7.4
# ===========================================

"""
Canonical Analogy Descriptor.

A descriptor exposes analogical reasoning metadata independently of execution.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


class AnalogyMode(Enum):
    """Modes of analogical reasoning."""
    
    STRUCTURAL_MAPPING = "structural_mapping"   # Map structure between domains
    CASE_BASED_REASONING = "case_based_reasoning"  # Reason from past cases
    SCHEMA_MATCHING = "schema_matching"          # Match relational schemas
    TRANSFER_LEARNING = "transfer_learning"      # Transfer knowledge across domains
    MULTI_SOURCE_ANALOGY = "multi_source_analogy" # Combine multiple analogies


class AnalogyLifecycle(Enum):
    """Analogy session lifecycle states."""
    
    CREATED = "created"
    INITIALIZING = "initializing"
    RETRIEVING = "retrieving"
    MAPPING = "mapping"
    TRANSFERRING = "transferring"
    VALIDATING = "validating"
    REFINING = "refining"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class AnalogyDescriptor:
    """
    Descriptor exposing analogical reasoning metadata independently of execution.
    
    A descriptor contains:
        - Semantic identity (immutable, persistent across runs)
        - Analogy mode and goal
        - Lifecycle state
        - Compatibility information
        - Provenance tracking
    
    Descriptors allow inspection of what analogy occurred without
    needing to execute the full reasoning process again.
    """
    
    # Identity
    descriptor_id: str                        # Unique descriptor identifier
    semantic_identity: str                    # Semantic identity (stable across runs)
    
    # Reasoning classification
    analogy_mode: AnalogyMode                 # What kind of analogical reasoning?
    reasoning_goal: str                       # What are we trying to achieve?
    
    # Target problem specification
    target_problem: str                       # The problem being solved
    source_candidates: Tuple[str, ...] = ()   # Potential source domains
    
    # Lifecycle state
    lifecycle_state: AnalogyLifecycle = AnalogyLifecycle.CREATED
    
    # Constraints and requirements
    structural_similarity_threshold: float = 0.5  # Minimum similarity for valid mapping
    max_mappings: int = 10                          # Maximum mappings to consider
    require_validation: bool = True                 # Must validation pass?
    
    # Compatibility
    compatibility_revision: int = 1                 # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    started_at_utc: Optional[float] = None
    completed_at_utc: Optional[float] = None
    
    # Provenance
    source_descriptor_id: Optional[str] = None      # If this is a refinement
    origin_context: str = "unknown"                 # Where did reasoning originate?
    
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
        """Check if analogy completed."""
        return self.lifecycle_state == AnalogyLifecycle.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if analogy failed."""
        return self.lifecycle_state == AnalogyLifecycle.FAILED
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        reasoning_goal: str,
        target_problem: str,
        analogy_mode: AnalogyMode = AnalogyMode.STRUCTURAL_MAPPING,
        origin_context: str = "unknown",
        source_candidates: Optional[List[str]] = None,
        source_descriptor_id: Optional[str] = None,
    ) -> AnalogyDescriptor:
        """Create a new analogy descriptor."""
        return cls(
            descriptor_id=f"analogy:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            reasoning_goal=reasoning_goal,
            target_problem=target_problem,
            source_candidates=tuple(source_candidates or []),
            analogy_mode=analogy_mode,
            origin_context=origin_context,
            source_descriptor_id=source_descriptor_id,
            started_at_utc=time.time(),
        )
    
    def to_state(self, new_state: AnalogyLifecycle) -> AnalogyDescriptor:
        """Return a copy with updated state."""
        return dataclass_replace(
            self,
            lifecycle_state=new_state,
            completed_at_utc=time.time() if new_state == AnalogyLifecycle.COMPLETED else None,
        )


@dataclass(frozen=True)
class AnalogySessionIdentity:
    """
    Immutable identity for an analogy session.
    
    Allows replay and verification of analogical results.
    """
    
    # Core identity
    semantic_identity: str                    # Stable identity across runs
    
    # Session context
    session_number: int = 1                   # For repeated sessions
    timestamp_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(cls, semantic_identity: str, session_number: int = 1) -> AnalogySessionIdentity:
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
    "AnalogyDescriptor",
    "AnalogySessionIdentity",
    "AnalogyMode",
    "AnalogyLifecycle",
]