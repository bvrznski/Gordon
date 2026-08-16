# Evolution Domain - Governance Subsystem

"""
Evolution: Architectural change evaluation for Memory.

The evolution domain:
    
    - Evaluates proposed architectural changes
    - Assesses compatibility with current architecture
    - Provides migration recommendations
    - Never deploys architectural changes
    
Evolution Laws:

    EVOLUTION-LAW-001: Evolution shall evaluate architectural change
    EVOLUTION-LAW-002: Evolution shall preserve backward compatibility analysis
    EVOLUTION-LAW-003: Evolution shall preserve ontology compatibility
    EVOLUTION-LAW-004: Evolution shall preserve migration evidence
    EVOLUTION-LAW-005: Evolution recommendations shall remain explicit
    EVOLUTION-LAW-006: Evolution shall never deploy architectural changes
    EVOLUTION-LAW-007: Evolution reports shall remain inspectable
    EVOLUTION-LAW-008: Evolution evaluation shall remain deterministic

Evolution Input:
    
    - Current architecture state
    - Proposed schema/changes
    - Compatibility analysis requirements

Evolution Output:
    
    - Evolution Report with compatibility assessment
    - Migration recommendation (immediate, staged, deferred)
    - Backward compatibility score
    
Anti-Patterns Rejected:
    
    - Direct architectural deployment
    - Hidden compatibility analysis
    - Non-deterministic evolution evaluation
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import time


# =============================================================================
# EVOLUTION COMPATIBILITY ASSESSMENT
# =============================================================================


@dataclass(frozen=True)
class CompatibilityAssessment:
    """
    Assessment of compatibility between architectures.
    
    Fields:
        compatibility_score: 0.0-1.0 score (higher = more compatible)
        
        semantic_compatibility:   Semantic layer compatibility
        structural_compatibility: Structural layer compatibility
        data_compatibility:       Data format compatibility
        
        breaking_changes: List of breaking changes identified
        non_breaking_changes: List of non-breaking changes identified
        
        recommended_action: "immediate", "staged", or "deferred"
    """
    
    compatibility_score: float = 1.0
    
    semantic_compatibility: float = 1.0
    structural_compatibility: float = 1.0
    data_compatibility: float = 1.0
    
    breaking_changes: Tuple[str, ...] = field(default_factory=tuple)
    non_breaking_changes: Tuple[str, ...] = field(default_factory=tuple)
    
    recommended_action: str = "immediate"  # immediate/staged/deferred
    
    @property
    def is_compatible(self) -> bool:
        """Check if architectures are compatible."""
        return self.compatibility_score >= 0.9
    
    @property
    def has_breaking_changes(self) -> bool:
        """Check if any breaking changes were found."""
        return len(self.breaking_changes) > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary representation."""
        return {
            "compatibility_score": self.compatibility_score,
            "semantic_compatibility": self.semantic_compatibility,
            "structural_compatibility": self.structural_compatibility,
            "data_compatibility": self.data_compatibility,
            "breaking_changes": list(self.breaking_changes),
            "non_breaking_changes": list(self.non_breaking_changes),
            "recommended_action": self.recommended_action,
        }


# =============================================================================
# EVOLUTION REPORT
# =============================================================================


@dataclass(frozen=True)
class EvolutionReport:
    """
    Report on architectural evolution assessment.
    
    Fields:
        report_id:          Unique identifier
        
        current_version:    Current architecture version
        proposed_version:   Proposed architecture version
        
        compatibility:      Compatibility assessment
        recommendations:    Suggested actions
        
        timestamp_utc:      When assessment was made
    """
    
    report_id: str                          # Unique identifier
    
    current_version: str                   # Current version identifier
    proposed_version: str                  # Proposed version identifier
    
    compatibility: CompatibilityAssessment
    
    recommendations: Tuple[str, ...] = field(default_factory=tuple)
    
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_evolution_ready(self) -> bool:
        """Check if evolution is recommended."""
        return self.compatibility.is_compatible and (
            self.compatibility.recommended_action in ("immediate", "staged")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary representation."""
        return {
            "report_id": self.report_id,
            "current_version": self.current_version,
            "proposed_version": self.proposed_version,
            "compatibility": self.compatibility.to_dict(),
            "recommendations": list(self.recommendations),
            "timestamp_utc": self.timestamp_utc,
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "CompatibilityAssessment",
    "EvolutionReport",
]