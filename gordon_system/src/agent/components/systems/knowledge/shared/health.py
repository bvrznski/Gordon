# Knowledge Health - Phase 5.4
# ============================

"""
Knowledge Health: Metrics for assessing the quality of knowledge artifacts.

Health metrics provide insight into the integrity, completeness, and reliability
of Gordon's semantic knowledge base.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import time
import uuid


# =============================================================================
# HEALTH METRICS - Semantic health assessment
# =============================================================================


@dataclass(frozen=True)
class KnowledgeHealthMetrics:
    """
    Health metrics for Gordon's knowledge system.
    
    Provides comprehensive metrics about the state of semantic artifacts.
    
    Fields:
        health_identity:       Unique identifier for this health record
        timestamp_utc:         When these metrics were captured
        total_concepts:        Number of concepts in the system
        total_beliefs:         Number of beliefs in the system
        total_assertions:      Number of assertions in the system
        total_relations:       Number of relations in the system
        conflict_count:        Number of conflicting beliefs
        orphans_count:         Number of orphaned concepts (no parents, no children)
        revision_depth_mean:   Mean revision depth across artifacts
        average_confidence:    Average semantic confidence
        average_uncertainty:   Average semantic uncertainty
        validation_rate:       Fraction of artifacts passing validation
    """
    
    # Identity and metadata (required)
    health_identity: str              # Unique ID for this health record
    
    timestamp_utc: float              # When metrics were captured
    
    # Counts
    total_concepts: int = 0
    total_beliefs: int = 0
    total_assertions: int = 0
    total_relations: int = 0
    
    # Quality metrics
    conflict_count: int = 0
    orphans_count: int = 0
    revision_depth_mean: float = 1.0
    average_confidence: float = 0.5
    average_uncertainty: float = 0.5
    validation_rate: float = 1.0
    
    @property
    def is_healthy(self) -> bool:
        """Check if knowledge system is in healthy state."""
        return (
            self.validation_rate >= 0.8 and
            self.conflict_count < self.total_beliefs * 0.2
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary for serialization."""
        return {
            "health_identity": self.health_identity,
            "timestamp_utc": self.timestamp_utc,
            "total_concepts": self.total_concepts,
            "total_beliefs": self.total_beliefs,
            "total_assertions": self.total_assertions,
            "total_relations": self.total_relations,
            "conflict_count": self.conflict_count,
            "orphans_count": self.orphans_count,
            "revision_depth_mean": self.revision_depth_mean,
            "average_confidence": self.average_confidence,
            "average_uncertainty": self.average_uncertainty,
            "validation_rate": self.validation_rate,
        }


# =============================================================================
# HEALTH INSPECTOR
# =============================================================================


class KnowledgeHealthInspector:
    """
    Inspects the health of Gordon's knowledge system.
    
    Provides diagnostic services for evaluating semantic artifact integrity.
    """
    
    def __init__(
        self,
        minimum_validation_rate: float = 0.8,
        maximum_conflict_ratio: float = 0.2,
    ):
        """
        Initialize the inspector.
        
        Args:
            minimum_validation_rate: Minimum acceptable validation rate
            maximum_conflict_ratio: Maximum ratio of conflicting beliefs
        """
        self._minimum_validation_rate = minimum_validation_rate
        self._maximum_conflict_ratio = maximum_conflict_ratio
    
    def inspect(
        self,
        concepts_count: int,
        beliefs_count: int,
        assertions_count: int,
        relations_count: int,
        conflicts_count: int,
        orphans_count: int,
        validation_rate: float,
    ) -> KnowledgeHealthMetrics:
        """
        Inspect the health of the knowledge system.
        
        Args:
            concepts_count: Total number of concepts
            beliefs_count: Total number of beliefs
            assertions_count: Total number of assertions
            relations_count: Total number of relations
            conflicts_count: Number of conflicting beliefs
            orphans_count: Number of orphaned concepts
            validation_rate: Fraction passing validation
            
        Returns:
            Health metrics record
        """
        return KnowledgeHealthMetrics(
            health_identity=f"health:{uuid.uuid4().hex[:16]}",
            timestamp_utc=time.time(),
            total_concepts=concepts_count,
            total_beliefs=beliefs_count,
            total_assertions=assertions_count,
            total_relations=relations_count,
            conflict_count=conflicts_count,
            orphans_count=orphans_count,
            revision_depth_mean=1.5,  # Simplified
            average_confidence=0.6,   # Simplified
            average_uncertainty=0.4,  # Simplified
            validation_rate=validation_rate,
        )
    
    def evaluate(
        self,
        metrics: KnowledgeHealthMetrics,
    ) -> Tuple[bool, List[str]]:
        """
        Evaluate health metrics and return issues.
        
        Args:
            metrics: Health metrics to evaluate
            
        Returns:
            (is_healthy, list_of_issues)
        """
        issues = []
        
        if metrics.validation_rate < self._minimum_validation_rate:
            issues.append(
                f"Validation rate below threshold: {metrics.validation_rate:.2f} "
                f"< {self._minimum_validation_rate}"
            )
        
        if metrics.total_beliefs > 0:
            conflict_ratio = metrics.conflict_count / metrics.total_beliefs
            if conflict_ratio > self._maximum_conflict_ratio:
                issues.append(
                    f"Conflict ratio above threshold: {conflict_ratio:.2f} "
                    f"> {self._maximum_conflict_ratio}"
                )
        
        return len(issues) == 0, issues


__all__ = [
    "KnowledgeHealthMetrics",
    "KnowledgeHealthInspector",
]