# Strategic Governance - Phase 7.18
# ================================

"""
Canonical Strategic Governance for Phase 7.18.

Governance evaluates strategy quality, policy consistency, objective alignment,
trade-off validity, adaptation robustness, and diagnostics. It is purely observational.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto


@dataclass(frozen=True)
class StrategicGovernance:
    """
    Governance evaluation for a strategic reasoning session.
    
    Governance is purely observational - it never modifies strategic artifacts directly.
    It evaluates:
        - Strategy quality (coherence, completeness, feasibility)
        - Policy consistency (no conflicts with governing policies)
        - Objective alignment (supports mission and objectives)
        - Trade-off validity (trade-offs are justifiable)
        - Adaptation robustness (adapts to changes appropriately)
        - Diagnostics (identifies issues for review)
    """
    
    # Identity
    governance_id: str                      # Unique governance identifier
    
    # Evaluated sessions
    evaluated_sessions: List[str] = field(default_factory=list)  # session IDs
    
    # Findings from evaluation
    findings: List[Dict[str, Any]] = field(default_factory=list)
    
    # Violations detected (if any)
    violations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Recommendations for improvement
    recommendations: List[str] = field(default_factory=list)
    
    # Overall governance assessment
    governance_assessment: str = "compliant"  # compliant, warnings, violations
    
    # Timing
    evaluated_at_utc: float = field(default_factory=time.time)
    evaluator_identity: str = ""            # Who/what performed evaluation?


@dataclass(frozen=True)
class GovernanceFinding:
    """A finding from governance evaluation."""
    
    # Finding type
    finding_type: str                       # e.g., "policy_violation", "inconsistent_tradeoff"
    
    # Context
    context_id: str                         # Which session/strategy?
    
    # Description
    description: str                        # What was found?
    
    # Severity (0-1, higher = more severe)
    severity: float = 0.0
    
    # Timing
    discovered_at_utc: float = field(default_factory=time.time)


@dataclass(frozen=True)
class GovernanceReport:
    """
    Complete governance report for a strategic session.
    """
    
    # Identity
    report_id: str
    
    # Evaluated strategy
    strategy_identity: str
    
    # Evaluation history
    evaluations: List[StrategicGovernance]
    
    # Current status
    current_status: str = "healthy"         # healthy, warning, critical
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    last_evaluation_at_utc: Optional[float] = None


__all__ = [
    "StrategicGovernance",
    "GovernanceFinding",
    "GovernanceReport",
]