# Gordon Phase 5.7.5-I: Presence Engine - Canonical Engine
# ===============================================================================
"""
Canonical Presence Engine integrating admission, persistence, fading,
and snapshot management for conscious accessibility.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional

# Gordon Phase 5.7.5 - Presence Engine imports (absolute paths for module use)
try:
    from gordon.agent.components.systems.consciousness import constants, exceptions, admission, persistence, fading, \
        transition, snapshot, diagnostics, integrity
except ImportError:
    # Absolute imports for standalone testing
    from gordon_system.src.agent.capabilities.consciousness.presence import (
        constants,
        exceptions,
        admission,
        persistence,
        fading,
        transition,
        snapshot,
        diagnostics,
        integrity,
    )

from .constants import (
    PRESENCE_STATE_CANDIDATE,
    PRESENCE_STATE_ADMITTED,
    PRESENCE_STATE_ACTIVE,
    PRESENCE_STATE_WEAKENING,
    PRESENCE_STATE_FADING,
    PRESENCE_STATE_SUSPENDED,
    PRESENCE_STATE_WITHDRAWN,
)
from .exceptions import InvalidAdmission, CapacityExceeded
from gordon.agent.components.systems.consciousnessadmission import AdmissionAuthority, AdmissionPolicy
from gordon.agent.components.systems.consciousnesspersistence import PersistenceManager, PersistencePolicy
from gordon.agent.components.systems.consciousnessfading import FadingManager, FadePolicy
from gordon.agent.components.systems.consciousnesstransition import PresenceTransition, TransitionBatch
from gordon.agent.components.systems.consciousnesssnapshot import PresenceSnapshot
from gordon.agent.components.systems.consciousnessdiagnostics import Diagnostics
from gordon.agent.components.systems.consciousnessintegrity import IntegrityEnforcer


@dataclass
class PresenceEngine:
    """
    Canonical Presence Engine for conscious accessibility.
    
    The Presence Engine determines what is consciously present right now.
    It answers: "What is currently accessible to higher cognitive systems?"
    
    Responsibilities:
        - Admit candidate content from Experiential Field, Intentional Context,
          and Temporal Context
        - Track presence lifecycle (candidate → admitted → active → fading → withdrawn)
        - Manage fading transitions with bounded persistence
        - Publish immutable snapshots for higher cognitive systems
        
    NOT responsible for:
        - Content evaluation or reasoning
        - Attention computation
        - Salience computation
        - Memory storage or retrieval
        - Planning or execution
    
    Integration points:
        - Experiential Field (proposes candidates)
        - Intentional Context (targets content)
        - Temporal Context (provides timing)
    """
    
    # Core components
    _admission: AdmissionAuthority = field(default_factory=AdmissionAuthority)
    """Admission authority."""
    
    _persistence: PersistenceManager = field(default_factory=PersistenceManager)
    """Persistence manager."""
    
    _fading: FadingManager = field(default_factory=FadingManager)
    """Fading manager."""
    
    _integrity: IntegrityEnforcer = field(default_factory=IntegrityEnforcer)
    """Integrity enforcer."""
    
    _diagnostics: Diagnostics = field(default_factory=Diagnostics)
    """Diagnostics collector."""
    
    # State tracking
    _items_by_id: Dict[str, Dict] = field(default_factory=dict)
    """Track items by ID with their metadata."""
    
    _generation: int = 0
    """Current snapshot generation."""
    
    _max_active: int = 100
    """Maximum concurrent active items."""
    
    def __post_init__(self) -> None:
        """Initialize empty state."""
        self._items_by_id.clear()
        self._diagnostics.record_admission()  # Initialize counter
    
    @property
    def current_generation(self) -> int:
        """Get current snapshot generation."""
        return self._generation
    
    @property
    def admission_authority(self) -> AdmissionAuthority:
        """Get the admission authority."""
        return self._admission
    
    @property
    def persistence_manager(self) -> PersistenceManager:
        """Get the persistence manager."""
        return self._persistence
    
    @property
    def fading_manager(self) -> FadingManager:
        """Get the fading manager."""
        return self._fading
    
    # ==========================================================================
    # ADMISSION - Deterministic policy-based admission
    # ==========================================================================
    
    def propose_candidate(
        self,
        item_id: str,
        source_id: str,
        contribution_id: Optional[str] = None,
        content_reference: Optional[str] = None,
        freshness_utc: Optional[float] = None,
        privacy_classification: str = "internal",
        trust_classification: str = "untrusted",
        now_utc: Optional[float] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Propose a candidate for conscious presence.
        
        This is the entry point for content from Experiential Field,
        Intentional Context, and Temporal Context.
        
        Args:
            item_id: Unique ID for this item
            source_id: Source proposing the content
            contribution_id: Contribution envelope ID (for provenance)
            content_reference: Reference to actual content
            freshness_utc: Content freshness timestamp
            privacy_classification: Privacy level
            trust_classification: Trust level (preserved, not granted)
            now_utc: Current time
            
        Returns:
            Tuple of (success, reason_if_failed)
        """
        if now_utc is None:
            now_utc = time.time()
        
        if freshness_utc is None:
            freshness_utc = now_utc
        
        # Check current counts
        active_count = sum(
            1 for item in self._items_by_id.values()
            if item.get("state") == PRESENCE_STATE_ACTIVE
        )
        
        admitted_count = sum(
            1 for item in self._items_by_id.values()
            if item.get("state") == PRESENCE_STATE_ADMITTED
        )
        
        # Try to admit directly (bypassing intermediate admitted state)
        allowed, reason = self._admission.evaluate_candidate(
            candidate_id=item_id,
            source_id=source_id,
            freshness_utc=freshness_utc,
            current_active_count=active_count,
            current_admitted_count=admitted_count + 1,
            now_utc=now_utc,
        )
        
        if not allowed:
            self._diagnostics.record_admission(success=False)
            return False, reason
        
        # Register for persistence
        success, reason = self._persistence.register_content(
            content_id=item_id,
            now_utc=now_utc,
        )
        
        if not success:
            return False, reason
        
        # Store item metadata
        self._items_by_id[item_id] = {
            "state": PRESENCE_STATE_ADMITTED,
            "source_id": source_id,
            "contribution_id": contribution_id,
            "content_reference": content_reference,
            "privacy_classification": privacy_classification,
            "trust_classification": trust_classification,
            "created_at_utc": now_utc,
            "admitted_at_utc": now_utc,
        }
        
        # Record transition
        self._diagnostics.record_admission(success=True)
        
        return True, None
    
    def activate_item(
        self,
        item_id: str,
        now_utc: Optional[float] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Activate an admitted item into conscious presence.
        
        Args:
            item_id: ID of the item to activate
            now_utc: Current time
            
        Returns:
            Tuple of (success, reason_if_failed)
        """
        if now_utc is None:
            now_utc = time.time()
        
        # Check if item exists and is admitted
        item = self._items_by_id.get(item_id)
        
        if item is None:
            return False, "Item not found"
        
        if item["state"] != PRESENCE_STATE_ADMITTED:
            return False, f"Item must be in admitted state (current: {item['state']})"
        
        # Check capacity
        active_count = sum(
            1 for i in self._items_by_id.values()
            if i.get("state") == PRESENCE_STATE_ACTIVE
        )
        
        if active_count >= self._max_active:
            return False, "Active capacity exceeded"
        
        # Activate
        item["state"] = PRESENCE_STATE_ACTIVE
        item["active_from_utc"] = now_utc
        
        self._diagnostics.record_transition(latency_ms=0.1)
        
        return True, None
    
    def withdraw_item(
        self,
        item_id: str,
        reason: Optional[str] = None,
        now_utc: Optional[float] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Withdraw an item from conscious presence.
        
        Args:
            item_id: ID of the item to withdraw
            reason: Reason for withdrawal (optional)
            now_utc: Current time
            
        Returns:
            Tuple of (success, reason_if_failed)
        """
        if now_utc is None:
            now_utc = time.time()
        
        item = self._items_by_id.get(item_id)
        
        if item is None:
            return False, "Item not found"
        
        # Record transition
        transition = PresenceTransition(
            item_id=item_id,
            from_state=item["state"],
            to_state=PRESENCE_STATE_WITHDRAWN,
            kind="withdrawal",
            timestamp_utc=now_utc,
            reason=reason,
            source_id=item.get("source_id", ""),
        )
        
        # Clean up
        del self._items_by_id[item_id]
        self._persistence.unregister_content(item_id)
        self._fading.clear_item(item_id)
        
        self._diagnostics.record_withdrawal(latency_ms=0.1)
        
        return True, None
    
    def fade_item(
        self,
        item_id: str,
        reason: Optional[str] = None,
        now_utc: Optional[float] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Fade an active item toward withdrawal.
        
        This starts the fading process: active → weakening → fading → withdrawn
        
        Args:
            item_id: ID of the item to fade
            reason: Reason for fading (optional)
            now_utc: Current time
            
        Returns:
            Tuple of (success, reason_if_failed)
        """
        if now_utc is None:
            now_utc = time.time()
        
        item = self._items_by_id.get(item_id)
        
        if item is None:
            return False, "Item not found"
        
        if item["state"] != PRESENCE_STATE_ACTIVE:
            return False, f"Item must be active (current: {item['state']})"
        
        # Check fading policy
        can_fade, reason = self._fading.policy.can_begin_fading(
            active_from_utc=item.get("active_from_utc"),
            now_utc=now_utc,
        )
        
        if not can_fade:
            return False, f"Fading policy check failed: {reason}"
        
        # Start fading
        item["state"] = PRESENCE_STATE_WEAKENING
        item["fading_started_utc"] = now_utc
        
        transition = PresenceTransition.fade_start(
            item_id=item_id,
            reason=reason,
            source_id=item.get("source_id", ""),
        )
        
        self._diagnostics.record_transition(latency_ms=0.1)
        
        return True, None
    
    def resume_item(
        self,
        item_id: str,
        now_utc: Optional[float] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Resume a suspended item to active presence.
        
        Args:
            item_id: ID of the item to resume
            now_utc: Current time
            
        Returns:
            Tuple of (success, reason_if_failed)
        """
        if now_utc is None:
            now_utc = time.time()
        
        item = self._items_by_id.get(item_id)
        
        if item is None:
            return False, "Item not found"
        
        if item["state"] != PRESENCE_STATE_SUSPENDED:
            return False, f"Item must be suspended (current: {item['state']})"
        
        # Resume
        item["state"] = PRESENCE_STATE_ACTIVE
        item["active_from_utc"] = now_utc
        
        transition = PresenceTransition.resume(
            item_id=item_id,
            source_id=item.get("source_id", ""),
        )
        
        self._diagnostics.record_transition(latency_ms=0.1)
        
        return True, None
    
    def interrupt_item(
        self,
        item_id: str,
        reason: Optional[str] = None,
        now_utc: Optional[float] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Interrupt an active item by suspending it.
        
        Args:
            item_id: ID of the item to interrupt
            reason: Reason for interruption (optional)
            now_utc: Current time
            
        Returns:
            Tuple of (success, reason_if_failed)
        """
        if now_utc is None:
            now_utc = time.time()
        
        item = self._items_by_id.get(item_id)
        
        if item is None:
            return False, "Item not found"
        
        if item["state"] != PRESENCE_STATE_ACTIVE:
            return False, f"Item must be active (current: {item['state']})"
        
        # Suspend
        item["state"] = PRESENCE_STATE_SUSPENDED
        
        transition = PresenceTransition.interrupt(
            item_id=item_id,
            reason=reason,
        )
        
        self._diagnostics.record_transition(latency_ms=0.1)
        
        return True, None
    
    def check_fading_progress(self, now_utc: Optional[float] = None) -> Tuple[int, int]:
        """
        Check fading progress and advance items as needed.
        
        Args:
            now_utc: Current time
            
        Returns:
            Tuple of (items advanced to fading, items withdrawn)
        """
        if now_utc is None:
            now_utc = time.time()
        
        advanced_to_fading = 0
        withdrawn = 0
        
        for item_id, item in self._items_by_id.items():
            state = item.get("state")
            
            if state == PRESENCE_STATE_WEAKENING:
                if self._fading.is_weakening_complete(item_id, now_utc):
                    item["state"] = PRESENCE_STATE_FADING
                    self._fading.begin_fading(item_id, now_utc)
                    advanced_to_fading += 1
            
            elif state == PRESENCE_STATE_FADING:
                if self._fading.is_fading_complete(item_id, now_utc):
                    self.withdraw_item(item_id, reason="fade_complete", now_utc=now_utc)
                    withdrawn += 1
        
        return advanced_to_fading, withdrawn
    
    # ==========================================================================
    # SNAPSHOTS - Immutable publications of presence state
    # ==========================================================================
    
    def get_snapshot(self, now_utc: Optional[float] = None) -> PresenceSnapshot:
        """
        Get an immutable snapshot of current presence state.
        
        Args:
            now_utc: Current time (uses current time if not provided)
            
        Returns:
            Immutable PresenceSnapshot with all active items
        """
        if now_utc is None:
            now_utc = time.time()
        
        # Build item lists
        active_items = tuple(
            item_id for item_id, item in self._items_by_id.items()
            if item.get("state") == PRESENCE_STATE_ACTIVE
        )
        
        fading_items = tuple(
            item_id for item_id, item in self._items_by_id.items()
            if item.get("state") in (PRESENCE_STATE_WEAKENING, PRESENCE_STATE_FADING)
        )
        
        suspended_items = tuple(
            item_id for item_id, item in self._items_by_id.items()
            if item.get("state") == PRESENCE_STATE_SUSPENDED
        )
        
        # Get source IDs
        source_ids = tuple(set(
            item.get("source_id", "") for item in self._items_by_id.values()
        ))
        
        snapshot = PresenceSnapshot(
            generation=self._generation,
            previous_generation=self._generation - 1 if self._generation > 0 else None,
            created_at_utc=now_utc,
            valid_from_utc=0.0,
            active_items=active_items,
            weakening_items=(),
            fading_items=fading_items,
            suspended_items=suspended_items,
            withdrawn_items=(),
            source_ids=source_ids,
        )
        
        return snapshot
    
    def advance_generation(self, now_utc: Optional[float] = None) -> int:
        """
        Advance to next generation (for replay/traceability).
        
        Args:
            now_utc: Current time
            
        Returns:
            New generation number
        """
        if now_utc is None:
            now_utc = time.time()
        
        self._generation += 1
        
        return self._generation
    
    # ==========================================================================
    # DIAGNOSTICS AND HEALTH
    # ==========================================================================
    
    @property
    def metrics(self) -> Dict[str, int]:
        """Get engine metrics."""
        diag_metrics = self._diagnostics.metrics
        
        return {
            "admitted_total": diag_metrics.admitted_total,
            "withdrawn_total": diag_metrics.withdrawn_total,
            "active_count": diag_metrics.active_count,
            "fading_count": diag_metrics.fading_count,
            "failure_count": diag_metrics.admission_failures,
            "generation": self._generation,
        }
    
    @property
    def health(self) -> Dict[str, bool]:
        """Get engine health status."""
        return {
            "can_admit": True,
            "can_withdraw": True,
            "can_transition": True,
        }