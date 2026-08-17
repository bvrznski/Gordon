# Deduction Health - Phase 7.1
# ============================

"""
Canonical Deduction Health Contract.

Deduction Health tracks metrics about the reasoning system.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class DeductionHealth:
    """
    Health metrics for deductive reasoning.
    
    Metrics include:
        - Proof count (how many proofs have been generated?)
        - Average proof depth (how complex are the proofs?)
        - Average branching factor (how many inference paths?)
        - Rule utilization (which rules are used most?)
        - Contradiction rate (how often do contradictions occur?)
        - Validation success rate
    
    Health remains descriptive; it never modifies the reasoning directly.
    """
    
    # Identity
    health_id: str                          # Unique identifier
    
    # Proof metrics
    proof_count: int = 0                    # Total proofs generated
    average_proof_depth: float = 0.0        # Average number of inference steps
    max_proof_depth: int = 0                # Maximum proof depth seen
    
    # Rule metrics
    rule_utilization: Dict[str, int] = field(default_factory=dict)
    # Maps rule_id -> application count
    
    # Contradiction metrics
    contradiction_count: int = 0            # Total contradictions detected
    resolved_contradictions: int = 0        # Contradictions that were analyzed
    unresolved_contradictions: int = 0      # Still pending analysis
    
    # Validation metrics
    validation_success_count: int = 0       # Validated proofs
    validation_failure_count: int = 0       # Invalid proofs
    
    # Timing
    recorded_at_utc: float = field(default_factory=time.time)
    
    @property
    def total_rules_used(self) -> int:
        """Count of unique rules used."""
        return len(self.rule_utilization)
    
    @property
    def validation_rate(self) -> float:
        """Validation success rate (0.0 to 1.0)."""
        total = self.validation_success_count + self.validation_failure_count
        if total == 0:
            return 0.0
        return self.validation_success_count / total
    
    @classmethod
    def create(cls) -> "DeductionHealth":
        """Create a new health record."""
        return cls(
            health_id=f"deduction_health:{uuid.uuid4().hex[:16]}",
        )
    
    def increment_proof(self, depth: int) -> "DeductionHealth":
        """Record a new proof."""
        new_count = self.proof_count + 1
        total_depth = self.average_proof_depth * self.proof_count + depth
        
        return dataclass_replace(
            self,
            proof_count=new_count,
            average_proof_depth=total_depth / new_count,
            max_proof_depth=max(self.max_proof_depth, depth),
        )
    
    def record_rule_application(self, rule_id: str) -> "DeductionHealth":
        """Record a rule application."""
        new_utilization = dict(self.rule_utilization)
        new_utilization[rule_id] = new_utilization.get(rule_id, 0) + 1
        
        return dataclass_replace(
            self,
            rule_utilization=new_utilization,
        )
    
    def record_contradiction(self, resolved: bool = False) -> "DeductionHealth":
        """Record a contradiction."""
        new_count = self.contradiction_count + 1
        if resolved:
            new_resolved = self.resolved_contradictions + 1
            return dataclass_replace(
                self,
                contradiction_count=new_count,
                resolved_contradictions=new_resolved,
                unresolved_contradictions=self.unresolved_contradictions,
            )
        else:
            return dataclass_replace(
                self,
                contradiction_count=new_count,
                unresolved_contradictions=self.unresolved_contradictions + 1,
            )
    
    def record_validation(self, passed: bool) -> "DeductionHealth":
        """Record a validation result."""
        if passed:
            return dataclass_replace(
                self,
                validation_success_count=self.validation_success_count + 1,
            )
        else:
            return dataclass_replace(
                self,
                validation_failure_count=self.validation_failure_count + 1,
            )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "DeductionHealth",
]