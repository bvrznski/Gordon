# Default Network Types and Identities
# ====================================

"""
Core type definitions for the DefaultNetwork.

This module establishes immutable identity types and fundamental data structures
for the network's semantic computations. All types are frozen to ensure:
- Deterministic behavior
- Thread safety
- Hashability (for use in sets/dicts)
- No side effects from modification

PHASE 4.3.1: Core Type Definitions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple, Any, Mapping
from datetime import datetime


# =============================================================================
# IDENTITY TYPES (stable, independent identifiers)
# =============================================================================

DefaultNetworkId = str
InputId = str
OutputId = str
AssessmentId = str
ProposalId = str
SourceId = str  # Source of input signal


# =============================================================================
# INPUT TYPES
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultProvenance:
    """
    Provenance tracking for inputs and outputs.
    
    Records where data came from without embedding implementation details.
    """
    
    # Input source identity
    source_id: SourceId
    
    # Processing metadata
    timestamp_utc: datetime  # When input was created (not processed)
    
    # Configuration version (for reproducibility)
    config_version: Optional[str] = None
    
    # Optional caller reference (for traceability)
    caller_id: Optional[str] = None


@dataclass(frozen=True, slots=True)
class DefaultInputContext:
    """
    Context information for the DefaultNetwork.
    
    This represents state owned by higher layers (Memory, Consciousness, etc.).
    The DefaultNetwork consumes this but does NOT own or modify it.
    """
    
    # Current cognitive state
    active_focus_strength: Optional[float] = None  # 0.0 to 1.0
    
    # Task-related information
    current_task_criticality: Optional[float] = None  # 0.0 to 1.0
    unresolved_goal_count: int = 0
    
    # Memory state
    recent_memory_reactivation_count: int = 0
    memory_continuity_score: Optional[float] = None  # 0.0 to 1.0
    
    # Narrative context
    current_narrative_id: Optional[str] = None
    narrative_continuity: Optional[float] = None  # 0.0 to 1.0


@dataclass(frozen=True, slots=True)
class DefaultInput:
    """
    A single input unit for DefaultNetwork assessment.
    
    This is the canonical input contract. All fields must be provided or
    explicitly set to None (for optionals).
    
    Requirements:
        - Immutable
        - Validated (see validation module)
        - Bounded (no arbitrary growth)
        - Serialization-ready
        - No live objects, callbacks, or service handles
    """
    
    # Identity
    input_id: InputId
    
    # Source information
    source_id: SourceId
    source_type: str  # e.g., "memory", "cognition", "consciousness"
    
    # Timestamp (required)
    timestamp_utc: datetime
    
    # Input category
    category: str  # e.g., "memory_reactivation", "reflection_candidate"
    
    # Content reference (pointer to actual content, not embedded)
    content_ref: Optional[str] = None
    
    # Semantic weight (0.0 to 1.0)
    semantic_weight: float = 0.5
    
    # Context hint
    context_hint: Optional[DefaultInputContext] = None
    
    # Provenance
    provenance: Optional[DefaultProvenance] = None


# =============================================================================
# OUTPUT TYPES (proposals and assessments)
# =============================================================================

@dataclass(frozen=True, slots=True)
class InternalAttentionProposal:
    """
    Proposal for internally oriented attention coordination.
    
    Suggests which internal processes should receive coordinated attention.
    Does NOT command execution - only proposes attention allocation patterns.
    """
    
    proposal_id: ProposalId
    
    # What is being proposed
    attention_target: str  # e.g., "memory_reactivation", "reflection_session"
    
    # Priority estimate (0.0 to 1.0)
    priority_estimate: float
    
    # Coordinated processes
    coordinated_processes: Tuple[str, ...]
    
    # Confidence in proposal (0.0 to 1.0)
    confidence: float = 0.5


@dataclass(frozen=True, slots=True)
class AssociationProposal:
    """
    Proposal for memory-driven associative activation.
    
    Suggests which memories or concepts should be associatively activated.
    """
    
    proposal_id: ProposalId
    
    # Association target (concept, memory, schema)
    association_target: str
    
    # Strength of association (0.0 to 1.0)
    association_strength: float
    
    # Related items
    related_items: Tuple[str, ...]
    
    # Confidence (0.0 to 1.0)
    confidence: float = 0.5


@dataclass(frozen=True, slots=True)
class MemoryReactivationProposal:
    """
    Proposal for memory reactivation and integration.
    
    Suggests which memories should be reactivated for integration or review.
    """
    
    proposal_id: ProposalId
    
    # Memory reference
    memory_ref: str
    
    # Reason for reactivation
    reason: str  # e.g., "narrative_continuity", "unresolved_goal"
    
    # Integration priority (0.0 to 1.0)
    integration_priority: float
    
    # Confidence (0.0 to 1.0)
    confidence: float = 0.5


@dataclass(frozen=True, slots=True)
class ReflectionProposal:
    """
    Proposal for self-referential processing.
    
    Suggests topics or patterns that deserve reflection.
    """
    
    proposal_id: ProposalId
    
    # Reflection topic
    topic: str
    
    # Reflection depth (0.0 to 1.0)
    depth_estimate: float
    
    # Potential insights
    potential_insights: Tuple[str, ...]
    
    # Confidence (0.0 to 1.0)
    confidence: float = 0.5


@dataclass(frozen=True, slots=True)
class SimulationProposal:
    """
    Proposal for prospective or counterfactual simulation.
    
    Suggests scenarios that should be simulated internally.
    """
    
    proposal_id: ProposalId
    
    # Simulation type
    simulation_type: str  # "prospective", "counterfactual", "hypothetical"
    
    # Scenario description reference
    scenario_ref: str
    
    # Expected outcomes (for comparison)
    expected_outcomes: Tuple[str, ...]
    
    # Confidence (0.0 to 1.0)
    confidence: float = 0.5


@dataclass(frozen=True, slots=True)
class ProspectionProposal:
    """
    Proposal for future-oriented processing.
    
    Suggests what-should-happen or what-could-happen scenarios.
    """
    
    proposal_id: ProposalId
    
    # Future state description
    future_state_ref: str
    
    # Motivation for this prospect
    motivation: str
    
    # Estimated probability (0.0 to 1.0)
    estimated_probability: float
    
    # Confidence (0.0 to 1.0)
    confidence: float = 0.5


@dataclass(frozen=True, slots=True)
class NarrativeIntegrationProposal:
    """
    Proposal for narrative continuity integration.
    
    Suggests how new information should be integrated into the current narrative.
    """
    
    proposal_id: ProposalId
    
    # Narrative element to integrate
    narrative_element_ref: str
    
    # Integration point (current narrative context)
    integration_point: str
    
    # Narrative fit score (0.0 to 1.0)
    fit_score: float
    
    # Confidence (0.0 to 1.0)
    confidence: float = 0.5


@dataclass(frozen=True, slots=True)
class UnresolvedGoalProposal:
    """
    Proposal for unresolved goal resurfacing or incubation.
    
    Suggests which goals should remain in the background or be revisited.
    """
    
    proposal_id: ProposalId
    
    # Goal reference
    goal_ref: str
    
    # Reason for resurfacing
    reason: str  # e.g., "incubation_complete", "context_change"
    
    # Priority adjustment (can be negative)
    priority_adjustment: float
    
    # Confidence (0.0 to 1.0)
    confidence: float = 0.5


@dataclass(frozen=True, slots=True)
class IncubationProposal:
    """
    Proposal for incubation processing.
    
    Suggests which problems or ideas should be given incubation time.
    """
    
    proposal_id: ProposalId
    
    # Problem/idea reference
    idea_ref: str
    
    # Incubation duration hint (seconds)
    suggested_duration_seconds: int
    
    # Expected benefit
    expected_benefit: str
    
    # Confidence (0.0 to 1.0)
    confidence: float = 0.5


@dataclass(frozen=True, slots=True)
class ContextReintegrationProposal:
    """
    Proposal for reintegrating background context.
    
    Suggests how background information should be recombined with foreground.
    """
    
    proposal_id: ProposalId
    
    # Background context reference
    context_ref: str
    
    # Integration target (foreground process)
    integration_target: str
    
    # Reintegration strength (0.0 to 1.0)
    strength: float
    
    # Confidence (0.0 to 1.0)
    confidence: float = 0.5


# =============================================================================
# OUTPUT COMPOSITION
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultOutput:
    """
    A single output from the DefaultNetwork.
    
    Represents a proposal or assessment that other systems may consider.
    Does NOT command execution - only proposes or assesses.
    """
    
    # Output identity
    output_id: OutputId
    
    # Timestamp when output was created
    timestamp_utc: datetime
    
    # Output type classification
    output_type: str  # e.g., "proposal", "assessment"
    
    # The actual proposal/assessment data
    content: Any  # One of the proposal types above
    
    # Source information (for provenance)
    source_info: Optional[DefaultProvenance] = None


@dataclass(frozen=True, slots=True)
class DefaultProposalSet:
    """
    A complete set of proposals from the DefaultNetwork.
    
    This is the canonical output format when multiple proposals are generated
    in a single assessment cycle.
    """
    
    # Assessment identity
    assessment_id: AssessmentId
    
    # Timestamp
    timestamp_utc: datetime
    
    # All proposals (frozen tuple)
    proposals: Tuple[DefaultOutput, ...]
    
    # Overall network activation summary
    activation_summary: "DefaultNetworkAssessment"


# =============================================================================
# ASSESSMENT TYPES
# =============================================================================

@dataclass(frozen=True, slots=True)
class DefaultNetworkAssessment:
    """
    Assessment of the DefaultNetwork's current state and recommendations.
    
    This is a semantic assessment - it does NOT command execution.
    """
    
    # Assessment identity
    assessment_id: AssessmentId
    
    # Timestamp
    timestamp_utc: datetime
    
    # Overall activation level (0.0 to 1.0)
    activation_level: float
    
    # Internal orientation score (0.0 to 1.0)
    internal_orientation_score: float
    
    # Proposal counts
    proposal_count: int
    active_proposal_types: Tuple[str, ...]
    
    # Confidence in assessment (0.0 to 1.0)
    confidence: float
    
    # Reasoning (brief explanation of key factors)
    reasoning: Tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DefaultNetworkStateSnapshot:
    """
    Immutable snapshot of the DefaultNetwork's computational state.
    
    This captures only bounded computational state. It does NOT include
    cognitive goals, active task state, or global history.
    """
    
    # Temporal statistics (bounded)
    recent_assessment_count: int = 0
    last_assessment_timestamp_utc: Optional[datetime] = None
    
    # Activation summary (bounded)
    average_activation_level: float = 0.0
    max_activation_level: float = 0.0
    
    # Proposal counts (bounded history)
    total_proposal_count: int = 0
    type_distribution: Mapping[str, int] = field(default_factory=dict)
    
    # Diagnostic counters
    assessment_count: int = 0


# =============================================================================
# VALIDATION TYPES
# =============================================================================

@dataclass(frozen=True, slots=True)
class ValidationResult:
    """
    Result of validation for a single check.
    
    Used by the validation module to report validation outcomes.
    """
    
    # Check identifier
    check_id: str
    
    # Whether validation passed
    is_valid: bool
    
    # Optional error message (only present if not valid)
    error_message: Optional[str] = None
    
    # Optional suggestion for fixing the issue
    suggestion: Optional[str] = None


# =============================================================================
# UTILITY TYPES
# =============================================================================

class NetworkPhase:
    """
    Phase identifier for the DefaultNetwork.
    
    Used to track which phase of development a particular implementation
    corresponds to, without embedding version strings in code.
    """
    
    SCAFFOLD = "4.3.1"