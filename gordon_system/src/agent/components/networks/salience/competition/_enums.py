# Salience Network Competition Enums
# ===================================

"""
Canonical enumeration types for competition (Phase 4.8.6).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto


class DominanceRelation(Enum):
    """
    Canonical dominance relationship between candidates.
    
    DOMINANCE INVARIANTS:
        - COMPETITION-DOMINANCE-INV-001: Exactly one relation per comparison
        - COMPETITION-DOMINANCE-INV-002: DOMINATED_BY is inverse of DOMINATES
        - COMPETITION-DOMINANCE-INV-003: EQUIVALENT is symmetric
    """
    
    DOMINATES = "dominates"
    """Candidate A is clearly more salient than Candidate B."""
    
    DOMINATED_BY = "dominated_by"
    """Candidate A is less salient than Candidate B (inverse of DOMINATES)."""
    
    EQUIVALENT = "equivalent"
    """Candidates have equal semantic priority evidence."""
    
    INCOMPARABLE = "incomparable"
    """Candidates cannot be compared due to incompatible semantics."""
    
    UNKNOWN = "unknown"
    """Insufficient information to determine relationship."""


class InhibitionStrength(Enum):
    """
    Canonical inhibition strength levels.
    
    INHIBITION INVARIANTS:
        - COMPETITION-INHIBITION-INV-001: Strengths form a total order
        - COMPETITION-INHIBITION-INV-002: UNKNOWN is weakest (no effect)
    """
    
    UNKNOWN = "unknown"
    """Inhibition relationship unknown or not evaluated."""
    
    SOFT = "soft"
    """Weak inhibition; priority may still be given to inhibited candidate."""
    
    MODERATE = "moderate"
    """Medium inhibition; inhibited candidate should be deprioritized."""
    
    STRONG = "strong"
    """Strong inhibition; inhibited candidate should rarely receive attention."""


class FacilitationStrength(Enum):
    """
    Canonical facilitation strength levels.
    
    FACILITATION INVARIANTS:
        - COMPETITION-FACILITATION-INV-001: Strengths form a total order
        - COMPETITION-FACILITATION-INV-002: UNKNOWN is weakest (no effect)
    """
    
    UNKNOWN = "unknown"
    """Facilitation relationship unknown or not evaluated."""
    
    WEAK = "weak"
    """Minor facilitation; slight priority boost."""
    
    MODERATE = "moderate"
    """Medium facilitation; meaningful priority boost."""
    
    STRONG = "strong"
    """Strong facilitation; significant priority boost when both present."""


class StabilityKind(Enum):
    """
    Canonical stability classifications for rankings.
    
    STABILITY INVARIANTS:
        - COMPETITION-STABILITY-INV-001: Stability is about recommendation behavior
        - COMPETITION-STABILITY-INV-002: Does not imply memory permanence
    """
    
    UNKNOWN = "unknown"
    """Stability cannot be determined (e.g., no previous state)."""
    
    VOLATILE = "volatile"
    """Rankings change frequently; candidates exchange priority."""
    
    TRANSIENT = "transient"
    """Rankings stable for short period but expected to change."""
    
    STABLE = "stable"
    """Rankings remain consistent across evaluations."""
    
    PERSISTENT = "persistent"
    """Rankings highly stable over many evaluation cycles."""


class PersistenceKind(Enum):
    """
    Canonical persistence classifications for candidates.
    
    PERSISTENCE INVARIANTS:
        - COMPETITION-PERSISTENCE-INV-001: Describes repeated relevance
        - COMPETITION-PERSISTENCE-INV-002: Independent from memory permanence
    """
    
    UNKNOWN = "unknown"
    """Persistence cannot be determined."""
    
    TRANSIENT = "transient"
    """Candidate is important only in immediate context."""
    
    SHORT_LIVED = "short_lived"
    """Candidate remains relevant for moderate duration."""
    
    LONG_LIVED = "long_lived"
    """Candidate maintains relevance across many evaluations."""
    
    PERSISTENT = "persistent"
    """Candidate consistently maintains semantic priority."""


class RecommendationLevel(Enum):
    """
    Canonical attention recommendation levels.
    
    RECOMMENDATION INVARIANTS:
        - COMPETITION-RECOMMENDATION-INV-001: Advisory only (not allocation)
        - COMPETITION-RECOMMENDATION-INV-002: Does not trigger downstream actions
    """
    
    BACKGROUND = "background"
    """Background level; low priority for attention."""
    
    LOW = "low"
    """Minimal priority recommendation."""
    
    MODERATE = "moderate"
    """Medium priority recommendation."""
    
    HIGH = "high"
    """High priority recommendation."""
    
    CRITICAL = "critical"
    """Highest priority recommendation."""


class TraceCode(Enum):
    """
    Canonical trace codes for competition operations.
    
    TRACE INVARIANTS:
        - COMPETITION-TRACE-INV-001: Each code identifies operation type
        - COMPETITION-TRACE-INV-002: Codes enable structural traceability
    """
    
    COMPARISON = "COMPARISON"
    """Pairwise comparison of candidates."""
    
    DOMINANCE = "DOMINANCE"
    """Dominance relationship evaluation."""
    
    INHIBITION = "INHIBITION"
    """Inhibition relationship evaluation."""
    
    FACILITATION = "FACILITATION"
    """Facilitation relationship evaluation."""
    
    RANKING = "RANKING"
    """Candidate ranking operation."""
    
    STABILITY = "STABILITY"
    """Stability estimation."""
    
    HYSTERESIS = "HYSTERESIS"
    """Hysteresis policy application."""
    
    RECOMMENDATION = "RECOMMENDATION"
    """Recommendation generation."""
    
    GRAPH_VALIDATION = "GRAPH_VALIDATION"
    """Competition graph validation."""


class GraphEdgeType(Enum):
    """
    Canonical edge types for competition graphs.
    
    GRAPH-EDGE INVARIANTS:
        - COMPETITION-GRAPH-EDGE-INV-001: Each edge has exactly one type
        - COMPETITION-GRAPH-EDGE-INV-002: Edges connect exactly two nodes
    """
    
    DOMINATES = "dominates"
    """Dominance relationship."""
    
    INHIBITS = "inhibits"
    """Inhibition relationship."""
    
    FACILITATES = "facilitates"
    """Facilitation relationship."""
    
    EQUIVALENT = "equivalent"
    """Equivalence relationship."""
    
    CONFLICTS = "conflicts"
    """Conflicting priority relationships."""


@dataclass(frozen=True)
class SalienceLevel:
    """
    Canonical qualitative salience level.
    
    Represents the semantic intensity of a salience assessment.
    """
    
    UNKNOWN = "unknown"
    NEGLIGIBLE = "negligible"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def from_value(cls, value: str) -> SalienceLevel:
        """Convert string to SalienceLevel."""
        mapping = {
            "unknown": cls.UNKNOWN,
            "negligible": cls.NEGLIGIBLE,
            "low": cls.LOW,
            "moderate": cls.MODERATE,
            "high": cls.HIGH,
            "critical": cls.CRITICAL,
        }
        if value not in mapping:
            raise ValueError(f"Unknown SalienceLevel value: {value}")
        return mapping[value]

    def is_valid(self) -> bool:
        """Check if this level represents valid evaluation output."""
        return self != self.UNKNOWN

    @property
    def intensity_rank(self) -> int:
        """Return numeric rank for comparison (higher = more intense)."""
        ranks = {
            SalienceLevel.UNKNOWN: 0,
            SalienceLevel.NEGLIGIBLE: 1,
            SalienceLevel.LOW: 2,
            SalienceLevel.MODERATE: 3,
            SalienceLevel.HIGH: 4,
            SalienceLevel.CRITICAL: 5,
        }
        return ranks[self]