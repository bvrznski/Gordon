# Phase 3.11.13 - Capability Invocation Integration
# ================================================
"""
Capability invocation within network activation context.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time

from . import (
    NetworkActivationPlan,
    CapabilityInvocationId,
    CapabilityInvocationPlan,
    CapabilityOutput,
)


@dataclass
class CapabilityInvoker:
    """
    Invokes capabilities within network activation context.
    
    The invoker receives capability invocation plans and executes them
    with proper resource management, deadline tracking, and result collection.
    """
    
    def invoke_capability(
        self,
        plan: CapabilityInvocationPlan,
        input_data: Dict[str, Any],
        systems: Optional[Dict[str, Any]] = None,
    ) -> CapabilityOutput:
        """
        Invoke one capability according to its invocation plan.
        
        Args:
            plan: The validated invocation plan
            input_data: Processed input data from the input snapshot
            systems: Available system services
            
        Returns:
            Capability output artifact
        """
        # Check deadline before invocation
        if plan.deadline is not None and time.time() > plan.deadline:
            return CapabilityOutput(
                output_id=str(time.time()),
                invocation_id=plan.invocation_id,
                status="timed_out",
                confidence=0.0,
                uncertainty=1.0,
                created_at_utc=time.time(),
            )
        
        # TODO: Invoke actual capability (stubbed)
        # This would call the capability implementation through a port
        capability_output = CapabilityOutput(
            output_id=str(time.time()),
            invocation_id=plan.invocation_id,
            artifact_reference=f"artifact:{plan.capability_id}:invoked",
            confidence=1.0,
            uncertainty=0.0,
            created_at_utc=time.time(),
            correlation_id=None,
            causation_id=None,
        )
        
        return capability_output
    
    def invoke_parallel_group(
        self,
        plan: NetworkActivationPlan,
        group_index: int,
        inputs: Dict[str, Any],
        systems: Optional[Dict[str, Any]] = None,
    ) -> List[CapabilityOutput]:
        """
        Invoke a parallel group of capabilities.
        
        Args:
            plan: The activation plan
            group_index: Index of the parallel group to invoke
            inputs: Input data for this invocation batch
            systems: Available system services
            
        Returns:
            List of outputs from each capability in the group
        """
        if group_index >= len(plan.capability_invocation_order):
            return []
        
        capabilities_in_group = plan.capability_invocation_order[group_index]
        results: List[CapabilityOutput] = []
        
        for cap_id in capabilities_in_group:
            invocation_plan = CapabilityInvocationPlan(
                invocation_id=CapabilityInvocationId.generate(),
                network_activation_id=str(time.time()),
                capability_id=cap_id,
                required_systems=plan.required_systems.copy(),
                deadline=plan.deadline,
                priority=0,  # All in same group have equal priority
            )
            
            output = self.invoke_capability(
                plan=invocation_plan,
                input_data=inputs,
                systems=systems,
            )
            results.append(output)
        
        return results


# =============================================================================
# Capability Output Validation
# =============================================================================


@dataclass
class OutputValidationResult:
    """Result of validating one capability output."""
    is_valid: bool
    reason: str = ""
    output_id: str = ""


@dataclass
class OutputValidator:
    """
    Validates capability outputs before routing.
    
    Ensures that outputs meet contract requirements and are safe to route
    to target streams.
    """
    
    def validate_output(
        self,
        output: CapabilityOutput,
        expected_schema: Optional[str] = None,
    ) -> OutputValidationResult:
        """
        Validate one capability output.
        
        Args:
            output: The output artifact from capability invocation
            expected_schema: Optional schema constraint
            
        Returns:
            Validation result with pass/fail status
        """
        # Check required fields exist
        if not output.output_id:
            return OutputValidationResult(
                is_valid=False,
                reason="missing_output_id",
                output_id=output.output_id,
            )
        
        if not output.invocation_id:
            return OutputValidationResult(
                is_valid=False,
                reason="missing_invocation_id",
                output_id=output.output_id,
            )
        
        # Check artifact reference exists
        if not output.artifact_reference:
            return OutputValidationResult(
                is_valid=False,
                reason="missing_artifact_reference",
                output_id=output.output_id,
            )
        
        # TODO: Validate schema if specified (stubbed)
        if expected_schema:
            pass  # Schema validation would go here
        
        # Check confidence/uncertainty bounds
        if output.confidence + output.uncertainty > 1.0:
            return OutputValidationResult(
                is_valid=False,
                reason="confidence_uncertainty_exceeds_1",
                output_id=output.output_id,
            )
        
        return OutputValidationResult(
            is_valid=True,
            output_id=output.output_id,
        )


# =============================================================================
# Capability Projection
# =============================================================================


@dataclass
class CapabilityProjection:
    """
    Bounded projection of input snapshot for one capability.
    
    A capability should only receive the data it needs, not full access to
    all selected records. This ensures least-privilege access.
    """
    
    capability_id: str
    
    # Which input records are projected (by reference)
    record_references: List[str]  # Record IDs that this capability can see
    
    # Metadata about projections
    projection_policy: str = "least_privilege"  # e.g., "minimal", "sufficient"
    privacy_masked_fields: List[str] = field(default_factory=list)
    
    def get_projection_summary(self) -> str:
        """Get human-readable summary of what this capability sees."""
        return (
            f"Capability {self.capability_id} can see "
            f"{len(self.record_references)} record(s), "
            f"policy={self.projection_policy}"
        )


@dataclass
class ProjectionBuilder:
    """
    Builds bounded projections for capabilities from input snapshots.
    
    Ensures that each capability only receives the data it needs according
    to its contract.
    """
    
    def build_projection(
        self,
        snapshot: "StageInputSnapshot",
        capability_id: str,
        capability_contract: Optional[str] = None,
    ) -> CapabilityProjection:
        """
        Build a bounded projection for one capability from an input snapshot.
        
        Args:
            snapshot: The stage's complete input snapshot
            capability_id: Which capability is being invoked
            capability_contract: Optional contract specifying data requirements
            
        Returns:
            Bounded projection with only required data references
        """
        # Start with all record references in the snapshot
        all_record_ids = [
            r.reference.record_id for r in snapshot.selected_records
        ]
        
        # Apply projection policy - by default, provide minimal access
        if capability_contract is None:
            # No contract specified - use minimal projection (first N records)
            project_count = min(5, len(all_record_ids))
            projected_ids = all_record_ids[:project_count]
        else:
            # Contract specified - parse to determine exact needs (stubbed)
            projected_ids = all_record_ids
        
        return CapabilityProjection(
            capability_id=capability_id,
            record_references=projected_ids,
            projection_policy="least_privilege",
            privacy_masked_fields=[],  # TODO: Apply masking if needed
        )