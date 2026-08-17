# Induction Refinement - Phase 7.2
# =================================

"""
Canonical Generalization Refinement Contract.

Generalizations evolve through new evidence and improved analysis.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class GeneralizationRefinement:
    """
    Refinement of a generalization.
    
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
    
    # Version history
    previous_version: int = 1             # Previous version number
    current_version: int = 2              # New version number
    
    # Changes made
    changed_assertion: bool = False       # Did the assertion change?
    changed_confidence: float = 0.0       # Change in confidence
    changed_coverage: float = 0.0         # Change in coverage ratio
    
    # Previous and refined values
    previous_assertion: str = ""
    refined_assertion: str = ""
    
    previous_confidence: float = 0.5
    refined_confidence: float = 0.5
    
    previous_coverage: float = 0.0
    refined_coverage: float = 0.0
    
    # Supporting changes
    new_supporting_observations: Tuple[str, ...] = ()  # IDs of new observations
    removed_observations: Tuple[str, ...] = ()         # IDs of removed observations
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    reason_for_refinement: str = "new_evidence"  # Why was this refined?
    provenance: Dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class PatternRefinement:
    """
    Refinement of a pattern.
    
    Patterns may be refined as more data becomes available.
    """
    
    refinement_identity: str
    base_pattern_id: str                  # ID of the original pattern
    
    # Version info
    previous_version: int = 1
    current_version: int = 2
    
    # Changes
    changed_description: bool = False     # Did description change?
    changed_support_measure: float = 0.0  # Change in support measure
    changed_confidence: float = 0.0       # Change in confidence
    
    # New values
    new_support_measure: float = 0.0
    new_confidence: float = 0.5
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    reason_for_refinement: str = "new_evidence"


@dataclass(frozen=True)
class HypothesisRefinement:
    """
    Refinement of an inductive hypothesis.
    
    Hypotheses may be refined as new evidence emerges.
    """
    
    refinement_identity: str
    base_hypothesis_id: str               # ID of original hypothesis
    
    # Version info
    previous_version: int = 1
    current_version: int = 2
    
    # Changes made
    changed_explanation: bool = False     # Did explanation change?
    changed_confidence: float = 0.0       # Change in confidence
    
    # New values
    refined_explanation: str = ""
    new_confidence: float = 0.5
    
    # Support changes
    added_patterns: Tuple[str, ...] = ()  # New supporting patterns
    removed_patterns: Tuple[str, ...] = ()  # Removed patterns
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    reason_for_refinement: str = "new_evidence"


@dataclass(frozen=True)
class RefinementTrace:
    """
    Trace of all refinements for a particular artifact.
    
    Allows full history reconstruction and audit.
    """
    
    trace_id: str                         # Unique trace identifier
    artifact_id: str                      # ID of the refined artifact
    
    # Refinement steps
    refinement_steps: Tuple[Dict[str, Any], ...] = ()  # Ordered list of refinements
    
    # Metadata
    initial_version: int = 1              # Starting version number
    current_version: int = 1              # Final version number
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @property
    def refinement_count(self) -> int:
        """Number of refinements in the trace."""
        return len(self.refinement_steps)
    
    def add_refinement(
        self,
        refinement_id: str,
        version_before: int,
        version_after: int,
        changes: Dict[str, Any],
    ) -> RefinementTrace:
        """Add a refinement step to the trace and return new trace."""
        new_step = {
            "refinement_id": refinement_id,
            "version_before": version_before,
            "version_after": version_after,
            "changes": changes,
            "timestamp_utc": time.time(),
        }
        
        return dataclass_replace(
            self,
            refinement_steps=self.refinement_steps + (new_step,),
            current_version=version_after,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "GeneralizationRefinement",
    "PatternRefinement",
    "HypothesisRefinement",
    "RefinementTrace",
]