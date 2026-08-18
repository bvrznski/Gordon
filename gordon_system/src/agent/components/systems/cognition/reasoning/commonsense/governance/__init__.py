# Commonsense Governance - Phase 7.45
# ====================================

"""
Governance contracts for Commonsense Reasoning.

Governance evaluates:
- Assumption quality
- Affordance quality
- Plausibility quality
- Commonsense consistency
- Diagnostics

Governance remains observational and never modifies artifacts directly.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


# =============================================================================
# GOVERNANCE EVALUATION
# =============================================================================

@dataclass(frozen=True)
class GovernanceEvaluation:
    """
    Evaluation of commonsense artifacts.
    
    Each evaluation includes:
        - What was evaluated
        - Whether it passed governance
        - Detailed findings
    """
    
    evaluation_id: str                        # Unique identifier
    evaluated_item_type: str                  # e.g., "assumption", "affordance"
    evaluated_item_id: str                    # ID of the item being evaluated
    
    passed: bool                              # Did it pass governance?
    issues_found: List[str] = field(default_factory=list)  # Any issues found?
    
    @classmethod
    def create(
        cls,
        evaluated_item_type: str,
        evaluated_item_id: str,
        passed: bool,
        issues_found: Optional[List[str]] = None,
    ) -> GovernanceEvaluation:
        """Create a new governance evaluation."""
        return cls(
            evaluation_id=f"governance_evaluation:{uuid.uuid4().hex[:16]}",
            evaluated_item_type=evaluated_item_type,
            evaluated_item_id=evaluated_item_id,
            passed=passed,
            issues_found=issues_found or [],
        )


# =============================================================================
# GOVERNANCE FINDINGS
# =============================================================================

@dataclass(frozen=True)
class GovernanceFindings:
    """
    Complete set of governance findings.
    
    Findings include:
        - All evaluation results
        - Summary statistics
        - Recommendations (if any issues found)
    """
    
    # Identity
    findings_id: str                          # Unique findings identifier
    
    # Results
    evaluations: Tuple[GovernanceEvaluation, ...] = field(default_factory=tuple)
    
    # Statistics
    total_evaluations: int = 0
    passed_evaluations: int = 0
    failed_evaluations: int = 0
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)  # How to improve?
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        evaluations: Tuple[GovernanceEvaluation, ...],
        recommendations: Optional[List[str]] = None,
    ) -> GovernanceFindings:
        """Create new governance findings."""
        total = len(evaluations)
        passed = sum(1 for e in evaluations if e.passed)
        return cls(
            findings_id=f"governance_findings:{uuid.uuid4().hex[:16]}",
            evaluations=evaluations,
            total_evaluations=total,
            passed_evaluations=passed,
            failed_evaluations=total - passed,
            recommendations=recommendations or [],
        )
    
    @property
    def is_governance_valid(self) -> bool:
        """Check if all evaluations passed."""
        return self.failed_evaluations == 0


# =============================================================================
# GOVERNANCE CONTRACT
# =============================================================================

@dataclass(frozen=True)
class CommonsenseGovernance:
    """
    Governance contract for commonsense reasoning.
    
    Governance remains observational and never modifies artifacts directly.
    """
    
    # Identity
    governance_id: str                        # Unique governance identifier
    
    # Governance data
    governed_sessions: Tuple[str, ...] = field(default_factory=tuple)  # Session IDs
    governance_type: str                      # Type of governance performed
    
    # Results
    findings: GovernanceFindings              # Complete set of findings
    
    # Provenance
    created_at_utc: float = field(default_factory=time.time)
    
    @classmethod
    def create(
        cls,
        governed_sessions: Tuple[str, ...],
        governance_type: str,
        findings: GovernanceFindings,
    ) -> CommonsenseGovernance:
        """Create a new commonsense governance."""
        return cls(
            governance_id=f"commonsense_governance:{uuid.uuid4().hex[:16]}",
            governed_sessions=governed_sessions,
            governance_type=governance_type,
            findings=findings,
        )


__all__ = [
    "GovernanceEvaluation",
    "GovernanceFindings",
    "CommonsenseGovernance",
]