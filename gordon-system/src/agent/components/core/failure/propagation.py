# Failure Propagation Module
# ===========================

"""
Failure propagation rules and path analysis for Phase 3.7.10.

This module handles:
    - Determining failure propagation paths through the domain hierarchy
    - Calculating propagation delays between domains
    - Identifying containment points in the propagation path
    - Predicting affected domains from a source failure
    
Key concepts:
    - UPWARD propagation: failures propagate toward root (runtime)
    - DOWNWARD propagation: recovery actions propagate downward
    - LATERAL propagation: failures affecting sibling domains
    
Propagation Rules:
    1. Failures always propagate UPWARD until contained
    2. Containment boundaries block propagation at domain transitions
    3. Propagation delay increases with each boundary crossed
    4. Root domain (runtime) cannot propagate further - must be contained locally
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple
import time

from .types import FailureKind, FailureSeverity, RuntimeFailure
from .domains import (
    FailureDomain,
    DomainHierarchy,
    get_domain_hierarchy,
    get_parent_domain,
    get_ancestor_chain,
    TransitionDirection,
)


# =============================================================================
# Propagation Event
# =============================================================================

@dataclass(frozen=True)
class PropagationEvent:
    """
    A single propagation event in the failure chain.
    
    Args:
        source_domain: Where this propagation originated from
        target_domain: Which domain was affected
        
        direction: UPWARD, DOWNWARD, or LATERAL
        delay_seconds: How long propagation took
        
        failure_kind: Kind of failure being propagated
        severity_at_source: Severity at the origin
        severity_at_target: Severity when it reached this domain
        
        blocked_by_boundary: Whether a boundary prevented propagation
    """
    
    event_id: str
    
    source_domain: FailureDomain
    target_domain: FailureDomain
    
    direction: TransitionDirection
    delay_seconds: float = 0.0
    
    failure_kind: Optional[FailureKind] = None
    severity_at_source: Optional[FailureSeverity] = None
    severity_at_target: Optional[FailureSeverity] = None
    
    blocked_by_boundary: bool = False


# =============================================================================
# Propagation Path Analysis
# =============================================================================

@dataclass(frozen=True)
class PropagationPath:
    """
    A complete failure propagation path from source to root.
    
    Args:
        source_domain: Where the failure originated
        target_domains: All domains affected in order
        
        events: Individual propagation events
        total_delay_seconds: Total time for full propagation
        
        containment_points: Domains where containment was applied
    """
    
    path_id: str
    
    source_domain: FailureDomain
    target_domains: List[FailureDomain]
    
    events: List[PropagationEvent] = field(default_factory=list)
    total_delay_seconds: float = 0.0
    
    containment_points: List[str] = field(default_factory=list)


class PropagationAnalysis:
    """
    Analyze how a failure would propagate through the system.
    
    This is used for:
        - Predicting affected systems before propagation completes
        - Planning containment boundaries
        - Estimating recovery scope
    """
    
    def __init__(self) -> None:
        """Initialize the propagation analyzer."""
        self._propagation_rules = self._build_propagation_rules()
    
    def _build_propagation_rules(self) -> Dict[str, Dict]:
        """Build rule mappings for propagation decisions."""
        return {
            "transient": {
                "can_propagate": True,
                "severity_decay": 0.0,  # Transient failures maintain severity
            },
            "recoverable": {
                "can_propagate": True,
                "severity_decay": 0.1,  # May lose some severity
            },
            "fatal": {
                "can_propagate": False,  # Fatal stops propagation (handled locally)
                "severity_decay": 1.0,
            },
            "data_corruption": {
                "can_propagate": True,
                "severity_decay": 0.2,  # Corruption spreads but at reduced impact
            },
        }
    
    def analyze_propagation(
        self,
        failure: RuntimeFailure,
        source_domain: Optional[FailureDomain] = None
    ) -> PropagationPath:
        """
        Analyze how a failure would propagate through the system.
        
        Args:
            failure: The failure to analyze
            source_domain: Override the failure's domain (optional)
            
        Returns:
            PropagationPath with all affected domains and events
        """
        source = source_domain or failure.domain
        
        # Get propagation path from source to root
        ancestor_chain = get_ancestor_chain(source)
        target_domains = [source] + ancestor_chain
        
        # Build propagation events
        events = []
        total_delay = 0.0
        
        for i, target in enumerate(ancestor_chain):
            hierarchy = get_domain_hierarchy(target)
            
            event = PropagationEvent(
                event_id=f"prop_{failure.failure_id}_{target.value}",
                source_domain=source,
                target_domain=target,
                direction=TransitionDirection.UPWARD,
                delay_seconds=self._calculate_propagation_delay(source, target),
                failure_kind=failure.kind,
                severity_at_source=failure.severity,
                severity_at_target=self._apply_severity_decay(failure.severity, i),
                blocked_by_boundary=False if hierarchy else True
            )
            
            events.append(event)
            total_delay += event.delay_seconds
        
        return PropagationPath(
            path_id=f"prop_path_{failure.failure_id}",
            source_domain=source,
            target_domains=target_domains,
            events=events,
            total_delay_seconds=total_delay,
            containment_points=[e.target_domain.value for e in events if not e.blocked_by_boundary]
        )
    
    def _calculate_propagation_delay(
        self, 
        source: FailureDomain, 
        target: FailureDomain
    ) -> float:
        """Calculate expected propagation delay between domains."""
        base_delay = 0.5
        
        # Get distance in hierarchy
        chain = get_ancestor_chain(source)
        
        try:
            distance = chain.index(target) + 1
        except ValueError:
            # Target not in chain - use default
            return base_delay
        
        # Add delay per boundary crossed
        delay = base_delay * min(distance, 5)  # Cap at 5 boundaries
        
        return delay
    
    def _apply_severity_decay(
        self, 
        severity: FailureSeverity,
        propagation_level: int
    ) -> FailureSeverity:
        """Apply severity decay based on propagation level."""
        severity_order = [
            FailureSeverity.INFO,
            FailureSeverity.NOTICE,
            FailureSeverity.WARNING,
            FailureSeverity.ERROR,
            FailureSeverity.CRITICAL,
            FailureSeverity.FATAL,
            FailureSeverity.PANIC,
        ]
        
        try:
            current_idx = severity_order.index(severity)
            
            # Decay by at most 2 levels
            new_idx = max(0, current_idx - min(propagation_level, 2))
            
            return severity_order[new_idx]
        except ValueError:
            return severity
    
    def get_all_affected_domains(
        self,
        failure: RuntimeFailure,
        containment_applied_at: Optional[FailureDomain] = None
    ) -> List[FailureDomain]:
        """
        Get list of all domains affected by this failure.
        
        If containment is applied at a specific domain, don't propagate beyond it.
        
        Args:
            failure: The failure being analyzed
            containment_applied_at: Domain where containment was applied (optional)
            
        Returns:
            List of affected domains in propagation order
        """
        ancestor_chain = get_ancestor_chain(failure.domain)
        affected = [failure.domain] + ancestor_chain
        
        # If containment applied, truncate the chain
        if containment_applied_at and containment_applied_at != failure.domain:
            try:
                containment_idx = [d.value for d in affected].index(containment_applied_at.value)
                affected = affected[:containment_idx + 1]
            except ValueError:
                pass
        
        return affected
    
    def predict_propagation_time(
        self,
        failure: RuntimeFailure,
        target_domain: Optional[FailureDomain] = None
    ) -> float:
        """
        Predict how long until failure reaches a specific domain.
        
        Args:
            failure: The failure to analyze
            target_domain: Target domain (None = predict full propagation)
            
        Returns:
            Estimated time in seconds for propagation
        """
        source = failure.domain
        
        if target_domain is None:
            # Predict full propagation to root
            return self._calculate_propagation_delay(source, FailureDomain.RUNTIME)
        
        chain = get_ancestor_chain(source)
        
        try:
            target_idx = [d.value for d in chain].index(target_domain.value)
            
            # Sum delays up to and including the target
            total_delay = 0.0
            for i, domain in enumerate(chain[:target_idx + 1]):
                hierarchy = get_domain_hierarchy(domain)
                
                base_delay = 0.5
                if hierarchy and hierarchy.requires_boundary:
                    base_delay *= (i + 1)
                
                total_delay += base_delay
            
            return min(total_delay, 30.0)  # Cap at 30 seconds
        except ValueError:
            return 30.0


# =============================================================================
# Propagation Path Builder
# =============================================================================

@dataclass(frozen=True)
class ContainmentBoundaryInfo:
    """Information about a containment boundary."""
    
    boundary_id: str
    source_domain: FailureDomain
    target_domain: FailureDomain
    active: bool = True


class PropagationPathBuilder:
    """
    Build and analyze failure propagation paths.
    
    This builder constructs complete propagation paths including all
    intermediate boundaries and propagation events.
    """
    
    def __init__(self) -> None:
        """Initialize the path builder."""
        self._analyzer = PropagationAnalysis()
    
    def build_path(
        self,
        source_domain: FailureDomain,
        failure_kind: Optional[FailureKind] = None
    ) -> PropagationPath:
        """
        Build a propagation path from a source domain.
        
        Args:
            source_domain: Where the failure originated
            failure_kind: Kind of failure (optional, for rule application)
            
        Returns:
            Complete propagation path with all details
        """
        ancestor_chain = get_ancestor_chain(source_domain)
        
        events = []
        total_delay = 0.0
        
        for target in ancestor_chain:
            hierarchy = get_domain_hierarchy(target)
            
            # Calculate delay
            delay = self._calculate_boundary_delay(hierarchy) if hierarchy else 0.5
            
            event = PropagationEvent(
                event_id=f"prop_event_{source_domain.value}_to_{target.value}",
                source_domain=source_domain,
                target_domain=target,
                direction=TransitionDirection.UPWARD,
                delay_seconds=delay,
                failure_kind=failure_kind,
                blocked_by_boundary=False if hierarchy else True
            )
            
            events.append(event)
            total_delay += delay
        
        return PropagationPath(
            path_id=f"prop_path_{source_domain.value}_{int(time.time())}",
            source_domain=source_domain,
            target_domains=[source_domain] + ancestor_chain,
            events=events,
            total_delay_seconds=min(total_delay, 30.0),
            containment_points=[]
        )
    
    def _calculate_boundary_delay(self, hierarchy: DomainHierarchy) -> float:
        """Calculate delay at a domain boundary."""
        if not hierarchy.requires_boundary:
            return 0.1
        
        # Base delay with boundary overhead
        base = 0.5
        
        # Add delay based on recovery capabilities
        if hierarchy.can_contain:
            base += 0.3  # Containment adds overhead
        
        if hierarchy.can_self_heal:
            base -= 0.2  # Self-healing reduces propagation time
        
        return max(0.1, min(base, 5.0))  # Clamp between 0.1 and 5.0
    
    def find_containment_points(
        self,
        source_domain: FailureDomain
    ) -> List[ContainmentBoundaryInfo]:
        """
        Find all potential containment points for a domain.
        
        These are boundaries where failure propagation can be stopped.
        
        Args:
            source_domain: The domain to analyze
            
        Returns:
            List of containment boundary info in propagation order
        """
        chain = get_ancestor_chain(source_domain)
        
        boundaries = []
        current = source_domain
        
        for target in chain:
            hierarchy = get_domain_hierarchy(current)
            
            if hierarchy and hierarchy.requires_boundary:
                boundaries.append(ContainmentBoundaryInfo(
                    boundary_id=f"boundary_{current.value}",
                    source_domain=current,
                    target_domain=target,
                    active=True
                ))
            
            current = target
        
        return boundaries


# =============================================================================
# Propagation Simulator
# =============================================================================

@dataclass(frozen=True)
class PropagationResult:
    """
    Result of a propagation simulation.
    
    Args:
        success: Whether propagation completed (not blocked)
        affected_domains: All domains that received the failure
        total_delay_seconds: Total propagation time
        containment_applied_at: Where containment was applied (if any)
    """
    
    success: bool
    affected_domains: List[FailureDomain]
    total_delay_seconds: float = 0.0
    containment_applied_at: Optional[FailureDomain] = None


class PropagationSimulator:
    """
    Simulate failure propagation with configurable parameters.
    
    This can be used for testing, planning, and prediction of how
    failures would affect the system under different conditions.
    """
    
    def __init__(self) -> None:
        """Initialize the simulator."""
        self._analyzer = PropagationAnalysis()
        self._boundary_active: Dict[str, bool] = {}
    
    def set_boundary_state(self, boundary_id: str, active: bool) -> None:
        """Set whether a specific boundary is active."""
        self._boundary_active[boundary_id] = active
    
    def simulate_propagation(
        self,
        source_domain: FailureDomain,
        failure_kind: Optional[FailureKind] = None
    ) -> PropagationResult:
        """
        Simulate how a failure would propagate.
        
        Args:
            source_domain: Where the failure originates
            failure_kind: Kind of failure (for rule application)
            
        Returns:
            PropagationResult with simulation outcome
        """
        chain = get_ancestor_chain(source_domain)
        
        affected = [source_domain]
        total_delay = 0.0
        
        for target in chain:
            boundary_id = f"boundary_{source_domain.value}_to_{target.value}"
            is_active = self._boundary_active.get(boundary_id, True)
            
            if not is_active:
                # Propagation blocked at this boundary
                return PropagationResult(
                    success=False,
                    affected_domains=affected,
                    total_delay_seconds=total_delay,
                    containment_applied_at=target
                )
            
            hierarchy = get_domain_hierarchy(target)
            delay = self._calculate_boundary_delay(hierarchy) if hierarchy else 0.5
            
            total_delay += delay
            affected.append(target)
        
        return PropagationResult(
            success=True,
            affected_domains=affected,
            total_delay_seconds=min(total_delay, 30.0),
            containment_applied_at=None
        )
    
    def _calculate_boundary_delay(self, hierarchy: Optional[DomainHierarchy]) -> float:
        """Calculate delay at a boundary."""
        if not hierarchy or not hierarchy.requires_boundary:
            return 0.1
        
        base = 0.5
        if hierarchy.can_contain:
            base += 0.3
        
        return max(0.1, min(base, 5.0))


# =============================================================================
# Propagation Path Utilities
# =============================================================================

def find_propagation_path(
    source_domain: FailureDomain,
    target_domain: Optional[FailureDomain] = None
) -> List[PropagationEvent]:
    """
    Find the propagation path from one domain to another.
    
    Args:
        source_domain: Starting domain
        target_domain: Target domain (None = go to root)
        
    Returns:
        List of propagation events in order
    """
    chain = get_ancestor_chain(source_domain)
    
    if target_domain is not None and target_domain != FailureDomain.RUNTIME:
        try:
            end_idx = [d.value for d in chain].index(target_domain.value) + 1
            chain = chain[:end_idx]
        except ValueError:
            pass
    
    events = []
    current = source_domain
    
    for target in chain:
        event = PropagationEvent(
            event_id=f"prop_{current.value}_to_{target.value}",
            source_domain=current,
            target_domain=target,
            direction=TransitionDirection.UPWARD,
            delay_seconds=0.5
        )
        
        events.append(event)
        current = target
    
    return events


def get_containment_points_for_failure(
    failure: RuntimeFailure
) -> List[str]:
    """
    Get containment points for a specific failure.
    
    These are domains where the failure can be contained before
    propagating further up the hierarchy.
    
    Args:
        failure: The failure to analyze
        
    Returns:
        List of domain values that can serve as containment points
    """
    chain = get_ancestor_chain(failure.domain)
    
    # First domain is always a valid containment point
    result = [failure.domain.value]
    
    for domain in chain:
        hierarchy = get_domain_hierarchy(domain)
        
        if hierarchy and hierarchy.can_contain:
            result.append(domain.value)
    
    return result


def predict_failure_scope(
    failure: RuntimeFailure,
    containment_threshold: int = 3
) -> Tuple[List[FailureDomain], bool]:
    """
    Predict the full scope of a failure.
    
    Args:
        failure: The failure to analyze
        containment_threshold: How many boundaries to try before giving up
        
    Returns:
        Tuple of (affected domains, fully_propagated)
    """
    chain = get_ancestor_chain(failure.domain)
    affected = [failure.domain]
    
    containment_count = 0
    
    for domain in chain:
        hierarchy = get_domain_hierarchy(domain)
        
        if not hierarchy or not hierarchy.can_contain:
            # Cannot contain here, continue propagating
            affected.append(domain)
            continue
        
        containment_count += 1
        
        if containment_count >= containment_threshold:
            # Reached threshold - stop here
            return affected, False
        
        affected.append(domain)
    
    # Propagated to root
    return affected, True


def get_propagation_delay_matrix() -> Dict[str, Dict[str, float]]:
    """
    Get a matrix of propagation delays between all domain pairs.
    
    Returns:
        Dict mapping source_domain -> {target_domain: delay_seconds}
    """
    matrix = {}
    
    for source in FailureDomain:
        chain = get_ancestor_chain(source)
        
        target_delays = {source.value: 0.0}
        
        current = source
        total_delay = 0.0
        
        for target in chain:
            hierarchy = get_domain_hierarchy(target)
            
            if hierarchy and hierarchy.requires_boundary:
                base_delay = 0.5
                if hierarchy.can_contain:
                    base_delay += 0.3
                
                total_delay += max(0.1, min(base_delay, 5.0))
            
            target_delays[target.value] = total_delay
            current = target
        
        matrix[source.value] = target_delays
    
    return matrix