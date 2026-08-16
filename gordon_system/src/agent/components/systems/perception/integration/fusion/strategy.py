# Fusion Strategy - Phase 5.2.3
# ============================

"""
Fusion strategies for combining evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class FusionStrategy:
    """
    A fusion strategy configuration.
    
    Fields:
        strategy_identity: Unique identifier
        strategy_kind: What kind of fusion?
        accepted_artifact_kinds: Which artifacts can this fuse?
        required_correspondence: Correspondence requirements
        field_selection_rules: How to choose integrated values?
        conflict_handling: How to handle conflicts?
    """
    
    strategy_identity: str
    
    strategy_kind: str = "complementary"  # See FusionStrategyKind
    
    accepted_artifact_kinds: Tuple[str, ...] = field(default_factory=tuple)
    required_correspondence: Dict[str, Any] = field(default_factory=dict)
    field_selection_rules: Dict[str, Any] = field(default_factory=dict)  # field -> rule
    conflict_handling: str = "preserve"  # preserve or resolve
    
    revision: int = 1
    provenance: Dict[str, Any] = field(default_factory=dict)


class FusionStrategyKind:
    """Kinds of fusion strategies."""
    
    COMPLEMENTARY = "complementary"
    CORROBORATIVE = "corroborative"
    COMPETITIVE = "competitive"
    HIERARCHICAL = "hierarchical"
    FIELD_LEVEL = "field_level"
    FEATURE_LEVEL = "feature_level"
    PERCEPT_LEVEL = "percept_level"
    EVENT_LEVEL = "event_level"
    SCENE_LEVEL = "scene_level"
    CONSENSUS = "consensus"
    ALTERNATIVE_PRESERVING = "alternative_preserving"


@dataclass(frozen=True)
class PerceptualSourceWeight:
    """
    Weight assessment for an evidence source.
    
    Fields:
        source_artifact: Which artifact?
        source_modality: What modality produced it?
        reliability: Known reliability (0.0-1.0)
        confidence: Confidence in this assessment
        uncertainty: Uncertainty about this assessment
        freshness: How recent is the observation?
        completeness: How complete is the data?
        independence: Independent of other sources?
        relevance: Relevant to current task?
    """
    
    source_artifact: str
    
    source_modality: str
    
    reliability: float = 1.0      # 0.0-1.0
    confidence: float = 1.0
    uncertainty: float = 0.0
    freshness: float = 1.0        # 0.0-1.0 (higher = fresher)
    completeness: float = 1.0     # 0.0-1.0 (higher = more complete)
    independence: str = "unknown"  # independent, partially_dependent, derived
    relevance: float = 1.0        # 0.0-1.0
    
    policy_constraints: Tuple[str, ...] = field(default_factory=tuple)
    
    resulting_weight: float = 1.0  # Final weight after all factors
    
    provenance: Dict[str, Any] = field(default_factory=dict)