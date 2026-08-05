# Failure Domains Module
# ======================

"""
Failure domains and containment boundaries for Phase 3.7.10.

This module extends the basic FailureDomain enum with:
    - Domain hierarchy definitions (parent-child relationships)
    - Containment boundary specifications
    - Propagation rules between domains
    - Recovery capability declarations per domain

Domain Hierarchy:
    RUNTIME (root) → KERNEL → ENGINE → [COORDINATORS] → EXECUTION
                    ↓              ↓                  ↓
                SYSTEM        COMPONENT          WORKER/TASK

Propagation Path:
    Lower domains propagate failures upward until containment is achieved.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set
import time


# =============================================================================
# Extended Failure Domain with Containment Boundaries
# =============================================================================

@dataclass(frozen=True)
class DomainHierarchy:
    """
    Defines parent-child relationships between domains.
    
    Used for failure propagation analysis and containment boundary placement.
    """
    
    domain: "FailureDomain"
    
    # Parent domain (None = root level)
    parent: Optional["FailureDomain"] = None
    
    # Children domains (if any)
    children: List["FailureDomain"] = field(default_factory=list)
    
    # Containment boundary setting
    requires_boundary: bool = True
    
    # Recovery capability
    can_self_heal: bool = False
    can_contain: bool = True


class FailureDomain(Enum):
    """
    System domain where failure occurs.
    
    Each domain defines:
        - Canonical owner responsible for containment
        - Propagation path to higher levels
        - Restart/rollback/recovery capability
        - Fatal conditions specific to this domain
    
    Domains form a hierarchy:
        TASK → EXECUTOR → SCHEDULER → RUNTIME
        SERVICE → KERNEL → RUNTIME
    """
    
    # =============================================================================
    # Core Infrastructure (Root domains)
    # =============================================================================
    
    RUNTIME = "runtime"
    KERNEL = "kernel"
    ENGINE = "engine"
    
    # =============================================================================
    # Coordination Domains
    # =============================================================================
    
    MANAGER = "manager"
    SCHEDULER = "scheduler"
    EXECUTOR = "executor"
    
    # =============================================================================
    # Execution Unit Domains  
    # =============================================================================
    
    WORKER = "worker"
    SERVICE = "service"
    DAEMON = "daemon"
    
    # =============================================================================
    # External Dependencies
    # =============================================================================
    
    MODEL = "model"
    DEVICE = "device"
    GPU = "gpu"
    
    # =============================================================================
    # Resource Management
    # =============================================================================
    
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    RESOURCE = "resource"
    
    # =============================================================================
    # Configuration and Data
    # =============================================================================
    
    DATABASE = "database"
    CONFIGURATION = "configuration"
    
    # =============================================================================
    # Plugin/System
    # =============================================================================
    
    PLUGIN = "plugin"
    BACKGROUND_LOOP = "background_loop"
    
    # =============================================================================
    # External Providers
    # =============================================================================
    
    EXTERNAL_PROVIDER = "external_provider"


# =============================================================================
# Domain Hierarchy Configuration
# =============================================================================

DOMAIN_HIERARCHY: Dict[FailureDomain, DomainHierarchy] = {
    FailureDomain.RUNTIME: DomainHierarchy(
        domain=FailureDomain.RUNTIME,
        parent=None,
        children=[
            FailureDomain.KERNEL,
            FailureDomain.ENGINE,
        ],
        requires_boundary=True,
        can_self_heal=False,
        can_contain=True,
    ),
    FailureDomain.KERNEL: DomainHierarchy(
        domain=FailureDomain.KERNEL,
        parent=FailureDomain.RUNTIME,
        children=[
            FailureDomain.MANAGER,
            FailureDomain.SCHEDULER,
        ],
        requires_boundary=True,
        can_self_heal=False,
        can_contain=True,
    ),
    FailureDomain.ENGINE: DomainHierarchy(
        domain=FailureDomain.ENGINE,
        parent=FailureDomain.RUNTIME,
        children=[
            FailureDomain.EXECUTOR,
        ],
        requires_boundary=True,
        can_self_heal=False,
        can_contain=True,
    ),
    FailureDomain.MANAGER: DomainHierarchy(
        domain=FailureDomain.MANAGER,
        parent=FailureDomain.KERNEL,
        children=[],
        requires_boundary=False,
        can_self_heal=True,
        can_contain=True,
    ),
    FailureDomain.SCHEDULER: DomainHierarchy(
        domain=FailureDomain.SCHEDULER,
        parent=FailureDomain.KERNEL,
        children=[
            FailureDomain.EXECUTOR,
        ],
        requires_boundary=True,
        can_self_heal=False,
        can_contain=True,
    ),
    FailureDomain.EXECUTOR: DomainHierarchy(
        domain=FailureDomain.EXECUTOR,
        parent=FailureDomain.ENGINE,
        children=[
            FailureDomain.WORKER,
        ],
        requires_boundary=True,
        can_self_heal=False,
        can_contain=True,
    ),
    FailureDomain.WORKER: DomainHierarchy(
        domain=FailureDomain.WORKER,
        parent=FailureDomain.EXECUTOR,
        children=[],
        requires_boundary=False,
        can_self_heal=True,
        can_contain=True,
    ),
    FailureDomain.SERVICE: DomainHierarchy(
        domain=FailureDomain.SERVICE,
        parent=FailureDomain.RUNTIME,
        children=[
            FailureDomain.DAEMON,
        ],
        requires_boundary=True,
        can_self_heal=True,
        can_contain=True,
    ),
    FailureDomain.DAEMON: DomainHierarchy(
        domain=FailureDomain.DAEMON,
        parent=FailureDomain.SERVICE,
        children=[],
        requires_boundary=False,
        can_self_heal=True,
        can_contain=True,
    ),
    FailureDomain.MODEL: DomainHierarchy(
        domain=FailureDomain.MODEL,
        parent=FailureDomain.EXTERNAL_PROVIDER,
        children=[],
        requires_boundary=True,
        can_self_heal=False,
        can_contain=True,
    ),
    FailureDomain.DEVICE: DomainHierarchy(
        domain=FailureDomain.DEVICE,
        parent=FailureDomain.EXTERNAL_PROVIDER,
        children=[
            FailureDomain.GPU,
        ],
        requires_boundary=True,
        can_self_heal=False,
        can_contain=True,
    ),
    FailureDomain.GPU: DomainHierarchy(
        domain=FailureDomain.GPU,
        parent=FailureDomain.DEVICE,
        children=[],
        requires_boundary=False,
        can_self_heal=True,
        can_contain=True,
    ),
    FailureDomain.MEMORY: DomainHierarchy(
        domain=FailureDomain.MEMORY,
        parent=FailureDomain.RESOURCE,
        children=[],
        requires_boundary=False,
        can_self_heal=False,
        can_contain=True,
    ),
    FailureDomain.STORAGE: DomainHierarchy(
        domain=FailureDomain.STORAGE,
        parent=FailureDomain.RESOURCE,
        children=[],
        requires_boundary=False,
        can_self_heal=False,
        can_contain=True,
    ),
    FailureDomain.NETWORK: DomainHierarchy(
        domain=FailureDomain.NETWORK,
        parent=FailureDomain.RESOURCE,
        children=[],
        requires_boundary=False,
        can_self_heal=False,
        can_contain=True,
    ),
    FailureDomain.RESOURCE: DomainHierarchy(
        domain=FailureDomain.RESOURCE,
        parent=FailureDomain.RUNTIME,
        children=[
            FailureDomain.MEMORY,
            FailureDomain.STORAGE,
            FailureDomain.NETWORK,
        ],
        requires_boundary=True,
        can_self_heal=False,
        can_contain=True,
    ),
}


# =============================================================================
# Containment Boundary
# =============================================================================

@dataclass(frozen=True)
class ContainmentBoundary:
    """
    A boundary that prevents failure propagation between domains.
    
    Boundaries are placed at domain transition points and must be
    explicitly crossed during recovery operations.
    
    Args:
        boundary_id: Unique identifier for this boundary
        source_domain: Where failures come from
        target_domain: Where failures would propagate to
        
        active: Whether the boundary is currently blocking
        barrier_id: ID of associated barrier if any
        
        containment_timeout_seconds: How long to wait at boundary
    """
    
    boundary_id: str
    
    source_domain: FailureDomain
    target_domain: FailureDomain
    
    active: bool = True
    barrier_id: Optional[str] = None
    
    containment_timeout_seconds: float = 30.0
    
    @property
    def is_active(self) -> bool:
        """Check if boundary is actively blocking propagation."""
        return self.active


@dataclass(frozen=True)
class DomainTransition:
    """
    Defines a valid transition between domains for failure propagation.
    
    Args:
        from_domain: Source domain
        to_domain: Target domain
        
        direction: UPWARD or DOWNWARD
        requires_boundary: Whether a boundary must exist
        can_be_contained: Whether the failure can be contained at this level
    """
    
    from_domain: FailureDomain
    to_domain: FailureDomain
    
    direction: "TransitionDirection"
    requires_boundary: bool = True
    can_be_contained: bool = True


class TransitionDirection(Enum):
    """Direction of domain transition."""
    
    UPWARD = "upward"     # Toward root (runtime)
    DOWNWARD = "downward"  # Away from root
    LATERAL = "lateral"   # Same level


# =============================================================================
# Recovery Capability by Domain
# =============================================================================

@dataclass(frozen=True)
class DomainRecoveryCapabilities:
    """
    Declares recovery capabilities available in a domain.
    
    Args:
        domain: Which domain these capabilities apply to
        
        can_retry: Can retry operations within this domain?
        can_rollback: Can rollback state within this domain?
        can_restart: Can restart components within this domain?
        
        has_state_store: Does this domain have persistent state?
        state_preservation_supported: Can state be preserved during recovery?
    """
    
    domain: FailureDomain
    
    can_retry: bool = False
    can_rollback: bool = False
    can_restart: bool = False
    
    has_state_store: bool = False
    state_preservation_supported: bool = False


DOMAIN_RECOVERY_CAPABILITIES: Dict[FailureDomain, DomainRecoveryCapabilities] = {
    FailureDomain.RUNTIME: DomainRecoveryCapabilities(
        domain=FailureDomain.RUNTIME,
        can_retry=False,
        can_rollback=False,
        can_restart=True,
        has_state_store=False,
        state_preservation_supported=False,
    ),
    FailureDomain.KERNEL: DomainRecoveryCapabilities(
        domain=FailureDomain.KERNEL,
        can_retry=False,
        can_rollback=False,
        can_restart=True,
        has_state_store=False,
        state_preservation_supported=False,
    ),
    FailureDomain.ENGINE: DomainRecoveryCapabilities(
        domain=FailureDomain.ENGINE,
        can_retry=False,
        can_rollback=False,
        can_restart=True,
        has_state_store=False,
        state_preservation_supported=False,
    ),
    FailureDomain.MANAGER: DomainRecoveryCapabilities(
        domain=FailureDomain.MANAGER,
        can_retry=True,
        can_rollback=True,
        can_restart=True,
        has_state_store=True,
        state_preservation_supported=True,
    ),
    FailureDomain.SCHEDULER: DomainRecoveryCapabilities(
        domain=FailureDomain.SCHEDULER,
        can_retry=False,
        can_rollback=True,
        can_restart=True,
        has_state_store=True,
        state_preservation_supported=True,
    ),
    FailureDomain.EXECUTOR: DomainRecoveryCapabilities(
        domain=FailureDomain.EXECUTOR,
        can_retry=True,
        can_rollback=True,
        can_restart=True,
        has_state_store=False,
        state_preservation_supported=True,
    ),
    FailureDomain.WORKER: DomainRecoveryCapabilities(
        domain=FailureDomain.WORKER,
        can_retry=True,
        can_rollback=True,
        can_restart=True,
        has_state_store=False,
        state_preservation_supported=True,
    ),
    FailureDomain.SERVICE: DomainRecoveryCapabilities(
        domain=FailureDomain.SERVICE,
        can_retry=True,
        can_rollback=True,
        can_restart=True,
        has_state_store=True,
        state_preservation_supported=True,
    ),
    FailureDomain.DAEMON: DomainRecoveryCapabilities(
        domain=FailureDomain.DAEMON,
        can_retry=True,
        can_rollback=True,
        can_restart=True,
        has_state_store=False,
        state_preservation_supported=True,
    ),
}


# =============================================================================
# Domain Utilities
# =============================================================================

def get_domain_hierarchy(domain: FailureDomain) -> Optional[DomainHierarchy]:
    """Get the hierarchy configuration for a domain."""
    return DOMAIN_HIERARCHY.get(domain)


def is_root_domain(domain: FailureDomain) -> bool:
    """Check if this domain is at the root of the hierarchy."""
    hierarchy = get_domain_hierarchy(domain)
    return hierarchy is not None and hierarchy.parent is None


def get_parent_domain(domain: FailureDomain) -> Optional[FailureDomain]:
    """Get the parent domain for propagation analysis."""
    hierarchy = get_domain_hierarchy(domain)
    return hierarchy.parent if hierarchy else None


def get_ancestor_chain(domain: FailureDomain) -> List[FailureDomain]:
    """
    Get chain of ancestor domains from this domain to root.
    
    Returns list in order from immediate parent to root.
    """
    chain = []
    current = domain
    while True:
        parent = get_parent_domain(current)
        if parent is None:
            break
        chain.append(parent)
        current = parent
    return chain


def get_containment_boundaries(domain: FailureDomain) -> List[ContainmentBoundary]:
    """Get all containment boundaries that affect a domain."""
    boundaries = []
    
    # For each ancestor, there's a boundary between it and this domain
    for ancestor in get_ancestor_chain(domain):
        boundaries.append(ContainmentBoundary(
            boundary_id=f"boundary_{domain.value}_to_{ancestor.value}",
            source_domain=domain,
            target_domain=ancestor,
            active=True,
            containment_timeout_seconds=30.0,
        ))
    
    return boundaries


def get_recovery_capabilities(domain: FailureDomain) -> DomainRecoveryCapabilities:
    """Get recovery capabilities for a domain."""
    return DOMAIN_RECOVERY_CAPABILITIES.get(domain, DomainRecoveryCapabilities(domain=domain))


@dataclass(frozen=True)
class Transition:
    """A single transition in a propagation path."""
    
    from_domain: FailureDomain
    to_domain: FailureDomain
    
    direction: TransitionDirection
    requires_boundary: bool = True
    can_be_contained: bool = True


def determine_propagation_path(failure_domain: FailureDomain) -> List[Transition]:
    """
    Determine the failure propagation path from a given domain.
    
    Returns list of transitions in order from source to root.
    """
    transitions = []
    current = failure_domain
    
    while True:
        parent = get_parent_domain(current)
        if parent is None:
            break
        
        hierarchy = get_domain_hierarchy(current)
        requires_boundary = hierarchy.requires_boundary if hierarchy else True
        
        transitions.append(Transition(
            from_domain=current,
            to_domain=parent,
            direction=TransitionDirection.UPWARD,
            requires_boundary=requires_boundary,
            can_be_contained=hierarchy.can_contain if hierarchy else True
        ))
        
        current = parent
    
    return transitions


def find_common_ancestor(domain_a: FailureDomain, domain_b: FailureDomain) -> Optional[FailureDomain]:
    """Find the lowest common ancestor of two domains."""
    chain_a = set(get_ancestor_chain(domain_a))
    
    current = domain_b
    while True:
        if current in chain_a:
            return current
        parent = get_parent_domain(current)
        if parent is None:
            break
        current = parent
    
    # Check if either is ancestor of the other
    if domain_b in chain_a:
        return domain_b
    if domain_a in set(get_ancestor_chain(domain_b)):
        return domain_a
    
    return None


def domains_are_siblings(domain_a: FailureDomain, domain_b: FailureDomain) -> bool:
    """Check if two domains share the same parent (are siblings)."""
    parent_a = get_parent_domain(domain_a)
    parent_b = get_parent_domain(domain_b)
    return parent_a is not None and parent_a == parent_b


def calculate_propagation_delay(domain: FailureDomain) -> float:
    """
    Calculate expected propagation delay for failures from this domain.
    
    This estimates how long it takes for a failure to propagate from
    the given domain up through the hierarchy.
    """
    delay = 0.0
    
    # Base delay per level (in seconds)
    base_delay = 0.5
    
    # Add delay for each boundary crossed
    transitions = get_ancestor_chain(domain)
    
    for i, _ in enumerate(transitions):
        # Each boundary adds propagation delay
        hierarchy = get_domain_hierarchy(domain)
        if hierarchy and hierarchy.requires_boundary:
            delay += base_delay * (i + 1)  # Increasing delay with distance
    
    return min(delay, 30.0)  # Cap at 30 seconds


from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .types import FailureKind


# Use string reference for forward compatibility
def is_fatal_in_domain(
    failure_kind: Union[str, "FailureKind"], 
    domain: FailureDomain
) -> bool:
    """
    Check if a failure kind is considered fatal in the given domain.
    
    Some domains treat certain failures as terminal.
    """
    # These kinds are always fatal regardless of domain
    if failure_kind in (FailureKind.FATAL, FailureKind.PANIC):
        return True
    
    # Domain-specific fatal conditions
    if domain == FailureDomain.KERNEL:
        # Kernel-level failures that can't be contained
        if failure_kind in (
            FailureKind.PROGRAMMING,
            FailureKind.INTEGRITY,
            FailureKind.STATE_CORRUPTION
        ):
            return True
    
    if domain == FailureDomain.ENGINE:
        # Engine-level fatal conditions
        if failure_kind == FailureKind.DATA_CORRUPTION:
            return True
    
    return False


def get_containment_boundary_for_domain(domain: FailureDomain) -> Optional[ContainmentBoundary]:
    """
    Get the primary containment boundary for a domain.
    
    This is the boundary that must be crossed when propagating failures
    from this domain to its parent.
    """
    hierarchy = get_domain_hierarchy(domain)
    if not hierarchy or not hierarchy.requires_boundary:
        return None
    
    parent = get_parent_domain(domain)
    if not parent:
        return None
    
    return ContainmentBoundary(
        boundary_id=f"boundary_{domain.value}",
        source_domain=domain,
        target_domain=parent,
        active=True,
        containment_timeout_seconds=hierarchy.can_contain * 30.0,  # 30s if can contain
    )