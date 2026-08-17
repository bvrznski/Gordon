# Transfer Validation - Phase 7.4
# ==============================

"""
Canonical Transfer Validation Contract.

Validation evaluates transferred knowledge without modifying it.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any


@dataclass(frozen=True)
class TransferValidation:
    """
    Validation of a knowledge transfer proposal.
    
    Validation evaluates:
        - Structural consistency (are structures compatible?)
        - Domain compatibility (does domain A match domain B?)
        - Constraint satisfaction (do all constraints hold?)
        - Causal preservation (is causality maintained?)
        - Functional equivalence (do functions produce same results?)
    
    Validation remains observational; it never modifies transferred knowledge.
    """
    
    # Identity
    validation_id: str                        # Unique identifier
    
    # Evaluated transfer
    evaluated_transfer_id: str                # Which transfer is validated?
    
    # Findings
    findings: Tuple[Dict[str, Any], ...] = ()  # What did we find?
    
    # Unsupported mappings (elements that couldn't be mapped)
    unsupported_mappings: Tuple[str, ...] = ()
    
    # Validation results
    is_structurally_consistent: bool = False   # Are structures compatible?
    is_domain_compatible: bool = False         # Do domains match?
    constraint_satisfaction_score: float = 0.0 # How well do constraints match?
    
    # Metadata
    validated_at_utc: float = field(default_factory=time.time)
    
    @property
    def finding_count(self) -> int:
        """Number of validation findings."""
        return len(self.findings)
    
    @classmethod
    def create(
        cls,
        evaluated_transfer_id: str,
    ) -> TransferValidation:
        """Create a new transfer validation."""
        return cls(
            validation_id=f"transfer_validation:{uuid.uuid4().hex[:16]}",
            evaluated_transfer_id=evaluated_transfer_id,
        )
    
    def add_finding(self, finding: Dict[str, Any]) -> TransferValidation:
        """Add a validation finding."""
        return dataclass_replace(
            self,
            findings=self.findings + (finding,),
        )


@dataclass(frozen=True)
class ValidationFindings:
    """
    Aggregated validation findings across multiple transfers.
    
    Used for reporting and governance evaluation.
    """
    
    # Identity
    findings_id: str                          # Unique identifier
    
    # Findings by category
    structural_issues: Tuple[str, ...] = ()
    domain_issues: Tuple[str, ...] = ()
    constraint_violations: Tuple[str, ...] = ()
    causal_discrepancies: Tuple[str, ...] = ()
    
    # Overall metrics
    total_transfers_validated: int = 0
    transfers_passed: int = 0
    transfers_failed: int = 0
    
    # Metadata
    generated_at_utc: float = field(default_factory=time.time)
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate."""
        if self.total_transfers_validated == 0:
            return 1.0
        return self.transfers_passed / self.total_transfers_validated
    
    @classmethod
    def create(cls) -> ValidationFindings:
        """Create a new findings set."""
        return cls(
            findings_id=f"validation_findings:{uuid.uuid4().hex[:16]}",
        )


def dataclass_replace(instance: Any, **kwargs: Any) -> Any:
    """Simple dataclass replace helper for frozen instances."""
    return instance.__class__(**{**instance.__dict__, **kwargs})


__all__ = [
    "TransferValidation",
    "ValidationFindings",
]