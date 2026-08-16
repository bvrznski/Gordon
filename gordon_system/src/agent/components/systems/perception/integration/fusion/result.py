# Perceptual Fusion Result - Phase 5.2.3
# ======================================

"""
Fusion Result: Outcome of a fusion operation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


@dataclass(frozen=True)
class PerceptualFusionResult:
    """
    Result of a perceptual fusion operation.
    
    Fields:
        request_reference: Reference to the original request
        fused_artifacts: Fused artifact IDs produced
        source_artifacts: Original artifact references
        integrated_fields: Which fields were integrated?
        unresolved_fields: Which fields remain separate?
        preserved_conflicts: Conflicts that couldn't be resolved
        source_weights: Weighting applied to each source
    """
    
    request_reference: str
    
    fused_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    source_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    
    integrated_fields: Tuple[Dict[str, Any], ...] = field(default_factory=tuple)
    unresolved_fields: Tuple[str, ...] = field(default_factory=tuple)
    preserved_conflicts: Tuple[str, ...] = field(default_factory=tuple)
    source_weights: Dict[str, float] = field(default_factory=dict)  # artifact -> weight
    
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    status: str = "unknown"  # See FusionStatus enum
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: Dict[str, Any] = field(default_factory=dict)


class FusionStatus:
    """Status of fusion operation."""
    COMPLETE = "complete"
    PARTIAL = "partial"
    ALTERNATIVE_PRESERVING = "alternative_preserving"
    CONFLICTED = "conflicted"
    AMBIGUOUS = "ambiguous"
    REJECTED = "rejected"
    FAILED = "failed"
    UNKNOWN = "unknown"


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
    
    COMPLEMENTARY = "complementary"       # Combine non-overlapping fields
    CORROBORATIVE = "corroborative"       # Aggregate supporting evidence
    COMPETITIVE = "competitive"           # Preserve incompatible alternatives
    HIERARCHICAL = "hierarchical"         # Preserve abstraction levels
    FIELD_LEVEL = "field_level"           # Field-level integration
    FEATURE_LEVEL = "feature_level"       # Feature-level fusion
    PERCEPT_LEVEL = "percept_level"       # Percept-level fusion
    EVENT_LEVEL = "event_level"           # Event-level fusion
    SCENE_LEVEL = "scene_level"           # Scene-level fusion
    CONSENSUS = "consensus"               # Consensus-based fusion
    ALTERNATIVE_PRESERVING = "alternative_preserving"  # Keep all alternatives


@dataclass(frozen=True)
class FieldFusionDecision:
    """
    Decision about how to fuse a specific field.
    
    Fields:
        field_name: Which field?
        candidate_values: Values from different sources
        source_artifacts: Which artifacts provided these values?
        source_weights: Weights for each source
        agreement_state: How do values agree? (see FieldAgreementState)
        selected_value: Value that was selected (if any)
        preserved_alternatives: Alternatives that remain visible
    """
    
    field_name: str
    
    candidate_values: Tuple[Any, ...] = field(default_factory=tuple)
    source_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    source_weights: Dict[str, float] = field(default_factory=dict)
    
    agreement_state: str = "unknown"  # See FieldAgreementState
    
    selected_value: Optional[Any] = None
    preserved_alternatives: Tuple[Any, ...] = field(default_factory=tuple)
    
    confidence: float = 1.0
    uncertainty: float = 0.0
    
    decision_basis: str = ""
    provenance: Dict[str, Any] = field(default_factory=dict)


class FieldAgreementState:
    """States of field agreement during fusion."""
    
    AGREED = "agreed"                   # All values match
    COMPATIBLE = "compatible"           # Values don't conflict
    COMPLEMENTARY = "complementary"     # Values add different information
    PARTIALLY_CONFLICTING = "partially_conflicting"
    CONFLICTING = "conflicting"         # Values directly contradict
    MISSING = "missing"                 # Some sources missing this field
    AMBIGUOUS = "ambiguous"             # Can't determine agreement
    UNRESOLVED = "unresolved"           # Decision deferred


@dataclass(frozen=True)
class IntegratedFieldProvenance:
    """
    Provenance for an integrated field.
    
    Fields:
        field_identity: Unique identifier
        integrated_artifact: Which artifact contains this field?
        field_name: Name of the field
        source_artifacts: Which artifacts contributed?
        source_values: Values from each source
        transformation_records: Processing steps applied
        conflict_state: Was there conflict?
    """
    
    field_identity: str
    
    integrated_artifact: str
    field_name: str
    
    source_artifacts: Tuple[str, ...]
    source_values: Tuple[Any, ...] = field(default_factory=tuple)
    transformation_records: Tuple[str, ...] = field(default_factory=tuple)
    
    conflict_state: str = "none"  # none, preserved, resolved