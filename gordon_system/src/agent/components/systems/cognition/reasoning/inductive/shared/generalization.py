# Induction Generalization - Phase 7.2
# =====================================

"""
Canonical Generalization Contract.

Generalization constructs broader rules from observed patterns.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class Generalization:
    """
    Generalization constructed from patterns and observations.
    
    A generalization contains:
        - Supporting patterns (the evidence for the general rule)
        - Resulting assertion (the general rule itself)
        - Confidence level
        - Provenance tracking
    
    Generalizations remain probabilistic and revisable.
    """
    
    # Identity
    generalization_identity: str          # Unique identifier for this generalization
    
    # Supporting patterns (references to PatternCandidates)
    supporting_patterns: Tuple[str, ...]  # IDs of patterns supporting this generalization
    
    # Resulting assertion
    resulting_assertion: str              # The generalized rule statement
    assertion_kind: str = "universal"     # e.g., "universal", "probabilistic"
    
    # Confidence and uncertainty
    confidence: float = 0.5               # Confidence in the generalization (0-1)
    uncertainty: float = 0.5              # Uncertainty about the generalization
    
    # Quality metrics
    support_count: int = 0                # Number of supporting observations
    coverage_ratio: float = 0.0           # Proportion of data covered
    
    # Exceptions and limitations
    known_exceptions: Tuple[str, ...] = ()  # Known cases where rule doesn't apply
    exception_count: int = 0              # Count of observed exceptions
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    derivation_method: str = "default"     # How was this derived?
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def is_strong_generalization(self) -> bool:
        """Check if this is a strong generalization."""
        return (
            self.confidence >= 0.8 and
            self.coverage_ratio >= 0.7 and
            self.exception_count <= max(1, int(self.support_count * 0.1))
        )
    
    @property
    def effective_confidence(self) -> float:
        """
        Calculate effective confidence considering exceptions.
        
        Exceptions reduce the effective strength of a generalization.
        """
        base = self.confidence
        
        # Penalty for exceptions (more exceptions = lower confidence)
        exception_penalty = min(0.3, self.exception_count / max(1, self.support_count) * 0.3)
        
        return max(0.0, min(1.0, base - exception_penalty))


@dataclass(frozen=True)
class GeneralizationPipeline:
    """
    Pipeline from patterns to generalizations.
    
    A pipeline records:
        - Participating patterns
        - Supporting statistics
        - Generated candidate assertions
        - Diagnostics
    
    The canonical pipeline is:
        Observations → Pattern Discovery → Statistical Evaluation → 
        Candidate Generalization → Validation → Candidate Assertion
    """
    
    # Identity
    pipeline_identity: str                # Unique identifier for this pipeline
    
    # Participating patterns (references)
    participating_patterns: Tuple[str, ...]
    
    # Supporting statistics
    supporting_statistics: Dict[str, Any] = field(default_factory=dict)
    
    # Generated generalizations
    candidate_assertions: Tuple[Generalization, ...]
    
    # Diagnostics
    pipeline_steps_completed: int = 0     # Steps completed in pipeline
    total_pipeline_steps: int = 5         # Total expected steps
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class GeneralizationRefinement:
    """
    Refinement of an existing generalization.
    
    Generalizations evolve through:
        - New observations
        - Additional evidence
        - Contradictory evidence
        - Better sampling
        - Improved models
    
    Identity remains stable across refinements.
    """
    
    # Identity (stable across refinements)
    refinement_identity: str              # Unique identifier for this refinement
    base_generalization_id: str           # ID of the generalization being refined
    
    # Previous version
    previous_assertion: str               # The assertion before refinement
    
    # Refined version
    refined_assertion: str                # The new assertion after refinement
    
    # Changes made
    supporting_changes: Tuple[str, ...]   # IDs of changes that triggered refinement
    
    # Confidence tracking
    previous_confidence: float = 0.5
    refined_confidence: float = 0.5
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    reason_for_refinement: str = "new_evidence"
    provenance: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class GeneralizationCandidate:
    """
    A candidate generalization awaiting validation.
    
    This is the output of the generalization phase before
    validation determines if it becomes accepted knowledge.
    """
    
    # Identity
    candidate_identity: str               # Unique identifier
    
    # Generalization details
    pattern_references: Tuple[str, ...]   # Pattern IDs supporting this
    assertion_text: str                   # The proposed generalized statement
    
    # Quality metrics
    confidence_estimate: float = 0.5
    support_count: int = 0
    coverage_ratio: float = 0.0
    
    # Validation state
    validation_status: str = "pending"    # pending, validated, rejected
    validator_id: Optional[str] = None    # Who/what validated this?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)


__all__ = [
    "Generalization",
    "GeneralizationPipeline",
    "GeneralizationRefinement",
    "GeneralizationCandidate",
]