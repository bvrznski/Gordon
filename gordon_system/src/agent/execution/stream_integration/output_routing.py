# Phase 3.11.13 - Output Routing and Commit Implementation
# =======================================================
"""
Output routing from capability outputs to streams, with commit ordering.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
import time

from . import (
    CapabilityOutput,
    OutputRouteDescriptor,
)


@dataclass
class RouteDecision(Enum):
    """Decision for one output route."""
    ROUTE = "route"           # Route to target stream
    SKIP = "skip"             # Skip this route (e.g., optional)
    REJECT = "reject"         # Reject due to policy violation


@dataclass
class RoutingResult:
    """Result of routing one capability output."""
    route_id: str
    status: str  # routed, skipped, rejected
    target_stream: Optional[str] = None
    commit_position: Optional[int] = None
    failure_reason: Optional[str] = None


@dataclass
class OutputRouter:
    """
    Routes capability outputs to target streams.
    
    Implements bounded fan-out with explicit route descriptors and
    deterministic ordering within each stream.
    """
    
    def route_outputs(
        self,
        outputs: List[CapabilityOutput],
        input_snapshot_id: str,
        stage_id: str,
        network_id: Optional[str] = None,
    ) -> Dict[str, RoutingResult]:
        """
        Route multiple capability outputs to target streams.
        
        Args:
            outputs: Capability outputs from activation
            input_snapshot_id: Reference to input snapshot that produced these
            stage_id: Originating stage
            network_id: Optional source network
            
        Returns:
            Mapping of route_id → routing result for each output
        """
        results: Dict[str, RoutingResult] = {}
        
        for i, output in enumerate(outputs):
            # Generate deterministic route ID based on position and output
            route_id = f"{input_snapshot_id}:{output.output_id}"
            
            # Check if output has valid target
            if not output.artifact_reference:
                results[route_id] = RoutingResult(
                    route_id=route_id,
                    status="rejected",
                    failure_reason="missing_artifact_reference",
                )
                continue
            
            # Determine target stream (simplified: use first suggested or default)
            target_stream = (
                output.suggested_routes[0]
                if output.suggested_routes
                else "default"
            )
            
            results[route_id] = RoutingResult(
                route_id=route_id,
                status="routed",
                target_stream=target_stream,
                commit_position=i,  # Simplified position
            )
        
        return results
    
    def build_route_descriptor(
        self,
        output: CapabilityOutput,
        target_stream_id: str,
        priority: int = 0,
    ) -> OutputRouteDescriptor:
        """
        Build an immutable route descriptor for one output.
        
        Args:
            output: The capability output to route
            target_stream_id: Where this output should go
            priority: Routing priority (higher = more urgent)
            
        Returns:
            Immutable route descriptor
        """
        return OutputRouteDescriptor(
            route_id=output.output_id,
            invocation_id=output.invocation_id,
            artifact_reference=output.artifact_reference,
            target_stream_id=target_stream_id,
            target_owner_id=None,  # TODO: Determine owner from stream registry
            priority=priority,
            expiration=None,  # No expiration by default
            delivery_expectation="best_effort",
            commit_policy="canonical_stream_authority",
            failure_policy="retry_then_fail",
        )


# =============================================================================
# Commit Order Planner
# =============================================================================


@dataclass
class CommitOrderPlan:
    """Plan for output commit ordering."""
    plan_id: str = field(default_factory=lambda: str(time.time()))
    routes: List[str] = field(default_factory=list)  # route_ids in order
    ordering_policy: str = "per_stream_sequential"  # per_stream, cross_stream_ordered


@dataclass
class CommitOrderPlanner:
    """
    Plans deterministic output commit ordering.
    
    Within one stream, canonical ordering is preserved. Cross-stream,
    no universal global order exists unless an explicit coordination
    contract provides one.
    """
    
    def plan_commit_order(
        self,
        route_results: Dict[str, RoutingResult],
    ) -> CommitOrderPlan:
        """
        Plan deterministic commit order from routing results.
        
        Args:
            route_results: Results of routing outputs to streams
            
        Returns:
            Ordered list of routes and ordering policy
        """
        # Collect successful routes
        successful_routes = [
            route_id
            for route_id, result in route_results.items()
            if result.status == "routed"
        ]
        
        # Sort deterministically by route_id (stable tie-breaking)
        ordered_routes = sorted(successful_routes)
        
        return CommitOrderPlan(
            plan_id=str(time.time()),
            routes=ordered_routes,
            ordering_policy="per_stream_sequential",
        )


# =============================================================================
# Bounded Fan-Out
# =============================================================================


@dataclass
class FanOutPolicy:
    """Policy for bounded fan-out from one activation."""
    
    max_routes_per_activation: int = 100
    max_records_per_route: int = 10
    required_routes_must_succeed: bool = True
    
    def validate_fan_out(self, route_count: int) -> bool:
        """Check if fan-out count is within policy bounds."""
        return route_count <= self.max_routes_per_activation


@dataclass
class FanOutEnforcer:
    """Enforces fan-out boundaries during output routing."""
    
    policy: FanOutPolicy
    
    def enforce_fan_out(
        self,
        outputs: List[CapabilityOutput],
    ) -> List[OutputRouteDescriptor]:
        """
        Enforce fan-out bounds on capability outputs.
        
        Args:
            outputs: Capability outputs to route
            
        Returns:
            Route descriptors for bounded subset
        """
        if len(outputs) > self.policy.max_routes_per_activation:
            # Truncate to bound (deterministic: take first N)
            outputs = outputs[:self.policy.max_routes_per_activation]
        
        return [
            OutputRouteDescriptor(
                route_id=output.output_id,
                invocation_id=output.invocation_id,
                artifact_reference=output.artifact_reference,
                target_stream_id=None,  # Will be determined by router
                priority=0,
            )
            for output in outputs
        ]