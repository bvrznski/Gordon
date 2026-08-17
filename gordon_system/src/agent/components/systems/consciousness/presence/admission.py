# Gordon Phase 5.7.5-I: Presence Engine - Admission Authority
# ===============================================================================
"""
Canonical admission authority for the Presence Engine.

The admission authority determines which candidate content becomes consciously
present. It operates according to policy-defined rules and never performs
reasoning or semantic evaluation.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional


# =============================================================================
# ADMISSION POLICY CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class AdmissionPolicy:
    """
    Immutable admission policy configuration.
    
    Defines the rules for determining which content becomes consciously present.
    Policies are checked deterministically without reasoning or inference.
    """
    
    source_validation: bool = True
    """Validate source identity before admission."""
    
    freshness_check: bool = True
    """Check content freshness timestamp before admission."""
    
    capacity_limit: int = 100
    """Maximum concurrent active presence items."""
    
    max_admitted: int = 200
    """Maximum admitted (but not yet active) items."""
    
    default_lifetime_seconds: float = 3600.0
    """Default lifetime for admitted content."""
    
    def can_admit(
        self,
        source_id: str,
        freshness_utc: float,
        current_active_count: int,
        current_admitted_count: int,
        now_utc: Optional[float] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if admission is allowed under current policy.
        
        Args:
            source_id: Source identity proposing content
            freshness_utc: Content freshness timestamp
            current_active_count: Currently active presence count
            current_admitted_count: Currently admitted (but not active) count
            now_utc: Current time for freshness check
            
        Returns:
            Tuple of (allowed, reason_if_not_allowed)
        """
        if now_utc is None:
            now_utc = time.time()
        
        # Source validation
        if self.source_validation and not source_id:
            return False, "Invalid source identity"
        
        # Freshness check
        if self.freshness_check:
            if now_utc > freshness_utc + 3600.0:  # Content older than 1 hour
                return False, "Content expired"
        
        # Capacity limit
        if current_active_count >= self.capacity_limit:
            return False, f"Active capacity exceeded ({current_active_count}/{self.capacity_limit})"
        
        # Admitted queue limit
        if current_admitted_count >= self.max_admitted:
            return False, f"Admitted queue full ({current_admitted_count}/{self.max_admitted})"
        
        return True, None


# =============================================================================
# ADMISSION AUTHORITY
# =============================================================================

@dataclass
class AdmissionAuthority:
    """
    Canonical admission authority for Presence Engine.
    
    Responsibilities:
        - Evaluate candidate content against policy rules
        - Determine admission eligibility
        - Track admission metrics and history
        
    NOT responsible for:
        - Content evaluation or reasoning
        - Truth assessment
        - Semantic validation beyond syntax/freshness
        - Source trust granting (preserves source trust)
    """
    
    _policy: AdmissionPolicy = field(default_factory=AdmissionPolicy)
    """Admission policy configuration."""
    
    _admitted_items: Dict[str, float] = field(default_factory=dict)
    """Track admitted items and their admission timestamps."""
    
    _metrics: Dict[str, int] = field(default_factory=dict)
    """Admission metrics."""
    
    def __post_init__(self) -> None:
        """Initialize metrics counters."""
        self._metrics["admitted_total"] = 0
        self._metrics["rejected_total"] = 0
        self._metrics["failure_reasons"] = {}
    
    @property
    def policy(self) -> AdmissionPolicy:
        """Get the current admission policy."""
        return self._policy
    
    def get_metrics(self) -> Dict[str, int]:
        """Get admission metrics (immutable copy)."""
        return dict(self._metrics)
    
    def evaluate_candidate(
        self,
        candidate_id: str,
        source_id: str,
        freshness_utc: float,
        current_active_count: int,
        current_admitted_count: int,
        now_utc: Optional[float] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Evaluate a candidate for admission.
        
        This is a deterministic policy check - no reasoning or inference.
        
        Args:
            candidate_id: ID of the candidate content
            source_id: Source proposing the content
            freshness_utc: Content freshness timestamp
            current_active_count: Currently active presence items
            current_admitted_count: Currently admitted (not yet active) items
            now_utc: Current time
            
        Returns:
            Tuple of (admissible, reason_if_not)
        """
        if now_utc is None:
            now_utc = time.time()
        
        allowed, reason = self._policy.can_admit(
            source_id=source_id,
            freshness_utc=freshness_utc,
            current_active_count=current_active_count,
            current_admitted_count=current_admitted_count,
            now_utc=now_utc,
        )
        
        return allowed, reason
    
    def admit_candidate(
        self,
        candidate_id: str,
        source_id: str,
        freshness_utc: float,
        trust_classification: str = "untrusted",
        privacy_classification: str = "internal",
        current_active_count: int = 0,
        current_admitted_count: int = 0,
        now_utc: Optional[float] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Attempt to admit a candidate to presence.
        
        Args:
            candidate_id: ID of the candidate content
            source_id: Source proposing the content
            freshness_utc: Content freshness timestamp
            trust_classification: Trust level (preserved, not granted)
            privacy_classification: Privacy classification
            current_active_count: Currently active presence items
            current_admitted_count: Currently admitted items
            now_utc: Current time
            
        Returns:
            Tuple of (success, reason_if_failed)
        """
        if now_utc is None:
            now_utc = time.time()
        
        # Evaluate against policy
        allowed, reason = self.evaluate_candidate(
            candidate_id=candidate_id,
            source_id=source_id,
            freshness_utc=freshness_utc,
            current_active_count=current_active_count,
            current_admitted_count=current_admitted_count,
            now_utc=now_utc,
        )
        
        if not allowed:
            self._metrics["rejected_total"] = self._metrics.get("rejected_total", 0) + 1
            if reason:
                self._metrics["failure_reasons"][reason] = (
                    self._metrics["failure_reasons"].get(reason, 0) + 1
                )
            return False, reason
        
        # Admit the candidate
        self._admitted_items[candidate_id] = now_utc
        self._metrics["admitted_total"] = self._metrics.get("admitted_total", 0) + 1
        
        return True, None
    
    def is_admitted(self, candidate_id: str) -> bool:
        """Check if a candidate has been admitted."""
        return candidate_id in self._admitted_items
    
    def get_admission_time(self, candidate_id: str) -> Optional[float]:
        """Get when a candidate was admitted."""
        return self._admitted_items.get(candidate_id)
    
    def revoke_admission(
        self,
        candidate_id: str,
        now_utc: Optional[float] = None,
    ) -> bool:
        """
        Revoke admission of a candidate.
        
        Args:
            candidate_id: ID of the candidate to revoke
            now_utc: Current time
            
        Returns:
            True if revoked, False if not admitted
        """
        if now_utc is None:
            now_utc = time.time()
        
        if candidate_id in self._admitted_items:
            del self._admitted_items[candidate_id]
            return True
        
        return False
    
    def clear_admissions(self) -> int:
        """Clear all admissions and return count."""
        count = len(self._admitted_items)
        self._admitted_items.clear()
        return count