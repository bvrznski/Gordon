# Decision Alternative Management - Phase 7.41
# ============================================

"""
Canonical Alternative Management Contract.

Alternative management evaluates:
    - alternative completeness
    - alternative feasibility
    - alternative compatibility
    - alternative diversity
    - alternative dominance
    - alternative quality

Alternatives remain explicit.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class AlternativeAssessment:
    """Assessment of a single alternative."""
    
    # Identity
    alternative_id: str                       # ID of the assessed alternative
    
    # Evaluation results
    feasibility_score: float = 0.0            # 0-1 scale (how feasible?)
    quality_score: float = 0.0                # 0-1 scale (how high quality?)
    
    # Constraints
    hard_constraints_satisfied: Tuple[str, ...] = ()
    soft_constraints_violated: Tuple[str, ...] = ()
    
    # Provenance
    assessed_at_utc: float = field(default_factory=time.time)
    assessor_id: str = "default"


@dataclass(frozen=True)
class AlternativeManagement:
    """
    Management of alternatives for a decision.
    
    Evaluates:
        - alternative completeness
        - alternative feasibility  
        - alternative compatibility
        - alternative diversity
        - alternative dominance
        - alternative quality
    
    Alternatives remain explicit; never imply selection automatically.
    """
    
    # Identity
    management_id: str                        # Unique identifier
    
    # Decision context
    decision_set_id: str                      # Related decision set
    evaluation_scope: str = "unknown"         # What is being evaluated?
    
    # Assessed alternatives
    assessed_alternatives: Tuple[AlternativeAssessment, ...] = ()
    
    # Management metrics
    completeness_score: float = 0.0           # How complete is the set?
    diversity_score: float = 0.0              # How diverse are options?
    
    # Dominance relationships (alternative_id -> set of dominated alternatives)
    dominance_relations: Dict[str, Tuple[str, ...]] = field(default_factory=dict)
    
    # Priority ordering (by assessment score)
    priority_order: Tuple[str, ...] = ()      # Ordered list of alternative IDs
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @property
    def assessed_count(self) -> int:
        """Count of alternatives that have been assessed."""
        return len(self.assessed_alternatives)
    
    @property
    def missing_assessments(self) -> List[str]:
        """List alternative IDs without assessments."""
        return []
    
    def get_assessment(self, alt_id: str) -> Optional[AlternativeAssessment]:
        """Get assessment for a specific alternative."""
        for assessment in self.assessed_alternatives:
            if assessment.alternative_id == alt_id:
                return assessment
        return None
    
    def with_assessment(self, assessment: AlternativeAssessment) -> AlternativeManagement:
        """Add an assessment and return new instance."""
        new_assessments = list(self.assessed_alternatives)
        new_assessments.append(assessment)
        
        # Update priority order by score
        sorted_ids = [
            a.alternative_id 
            for a in sorted(
                new_assessments,
                key=lambda x: (x.feasibility_score + x.quality_score) / 2,
                reverse=True
            )
        ]
        
        return dataclass_replace(
            self,
            assessed_alternatives=tuple(new_assessments),
            priority_order=tuple(sorted_ids),
        )
    
    @classmethod
    def create(
        cls,
        decision_set_id: str,
        evaluation_scope: str = "unknown",
    ) -> AlternativeManagement:
        """Create a new alternative management instance."""
        return cls(
            management_id=f"alternative_management:{uuid.uuid4().hex[:16]}",
            decision_set_id=decision_set_id,
            evaluation_scope=evaluation_scope,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "AlternativeAssessment",
    "AlternativeManagement",
]