# Integrity Domain - Governance Subsystem

"""
Integrity: Structural correctness evaluation for Memory.

The integrity domain evaluates:
    
    - Artifact identity preservation
    - Relations and connections between artifacts
    - Provenance completeness
    - Revision graph integrity
    - Semantic consistency
    - Ontology consistency
    
Integrity Laws (GOVERNANCE-LAW-001 through GOVERNANCE-LAW-008):

    INTEGRITY-LAW-001: Integrity evaluation shall verify Memory consistency.
    INTEGRITY-LAW-002: Integrity shall preserve artifact identity.
    INTEGRITY-LAW-003: Integrity shall preserve provenance.
    INTEGRITY-LAW-004: Integrity shall preserve revision graphs.
    INTEGRITY-LAW-005: Integrity violations shall remain explicit.
    INTEGRITY-LAW-006: Integrity shall never repair Memory.
    INTEGRITY-LAW-007: Integrity evaluations shall remain inspectable.
    INTEGRITY-LAW-008: Integrity evaluation shall remain deterministic.

Integrity Input:
    
    - Memory Artifacts
    - Relations between artifacts
    - Revision history
    - Identity records
    - Ontology definitions

Integrity Output:
    
    - Integrity Report (findings, violations, warnings)
    - Evidence records for each check
    - Diagnostics information
    
Integrity Constraints:

    - Never repairs Memory (detection only, no action)
    - Violations are explicit and inspectable
    - All evaluations are deterministic
    - Results can be audited and traced

Anti-Patterns Rejected:
    
    - Automatic repair of violations
    - Silent suppression of issues
    - Non-deterministic evaluation
    - Hidden criteria or logic
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
import time


# =============================================================================
# INTEGRITY VIOLATION TYPES
# =============================================================================


class IntegrityViolationType:
    """Categories of integrity violations."""
    
    IDENTITY_MISMATCH = "identity_mismatch"
    PROVENANCE_INCOMPLETE = "provenance_incomplete"
    REVISION_GRAPH_BROKEN = "revision_graph_broken"
    SEMANTIC_INCONSISTENCY = "semantic_inconsistency"
    ONTOLOGY_VIOLATION = "ontology_violation"
    RELATION_BROKEN = "relation_broken"


# =============================================================================
# INTEGRITY DIAGNOSTICS
# =============================================================================


@dataclass(frozen=True)
class IntegrityDiagnostics:
    """Diagnostic information from integrity evaluation."""
    
    check_count: int = 0
    violation_count: int = 0
    warning_count: int = 0
    
    # Check breakdowns
    identity_checks: int = 0
    provenance_checks: int = 0
    revision_checks: int = 0
    consistency_checks: int = 0
    
    # Timing
    start_time_utc: float = field(default_factory=time.time)
    end_time_utc: float = field(default_factory=time.time)
    
    @property
    def duration_seconds(self) -> float:
        """Get evaluation duration in seconds."""
        return self.end_time_utc - self.start_time_utc
    
    @property
    def is_healthy(self) -> bool:
        """Check if integrity is healthy (no violations)."""
        return self.violation_count == 0


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "IntegrityViolationType",
    "IntegrityDiagnostics",
]