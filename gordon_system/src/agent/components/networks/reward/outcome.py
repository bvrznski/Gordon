# Reward Network - Outcome Model
# ===============================

"""
Outcome model for reward evaluation.

Outcomes represent terminal cognitive or behavioral results that reward 
estimates are computed from. Outcomes remain immutable semantic artifacts.

OUTCOME LAWS:
    OUTCOME-LAW-001: Every Outcome possesses a stable semantic identity.
    OUTCOME-LAW-002: Outcomes are immutable.
    OUTCOME-LAW-003: Outcomes preserve provenance.
    OUTCOME-LAW-004: Outcomes preserve semantic context.
    OUTCOME-LAW-005: Outcomes preserve temporal semantics.
    OUTCOME-LAW-006: Outcome revisions create new Outcome revisions.
    OUTCOME-LAW-007: Outcome schemas remain validated.
    OUTCOME-LAW-008: Outcomes never contain executable behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


OutcomeId = str
"""Unique identifier for an outcome."""


@dataclass(frozen=True)
class OutcomeCategory:
    """
    Canonical category for an outcome type.
    
    Outcome categories define the semantic kind of outcome being evaluated.
    Each category has associated reward evaluation semantics.
    
    CATEGORY KINDS:
        • task_completed: Goal-directed action completed successfully
        • task_failed: Goal-directed action did not achieve target
        • goal_progress: Advance toward a strategic objective
        • resource_acquired: New resources gained (knowledge, material, etc.)
        • resource_lost: Resources lost or depleted
        • prediction_success: Predictive processing succeeded
        • prediction_failure: Prediction error occurred
        • social_interaction: Interaction with other agents
        • cognitive_event: Internal mental state change
        • learning_opportunity: New learning capacity gained
    """
    
    kind: str  # OutcomeCategoryKind.*
    """The category kind (OutcomeCategoryKind.*)"""
    
    @property
    def is_positive(self) -> bool:
        """Check if this category typically indicates positive outcomes."""
        return self.kind in (
            "task_completed",
            "goal_progress", 
            "resource_acquired",
            "prediction_success",
            "social_interaction_positive",
            "learning_opportunity",
        )
    
    @property
    def is_negative(self) -> bool:
        """Check if this category typically indicates negative outcomes."""
        return self.kind in (
            "task_failed",
            "resource_lost",
            "prediction_failure",
            "social_interaction_negative",
        )


@dataclass(frozen=True)
class OutcomeSourceSubsystem:
    """
    Origin subsystem that produced or triggered the outcome.
    
    Source subsystem identification preserves architectural boundaries
    and enables source-specific reward estimation policies.
    
    SUBSYSTEMS:
        • predictive: Predictive Processing Network
        • salience: Salience Network  
        • attention: Attention Network
        • executive: Executive Control Network
        • motivation: Motivation System
        • memory: Memory System
        • action: Action Selection System
    """
    
    subsystem: str  # SourceSubsystem.*
    """Source subsystem identifier."""
    
    trace_id: Optional[str] = None
    """Optional trace ID for cross-network tracking."""


# =============================================================================
# OUTCOME MODEL (Phase 4.10.1 - Part 2)
# =============================================================================

@dataclass(frozen=True, slots=True)
class Outcome:
    """
    Immutable semantic artifact representing a cognitive or behavioral outcome.
    
    Every reward estimate is attached to exactly one Outcome. Outcomes preserve
    identity across all reward computations.
    
    PROPERTIES:
        • outcome_id: Unique identifier for this outcome
        • category: What type of result (OutcomeCategory)
        • source_subsystem: Which network produced this outcome
        • semantic_object: The object/state that was evaluated
        • context: Semantic context for evaluation
        • timescale: Temporal scope (immediate, short-term, etc.)
        • provenance: Traceable documentation reference
        
    OUTCOME KINDS:
        • task_completed: Goal-directed action completed successfully
        • task_failed: Goal-directed action did not achieve target  
        • goal_progress: Advance toward a strategic objective
        • resource_acquired: New resources gained (knowledge, material)
        • resource_lost: Resources lost or depleted
        • prediction_success: Predictive processing succeeded
        • prediction_failure: Prediction error occurred
        • social_interaction: Interaction with other agents
        • cognitive_event: Internal mental state change
        • learning_opportunity: New learning capacity gained
        
    BOUNDEDNESS:
        • summary: Brief text description (not unlimited content)
        • references: References to supporting artifacts, not payloads
        
    NOT RESPONSIBLE FOR:
        • Directly mutating memory, identity, or workspace
        • Creating runtime tasks or threads
        • Scheduling further processing
    """
    
    # Identity and reference
    outcome_id: OutcomeId
    """Unique identifier for this outcome."""
    
    revision: int = 0
    """Revision number for versioning."""
    
    category: OutcomeCategory
    """Semantic category of this outcome."""
    
    source_subsystem: OutcomeSourceSubsystem
    """Origin subsystem that produced or triggered this outcome."""
    
    # Semantic content (bounded)
    semantic_object: str
    """The object, state, or event being evaluated."""
    
    context: Tuple[str, ...] = field(default_factory=tuple)
    """Semantic context for evaluation (e.g., goal_id, task_id)."""
    
    timescale: str = "immediate"  # TimescaleKind.*
    """Temporal scope of this outcome."""
    
    summary: str = ""
    """Brief text description of the outcome."""
    
    references: Tuple[str, ...] = field(default_factory=tuple)
    """References to supporting artifacts (not full payloads)."""
    
    provenance: Optional[str] = None
    """Provenance reference (where this outcome type is documented)."""
    
    # Quality assessment (for traceability, not evaluation)
    confidence: float = 0.5
    """Confidence in the outcome representation."""
    
    created_at_utc: str = ""
    """When this outcome was produced (ISO 8601)."""
    
    @classmethod
    def create(
        cls,
        outcome_id: str,
        category: OutcomeCategory,
        semantic_object: str,
        source_subsystem: OutcomeSourceSubsystem,
        timescale: str = "immediate",
        summary: str = "",
        context: Tuple[str, ...] = tuple(),
    ) -> Outcome:
        """
        Create a new outcome.
        
        Args:
            outcome_id: Unique identifier for this outcome
            category: Semantic category of the outcome
            semantic_object: Object/state being evaluated  
            source_subsystem: Origin subsystem
            timescale: Temporal scope
            summary: Brief description
            context: Semantic context
            
        Returns:
            New Outcome instance
        """
        return cls(
            outcome_id=outcome_id,
            revision=0,
            category=category,
            semantic_object=semantic_object,
            source_subsystem=source_subsystem,
            timescale=timescale,
            summary=summary,
            context=context,
        )
    
    @property
    def canonical_identity(self) -> str:
        """Return fully qualified canonical identity."""
        return f"{self.outcome_id}@v{self.revision}"