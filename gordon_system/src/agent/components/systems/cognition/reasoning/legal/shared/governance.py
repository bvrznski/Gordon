# Legal Governance - Phase 7.47 Part 1
# =====================================

"""
Governance Contract.

Legal governance evaluates:
    - interpretation quality
    - source completeness
    - compliance quality
    - jurisdiction correctness
    - legal consistency
    - diagnostics

Governance remains observational.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class GovernanceEvaluation:
    """
    Governance evaluation for a legal reasoning process.
    
    A governance evaluation includes:
        - Components evaluated
        - Findings (quality issues or confirmations)
        - Recommendations
        - Diagnostics
    
    Governance remains observational and never modifies artifacts directly.
    """
    
    # Identity
    evaluation_id: str                        # Unique identifier
    
    # Input
    target_type: str                          # e.g., "session", "interpretation"
    target_id: str                            # ID of component being evaluated
    
    # Evaluation criteria
    criteria_performed: Tuple[str, ...] = ()  # Which criteria were checked?
    
    # Findings
    passed_criteria: Tuple[Dict[str, Any], ...] = ()
    failed_criteria: Tuple[Dict[str, Any], ...] = ()
    warnings: Tuple[Dict[str, Any], ...] = ()
    recommendations: Tuple[Dict[str, Any], ...] = ()
    
    # Overall result
    governance_status: Optional[str] = None   # e.g., "good", "needs_attention"
    
    # Diagnostics
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    started_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        target_type: str,
        target_id: str,
    ) -> GovernanceEvaluation:
        """Create a new governance evaluation."""
        return cls(
            evaluation_id=f"governance:{uuid.uuid4().hex[:16]}",
            target_type=target_type,
            target_id=target_id,
            criteria_performed=(),
        )
    
    def with_passed_criteria(self, criteria: List[Dict[str, Any]]) -> GovernanceEvaluation:
        """Add passed criteria to evaluation."""
        return dataclass_replace(
            self,
            passed_criteria=self.passed_criteria + tuple(criteria),
        )
    
    def with_failed_criteria(self, criteria: List[Dict[str, Any]]) -> GovernanceEvaluation:
        """Add failed criteria to evaluation."""
        return dataclass_replace(
            self,
            failed_criteria=self.failed_criteria + tuple(criteria),
            governance_status="needs_attention",
        )


@dataclass(frozen=True)
class GovernanceSession:
    """
    A governance session tracking multiple evaluations.
    
    Includes:
        - Session metadata
        - All governance evaluations
        - Summary statistics
    """
    
    # Identity
    session_id: str                           # Unique identifier
    
    # Input
    legal_question: str                       # Question being governed
    
    # Results
    evaluation_results: Tuple[GovernanceEvaluation, ...] = ()
    
    # Summary
    total_evaluations: int = 0                # Count of results
    total_passed: int = 0                     # How many passed?
    total_failed: int = 0                     # How many failed?
    
    # Timing
    created_at_utc: float = field(default_factory=time.time)
    completed_at_utc: Optional[float] = None
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        legal_question: str,
    ) -> GovernanceSession:
        """Create a new governance session."""
        return cls(
            session_id=f"governance_session:{uuid.uuid4().hex[:16]}",
            legal_question=legal_question,
        )
    
    def add_result(self, result: GovernanceEvaluation) -> GovernanceSession:
        """Add an evaluation result to the session."""
        total = self.total_evaluations + 1
        passed = self.total_passed + (1 if result.governance_status != "needs_attention" else 0)
        
        return dataclass_replace(
            self,
            evaluation_results=self.evaluation_results + (result,),
            total_validations=total,
            total_passed=passed,
            total_failed=total - passed,
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "GovernanceEvaluation",
    "GovernanceSession",
]