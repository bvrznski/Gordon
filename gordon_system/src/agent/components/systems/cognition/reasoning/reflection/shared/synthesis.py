# Experience Synthesis - Phase 7.28
# ==================================

"""
Experience Synthesis derives patterns and themes from completed cognition.

Synthesis evaluates:
    - Historical consistency
    - Recurring patterns
    - Causal relationships
    - System-wide effects
    - Cross-session regularities
    - Important events

Synthesis remains explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class ExperienceSynthesis:
    """
    Synthesized experience from completed cognition.
    
    A synthesis contains:
        - Explicit identity
        - Synthesized experiences (patterns, themes, events)
        - Synthesis strategy used
        - Synthesis metrics
        - Provenance tracking
    
    Syntheses remain independently inspectable.
    """
    
    # Identity
    synthesis_id: str                         # Unique synthesis identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Synthesized experience content
    synthesized_patterns: List[str]           # Extracted patterns
    synthesized_themes: List[str]             # Extracted themes
    synthesized_events: List[Dict[str, Any]]  # Significant events
    synthesized_causal_relationships: List[Dict[str, Any]] = field(default_factory=list)  # Causal links
    
    # Synthesis strategy
    synthesis_strategy: str                   # Strategy used for synthesis
    
    # Metrics
    pattern_count: int = 0                    # Number of patterns extracted
    theme_count: int = 0                      # Number of themes identified
    evidence_count: int = 0                   # Evidence items supporting synthesis
    confidence_score: float = 0.0             # Confidence in synthesis
    
    # Constraints met
    min_evidence_per_pattern: int = 1         # Minimum evidence per pattern
    max_patterns: int = 20                    # Maximum patterns to extract
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_sessions: List[str] = field(default_factory=list)   # Source sessions
    origin_context: str = "unknown"                             # Where synthesis originated
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        synthesized_patterns: List[str],
        synthesized_themes: List[str],
        synthesized_events: List[Dict[str, Any]],
        synthesis_strategy: str = "default",
        source_sessions: Optional[List[str]] = None,
        origin_context: str = "unknown",
    ) -> ExperienceSynthesis:
        """Create a new experience synthesis."""
        return cls(
            synthesis_id=f"synthesis:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            synthesized_patterns=synthesized_patterns,
            synthesized_themes=synthesized_themes,
            synthesized_events=synthesized_events,
            synthesis_strategy=synthesis_strategy,
            pattern_count=len(synthesized_patterns),
            theme_count=len(synthesized_themes),
            evidence_count=sum(len(e.get("evidence_items", [])) for e in synthesized_events),
            source_sessions=source_sessions or [],
            origin_context=origin_context,
        )


@dataclass(frozen=True)
class ExperienceSynthesisManagement:
    """
    Management of experience synthesis process.
    
    A management object contains:
        - Synthesis identity and strategy
        - Current state
        - Quality metrics
        - Provenance tracking
    """
    
    # Identity
    management_id: str                        # Unique management identifier
    semantic_identity: str                    # Semantic identity for replay
    
    # Synthesis configuration
    synthesis_strategy: str                   # Strategy for synthesis
    min_evidence_per_pattern: int = 1         # Minimum evidence per pattern
    max_patterns: int = 20                    # Maximum patterns to extract
    
    # Current state
    current_stage: str = "initializing"       # Synthesis stage
    
    # Results (can be None if not yet completed)
    synthesis_result: Optional[ExperienceSynthesis] = None
    
    # Quality metrics
    pattern_quality_score: float = 0.0        # Quality score for patterns
    theme_coherence_score: float = 0.0        # Coherence of themes
    evidence_coverage: float = 0.0            # Coverage of evidence
    
    # Compatibility
    compatibility_revision: int = 1           # For schema evolution tracking
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_sessions: List[str] = field(default_factory=list)   # Source sessions
    origin_context: str = "unknown"                             # Where synthesis originated
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
        synthesis_strategy: str,
        source_sessions: Optional[List[str]] = None,
        origin_context: str = "unknown",
    ) -> ExperienceSynthesisManagement:
        """Create a new experience synthesis management."""
        return cls(
            management_id=f"synthesis_management:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            synthesis_strategy=synthesis_strategy,
            source_sessions=source_sessions or [],
            origin_context=origin_context,
        )


__all__ = [
    "ExperienceSynthesis",
    "ExperienceSynthesisManagement",
]