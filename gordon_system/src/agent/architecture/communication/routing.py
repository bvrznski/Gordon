# Gordon Core - Routing & Addressing (Phase 3.21.6)
# ===================================================
#
# Canonical routing and addressing architecture for message delivery
#
# Routing determines how messages are delivered from sender to recipient.
# This module defines deterministic, policy-driven routing algorithms.

"""
Canonical Routing & Addressing for Gordon Phase 3.21.6

ROUTING TYPES:
--------------
1. Direct: Message sent to a specific endpoint by ID
2. Broadcast: Message sent to all registered endpoints
3. Multicast: Message sent to a subset of endpoints matching criteria
4. Anycast: Message sent to one of multiple possible recipients
5. Hierarchical: Route through intermediate nodes to final destination

ADDRESSING SCHEMES:
-------------------
- EndpointAddress: Direct endpoint identifier
- TopicAddress: Publish-subscribe topic name
- TypeAddress: Address by message type
- ScopedAddress: Address within specific scope/correlation

ROUTING POLICIES:
-----------------
- ExactMatch: Require exact match for routing
- PatternMatch: Support wildcard patterns in routing keys
- PriorityBased: Route based on priority levels
- LoadBalanced: Distribute across multiple recipients
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Tuple, List
from enum import Enum, auto
import uuid


# =============================================================================
# ROUTE TYPES
# =============================================================================

class RouteType(Enum):
    """
    Canonical route types.
    
    Invariants:
        - RT-001: Every message has exactly one route type
        - RT-002: Route type determines delivery mechanism
    """
    
    DIRECT = "direct"          # Point-to-point to specific endpoint
    BROADCAST = "broadcast"    # To all subscribers
    MULTICAST = "multicast"    # To selected subset of endpoints
    ANYCAST = "anycast"        # To one of multiple possible recipients
    HIERARCHICAL = "hierarchical"  # Through intermediate nodes


@dataclass(frozen=True)
class Route:
    """
    Immutable route definition.
    
    Args:
        route_type: Type of this route
        path: List of endpoint IDs in the delivery path
        metadata: Additional routing information
    """
    
    route_type: RouteType
    path: Tuple[str, ...] = field(default_factory=tuple)
    metadata: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# ADDRESS TYPES
# =============================================================================

class AddressType(Enum):
    """
    Canonical address types.
    """
    
    ENDPOINT_ID = "endpoint_id"     # Direct endpoint identifier
    TOPIC = "topic"                 # Publish-subscribe topic name
    MESSAGE_TYPE = "message_type"   # Address by message type pattern
    SCOPED = "scoped"               # Address within a scope


@dataclass(frozen=True)
class Address:
    """
    Immutable address for message routing.
    
    Args:
        address_type: Type of this address
        value: The actual address value (ID, topic name, etc.)
        scope: Optional scope identifier
    """
    
    address_type: AddressType
    value: str
    scope: Optional[str] = None
    
    @classmethod
    def endpoint_id(cls, endpoint_id: str) -> "Address":
        """Create an endpoint ID address."""
        return cls(address_type=AddressType.ENDPOINT_ID, value=endpoint_id)
    
    @classmethod
    def topic(cls, topic_name: str, scope: Optional[str] = None) -> "Address":
        """Create a topic address."""
        return cls(
            address_type=AddressType.TOPIC,
            value=topic_name,
            scope=scope,
        )
    
    @classmethod
    def message_type(cls, message_type: str, scope: Optional[str] = None) -> "Address":
        """Create a message type address."""
        return cls(
            address_type=AddressType.MESSAGE_TYPE,
            value=message_type,
            scope=scope,
        )


# =============================================================================
# ROUTING RULES
# =============================================================================

@dataclass(frozen=True)
class RoutingRule:
    """
    Immutable routing rule.
    
    Args:
        rule_id: Unique identifier for this rule
        source_address: Source address pattern (empty = all sources)
        target_address: Target address pattern
        route_type: Type of route to use
        priority: Rule priority (higher = more specific, processed first)
        conditions: Additional conditions that must be met
    """
    
    rule_id: str
    source_address: Address
    target_address: Address
    route_type: RouteType = RouteType.DIRECT
    priority: int = 0
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_direct(
        cls,
        source_endpoint_id: str,
        target_endpoint_id: str,
        priority: int = 1,
    ) -> "RoutingRule":
        """Create a direct routing rule."""
        return cls(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            source_address=Address.endpoint_id(source_endpoint_id),
            target_address=Address.endpoint_id(target_endpoint_id),
            route_type=RouteType.DIRECT,
            priority=priority,
        )
    
    @classmethod
    def create_broadcast(
        cls,
        topic: str,
        priority: int = 0,
    ) -> "RoutingRule":
        """Create a broadcast routing rule for a topic."""
        return cls(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            source_address=Address.topic(topic),
            target_address=Address.topic(topic),
            route_type=RouteType.BROADCAST,
            priority=priority,
        )
    
    @classmethod
    def create_multicast(
        cls,
        pattern: str,
        target_topic: str,
        priority: int = 0,
    ) -> "RoutingRule":
        """Create a multicast routing rule with pattern matching."""
        return cls(
            rule_id=f"rule_{uuid.uuid4().hex[:8]}",
            source_address=Address.topic(pattern),
            target_address=Address.topic(target_topic),
            route_type=RouteType.MULTICAST,
            priority=priority,
        )


# =============================================================================
# ROUTING POLICIES
# =============================================================================

class RoutingPolicy(Enum):
    """
    Canonical routing policy types.
    
    Invariants:
        - RP-001: Policy determines how routes are resolved
        - RP-002: Policy is evaluated before route selection
    """
    
    EXACT_MATCH = "exact_match"         # Require exact match
    PATTERN_MATCH = "pattern_match"     # Support wildcard patterns
    PRIORITY_BASED = "priority_based"   # Use priority for ordering
    LOAD_BALANCED = "load_balanced"     # Distribute across recipients


@dataclass(frozen=True)
class RoutingPolicyConfig:
    """
    Immutable routing policy configuration.
    
    Args:
        policy_type: Type of routing policy to use
        default_route: Default route if no rules match
        max_hops: Maximum hops in hierarchical routing
        fail_fast: Whether to fail immediately on first error
    """
    
    policy_type: RoutingPolicy = RoutingPolicy.EXACT_MATCH
    default_route: Optional[Route] = None
    max_hops: int = 5
    fail_fast: bool = False


# =============================================================================
# ADDRESS RESOLVER
# =============================================================================

@dataclass(slots=True)
class AddressResolver:
    """
    Immutable address resolver.
    
    Resolves addresses to routes based on current routing rules.
    
    Note: This class is mutable (for dynamic route updates) but
    returns immutable Route objects.
    """
    
    _rules: Dict[str, RoutingRule] = field(default_factory=dict)
    _policy_config: RoutingPolicyConfig = field(
        default_factory=RoutingPolicyConfig
    )
    
    def add_rule(self, rule: RoutingRule) -> bool:
        """Add or update a routing rule."""
        self._rules[rule.rule_id] = rule
        return True
    
    def remove_rule(self, rule_id: str) -> bool:
        """Remove a routing rule by ID."""
        if rule_id in self._rules:
            del self._rules[rule_id]
            return True
        return False
    
    def get_rules_for_address(self, address: Address) -> Tuple[RoutingRule, ...]:
        """Get all rules matching the given address."""
        # Get matching rules sorted by priority (highest first)
        matching = [
            rule for rule in self._rules.values()
            if self._rule_matches(rule, address)
        ]
        
        return tuple(sorted(matching, key=lambda r: r.priority, reverse=True))
    
    def _rule_matches(self, rule: RoutingRule, address: Address) -> bool:
        """Check if a routing rule matches the given address."""
        # Check source address match
        if (
            rule.source_address.value and 
            rule.source_address.value != address.value
        ):
            return False
        
        # Check target address match (if specified)
        if (
            rule.target_address.value and
            rule.target_address.value != address.value
        ):
            return False
        
        return True
    
    def resolve(self, source: Address, target: Address) -> Route:
        """Resolve a route from source to target."""
        rules = self.get_rules_for_address(target)
        
        if not rules:
            # Use default route or create direct path
            if self._policy_config.default_route:
                return self._policy_config.default_route
            
            return Route(
                route_type=RouteType.DIRECT,
                path=(target.value,),
            )
        
        # Return highest priority matching rule's route
        primary_rule = rules[0]
        return Route(
            route_type=primary_rule.route_type,
            path=(source.value, target.value),
            metadata=dict(primary_rule.conditions),
        )


# =============================================================================
# ROUTE TABLE
# =============================================================================

@dataclass(slots=True)
class RouteTable:
    """
    Mutable table of routes for efficient lookup.
    
    Organizes routes by source and target for fast resolution.
    """
    
    _routes: Dict[str, Dict[str, Route]] = field(default_factory=dict)
    
    def add_route(
        self,
        source_address: str,
        target_address: str,
        route: Route,
    ) -> bool:
        """Add a route from source to target."""
        if source_address not in self._routes:
            self._routes[source_address] = {}
        
        self._routes[source_address][target_address] = route
        return True
    
    def get_route(
        self,
        source_address: str,
        target_address: str,
    ) -> Optional[Route]:
        """Get the route from source to target."""
        if source_address in self._routes:
            return self._routes[source_address].get(target_address)
        return None
    
    def remove_route(
        self,
        source_address: str,
        target_address: str,
    ) -> bool:
        """Remove a route between addresses."""
        if source_address in self._routes:
            if target_address in self._routes[source_address]:
                del self._routes[source_address][target_address]
                return True
        return False
    
    def get_routes_for_source(self, source_address: str) -> Tuple[Route, ...]:
        """Get all routes originating from a source."""
        if source_address in self._routes:
            return tuple(self._routes[source_address].values())
        return ()


# =============================================================================
# ENDPOINT ROUTING TABLE
# =============================================================================

@dataclass(frozen=True)
class EndpointRoutingTableEntry:
    """
    Immutable routing table entry for an endpoint.
    
    Args:
        endpoint_id: The endpoint these routes apply to
        input_routes: Routes for messages coming TO this endpoint
        output_routes: Routes for messages going FROM this endpoint
        is_gateway: Whether this endpoint acts as a gateway
    """
    
    endpoint_id: str
    input_routes: Tuple[Route, ...] = field(default_factory=tuple)
    output_routes: Tuple[Route, ...] = field(default_factory=tuple)
    is_gateway: bool = False


# =============================================================================
# PUBLIC API
# =============================================================================

__all__ = [
    # Route types
    "RouteType",
    "Route",
    
    # Address types
    "AddressType",
    "Address",
    
    # Routing rules
    "RoutingRule",
    
    # Routing policies
    "RoutingPolicy",
    "RoutingPolicyConfig",
    
    # Resolution and tables
    "AddressResolver",
    "RouteTable",
    "EndpointRoutingTableEntry",
]