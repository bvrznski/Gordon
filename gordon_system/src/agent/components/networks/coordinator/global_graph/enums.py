# Gordon Cognitive Architecture - Phase 4.11.4
# ===========================================

"""
Global Coordination Graph Enums and Kinds
=========================================

Canonical enumerations for the Global Coordination Graph.

GRAPHLAW-001: All enums are deeply immutable to ensure deterministic behavior.
GRAPHLAW-002: Kinds are canonical and stable across revisions.
"""

from __future__ import annotations

from enum import Enum, auto
from dataclasses import dataclass


# =============================================================================
# GRAPH NODE KINDS
# =============================================================================

class CoordinationGraphNodeKind(Enum):
    """
    Canonical kinds of nodes in the Global Coordination Graph.
    
    GRAPHLAW-011: Node kinds are canonical and stable
    GRAPHLAW-012: Every node possesses exactly one kind
    GRAPHLAW-013: Kinds are mutually exclusive
    """
    # Core network nodes (persistent across revisions)
    NETWORK = auto()
    """Base kind for all coordinated cognitive networks."""
    
    ALERTING_NETWORK = auto()
    DEFAULT_NETWORK = auto()
    EXECUTIVE_NETWORK = auto()
    FOCUSING_NETWORK = auto()
    ORIENTED_NETWORK = auto()
    PREDICTIVE_NETWORK = auto()
    REWARD_NETWORK = auto()
    SALIENCE_NETWORK = auto()
    SENSORIMOTOR_NETWORK = auto()
    WORKSPACE_NETWORK = auto()
    
    # Revision-scoped network projections
    NETWORK_PROJECTION = auto()
    """Network projection for a specific coordination cycle."""
    
    ALERTING_PROJECTION = auto()
    DEFAULT_PROJECTION = auto()
    EXECUTIVE_PROJECTION = auto()
    FOCUSING_PROJECTION = auto()
    ORIENTED_PROJECTION = auto()
    PREDICTIVE_PROJECTION = auto()
    REWARD_PROJECTION = auto()
    SALIENCE_PROJECTION = auto()
    SENSORIMOTOR_PROJECTION = auto()
    WORKSPACE_PROJECTION = auto()
    
    # Capability and requirement nodes
    CAPABILITY = auto()
    """A capability that can be provided by a network."""
    
    REQUIREMENT = auto()
    """A requirement that must be satisfied for coordination."""
    
    REQUIREMENT_SATISFACTION = auto()
    """Record of how a requirement is satisfied."""
    
    PROVIDER_CANDIDATE = auto()
    """Candidate network for providing a capability."""
    
    PROVIDER_SELECTION = auto()
    """Selected provider for a capability."""
    
    # Dependency nodes
    DEPENDENCY = auto()
    """A dependency relationship between coordination elements."""
    
    CONSTRAINT = auto()
    """A constraint limiting coordination options."""
    
    # Transition and interaction nodes
    TRANSITION_INTENTION = auto()
    """Declared transition intention from a network."""
    
    INTERACTION = auto()
    """Interaction relation between coordination elements."""
    
    CONFLICT = auto()
    """Conflict between coordination elements."""
    
    DEADLOCK = auto()
    """Deadlock state identified during coordination."""
    
    SYNCHRONIZATION_GROUP = auto()
    """Group of nodes that must synchronize."""
    
    DEPENDENCY_LAYER = auto()
    """Layer in the dependency hierarchy."""
    
    SYNCHRONIZATION_BARRIER = auto()
    """Synchronization barrier for a coordination cycle."""
    
    # Coordination artifacts
    COORDINATION_SNAPSHOT = auto()
    """Snapshot of coordination state at a point in time."""
    
    COORDINATION_DELTA = auto()
    """Delta representing changes between coordination states."""
    
    COORDINATION_PLAN = auto()
    """Coordination plan for a specific cycle."""
    
    PLAN_ALTERNATIVE = auto()
    """Alternative plan option."""
    
    COORDINATION_EPOCH = auto()
    """Epoch containing multiple coordination cycles."""
    
    COORDINATION_CYCLE = auto()
    """Single coordination cycle."""
    
    COORDINATION_STATE = auto()
    """Coordination state for a specific cycle."""
    
    STATE_PUBLICATION = auto()
    """Publication of coordination state to consumers."""
    
    CONSUMER_VIEW = auto()
    """View of the graph from a consumer's perspective."""
    
    # Policy and semantic nodes
    POLICY = auto()
    """Coordination policy governing behavior."""
    
    FINDING = auto()
    """Finding discovered during graph construction or validation."""
    
    LIMITATION = auto()
    """Limitation on graph completeness or quality."""
    
    DOMAIN = auto()
    """Semantic domain (e.g., language, navigation)."""
    
    PARTITION = auto()
    """Semantic partition of the graph."""
    
    COMPONENT = auto()
    """Connected component in the graph topology."""
    
    CONTEXT = auto()
    """Context information for coordination."""
    
    # Revision management
    GRAPH_REVISION = auto()
    """Revision of the global coordination graph."""
    
    GRAPH_SNAPSHOT = auto()
    """Snapshot of a specific graph revision."""
    
    GRAPH_DELTA = auto()
    """Delta between two graph revisions."""
    
    UNKNOWN = auto()
    """Unknown node kind."""


# =============================================================================
# GRAPH EDGE KINDS
# =============================================================================

class CoordinationGraphEdgeKind(Enum):
    """
    Canonical kinds of edges in the Global Coordination Graph.
    
    GRAPHLAW-021: Edge kinds are canonical and stable
    GRAPHLAW-022: Every edge possesses exactly one kind
    GRAPHLAW-023: Kinds preserve semantic directionality
    """
    # Projection relationships
    PROJECTS = auto()
    """Network projects a specific coordination state."""
    
    PROVIDES = auto()
    """Network provides a capability."""
    
    REQUIRES = auto()
    """Network requires a capability or dependency."""
    
    SATISFIES = auto()
    """Capability satisfies a requirement."""
    
    PARTIALLY_SATISFIES = auto()
    """Capability partially satisfies a requirement with limitations."""
    
    CANDIDATE_PROVIDER_FOR = auto()
    """Node is a candidate provider for a capability."""
    
    SELECTED_PROVIDER_FOR = auto()
    """Node was selected as provider for a capability."""
    
    FALLBACK_PROVIDER_FOR = auto()
    """Node serves as fallback provider for a capability."""
    
    # Dependency relationships
    DEPENDS_ON = auto()
    """Node depends on another node."""
    
    REQUIRES_BEFORE = auto()
    """Node requires that prerequisite completes first."""
    
    REQUIRES_AFTER = auto()
    """Node requires that prerequisite completes after."""
    
    REQUIRES_TOGETHER = auto()
    """Nodes must be satisfied together."""
    
    OPTIONAL_DEPENDENCY_ON = auto()
    """Optional dependency relationship."""
    
    # Constraint relationships
    CONSTRAINS = auto()
    """Node constrains another node's behavior."""
    
    BLOCKS = auto()
    """Node blocks another node's transition or action."""
    
    ENABLES = auto()
    """Node enables another node's operation."""
    
    SUPPORTS = auto()
    """Node supports another node's function."""
    
    # Conflict and invalidation
    CONFLICTS_WITH = auto()
    """Nodes have conflicting requirements or states."""
    
    CORROBORATES = auto()
    """Node corroborates another node's state."""
    
    INVALIDATES = auto()
    """Node invalidates another node's previous state."""
    
    # Revision relationships
    SUPERSEDES = auto()
    """New revision supersedes old revision."""
    
    REPLACES = auto()
    """Node replaces another node."""
    
    DERIVED_FROM = auto()
    """Node is derived from another node."""
    
    CAUSED_BY = auto()
    """Event or state caused by another."""
    
    TRIGGERED_BY = auto()
    """Event triggered by another event."""
    
    # Participation relationships
    PARTICIPATES_IN = auto()
    """Node participates in a coordination cycle or plan."""
    
    BELONGS_TO = auto()
    """Node belongs to a partition or domain."""
    
    MEMBER_OF = auto()
    """Node is a member of a group."""
    
    CONTAINS = auto()
    """Node contains other nodes."""
    
    # Publication relationships
    PUBLISHED_IN = auto()
    """State was published in a snapshot."""
    
    ACCEPTED_IN = auto()
    """State was accepted in a snapshot."""
    
    REJECTED_IN = auto()
    """State was rejected in a snapshot."""
    
    REUSED_IN = auto()
    """Element reused in later revision."""
    
    DEFERRED_IN = auto()
    """Element deferred to future revision."""
    
    # Synchronization
    SYNCHRONIZES_WITH = auto()
    """Nodes must synchronize their states."""
    
    WAITS_FOR = auto()
    """Node waits for another node's completion."""
    
    ACKNOWLEDGES = auto()
    """Node acknowledges state from another node."""
    
    # Consumption/production
    CONSUMES = auto()
    """Node consumes state or output from another."""
    
    PRODUCES = auto()
    """Node produces state or output for another."""
    
    OBSERVES = auto()
    """Node observes state from another."""
    
    EXPOSES = auto()
    """Node exposes internal state externally."""
    
    REFERENCES = auto()
    """Node references another node's identity."""
    
    RESOLVED_BY = auto()
    """Element resolved by another element."""
    
    OWNED_BY = auto()
    """Node is owned by a specific entity."""
    
    GOVERNED_BY = auto()
    """Node behavior governed by policy or constraint."""
    
    LIMITED_BY = auto()
    """Node limited by constraint or resource."""
    
    HAS_FINDING = auto()
    """Graph has a finding recorded."""
    
    HAS_LIMITATION = auto()
    """Graph has a limitation recorded."""
    
    # Context relationships
    CONTEXT_FOR = auto()
    """Context provides information for this node."""
    
    DOMAIN_OF = auto()
    """Node belongs to this domain."""
    
    PARTITION_OF = auto()
    """Node belongs to this partition."""
    
    COMPONENT_OF = auto()
    """Node is part of this connected component."""
    
    # Revision lineage
    PREVIOUS_REVISION_OF = auto()
    """Previous revision in the lineage chain."""
    
    NEXT_REVISION_OF = auto()
    """Next revision in the lineage chain."""
    
    VERSION_OF = auto()
    """Version in a revision chain."""
    
    UNKNOWN = auto()
    """Unknown edge kind."""


# =============================================================================
# GRAPH NODE STATUS
# =============================================================================

class CoordinationNodeStatus(Enum):
    """
    Status of a graph node.
    
    GRAPHLAW-031: Status is explicit and immutable after creation
    GRAPHLAW-032: Historical status transitions are preserved
    """
    ACTIVE = "active"
    """Node is currently active in the graph."""
    
    HISTORICAL = "historical"
    """Node was active but is now historical."""
    
    SUPERSEDED = "superseded"
    """Node has been superseded by a newer revision."""
    
    DEPRECATED = "deprecated"
    """Node is deprecated and should not be used."""
    
    INVALID = "invalid"
    """Node failed validation or contains invalid data."""
    
    BLOCKED = "blocked"
    """Node's operation is blocked by constraints."""
    
    DEFERRED = "deferred"
    """Node's action has been deferred to later cycle."""
    
    UNKNOWN = "unknown"
    """Status cannot be determined."""


# =============================================================================
# GRAPH EDGE STATUS
# =============================================================================

class CoordinationEdgeStatus(Enum):
    """
    Status of a graph edge.
    
    GRAPHLAW-041: Edge status is explicit and immutable after creation
    GRAPHLAW-042: Edge status transitions are preserved
    """
    ACTIVE = "active"
    """Edge represents current valid relationship."""
    
    HISTORICAL = "historical"
    """Edge was active but is now historical."""
    
    SUPERSEDED = "superseded"
    """Edge has been superseded by a newer revision."""
    
    INVALIDATED = "invalidated"
    """Edge was invalidated during validation."""
    
    BLOCKED = "blocked"
    """Edge's relationship is currently blocked."""
    
    DEFERRED = "deferred"
    """Edge's activation deferred to future cycle."""
    
    UNKNOWN = "unknown"
    """Status cannot be determined."""


# =============================================================================
# GRAPH REVISION KINDS
# =============================================================================

class GraphRevisionKind(Enum):
    """
    Kinds of graph revisions.
    
    GRAPHLAW-051: Revision kinds determine how revisions are constructed
    GRAPHLAW-052: Revision kind is preserved in lineage
    """
    INITIAL = "initial"
    """First graph revision in the sequence."""
    
    FULL_REBUILD = "full_rebuild"
    """Complete reconstruction from source artifacts."""
    
    INCREMENTAL = "incremental"
    """Incremental update based on delta."""
    
    REVALIDATION = "revalidation"
    """Revalidation of existing structure with new policy."""
    
    RECOVERY = "recovery"
    """Recovery from corrupted or inconsistent state."""
    
    DOMAIN_MERGE = "domain_merge"
    """Merge additional domains into the graph."""
    
    PARTITION_REBUILD = "partition_rebuild"
    """Rebuild specific partitions."""
    
    CORRECTION = "correction"
    """Correction of an error in a previous revision."""
    
    SUPERSESSION = "supersession"
    """Explicit supersession of previous revision."""
    
    UNKNOWN = "unknown"
    """Revision kind cannot be determined."""


# =============================================================================
# COMPONENT KINDS
# =============================================================================

class ComponentKind(Enum):
    """
    Kinds of connected components.
    
    GRAPHLAW-061: Component kinds describe graph topology
    GRAPHLAW-062: Component classification is deterministic
    """
    CONNECTED = "connected"
    """Nodes are connected via at least one path."""
    
    STRONGLY_CONNECTED = "strongly_connected"
    """All nodes are mutually reachable (directed)."""
    
    DEPENDENCY_REGION = "dependency_region"
    """Region of the graph representing dependency chains."""
    
    SYNCHRONIZATION_REGION = "synchronization_region"
    """Region requiring synchronized state changes."""
    
    FEEDBACK_REGION = "feedback_region"
    """Region containing feedback loops."""
    
    DEADLOCK_REGION = "deadlock_region"
    """Region identified as a deadlock."""
    
    CONFLICT_REGION = "conflict_region"
    """Region containing conflicting states."""
    
    ISOLATED = "isolated"
    """Single node with no connections."""
    
    HISTORICAL = "historical"
    """Component from previous revision."""
    
    UNKNOWN = "unknown"
    """Component kind cannot be determined."""


# =============================================================================
# PARTITION KINDS
# =============================================================================

class GraphPartitionKind(Enum):
    """
    Kinds of graph partitions.
    
    GRAPHLAW-071: Partition kinds define semantic groupings
    GRAPHLAW-072: Partitions may overlap (nodes in multiple partitions)
    """
    NETWORK = "network"
    """Partition for network-related nodes."""
    
    EXECUTIVE = "executive"
    """Executive network partition."""
    
    PREDICTIVE = "predictive"
    """Predictive network partition."""
    
    REWARD = "reward"
    """Reward network partition."""
    
    SALIENCE = "salience"
    """Salience network partition."""
    
    WORKSPACE = "workspace"
    """Workspace network partition."""
    
    SENSORIMOTOR = "sensorimotor"
    """Sensorimotor network partition."""
    
    ALERTING = "alerting"
    """Alerting network partition."""
    
    DEFAULT = "default"
    """Default network partition."""
    
    FOCUSING = "focusing"
    """Focusing network partition."""
    
    ORIENTED = "oriented"
    """Oriented network partition."""
    
    DOMAIN = "domain"
    """Semantic domain partition (e.g., language, navigation)."""
    
    TEMPORAL = "temporal"
    """Temporal coordination partition."""
    
    POLICY = "policy"
    """Policy-related constraints and rules."""
    
    DEPENDENCY = "dependency"
    """Dependency relationship partition."""
    
    CONFLICT = "conflict"
    """Conflict state partition."""
    
    CONSUMER = "consumer"
    """Consumer view partition."""
    
    HISTORICAL = "historical"
    """Historical revision partition."""
    
    UNKNOWN = "unknown"
    """Partition kind cannot be determined."""


# =============================================================================
# DOMAIN KINDS
# =============================================================================

class GraphDomainKind(Enum):
    """
    Kinds of semantic domains.
    
    GRAPHLAW-081: Domain kinds define semantic operating contexts
    GRAPHLAW-082: Domains may contain nodes from multiple partitions
    """
    LANGUAGE = "language"
    """Language processing domain."""
    
    NAVIGATION = "navigation"
    """Spatial navigation domain."""
    
    TOOL_USE = "tool_use"
    """Tool usage and manipulation domain."""
    
    REFLECTION = "reflection"
    """Self-reflection and introspection domain."""
    
    PLANNING = "planning"
    """Planning and sequence construction domain."""
    
    VISION = "vision"
    """Visual processing domain."""
    
    AUDITION = "audition"
    """Auditory processing domain."""
    
    INTERNAL_COGNITION = "internal_cognition"
    """Internal cognitive processes domain."""
    
    SOCIAL = "social"
    """Social cognition domain."""
    
    EMOTIONAL = "emotional"
    """Emotional state domain."""
    
    TEMPORAL = "temporal"
    """Temporal reasoning domain."""
    
    CAUSAL = "causal"
    """Causal reasoning domain."""
    
    METACOGNITION = "metacognition"
    """Metacognitive processes domain."""
    
    UNKNOWN = "unknown"
    """Domain kind cannot be determined."""


# =============================================================================
# SEMANTIC SCOPE
# =============================================================================

@dataclass(frozen=True, slots=True)
class SemanticScope:
    """
    Scope of semantic relevance for a graph element.
    
    GRAPHLAW-091: Semantic scope is immutable and explicit
    GRAPHLAW-092: Elements may have multiple scopes
    """
    domain_kinds: tuple[GraphDomainKind, ...]
    """Domains this element belongs to."""
    
    partition_kinds: tuple[GraphPartitionKind, ...]
    """Partitions this element belongs to."""
    
    coordination_cycle_ref: str = ""
    """Reference to coordination cycle if cycle-scoped."""
    
    epoch_ref: str = ""
    """Reference to coordination epoch if epoch-scoped."""
    
    def is_scope_consistent(self) -> bool:
        """Check if scope has valid domain-partition relationships."""
        # Basic consistency check
        return len(self.domain_kinds) > 0 and len(self.partition_kinds) > 0


# =============================================================================
# GRAPH CONSTRUCTION POLICY
# =============================================================================

@dataclass(frozen=True, slots=True)
class GraphConstructionPolicy:
    """
    Policy for graph construction operations.
    
    GRAPHLAW-101: Construction policy is immutable
    GRAPHLAW-102: Policy determines construction behavior
    """
    allow_incremental_rebuilds: bool = True
    """Allow incremental updates from deltas."""
    
    require_strong_validation: bool = True
    """Fail on validation errors instead of warning."""
    
    preserve_historical_nodes: bool = True
    """Keep historical nodes for traceability."""
    
    enable_deterministic_ordering: bool = True
    """Enforce deterministic ordering in all outputs."""
    
    maximum_trace_depth: int = 100
    """Maximum depth for traceable relationships."""
    
    require_all_endpoints_valid: bool = True
    """Reject edges with invalid endpoints."""
    
    def is_compatible_with(self, other_policy: GraphConstructionPolicy) -> bool:
        """
        Check if policies are compatible.
        
        Returns:
            True if all non-default values match
        """
        if self.require_strong_validation != other_policy.require_strong_validation:
            return False
        if self.require_all_endpoints_valid != other_policy.require_all_endpoints_valid:
            return False
        return True