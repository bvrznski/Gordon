# Consolidation - Phase 7.28
# =========================

"""
Consolidation determines what should be preserved from completed cognition.

Consolidation evaluates:
    - Knowledge candidates (what to remember)
    - Memory candidates (how to store)
    - Behavior candidates (how to act)
    - Policy candidates (rules to follow)

Consolidation remains explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ConsolidationCandidate:
    """
    A candidate for consolidation from completed cognition.
    
    A candidate contains:
        - Explicit identity
        - Candidate type (knowledge, memory, behavior, policy)
        - Content to be consolidated
        - Priority level
        - Provenance tracking
    """
    
    # Identity
    candidate_id: str                         # Unique candidate identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Classification
    candidate_type: str                       # knowledge, memory, behavior, policy
    candidate_category: str                   # Specific category
    
    # Content
    content: Dict[str, Any]                   # What to consolidate
    rationale: Dict[str, Any]                 # Why consolidate this?
    
    # Priority and conditions
    priority: int = 0                         # Higher = more important
    applicability_conditions: Dict[str, Any] = field(default_factory=dict)   # When applicable?
    
    # Quality metrics
    confidence_score: float = 0.0             # Confidence in candidate value
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_sessions: List[str] = field(default_factory=list)   # Source sessions
    origin_context: str = "unknown"                             # Where consolidation originated
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        candidate_type: str,
        content: Dict[str, Any],
        rationale: Dict[str, Any],
        source_sessions: Optional[List[str]] = None,
        origin_context: str = "unknown",
    ) -> ConsolidationCandidate:
        """Create a new consolidation candidate."""
        return cls(
            candidate_id=f"consolidation:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            candidate_type=candidate_type,
            candidate_category="general",
            content=content,
            rationale=rationale,
            source_sessions=source_sessions or [],
            origin_context=origin_context,
        )


@dataclass(frozen=True)
class ReflectionConsolidation:
    """
    Consolidation proposal from reflection analysis.
    
    A consolidation contains:
        - Explicit identity
        - Consolidation candidates
        - Consolidation policy (how to consolidate)
        - Expected benefits
        - Provenance tracking
    
    Proposals remain independently inspectable.
    """
    
    # Identity
    consolidation_id: str                     # Unique consolidation identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Candidates
    candidates: List[ConsolidationCandidate]  # All candidates to consolidate
    
    # Consolidation policy
    consolidation_policy: Dict[str, Any]      # How to consolidate?
    
    # Expected benefits
    expected_benefits: List[str] = field(default_factory=list)   # What gains?
    
    # Quality metrics
    total_candidates: int = 0                 # Total candidates proposed
    confidence_score: float = 0.0             # Overall confidence
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_sessions: List[str] = field(default_factory=list)   # Source sessions
    origin_context: str = "unknown"                             # Where consolidation originated
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        candidates: List[ConsolidationCandidate],
        consolidation_policy: Dict[str, Any],
        source_sessions: Optional[List[str]] = None,
        origin_context: str = "unknown",
    ) -> ReflectionConsolidation:
        """Create a new reflection consolidation."""
        return cls(
            consolidation_id=f"consolidation:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            candidates=candidates,
            consolidation_policy=consolidation_policy,
            total_candidates=len(candidates),
            source_sessions=source_sessions or [],
            origin_context=origin_context,
        )


@dataclass(frozen=True)
class ConsolidationManagement:
    """
    Management of consolidation process.
    
    A management object contains:
        - Consolidation identity and policy
        - Current state
        - Candidates evaluated
        - Provenance tracking
    """
    
    # Identity
    management_id: str                        # Unique management identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Configuration
    consolidation_policy: Dict[str, Any]      # Policy to apply
    min_priority_threshold: int = 1           # Minimum priority threshold
    max_candidates: int = 20                  # Maximum candidates to consider
    
    # Current state
    current_stage: str = "initializing"       # Consolidation stage
    
    # Results (can be None if not yet completed)
    consolidation_result: Optional[ReflectionConsolidation] = None
    
    # Quality metrics
    candidate_evaluation_score: float = 0.0   # Evaluation quality
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_sessions: List[str] = field(default_factory=list)   # Source sessions
    origin_context: str = "unknown"                             # Where consolidation originated
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        consolidation_policy: Dict[str, Any],
        source_sessions: Optional[List[str]] = None,
        origin_context: str = "unknown",
    ) -> ConsolidationManagement:
        """Create a new consolidation management."""
        return cls(
            management_id=f"consolidation_management:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            consolidation_policy=consolidation_policy,
            source_sessions=source_sessions or [],
            origin_context=origin_context,
        )


__all__ = [
    "ConsolidationCandidate",
    "ReflectionConsolidation",
    "ConsolidationManagement",
]