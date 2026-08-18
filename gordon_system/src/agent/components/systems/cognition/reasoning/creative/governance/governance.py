# Creative Governance - Phase 7.33
# ================================

"""
Canonical Creative Governance.

Creative Governance evaluates:
- Novelty quality
- Coherence quality  
- Usefulness quality
- Exploration diversity
- Creative robustness
- Diagnostics

Governance remains observational only.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class CreativeGovernance:
    """
    Observational governance for creative reasoning.
    
    A governance evaluation includes:
        - Evaluated sessions
        - Governance findings
        - Violation detection
        - Recommendations
    
    Governance never modifies creative artifacts directly.
    """
    
    # Identity
    governance_id: str                      # Unique governance identifier
    semantic_identity: str                  # Semantic identity
    
    # Evaluated sessions
    evaluated_session_ids: List[str] = field(default_factory=list)
    
    # Findings (list of finding dictionaries)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    
    # Violations detected
    violations: List[str] = field(default_factory=list)  # Description of each violation
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    
    # Metrics (0-1 scale for quality dimensions)
    novelty_quality_score: float = 0.0
    coherence_quality_score: float = 0.0
    usefulness_quality_score: float = 0.0
    exploration_diversity_score: float = 0.0
    
    # Metadata
    evaluated_at_utc: float = field(default_factory=time.time)
    
    @property
    def is_clean(self) -> bool:
        """Check if no violations detected."""
        return len(self.violations) == 0
    
    @classmethod
    def create(
        cls,
        semantic_identity: str,
    ) -> CreativeGovernance:
        """Create a new governance instance."""
        return cls(
            governance_id=f"governance:{uuid.uuid4().hex[:16]}",
            semantic_identity=semantic_identity,
            evaluated_at_utc=time.time(),
        )
    
    def with_novelty_quality(self, score: float) -> CreativeGovernance:
        """Return a copy with updated novelty quality score."""
        return dataclass_replace(
            self,
            novelty_quality_score=max(0.0, min(1.0, score)),
        )
    
    def with_coherence_quality(self, score: float) -> CreativeGovernance:
        """Return a copy with updated coherence quality score."""
        return dataclass_replace(
            self,
            coherence_quality_score=max(0.0, min(1.0, score)),
        )
    
    def with_usefulness_quality(self, score: float) -> CreativeGovernance:
        """Return a copy with updated usefulness quality score."""
        return dataclass_replace(
            self,
            usefulness_quality_score=max(0.0, min(1.0, score)),
        )
    
    def with_exploration_diversity(self, score: float) -> CreativeGovernance:
        """Return a copy with updated exploration diversity score."""
        return dataclass_replace(
            self,
            exploration_diversity_score=max(0.0, min(1.0, score)),
        )
    
    def add_finding(self, finding_type: str, details: Dict[str, Any]) -> CreativeGovernance:
        """Add a governance finding."""
        finding = {
            "finding_id": f"finding:{uuid.uuid4().hex[:8]}",
            "finding_type": finding_type,
            "timestamp_utc": time.time(),
            **details,
        }
        return dataclass_replace(
            self,
            findings=list(self.findings) + [finding],
        )
    
    def add_violation(self, violation: str) -> CreativeGovernance:
        """Add a detected violation."""
        return dataclass_replace(
            self,
            violations=list(self.violations) + [violation],
        )
    
    def add_recommendation(self, recommendation: str) -> CreativeGovernance:
        """Add a governance recommendation."""
        return dataclass_replace(
            self,
            recommendations=list(self.recommendations) + [recommendation],
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    # For Python 3.12+, use dataclasses.replace
    # This is a simple implementation for compatibility
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "CreativeGovernance",
]