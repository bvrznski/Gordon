# Core Resource Verification
# ==========================
"""
Resource accounting verification and corruption detection.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import time


@dataclass(frozen=True)
class VerificationStatus(Enum):
    """Status of a verification check."""
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass(frozen=True)
class AccountingViolation:
    """
    Record of an accounting violation.
    
    Indicates that capacity accounting has gone negative or inconsistent.
    """
    violation_id: str
    violation_type: str      # e.g., "negative_balance", "capacity_mismatch"
    domain: Optional[str] = None
    
    expected_value: Optional[float] = None
    actual_value: Optional[float] = None
    
    timestamp_utc: float = field(default_factory=time.time)
    
    severity: str = "critical"  # critical, warning


@dataclass(frozen=True)
class CorruptedAccounting:
    """
    Record of accounting corruption.
    
    More severe than a violation - indicates the accounting ledger is unreliable.
    """
    corruption_id: str
    affected_domains: Tuple[str, ...]
    corruption_type: str   # e.g., "negative_total", "unreconcilable"
    
    estimated_impact: float  # Potential incorrect capacity values
    
    timestamp_utc: float = field(default_factory=time.time)
    
    needs_manual_review: bool = True


@dataclass(frozen=True)
class SplitBrainDetection:
    """
    Detection of split-brain in resource authority.
    
    Multiple authorities claiming the same resources.
    """
    detection_id: str
    conflicting_authorities: Tuple[str, ...]  # Runtime IDs
    affected_resources: Tuple[str, ...]
    
    timestamp_utc: float = field(default_factory=time.time)
    
    severity: str = "critical"


class ResourceAccountingVerifier:
    """
    Verifier for resource accounting integrity.
    
    Monitors capacity tracking for corruption and inconsistencies.
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        self._lock = __import__("threading").RLock()
        
        # Violations detected
        self._violations: List[AccountingViolation] = []
        self._corruptions: List[CorruptedAccounting] = []
    
    def verify_capacity_integrity(
        self,
        total_capacity: float,
        reserved: float,
        allocated: float,
        used: float
    ) -> Tuple[bool, List[AccountingViolation]]:
        """
        Verify capacity accounting integrity.
        
        Checks:
            - No negative values
            - Reserved + Allocated <= Total (within bounds)
            - Used <= Allocated
        
        Returns:
            Tuple of (intact, list_of_violations)
        """
        with self._lock:
            violations: List[AccountingViolation] = []
            
            if total_capacity < 0:
                violations.append(AccountingViolation(
                    violation_id=f"cap_{time.time():.0f}_1",
                    violation_type="negative_total_capacity",
                    severity="critical",
                ))
            
            if reserved < 0:
                violations.append(AccountingViolation(
                    violation_id=f"cap_{time.time():.0f}_2",
                    violation_type="negative_reserved",
                    severity="critical",
                ))
            
            if allocated < 0:
                violations.append(AccountingViolation(
                    violation_id=f"cap_{time.time():.0f}_3",
                    violation_type="negative_allocated",
                    severity="critical",
                ))
            
            if used < 0:
                violations.append(AccountingViolation(
                    violation_id=f"cap_{time.time():.0f}_4",
                    violation_type="negative_used",
                    severity="critical",
                ))
            
            # Check consistency
            if reserved + allocated > total_capacity:
                violations.append(AccountingViolation(
                    violation_id=f"cap_{time.time():.0f}_5",
                    violation_type="capacity_overflow",
                    severity="warning",
                ))
            
            if used > allocated:
                violations.append(AccountingViolation(
                    violation_id=f"cap_{time.time():.0f}_6",
                    violation_type="used_greater_than_allocated",
                    severity="warning",
                ))
            
            return len(violations) == 0, violations
    
    def detect_split_brain(
        self,
        authority_ids: List[str],
        resource_ownership_by_authority: Dict[str, List[str]]
    ) -> Optional[SplitBrainDetection]:
        """
        Detect split-brain scenario.
        
        Checks if multiple authorities claim ownership of the same resources.
        
        Returns:
            Detection record if split-brain found
        """
        with self._lock:
            # Build resource -> authority map
            resource_authorities: Dict[str, List[str]] = {}
            
            for auth_id, resources in resource_ownership_by_authority.items():
                for res_id in resources:
                    if res_id not in resource_authorities:
                        resource_authorities[res_id] = []
                    resource_authorities[res_id].append(auth_id)
            
            # Find conflicts
            conflicts = [
                (res, auths) for res, auths in resource_authorities.items()
                if len(auths) > 1
            ]
            
            if not conflicts:
                return None
            
            affected_resources = tuple(res for res, _ in conflicts[:10])  # Limit
            conflicting_auths = tuple(set(
                auth for _, auths in conflicts for auth in auths
            ))
            
            return SplitBrainDetection(
                detection_id=f"split_{time.time():.0f}",
                conflicting_authorities=conflicting_auths,
                affected_resources=affected_resources,
            )


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "VerificationStatus",
    "AccountingViolation",
    "CorruptedAccounting",
    "SplitBrainDetection",
    "ResourceAccountingVerifier",
]