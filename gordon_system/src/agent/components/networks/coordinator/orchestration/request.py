# Gordon Cognitive Architecture - Phase 4.11.7
# ===========================================
"""
Cognitive Orchestration Request Model
=====================================

The orchestration request that initiates a cognitive cycle.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class CognitiveOrchestrationRequest:
    """
    Immutable orchestration request model.
    
    ORCHESTRATION-LAW-001: Every orchestration plan possesses one stable semantic identity
    ORCHESTRATION-LAW-003: Equivalent requests produce equivalent identities
    
    Suggested fields per spec:
        orchestration_scope
        goal_reference
        triggering_event_reference
        coordination_state_reference
        participating_network_candidates
        capability_requirements
        constraints
        orchestration_policy
        provenance
    """
    
    identity_ref: str = ""
    """Reference to the generated identity."""
    
    orchestration_scope: str = ""
    """Scope of this orchestration (micro, interaction, task, goal, mission)."""
    
    goal_reference: str = ""
    """Reference to the goal being pursued."""
    
    triggering_event_reference: str = ""
    """Reference to the event that triggered this orchestration."""
    
    coordination_state_reference: str = ""
    """Reference to current coordination state."""
    
    participating_network_candidates: tuple[str, ...] = ()
    """Candidate networks for participation."""
    
    capability_requirements: tuple[str, ...] = ()
    """Required capabilities for participation."""
    
    constraints: tuple[str, ...] = ()
    """Constraints that must be satisfied."""
    
    orchestration_policy: str = ""
    """Policy for this orchestration (execution and completion policies)."""
    
    provenance_ref: str = ""
    """Reference to provenance record."""
    
    @classmethod
    def create(
        cls,
        orchestration_scope: str,
        goal_reference: str,
        triggering_event_reference: str = "",
        coordination_state_reference: str = "",
        participating_network_candidates: tuple[str, ...] = (),
        capability_requirements: tuple[str, ...] = (),
        constraints: tuple[str, ...] = (),
        orchestration_policy: str = "",
    ) -> CognitiveOrchestrationRequest:
        """
        Create a new orchestration request.
        
        Args:
            orchestration_scope: Scope of orchestration
            goal_reference: Reference to the goal
            triggering_event_reference: Event that triggered orchestration
            coordination_state_reference: Current state reference
            participating_network_candidates: Candidate networks
            capability_requirements: Required capabilities
            constraints: Constraints to satisfy
            orchestration_policy: Policy for orchestration
            
        Returns:
            A new CognitiveOrchestrationRequest instance
        """
        return cls(
            identity_ref="",
            orchestration_scope=orchestration_scope,
            goal_reference=goal_reference,
            triggering_event_reference=triggering_event_reference,
            coordination_state_reference=coordination_state_reference,
            participating_network_candidates=tuple(participating_network_candidates),
            capability_requirements=tuple(capability_requirements),
            constraints=tuple(constraints),
            orchestration_policy=orchestration_policy,
            provenance_ref="",
        )
    
    def __str__(self) -> str:
        return f"CognitiveOrchestrationRequest(scope={self.orchestration_scope}, goal={self.goal_reference})"