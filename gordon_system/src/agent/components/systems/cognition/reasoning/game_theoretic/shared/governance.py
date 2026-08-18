# Game Governance - Phase 7.43
# ==========================

"""
Canonical Game Governance definitions.

Governance evaluates and never modifies artifacts directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class GovernanceFindings:
    """Findings from governance evaluation."""
    
    finding_id: str                         # Unique identifier
    
    category: str                           # Category (e.g., "equilibrium", "payoff")
    severity: str = "info"                  # info, warning, error
    description: str = ""                   # What was found?
    recommendation: str = ""                # What should be done?


@dataclass(frozen=True)
class GameGovernance:
    """
    Governance of game-theoretic reasoning.
    
    Governance is observational and never modifies artifacts directly.
    """
    
    # Identity
    governance_identity: str                # Unique identifier
    
    # Sessions evaluated
    evaluated_sessions: Tuple[str, ...] = ()  # Session IDs evaluated
    
    # Findings
    findings: Tuple[GovernanceFindings, ...] = ()  # All findings
    
    # Violations
    violations: Tuple[str, ...] = ()        # Any violations detected?
    
    # Recommendations
    recommendations: Tuple[str, ...] = ()   # General recommendations
    
    # Metadata
    created_at_utc: float = field(default_factory=time.time)
    
    # Provenance
    source_session_id: Optional[str] = None
    
    @classmethod
    def create(
        cls,
        evaluated_sessions: List[str],
        source_session_id: Optional[str] = None,
    ) -> GameGovernance:
        """Create a new game governance."""
        return cls(
            governance_identity=f"governance:{uuid.uuid4().hex[:16]}",
            evaluated_sessions=tuple(evaluated_sessions),
            source_session_id=source_session_id,
        )
    
    def add_finding(self, finding: GovernanceFindings) -> GameGovernance:
        """Add a governance finding."""
        return dataclass_replace(
            self,
            findings=self.findings + (finding,),
            recommendations=self.recommendations + (finding.recommendation,) if finding.recommendation else self.recommendations,
        )


__all__ = [
    "GovernanceFindings",
    "GameGovernance",
]
