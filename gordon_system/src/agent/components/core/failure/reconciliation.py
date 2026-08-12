# Reconciliation System Module
# =============================

"""
External state reconciliation for Phase 3.7.10 failure recovery.

This module provides:
    - External state comparison against system state
    - Reconciliation for detecting drift between expected and actual states
    - State validation after recovery/rollback operations
    
Key concepts:
    - Expected state (from plan/commit) vs actual state (system observation)
    - Drift detection between planned and actual state
    - Automatic reconciliation of minor discrepancies
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
import time


# =============================================================================
# State Comparison Results
# =============================================================================

@dataclass(frozen=True)
class ReconciliationResult:
    """
    Result of a state reconciliation comparison.
    
    Args:
        match: Whether states fully match
        
        expected_state: What the system should be in
        actual_state: What the system is actually in
        
        drift_entities: Entities where states differ
        missing_entities: Entities in expected but not found in actual
        extra_entities: Entities in actual but not in expected
        
        reconciliation_actions: Actions needed to reconcile differences
    """
    
    match: bool
    confidence: float = 0.0
    
    expected_state: Optional[str] = None
    actual_state: Optional[str] = None
    
    drift_entities: List[str] = field(default_factory=list)
    missing_entities: List[str] = field(default_factory=list)
    extra_entities: List[str] = field(default_factory=list)
    
    reconciliation_actions: List["ReconciliationAction"] = field(default_factory=list)


@dataclass(frozen=True)
class ReconciliationAction:
    """
    An action needed to reconcile state differences.
    
    Args:
        action_id: Unique identifier for this action
        action_type: What type of action (ADD, REMOVE, UPDATE, VERIFY)
        
        target_entity: Entity to act on
        expected_value: Expected state value
        actual_value: Current state value
        
        priority: Higher = more urgent
    """
    
    action_id: str
    
    action_type: "ReconciliationType"
    
    target_entity: Optional[str] = None
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    
    priority: int = 0


class ReconciliationType(Enum):
    """Types of reconciliation actions."""
    
    ADD = "add"              # Add missing entity
    REMOVE = "remove"        # Remove extra entity
    UPDATE = "update"        # Update existing entity state
    VERIFY = "verify"        # Verify entity is in correct state
    RESTART = "restart"      # Restart entity to reconcile state


# =============================================================================
# State Source Interface
# =============================================================================

class StateSource:
    """
    Interface for state sources (external systems that provide expected state).
    
    Implementations query external systems for the expected/committed state
    against which we compare actual system state.
    """
    
    async def get_expected_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get expected state for an entity from the source."""
        raise NotImplementedError
    
    async def get_all_expected_states(self) -> Dict[str, Dict[str, Any]]:
        """Get all expected states known to this source."""
        raise NotImplementedError
    
    @property
    def source_name(self) -> str:
        """Name of this state source."""
        raise NotImplementedError


# =============================================================================
# System State Observer
# =============================================================================

class SystemStateObserver:
    """
    Interface for observing actual system state.
    
    This is separate from the reconciliation system - it provides
    the "actual" states to compare against expected states.
    """
    
    async def get_actual_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get actual state of an entity."""
        raise NotImplementedError
    
    async def get_all_actual_states(self) -> Dict[str, Dict[str, Any]]:
        """Get states of all known entities."""
        raise NotImplementedError


# =============================================================================
# External State Reconciler
# =============================================================================

@dataclass(frozen=True)
class ReconciliationRequest:
    """
    Request to perform state reconciliation.
    
    Args:
        request_id: Unique identifier for this request
        entity_ids: Entities to reconcile (None = all)
        
        expected_state_source: Source for expected states
        actual_state_observer: Observer for actual states
        
        tolerance_threshold: How much drift is acceptable before action
        auto_reconcile: Whether to perform automatic reconciliation
    """
    
    request_id: str
    
    entity_ids: Optional[List[str]] = None
    
    expected_state_source: Optional[StateSource] = None
    actual_state_observer: Optional[SystemStateObserver] = None
    
    tolerance_threshold: float = 0.1  # 10% drift tolerance
    auto_reconcile: bool = False


class ExternalStateReconciler:
    """
    Reconciles expected states with actual system states.
    
    This is used to detect and remediate state drift that may have
    occurred due to failures, recovery actions, or external changes.
    """
    
    def __init__(self) -> None:
        """Initialize the reconciler."""
        self._expected_sources: Dict[str, StateSource] = {}
        self._actual_observers: List[SystemStateObserver] = []
        
        self._last_reconciliation: Optional[float] = None
        self._reconciliation_history: List[ReconciliationResult] = []
    
    def register_expected_source(self, source: StateSource) -> None:
        """Register a state source for expected states."""
        self._expected_sources[source.source_name] = source
    
    def register_actual_observer(self, observer: SystemStateObserver) -> None:
        """Register an observer for actual system states."""
        self._actual_observers.append(observer)
    
    async def reconcile(
        self,
        request: ReconciliationRequest
    ) -> ReconciliationResult:
        """
        Perform state reconciliation.
        
        Args:
            request: Reconciliation request with source and targets
            
        Returns:
            Result showing match status and needed actions
        """
        import uuid
        
        # Get expected states from registered sources
        expected_states = {}
        for source_name, source in self._expected_sources.items():
            try:
                states = await source.get_all_expected_states()
                expected_states.update(states)
            except Exception:
                continue
        
        # Filter to requested entities if specified
        if request.entity_ids:
            expected_states = {
                k: v for k, v in expected_states.items()
                if k in request.entity_ids
            }
        
        # Get actual states from all observers
        actual_states = {}
        for observer in self._actual_observers:
            try:
                states = await observer.get_all_actual_states()
                actual_states.update(states)
            except Exception:
                continue
        
        # Perform comparison
        return await self._compare_states(
            expected_states=expected_states,
            actual_states=actual_states,
            tolerance=request.tolerance_threshold
        )
    
    async def _compare_states(
        self,
        expected_states: Dict[str, Dict[str, Any]],
        actual_states: Dict[str, Dict[str, Any]],
        tolerance: float = 0.1
    ) -> ReconciliationResult:
        """Compare expected and actual states."""
        import uuid
        
        # Find entities in each category
        expected_ids = set(expected_states.keys())
        actual_ids = set(actual_states.keys())
        
        missing = expected_ids - actual_ids
        extra = actual_ids - expected_ids
        common = expected_ids & actual_ids
        
        drift_entities = []
        reconciliation_actions = []
        action_id_counter = 0
        
        def make_action_id() -> str:
            nonlocal action_id_counter
            action_id_counter += 1
            return f"action_{action_id_counter}"
        
        # Check missing entities - need to add them
        for entity_id in missing:
            reconciliation_actions.append(ReconciliationAction(
                action_id=make_action_id(),
                action_type=ReconciliationType.ADD,
                target_entity=entity_id,
                expected_value=str(expected_states.get(entity_id, {})),
                priority=1  # High priority - missing expected state
            ))
        
        # Check extra entities - need to remove them (or verify)
        for entity_id in extra:
            reconciliation_actions.append(ReconciliationAction(
                action_id=make_action_id(),
                action_type=ReconciliationType.REMOVE,
                target_entity=entity_id,
                actual_value=str(actual_states.get(entity_id, {})),
                priority=2  # Medium priority - unexpected state
            ))
        
        # Compare common entities
        for entity_id in common:
            expected = expected_states[entity_id]
            actual = actual_states[entity_id]
            
            if not self._states_match(expected, actual, tolerance):
                drift_entities.append(entity_id)
                
                reconciliation_actions.append(ReconciliationAction(
                    action_id=make_action_id(),
                    action_type=ReconciliationType.UPDATE,
                    target_entity=entity_id,
                    expected_value=str(expected),
                    actual_value=str(actual),
                    priority=3  # Lower priority - update needed
                ))
        
        # Calculate confidence based on match quality
        total_expected = len(expected_ids)
        if total_expected == 0:
            confidence = 1.0  # No expected states, nothing to reconcile
        else:
            matched = total_expected - len(missing) - len(drift_entities)
            confidence = max(0.0, min(1.0, matched / total_expected))
        
        match = len(missing) == 0 and len(extra) == 0 and len(drift_entities) == 0
        
        # Record reconciliation
        result = ReconciliationResult(
            match=match,
            confidence=confidence,
            expected_state=",".join(sorted(expected_ids)) if expected_ids else "none",
            actual_state=",".join(sorted(actual_ids)) if actual_ids else "none",
            drift_entities=drift_entities,
            missing_entities=list(missing),
            extra_entities=list(extra),
            reconciliation_actions=reconciliation_actions
        )
        
        self._reconciliation_history.append(result)
        self._last_reconciliation = time.time()
        
        return result
    
    def _states_match(
        self,
        expected: Dict[str, Any],
        actual: Dict[str, Any],
        tolerance: float
    ) -> bool:
        """Check if states match within tolerance."""
        # For now, do a simple check - in production this would be more sophisticated
        return expected == actual
    
    def get_reconciliation_history(
        self,
        limit: int = 100
    ) -> List[ReconciliationResult]:
        """Get recent reconciliation results."""
        return list(reversed(self._reconciliation_history))[:limit]
    
    def get_last_reconciliation_time(self) -> Optional[float]:
        """Get the timestamp of the last reconciliation."""
        return self._last_reconciliation


# =============================================================================
# State Drift Detector
# =============================================================================

@dataclass(frozen=True)
class DriftReport:
    """
    Report on state drift between expected and actual.
    
    Args:
        entity_id: Which entity has drifted
        
        drift_type: Type of drift (ADDED, REMOVED, MODIFIED)
        
        expected_value: What was expected
        actual_value: What was observed
        
        drift_magnitude: How much drift occurred (0.0-1.0)
    """
    
    entity_id: str
    
    drift_type: "DriftType"
    
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    
    drift_magnitude: float = 0.0


class DriftType(Enum):
    """Types of state drift."""
    
    ADDED = "added"           # Entity exists but shouldn't
    REMOVED = "removed"       # Entity missing but should exist
    MODIFIED = "modified"     # Entity state changed unexpectedly
    CORRUPTED = "corrupted"   # State is corrupted or invalid


class DriftDetector:
    """
    Detects and categorizes state drift.
    
    This can be used to identify when external changes have affected
    system state unexpectedly.
    """
    
    def __init__(self) -> None:
        """Initialize the drift detector."""
        self._baseline_states: Dict[str, Dict[str, Any]] = {}
        self._drift_thresholds: Dict[str, float] = {}  # entity_id -> tolerance
    
    def set_baseline_state(
        self,
        entity_id: str,
        state: Dict[str, Any]
    ) -> None:
        """Set a baseline state for an entity."""
        self._baseline_states[entity_id] = state
    
    def clear_baseline(self, entity_id: str) -> bool:
        """Clear baseline state for an entity."""
        if entity_id in self._baseline_states:
            del self._baseline_states[entity_id]
            return True
        return False
    
    def set_drift_threshold(
        self,
        entity_id: str,
        threshold: float
    ) -> None:
        """Set drift tolerance threshold for an entity."""
        self._drift_thresholds[entity_id] = max(0.0, min(1.0, threshold))
    
    async def detect_drift(
        self,
        current_states: Dict[str, Any]
    ) -> List[DriftReport]:
        """
        Detect state drift compared to baselines.
        
        Args:
            current_states: Current observed states
            
        Returns:
            List of drift reports
        """
        reports = []
        
        for entity_id, current_state in current_states.items():
            baseline = self._baseline_states.get(entity_id)
            
            if baseline is None:
                # No baseline - consider as added drift
                reports.append(DriftReport(
                    entity_id=entity_id,
                    drift_type=DriftType.ADDED,
                    actual_value=str(current_state),
                    drift_magnitude=1.0
                ))
                continue
            
            # Check for modified state
            if not self._states_match(baseline, current_state):
                reports.append(DriftReport(
                    entity_id=entity_id,
                    drift_type=DriftType.MODIFIED,
                    expected_value=str(baseline),
                    actual_value=str(current_state),
                    drift_magnitude=self._calculate_drift_magnitude(baseline, current_state)
                ))
        
        # Check for removed entities
        for entity_id in self._baseline_states:
            if entity_id not in current_states:
                reports.append(DriftReport(
                    entity_id=entity_id,
                    drift_type=DriftType.REMOVED,
                    expected_value=str(self._baseline_states[entity_id]),
                    drift_magnitude=1.0
                ))
        
        return reports
    
    def _states_match(
        self,
        baseline: Dict[str, Any],
        current: Dict[str, Any]
    ) -> bool:
        """Check if states match."""
        # Simple comparison - in production this would be more sophisticated
        return baseline == current
    
    def _calculate_drift_magnitude(
        self,
        baseline: Dict[str, Any],
        current: Dict[str, Any]
    ) -> float:
        """Calculate how much drift occurred (0.0-1.0)."""
        # Count mismatched keys as a percentage
        all_keys = set(baseline.keys()) | set(current.keys())
        
        if not all_keys:
            return 0.0
        
        mismatches = sum(
            1 for k in all_keys
            if baseline.get(k) != current.get(k)
        )
        
        return mismatches / len(all_keys)


# =============================================================================
# Reconciliation utilities
# =============================================================================

def determine_reconciliation_priority(result: ReconciliationResult) -> str:
    """
    Determine overall reconciliation priority based on result.
    
    Returns priority level string (CRITICAL, HIGH, MEDIUM, LOW).
    """
    if not result.match:
        # Check for critical issues first
        has_missing = len(result.missing_entities) > 0
        has_drift = len(result.drift_entities) > 0
        
        if has_missing:
            return "CRITICAL"  # Missing expected entities is serious
        elif has_drift and len(result.reconciliation_actions) > 5:
            return "HIGH"
    
    if result.confidence < 0.5:
        return "MEDIUM"
    
    return "LOW"


def format_reconciliation_summary(result: ReconciliationResult) -> Dict[str, Any]:
    """
    Format a reconciliation result as a summary for logging/reporting.
    
    Args:
        result: The reconciliation result
        
    Returns:
        Summary dictionary
    """
    return {
        "match": result.match,
        "confidence": round(result.confidence, 3),
        "expected_state": result.expected_state or "none",
        "actual_state": result.actual_state or "none",
        "drift_count": len(result.drift_entities),
        "missing_count": len(result.missing_entities),
        "extra_count": len(result.extra_entities),
        "actions_needed": len(result.reconciliation_actions),
    }