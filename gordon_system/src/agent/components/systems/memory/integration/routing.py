# Integration Routing - Phase 5.1.7 Request Routing System
# =========================================================

"""
Memory Integration Routing: Routes requests to appropriate integration handlers.

Routing responsibilities:
    - Route requests based on consumer and request type
    - Select appropriate contract for the integration
    - Apply version compatibility checks
    - Handle routing failures gracefully

Routing Laws:
    ROUTING-LAW-001: Routing must be deterministic
    ROUTING-LAW-002: Routing never modifies Memory
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable
from enum import Enum, auto
import time


# =============================================================================
# ROUTE TYPES - How should requests be routed?
# =============================================================================


class RouteType(Enum):
    """
    Types of routing strategies.
    
    | Type        | Description                                     |
    |-------------|-------------------------------------------------|
    | DIRECT      | Direct route to specific consumer               |
    | BROADCAST   | Send to all matching consumers                  |
    | PRIORITY    | Priority-based selection                        |
    | ROUND_ROBIN | Round-robin load balancing                      |
    """
    
    DIRECT = "direct"
    BROADCAST = "broadcast"
    PRIORITY = "priority"
    ROUND_ROBIN = "round_robin"


# =============================================================================
# ROUTE MATCH
# =============================================================================


@dataclass(frozen=True)
class RouteMatch:
    """
    Result of a routing decision.
    
    Fields:
        route_type:      Type of route selected
        target:          Target consumer/integration
        contract_valid:  Is the contract valid for this route?
        
        # Priority info
        priority:        Routing priority (higher = more preferred)
        
        # Route metadata
        selected_at_utc: When was this route selected?
    """
    
    route_type: RouteType = RouteType.DIRECT
    
    target: str = ""                        # Target integration name
    contract_valid: bool = True
    
    priority: int = 0
    
    selected_at_utc: float = field(default_factory=time.time)
    
    def __lt__(self, other: "RouteMatch") -> bool:
        """Compare by priority (lower is higher priority)."""
        return self.priority < other.priority


# =============================================================================
# ROUTING TABLE
# =============================================================================


@dataclass(frozen=True)
class RoutingTableEntry:
    """
    Entry in the routing table.
    
    Fields:
        integration_type: Which integration type?
        
        # Consumer info
        consumer_id:     Unique consumer identifier
        route_type:      How should requests be routed?
        
        # Constraints
        priority:        Route priority (lower = higher priority)
        conditions:      When should this route be used?
        
        # Status
        enabled:         Is this route active?
    """
    
    integration_type: str                   # e.g., "perception", "workspace"
    
    consumer_id: str                        # Target consumer identifier
    
    route_type: RouteType = RouteType.DIRECT
    
    priority: int = 0
    conditions: Dict[str, Any] = field(default_factory=dict)
    
    enabled: bool = True


# =============================================================================
# ROUTER
# =============================================================================


class Router:
    """
    Routes requests to appropriate integration handlers.
    
    Determines which consumer should handle a request based on:
        - Request type
        - Consumer capabilities
        - Version compatibility
        - Current load (for load balancing)
    
    Usage:
        router = Router()
        route = router.route_request("perception", "query")
    """
    
    def __init__(self):
        self._routes: Dict[str, List[RoutingTableEntry]] = {}
        self._round_robin_counter: Dict[str, int] = {}
        self._route_history: List[Tuple[float, str, str]] = []
    
    def register_route(self, route: RoutingTableEntry) -> None:
        """Register a new routing entry."""
        if route.integration_type not in self._routes:
            self._routes[route.integration_type] = []
        
        # Remove existing route for same consumer
        self._routes[route.integration_type] = [
            r for r in self._routes[route.integration_type]
            if r.consumer_id != route.consumer_id
        ]
        
        self._routes[route.integration_type].append(route)
    
    def unregister_route(self, integration_type: str, consumer_id: str) -> None:
        """Unregister a routing entry."""
        if integration_type in self._routes:
            self._routes[integration_type] = [
                r for r in self._routes[integration_type]
                if r.consumer_id != consumer_id
            ]
    
    def route_request(self, integration_type: str,
                      request_type: Optional[str] = None) -> Tuple[RouteMatch, ...]:
        """
        Determine routing for a request.
        
        Args:
            integration_type: Which integration is this?
            request_type:     Type of request (optional)
            
        Returns:
            Tuple of route matches (sorted by priority).
        """
        if integration_type not in self._routes:
            return ()
        
        # Get enabled routes
        enabled_routes = [
            r for r in self._routes[integration_type]
            if r.enabled
        ]
        
        if not enabled_routes:
            return ()
        
        # Filter by request type if specified
        filtered_routes = enabled_routes
        if request_type:
            filtered_routes = [
                r for r in enabled_routes
                if self._matches_request(r, request_type)
            ]
        
        # Apply routing strategy
        if len(filtered_routes) == 1:
            route = filtered_routes[0]
        else:
            route = self._apply_strategy(integration_type, filtered_routes)
        
        match = RouteMatch(
            route_type=route.route_type,
            target=route.consumer_id,
            contract_valid=True,
            priority=route.priority
        )
        
        # Record history
        self._route_history.append((time.time(), integration_type, route.consumer_id))
        
        return (match,)
    
    def get_routes(self, integration_type: str) -> Tuple[RoutingTableEntry, ...]:
        """Get all routes for an integration type."""
        if integration_type not in self._routes:
            return ()
        return tuple(self._routes[integration_type])
    
    def _matches_request(self, route: RoutingTableEntry, request_type: str) -> bool:
        """Check if a route matches a request type."""
        conditions = route.conditions
        if "request_types" in conditions:
            return request_type in conditions["request_types"]
        return True
    
    def _apply_strategy(self, integration_type: str,
                        routes: List[RoutingTableEntry]) -> RoutingTableEntry:
        """Apply routing strategy to select a route."""
        # Sort by priority
        sorted_routes = sorted(routes, key=lambda r: r.priority)
        
        if not sorted_routes:
            return routes[0]
        
        # Apply round-robin for equal priorities
        counter_key = f"{integration_type}:round_robin"
        if counter_key not in self._round_robin_counter:
            self._round_robin_counter[counter_key] = 0
        
        # Find all routes with the same priority as the first one
        best_priority = sorted_routes[0].priority
        equal_priority_routes = [
            r for r in sorted_routes 
            if r.priority == best_priority
        ]
        
        if len(equal_priority_routes) > 1:
            idx = self._round_robin_counter[counter_key] % len(equal_priority_routes)
            self._round_robin_counter[counter_key] += 1
            return equal_priority_routes[idx]
        
        # Return highest priority route
        return sorted_routes[0]


# =============================================================================
# ROUTING DECISION
# =============================================================================


@dataclass(frozen=True)
class RoutingDecision:
    """
    Complete routing decision.
    
    Fields:
        request_id:      ID of the request being routed
        
        # Route info
        route_type:      Type of route selected
        target:          Target consumer/integration
        
        # Validation
        contract_valid:  Is the contract valid?
        version_match:   Are versions compatible?
        
        # Timing
        routing_time_ms: How long did routing take?
    """
    
    request_id: str                         # ID of routed request
    
    route_type: RouteType = RouteType.DIRECT
    target: str = ""
    
    contract_valid: bool = True
    version_match: bool = True
    
    routing_time_ms: float = 0.0