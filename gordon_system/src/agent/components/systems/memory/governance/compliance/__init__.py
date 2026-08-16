# Compliance Domain - Governance Subsystem

"""
Compliance: Architectural rules verification for Memory.

The compliance domain verifies:
    
    - Policy adherence
    - Ontology rules
    - Lifecycle correctness
    - Contract fulfillment
    - Access control compliance
    
Compliance Laws:

    COMPLIANCE-LAW-001: Verify architectural contracts
    COMPLIANCE-LAW-002: Verify ontology rules
    COMPLIANCE-LAW-003: Verify policy consistency
    COMPLIANCE-LAW-004: Verify lifecycle correctness
    COMPLIANCE-LAW-005: Preserve evidence
    COMPLIANCE-LAW-006: Never modify Memory
    COMPLIANCE-LAW-007: Reports remain inspectable
    COMPLIANCE-LAW-008: Evaluation remains deterministic

Compliance Input:
    
    - Policies (admission, activation, retention, archival)
    - Lifecycle states and transitions
    - Contracts and agreements
    - Ontology definitions
    - Access control rules

Compliance Output:
    
    - Compliance Report (pass/fail/conditional)
    - Violations with recommendations
    - Evidence records
    
Compliance Constraints:

    - Never modifies Memory (verification only)
    - All violations are explicit and inspectable
    - Deterministic evaluation
    - Evidence preserved for audit trail

Anti-Patterns Rejected:
    
    - Silent correction of errors
    - Non-deterministic compliance checks
    - Hidden criteria or logic
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import time


# =============================================================================
# COMPLIANCE VIOLATION TYPES
# =============================================================================


class ComplianceViolationType:
    """Categories of compliance violations."""
    
    POLICY_VIOLATION = "policy_violation"
    ONTOLOGY_VIOLATION = "ontology_violation"
    LIFECYCLE_VIOLATION = "lifecycle_violation"
    CONTRACT_VIOLATION = "contract_violation"
    ACCESS_VIOLATION = "access_violation"


# =============================================================================
# COMPLIANCE DIAGNOSTICS
# =============================================================================


@dataclass(frozen=True)
class ComplianceDiagnostics:
    """Diagnostic information from compliance evaluation."""
    
    check_count: int = 0
    violation_count: int = 0
    warning_count: int = 0
    
    # Check breakdowns
    policy_checks: int = 0
    ontology_checks: int = 0
    lifecycle_checks: int = 0
    contract_checks: int = 0
    
    # Timing
    start_time_utc: float = field(default_factory=time.time)
    end_time_utc: float = field(default_factory=time.time)
    
    @property
    def duration_seconds(self) -> float:
        """Get evaluation duration in seconds."""
        return self.end_time_utc - self.start_time_utc
    
    @property
    def is_compliant(self) -> bool:
        """Check if compliance check passed."""
        return self.violation_count == 0


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ComplianceViolationType",
    "ComplianceDiagnostics",
]