# Phase 3.11.13 - Network Activation Implementation
# ================================================
"""
Network eligibility evaluation and activation lifecycle management.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
import time
import uuid

from . import (
    StageAdmissionResult,
    NetworkEligibilityStatus,
    NetworkEligibilityContext,
    NetworkEligibilityResult,
    ActivationState,
    NetworkActivationRequest,
    NetworkActivationRequestId,
    NetworkActivationPlan,
    NetworkActivationPlanId,
    NetworkActivationContext,
)


class ActivationLifecycle(Enum):
    """States in the activation lifecycle."""
    PLANNED = "planned"               # Request received, not yet validated
    VALIDATED = "validated"          # Plan created and validated
    ADMITTED = "admitted"            # Stage admitted, ready to start
    STARTING = "starting"            # Activation beginning execution
    ACTIVE = "active"                # Running capability invocations
    WAITING = "waiting"              # Waiting for dependencies
    COMPLETING = "completing"        # Finalizing outputs
    COMPLETED = "completed"          # All work completed
    PARTIALLY_COMPLETED = "partially_completed"
    CANCELLING = "cancelling"        # Cancellation in progress
    CANCELLED = "cancelled"          # Cancelled by policy
    TIMED_OUT = "timed_out"          # Deadline exceeded
    FAILING = "failing"              # Error handling in progress
    FAILED = "failed"                # Failed to complete


@dataclass
class NetworkEligibilityEvaluator:
    """
    Evaluator for network eligibility given one admitted stage.
    
    Determines which networks are eligible for activation by a stage,
    based on the stage's requirements and available resources.
    """
    
    def evaluate_eligibility(
        self,
        stage_id: str,
        cycle_id: str,
        input_snapshot_id: Optional[str] = None,
        stage_kind: str = "",
        stage_objective: str = "",
        available_networks: Optional[List[Dict[str, Any]]] = None,
    ) -> List[NetworkEligibilityResult]:
        """
        Evaluate which networks are eligible for one admitted stage.
        
        Args:
            stage_id: The admitted stage requesting network activation
            cycle_id: Parent cycle ID
            input_snapshot_id: Optional reference to input snapshot
            stage_kind: Type of stage (e.g., "perception", "reasoning")
            stage_objective: Semantic purpose of the stage
            available_networks: Optional list of networks with their properties
            
        Returns:
            List of eligibility results for each network
        """
        if available_networks is None:
            # Return empty if no networks specified - caller will provide actual data
            return []
        
        results = []
        
        for network in available_networks:
            result = self._evaluate_one_network(
                stage_id=stage_id,
                cycle_id=cycle_id,
                input_snapshot_id=input_snapshot_id,
                network=network,
                stage_kind=stage_kind,
                stage_objective=stage_objective,
            )
            results.append(result)
        
        return results
    
    def _evaluate_one_network(
        self,
        stage_id: str,
        cycle_id: str,
        input_snapshot_id: Optional[str],
        network: Dict[str, Any],
        stage_kind: str,
        stage_objective: str,
    ) -> NetworkEligibilityResult:
        """Evaluate one network's eligibility."""
        network_id = network.get("network_id", "unknown")
        
        # Build context
        context = NetworkEligibilityContext(
            stage_id=stage_id,
            cycle_id=cycle_id,
            input_snapshot_id=input_snapshot_id,
            stage_kind=stage_kind,
            stage_objective=stage_objective,
            available_capabilities=network.get("capabilities", []),
            available_systems=network.get("required_systems", []),
        )
        
        # Check if network is disabled
        if not network.get("enabled", True):
            return NetworkEligibilityResult(
                network_id=network_id,
                status=NetworkEligibilityStatus.INELIGIBLE,
                ineligibility_reasons=["network_disabled"],
                evaluated_at_utc=time.time(),
                stage_id=stage_id,
                cycle_id=cycle_id,
            )
        
        # Check if network matches stage kind
        network_kinds = network.get("kinds", [])
        if network_kinds and stage_kind not in network_kinds:
            return NetworkEligibilityResult(
                network_id=network_id,
                status=NetworkEligibilityStatus.INELIGIBLE,
                ineligibility_reasons=[f"stage_kind '{stage_kind}' not supported"],
                evaluated_at_utc=time.time(),
                stage_id=stage_id,
                cycle_id=cycle_id,
            )
        
        # Check required capabilities
        required_capabilities = network.get("required_capabilities", [])
        available_caps = set(context.available_capabilities)
        
        missing_caps = [
            c for c in required_capabilities 
            if c not in available_caps
        ]
        
        if missing_caps:
            return NetworkEligibilityResult(
                network_id=network_id,
                status=NetworkEligibilityStatus.WAITING,
                wait_condition=f"waiting_for_capabilities: {', '.join(missing_caps)}",
                evaluated_at_utc=time.time(),
                stage_id=stage_id,
                cycle_id=cycle_id,
            )
        
        # Network passes all checks
        return NetworkEligibilityResult(
            network_id=network_id,
            status=NetworkEligibilityStatus.ELIGIBLE,
            eligibility_reasons=[
                "network_enabled",
                f"supports_stage_kind: {stage_kind}",
                "all_required_capabilities_available",
            ],
            evaluated_at_utc=time.time(),
            stage_id=stage_id,
            cycle_id=cycle_id,
        )


@dataclass
class ActivationRequestBuilder:
    """Builder for activation requests with fluent interface."""
    
    stage_id: str = ""
    cycle_id: str = ""
    network_id: str = ""
    input_snapshot_id: Optional[str] = None
    requested_capabilities: List[str] = field(default_factory=list)
    resource_budget: Dict[str, int] = field(default_factory=dict)
    deadline: Optional[float] = None
    priority: int = 0
    
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    def set_stage(self, stage_id: str, cycle_id: str) -> "ActivationRequestBuilder":
        """Set the stage and cycle for this activation."""
        self.stage_id = stage_id
        self.cycle_id = cycle_id
        return self
    
    def set_network(self, network_id: str) -> "ActivationRequestBuilder":
        """Set the target network."""
        self.network_id = network_id
        return self
    
    def set_input_snapshot(self, snapshot_id: str) -> "ActivationRequestBuilder":
        """Set reference to input snapshot."""
        self.input_snapshot_id = snapshot_id
        return self
    
    def add_capability(self, capability_id: str) -> "ActivationRequestBuilder":
        """Add a required capability."""
        if capability_id not in self.requested_capabilities:
            self.requested_capabilities.append(capability_id)
        return self
    
    def set_deadline(self, deadline_utc: float) -> "ActivationRequestBuilder":
        """Set UTC deadline for completion."""
        self.deadline = deadline_utc
        return self
    
    def set_priority(self, priority: int) -> "ActivationRequestBuilder":
        """Set activation priority (higher = more urgent)."""
        self.priority = priority
        return self
    
    def set_correlation(self, correlation_id: str) -> "ActivationRequestBuilder":
        """Set correlation ID for traceability."""
        self.correlation_id = correlation_id
        return self
    
    def build(self) -> NetworkActivationRequest:
        """Build the activation request."""
        return NetworkActivationRequest(
            request_id=NetworkActivationRequestId.generate(),
            stage_id=self.stage_id,
            cycle_id=self.cycle_id,
            network_id=self.network_id,
            input_snapshot_id=self.input_snapshot_id,
            requested_capabilities=self.requested_capabilities.copy(),
            resource_budget=dict(self.resource_budget),
            deadline=self.deadline,
            priority=self.priority,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
        )


@dataclass
class ActivationPlanBuilder:
    """Builder for activation plans."""
    
    request: NetworkActivationRequest = None  # type: ignore
    
    eligible_capabilities: List[str] = field(default_factory=list)
    capability_invocation_order: List[List[str]] = field(default_factory=list)
    required_systems: List[str] = field(default_factory=list)
    
    cancellation_policy: str = "immediate"
    failure_policy: str = "fail_stage"
    
    def set_request(self, request: NetworkActivationRequest) -> "ActivationPlanBuilder":
        """Set the source activation request."""
        self.request = request
        return self
    
    def add_capability_group(
        self,
        capabilities: List[str],
    ) -> "ActivationPlanBuilder":
        """Add a group of capabilities that can run in parallel."""
        if capabilities:
            self.capability_invocation_order.append(capabilities)
            # Update eligible capabilities set
            for c in capabilities:
                if c not in self.eligible_capabilities:
                    self.eligible_capabilities.append(c)
        return self
    
    def add_system(self, system_id: str) -> "ActivationPlanBuilder":
        """Add a required system."""
        if system_id not in self.required_systems:
            self.required_systems.append(system_id)
        return self
    
    def build(self) -> NetworkActivationPlan:
        """Build the activation plan."""
        if self.request is None:
            raise ValueError("Cannot build plan without source request")
        
        return NetworkActivationPlan(
            plan_id=NetworkActivationPlanId.generate(),
            request_id=self.request.request_id,
            network_id=self.request.network_id,
            stage_id=self.request.stage_id,
            cycle_id=self.request.cycle_id,
            input_snapshot_id=self.request.input_snapshot_id,
            eligible_capabilities=self.eligible_capabilities.copy(),
            capability_invocation_order=[
                group.copy() for group in self.capability_invocation_order
            ],
            required_systems=self.required_systems.copy(),
            resource_budget=dict(self.request.resource_budget),
            deadline=self.request.deadline,
            cancellation_policy=self.cancellation_policy,
            failure_policy=self.failure_policy,
            created_at_utc=time.time(),
        )


@dataclass
class ActivationContextBuilder:
    """Builder for activation contexts."""
    
    network_id: str = ""
    stage_id: str = ""
    cycle_id: str = ""
    thread_id: str = ""
    loop_id: str = ""
    input_snapshot_ref: str = ""  # Reference, not the full snapshot
    
    capability_plan_id: Optional[str] = None
    capability_invocation_ids: List[str] = field(default_factory=list)
    
    system_references: List[str] = field(default_factory=list)
    resource_budget: Dict[str, int] = field(default_factory=dict)
    deadline: Optional[float] = None
    
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    
    def set_network(self, network_id: str) -> "ActivationContextBuilder":
        self.network_id = network_id
        return self
    
    def set_stage(self, stage_id: str, cycle_id: str) -> "ActivationContextBuilder":
        self.stage_id = stage_id
        self.cycle_id = cycle_id
        return self
    
    def set_thread_loop(self, thread_id: str, loop_id: str) -> "ActivationContextBuilder":
        self.thread_id = thread_id
        self.loop_id = loop_id
        return self
    
    def set_input_snapshot_ref(self, ref: str) -> "ActivationContextBuilder":
        """Set reference to stored snapshot (not the full object)."""
        self.input_snapshot_ref = ref
        return self
    
    def add_capability_invocation(
        self,
        invocation_id: str,
    ) -> "ActivationContextBuilder":
        if invocation_id not in self.capability_invocation_ids:
            self.capability_invocation_ids.append(invocation_id)
        return self
    
    def add_system(self, system_ref: str) -> "ActivationContextBuilder":
        if system_ref not in self.system_references:
            self.system_references.append(system_ref)
        return self
    
    def set_deadline(self, deadline_utc: float) -> "ActivationContextBuilder":
        self.deadline = deadline_utc
        return self
    
    def build(self) -> NetworkActivationContext:
        """Build the immutable activation context."""
        return NetworkActivationContext(
            activation_id=str(uuid.uuid4()),
            network_id=self.network_id,
            stage_id=self.stage_id,
            cycle_id=self.cycle_id,
            thread_id=self.thread_id,
            loop_id=self.loop_id,
            input_snapshot_ref=self.input_snapshot_ref,
            capability_plan_id=self.capability_plan_id,
            capability_invocation_ids=self.capability_invocation_ids.copy(),
            system_references=self.system_references.copy(),
            resource_budget=dict(self.resource_budget),
            deadline=self.deadline,
            correlation_id=self.correlation_id,
            causation_id=self.causation_id,
            created_at_utc=time.time(),
        )