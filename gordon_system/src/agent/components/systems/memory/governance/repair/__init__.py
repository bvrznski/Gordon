# Repair Domain - Governance Subsystem

"""
Repair: Restoration strategy proposal for Memory.

The repair domain:
    
    - Evaluates how memory may be restored after corruption
    - Proposes corrective actions (never executes them)
    - Provides supporting evidence for proposals
    - Preserves provenance of repair strategies
    
Repair Laws:

    REPAIR-LAW-001: Repair shall propose corrective actions only
    REPAIR-LAW-002: Repair shall never execute Memory changes
    REPAIR-LAW-003: Repair proposals shall preserve supporting evidence
    REPAIR-LAW-004: Repair shall preserve provenance
    REPAIR-LAW-005: Repair confidence shall remain explicit
    REPAIR-LAW-006: Repair recommendations shall remain explainable
    REPAIR-LAW-007: Repair proposals shall remain observable
    REPAIR-LAW-008: Repair evaluation shall remain deterministic

Repair Input:
    
    - Integrity failures detected
    - Diagnostics information
    - History of previous repairs
    - Policies for repair strategies

Repair Output:
    
    - Repair Proposal (what needs to be fixed)
    - Repair Priority (order of execution)
    - Confidence score (0.0-1.0)
    - Supporting evidence
    
Anti-Patterns Rejected:
    
    - Direct memory modification
    - Silent repairs without evidence
    - Non-deterministic repair proposals
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import time


# =============================================================================
# REPAIR PROPOSAL - Suggested restoration strategy
# =============================================================================


@dataclass(frozen=True)
class RepairProposal:
    """
    A proposed repair strategy for memory corruption.
    
    Proposals are advisory only - they must be approved and executed externally.
    
    Fields:
        proposal_id:     Unique identifier for this proposal
        violation_id:    ID of the violation being repaired
        description:     What needs to be fixed
        strategy:        How to fix it (detailed steps)
        
        confidence:      0.0-1.0 confidence in this repair
        priority:        Order of execution (lower = higher priority)
        
        evidence:        Supporting evidence for the proposal
        estimated_impact: What artifacts will be affected
        
        timestamp_utc:   When proposal was created
    """
    
    proposal_id: str                        # Unique identifier
    
    violation_id: str                       # ID of violation being repaired
    description: str                       # What needs to be fixed
    strategy: str                          # How to fix it (detailed)
    
    confidence: float                      # 0.0-1.0 confidence score
    priority: int = 100                    # Order of execution (lower = higher)
    
    evidence: Any = None                   # Supporting evidence
    estimated_impact: Tuple[str, ...] = field(default_factory=tuple)  # Affected artifact IDs
    
    timestamp_utc: float = field(default_factory=time.time)
    
    @property
    def is_high_priority(self) -> bool:
        """Check if this proposal is high priority."""
        return self.priority < 50
    
    @property
    def is_confident(self) -> bool:
        """Check if this proposal has sufficient confidence."""
        return self.confidence >= 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert proposal to dictionary representation."""
        return {
            "proposal_id": self.proposal_id,
            "violation_id": self.violation_id,
            "description": self.description,
            "strategy": self.strategy,
            "confidence": self.confidence,
            "priority": self.priority,
            "estimated_impact": list(self.estimated_impact),
            "timestamp_utc": self.timestamp_utc,
        }


# =============================================================================
# REPAIR PROPOSAL SET - Collection of repair proposals
# =============================================================================


@dataclass(frozen=True)
class RepairProposalSet:
    """
    A set of repair proposals for a single evaluation cycle.
    
    Fields:
        proposal_set_id: Unique identifier
        proposals: All proposed repairs
        total_priority_score: Sum of all priorities (lower = better)
        
    Properties:
        high_priority_count: Number of high-priority proposals
        average_confidence: Mean confidence across all proposals
    """
    
    proposal_set_id: str                    # Unique identifier
    proposals: Tuple[RepairProposal, ...]  # All proposed repairs
    
    @property
    def total_priority_score(self) -> int:
        """Get sum of all priorities."""
        return sum(p.priority for p in self.proposals)
    
    @property
    def high_priority_count(self) -> int:
        """Get count of high-priority proposals."""
        return sum(1 for p in self.proposals if p.is_high_priority)
    
    @property
    def average_confidence(self) -> float:
        """Get mean confidence score across all proposals."""
        if not self.proposals:
            return 0.0
        return sum(p.confidence for p in self.proposals) / len(self.proposals)
    
    @property
    def proposal_count(self) -> int:
        """Get total number of proposals."""
        return len(self.proposals)
    
    def get_proposals_by_priority(
        self,
        max_priority: int = 100,
    ) -> Tuple[RepairProposal, ...]:
        """Get proposals with priority below threshold."""
        return tuple(p for p in self.proposals if p.priority <= max_priority)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert proposal set to dictionary representation."""
        return {
            "proposal_set_id": self.proposal_set_id,
            "proposal_count": len(self.proposals),
            "high_priority_count": self.high_priority_count,
            "average_confidence": self.average_confidence,
            "total_priority_score": self.total_priority_score,
            "proposals": [p.to_dict() for p in self.proposals],
        }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "RepairProposal",
    "RepairProposalSet",
]