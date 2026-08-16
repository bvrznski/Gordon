# Reflection Plan Models
# ======================

"""
Immutable models for reflection plans.

ARCHITECTURAL PRINCIPLES:
    - Plans are declarative (describe what, not how)
    - All plan steps form a DAG (no cycles)
    - No runtime dependencies in domain objects
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


# =============================================================================
# REFLECTION STEP KINDS
# =============================================================================

class ReflectionStepKind:
    """
    Canonical kinds of reflection plan steps.
    
    Each kind represents a coordination step that the reflection
    coordinator should execute. Actual computation is delegated to
    external capabilities.
    """
    
    VALIDATE_SUBJECT = "validate_subject"
    """Validate the subject is appropriate for reflection."""
    
    VALIDATE_CONTEXT = "validate_context"
    """Validate context meets requirements."""
    
    RECONSTRUCT_CONTEXT = "reconstruct_context"
    """Reconstruct context from projections."""
    
    REQUEST_MEMORY_EVIDENCE = "request_memory_evidence"
    """Request memory evidence through contracts."""
    
    REQUEST_EXECUTION_EVIDENCE = "request_execution_evidence"
    """Request execution evidence through contracts."""
    
    REQUEST_IDENTITY_PROJECTION = "request_identity_projection"
    """Request identity state projection."""
    
    REQUEST_NARRATIVE_PROJECTION = "request_narrative_projection"
    """Request narrative projection."""
    
    REQUEST_PREDICTIVE_EVIDENCE = "request_predictive_evidence"
    """Request predictive model evidence."""
    
    COLLECT_THOUGHTS = "collect_thoughts"
    """Collect relevant prior thoughts."""
    
    IDENTIFY_ASSUMPTIONS = "identify_assumptions"
    """Identify assumptions in the subject."""
    
    IDENTIFY_PATTERNS = "identify_patterns"
    """Identify patterns across evidence."""
    
    IDENTIFY_CONTRADICTIONS = "identify_contradictions"
    """Identify contradictions between evidence sources."""
    
    ANALYZE_CAUSES = "analyze_causes"
    """Analyze causal relationships."""
    
    ANALYZE_CONSEQUENCES = "analyze_consequences"
    """Analyze potential consequences."""
    
    GENERATE_INSIGHT_CANDIDATES = "generate_insight_candidates"
    """Generate candidate insights."""
    
    GENERATE_CORRECTION_CANDIDATES = "generate_correction_candidates"
    """Generate correction proposals."""
    
    EVALUATE_REFLECTIVE_PRODUCTS = "evaluate_reflective_products"
    """Evaluate products against criteria."""
    
    VALIDATE_INSIGHT = "validate_insight"
    """Validate individual insights."""
    
    COMPOSE_OUTCOME = "compose_outcome"
    """Compose final reflection outcome."""
    
    PREPARE_PROPOSALS = "prepare_proposals"
    """Prepare follow-up proposals and recommendations."""
    
    @classmethod
    def all_kinds(cls) -> tuple[str, ...]:
        """Return all step kinds."""
        return (
            cls.VALIDATE_SUBJECT,
            cls.VALIDATE_CONTEXT,
            cls.RECONSTRUCT_CONTEXT,
            cls.REQUEST_MEMORY_EVIDENCE,
            cls.REQUEST_EXECUTION_EVIDENCE,
            cls.REQUEST_IDENTITY_PROJECTION,
            cls.REQUEST_NARRATIVE_PROJECTION,
            cls.REQUEST_PREDICTIVE_EVIDENCE,
            cls.COLLECT_THOUGHTS,
            cls.IDENTIFY_ASSUMPTIONS,
            cls.IDENTIFY_PATTERNS,
            cls.IDENTIFY_CONTRADICTIONS,
            cls.ANALYZE_CAUSES,
            cls.ANALYZE_CONSEQUENCES,
            cls.GENERATE_INSIGHT_CANDIDATES,
            cls.GENERATE_CORRECTION_CANDIDATES,
            cls.EVALUATE_REFLECTIVE_PRODUCTS,
            cls.VALIDATE_INSIGHT,
            cls.COMPOSE_OUTCOME,
            cls.PREPARE_PROPOSALS,
        )


# =============================================================================
# REFLECTION PLAN STEP
# =============================================================================

@dataclass(frozen=True, slots=True)
class ReflectionPlanStep:
    """
    Immutable single step in a reflection plan.
    
    A plan step describes one unit of coordination work that the
    reflection coordinator should perform. Actual computation is
    delegated to external capabilities.
    """
    
    step_id: str
    """Unique identifier for this step."""
    
    kind: str  # ReflectionStepKind.*
    """The kind of step."""
    
    description: str = ""
    """Human-readable description."""
    
    dependency_ids: tuple[str, ...] = field(default_factory=tuple)
    """IDs of steps that must complete before this one."""
    
    context_requirements: tuple[str, ...] = field(default_factory=tuple)
    """Context elements required for this step."""
    
    capability_request_kind: Optional[str] = None
    """Capability request kind if this step delegates to a capability."""
    
    @classmethod
    def validate_subject(cls) -> ReflectionPlanStep:
        """Create a subject validation step."""
        return cls(
            step_id="step_validate_subject",
            kind=ReflectionStepKind.VALIDATE_SUBJECT,
            description="Validate the reflection subject is appropriate",
        )
    
    @classmethod
    def reconstruct_context(cls) -> ReflectionPlanStep:
        """Create a context reconstruction step."""
        return cls(
            step_id="step_reconstruct_context",
            kind=ReflectionStepKind.RECONSTRUCT_CONTEXT,
            description="Reconstruct context from projections",
            capability_request_kind="context_projection",
        )
    
    @classmethod
    def identify_assumptions(cls) -> ReflectionPlanStep:
        """Create an assumption identification step."""
        return cls(
            step_id="step_identify_assumptions",
            kind=ReflectionStepKind.IDENTIFY_ASSUMPTIONS,
            description="Identify assumptions influencing activity",
            capability_request_kind="assumption_analysis",
        )
    
    @classmethod
    def identify_patterns(cls) -> ReflectionPlanStep:
        """Create a pattern identification step."""
        return cls(
            step_id="step_identify_patterns",
            kind=ReflectionStepKind.IDENTIFY_PATTERNS,
            description="Identify patterns across evidence",
            dependency_ids=("step_reconstruct_context",),
            capability_request_kind="pattern_detection",
        )
    
    @classmethod
    def compose_outcome(cls) -> ReflectionPlanStep:
        """Create an outcome composition step."""
        return cls(
            step_id="step_compose_outcome",
            kind=ReflectionStepKind.COMPOSE_OUTCOME,
            description="Compose final reflection outcome from products",
            dependency_ids=("step_evaluate_products",),
        )
    
    @classmethod
    def prepare_proposals(cls) -> ReflectionPlanStep:
        """Create a proposals preparation step."""
        return cls(
            step_id="step_prepare_proposals",
            kind=ReflectionStepKind.PREPARE_PROPOSALS,
            description="Prepare follow-up proposals and recommendations",
            dependency_ids=("step_compose_outcome",),
        )


# =============================================================================
# REFLECTION PLAN
# =============================================================================

@dataclass(frozen=True, slots=True)
class ReflectionPlan:
    """
    Immutable declarative reflection plan.
    
    A reflection plan specifies the sequence of coordination steps
    that should be performed for a particular type of reflection.
    Plans remain declarative and delegate actual computation to
    external capabilities.
    """
    
    plan_id: str
    """Unique identifier for this plan."""
    
    purpose_kind: str  # ReflectionPurposeKind.*
    """The purpose this plan serves."""
    
    subject_kind: Optional[str] = None
    """Optional subject kind constraint."""
    
    depth: int = 1
    """Depth level of this plan in the recursion hierarchy."""
    
    steps: tuple[ReflectionPlanStep, ...] = field(default_factory=tuple)
    """Steps in this plan (must form a DAG)."""
    
    default_context_requirements: tuple[str, ...] = field(default_factory=tuple)
    """Default context requirements for all steps."""
    
    @classmethod
    def outcome_review_plan(cls) -> ReflectionPlan:
        """Create an outcome review plan template."""
        return cls(
            plan_id="plan_outcome_review",
            purpose_kind="outcome_review",
            depth=1,
            steps=(
                ReflectionPlanStep.validate_subject(),
                ReflectionPlanStep.reconstruct_context(),
                ReflectionPlanStep.identify_patterns(),
                ReflectionPlanStep.compose_outcome(),
            ),
        )
    
    @classmethod
    def assumption_review_plan(cls) -> ReflectionPlan:
        """Create an assumption review plan template."""
        return cls(
            plan_id="plan_assumption_review",
            purpose_kind="assumption_review",
            depth=1,
            steps=(
                ReflectionPlanStep.validate_subject(),
                ReflectionPlanStep.reconstruct_context(),
                ReflectionPlanStep.identify_assumptions(),
                ReflectionPlanStep.compose_outcome(),
            ),
        )
    
    @classmethod
    def pattern_discovery_plan(cls) -> ReflectionPlan:
        """Create a pattern discovery plan template."""
        return cls(
            plan_id="plan_pattern_discovery",
            purpose_kind="pattern_discovery",
            depth=1,
            steps=(
                ReflectionPlanStep.validate_subject(),
                ReflectionPlanStep.reconstruct_context(),
                ReflectionPlanStep.identify_patterns(),
                ReflectionPlanStep.compose_outcome(),
            ),
        )
    
    def get_step(self, step_id: str) -> Optional[ReflectionPlanStep]:
        """Get a step by its ID."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None
    
    def has_cycle(self) -> bool:
        """Check if plan steps have dependency cycles."""
        step_ids = {step.step_id for step in self.steps}
        
        # Build adjacency list
        dep_map = {}
        for step in self.steps:
            dep_map[step.step_id] = set(step.dependency_ids)
        
        visited = set()
        rec_stack = set()
        
        def has_cycle_from(node_id: str) -> bool:
            if node_id in rec_stack:
                return True
            if node_id not in step_ids:
                return False
            if node_id in visited:
                return False
            
            visited.add(node_id)
            rec_stack.add(node_id)
            
            for dep_id in dep_map.get(node_id, []):
                if has_cycle_from(dep_id):
                    return True
            
            rec_stack.remove(node_id)
            return False
        
        for step_id in step_ids:
            if has_cycle_from(step_id):
                return True
        return False
    
    def is_valid(self) -> bool:
        """Check if plan is valid (DAG, has steps, etc.)."""
        if not self.steps:
            return False
        
        if self.has_cycle():
            return False
        
        return True

