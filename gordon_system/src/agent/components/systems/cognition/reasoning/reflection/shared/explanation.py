# Self-Explanation - Phase 7.28
# =============================

"""
Self-Explanation derives reasons for cognitive activity.

Self-explanation evaluates:
    - Decision rationale
    - Reasoning rationale
    - Execution rationale
    - Adaptation rationale
    - Strategy rationale
    - Behavioral rationale

Explanation remains explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class SelfExplanation:
    """
    Self-explanation of cognitive activity rationale.
    
    An explanation contains:
        - Explicit identity
        - Explained artifacts (decisions, actions, reasoning steps)
        - Explanation model used
        - Explanation quality metrics
        - Provenance tracking
    
    Explanations remain independently inspectable.
    """
    
    # Identity
    explanation_id: str                       # Unique explanation identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Explained artifacts
    explained_artifacts: List[str]            # IDs of artifacts being explained
    explanation_types: List[str]              # Types of explanations (decision, reasoning, etc.)
    
    # Explanation content
    rationale: Dict[str, Any]                 # Detailed rationale
    causal_factors: List[Dict[str, Any]] = field(default_factory=list)  # Causal factors
    alternatives_considered: List[Dict[str, Any]] = field(default_factory=list)  # Alternatives
    
    # Explanation model
    explanation_model: str                    # Model used for explanation (e.g., "causal_chain")
    
    # Quality metrics
    completeness_score: float = 0.0           # Completeness of explanation
    coherence_score: float = 0.0              # Coherence of reasoning
    evidence_support_score: float = 0.0       # Evidence support for explanation
    
    # Constraints met
    max_alternatives_explained: int = 10      # Maximum alternatives to consider
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_sessions: List[str] = field(default_factory=list)   # Source sessions
    origin_context: str = "unknown"                             # Where explanation originated
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        explained_artifacts: List[str],
        rationale: Dict[str, Any],
        explanation_model: str = "causal_chain",
        source_sessions: Optional[List[str]] = None,
        origin_context: str = "unknown",
    ) -> SelfExplanation:
        """Create a new self-explanation."""
        return cls(
            explanation_id=f"explanation:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            explained_artifacts=explained_artifacts,
            explanation_types=["rationale"],
            rationale=rationale,
            explanation_model=explanation_model,
            source_sessions=source_sessions or [],
            origin_context=origin_context,
        )


@dataclass(frozen=True)
class SelfExplanationManagement:
    """
    Management of self-explanation process.
    
    A management object contains:
        - Explanation identity and model
        - Current state
        - Quality metrics
        - Provenance tracking
    """
    
    # Identity
    management_id: str                        # Unique management identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Explanation configuration
    explanation_model: str                    # Model for explanation
    max_alternatives_explained: int = 10      # Maximum alternatives to consider
    
    # Current state
    current_stage: str = "initializing"       # Explanation stage
    
    # Results (can be None if not yet completed)
    explanation_result: Optional[SelfExplanation] = None
    
    # Quality metrics
    completeness_score: float = 0.0           # Completeness score
    coherence_score: float = 0.0              # Coherence score
    evidence_coverage: float = 0.0            # Evidence coverage
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_sessions: List[str] = field(default_factory=list)   # Source sessions
    origin_context: str = "unknown"                             # Where explanation originated
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        explanation_model: str,
        source_sessions: Optional[List[str]] = None,
        origin_context: str = "unknown",
    ) -> SelfExplanationManagement:
        """Create a new self-explanation management."""
        return cls(
            management_id=f"explanation_management:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            explanation_model=explanation_model,
            source_sessions=source_sessions or [],
            origin_context=origin_context,
        )


__all__ = [
    "SelfExplanation",
    "SelfExplanationManagement",
]