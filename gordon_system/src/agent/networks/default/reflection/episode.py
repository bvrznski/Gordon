# Reflection Episode Models
# =========================

"""
ReflectionEpisode specialization and declarative plans.

ARCHITECTURAL PRINCIPLES:
    - ReflectionEpisode reuses InternalEpisode identity model
    - Plans are declarative, not executable
    - Step kinds define coordination, not algorithms
    - No runtime dependencies
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional, FrozenSet


# =============================================================================
# REFLECTION STEP KINDS - Coordination step categories
# =============================================================================

class ReflectionStepKind:
    """
    Canonical kinds of reflection coordination steps.
    
    Each step kind describes WHAT coordination should occur,
    not HOW it should be implemented. Implementation belongs to
    capability owners.
    
    PROGRESSION FLOW (typical):
        VALIDATE_SUBJECT
            ↓
        RECONSTRUCT_CONTEXT
            ↓
        REQUEST_EVIDENCE
            ↓
        IDENTIFY_ASSUMPTIONS / IDENTIFY_PATTERNS
            ↓
        ANALYZE_CAUSES / GENERATE_PRODUCTS
            ↓
        EVALUATE_PRODUCTS
            ↓
        COMPOSE_OUTCOME
            ↓
        PREPARE_PROPOSALS
    """
    
    # Validation and setup
    VALIDATE_SUBJECT = "validate_subject"
    """Validate subject identity and availability."""
    
    VALIDATE_CONTEXT = "validate_context"
    """Verify context is sufficient for reflection."""
    
    RECONSTRUCT_CONTEXT = "reconstruct_context"
    """Reconstruct relevant context from projections."""
    
    # Evidence collection
    REQUEST_EVIDENCE = "request_evidence"
    """Request evidence from external sources."""
    
    REQUEST_MEMORY_EVIDENCE = "request_memory_evidence"
    """Request memory projections."""
    
    REQUEST_EXECUTION_EVIDENCE = "request_execution_evidence"
    """Request execution state projections."""
    
    REQUEST_IDENTITY_PROJECTION = "request_identity_projection"
    """Request identity state projection."""
    
    REQUEST_NARRATIVE_PROJECTION = "request_narrative_projection"
    """Request narrative projection."""
    
    COLLECT_THOUGHTS = "collect_thoughts"
    """Gather internal thoughts for analysis."""
    
    # Analysis steps
    IDENTIFY_ASSUMPTIONS = "identify_assumptions"
    """Identify assumptions influencing activity."""
    
    IDENTIFY_PATTERNS = "identify_patterns"
    """Detect patterns across evidence."""
    
    IDENTIFY_CONTRADICTIONS = "identify_contradictions"
    """Detect contradictions or inconsistencies."""
    
    ANALYZE_CAUSES = "analyze_causes"
    """Analyze causal relationships."""
    
    ANALYZE_CONSEQUENCES = "analyze_consequences"
    """Analyze outcome consequences."""
    
    # Product generation
    GENERATE_INSIGHT_CANDIDATES = "generate_insight_candidates"
    """Generate potential insights."""
    
    GENERATE_CORRECTION_CANDIDATES = "generate_correction_candidates"
    """Generate correction proposals."""
    
    EVALUATE_REFLECTIVE_PRODUCTS = "evaluate_reflective_products"
    """Evaluate products for confidence and validity."""
    
    VALIDATE_INSIGHT = "validate_insight"
    """Validate a specific insight candidate."""
    
    # Outcome and continuation
    COMPOSE_OUTCOME = "compose_outcome"
    """Compose terminal outcome from products."""
    
    PREPARE_PROPOSALS = "prepare_proposals"
    """Prepare follow-up proposals and recommendations."""
    
    @classmethod
    def all_step_kinds(cls) -> Tuple[str, ...]:
        """Return all valid step kinds."""
        return (
            cls.VALIDATE_SUBJECT,
            cls.VALIDATE_CONTEXT,
            cls.RECONSTRUCT_CONTEXT,
            cls.REQUEST_EVIDENCE,
            cls.REQUEST_MEMORY_EVIDENCE,
            cls.REQUEST_EXECUTION_EVIDENCE,
            cls.REQUEST_IDENTITY_PROJECTION,
            cls.REQUEST_NARRATIVE_PROJECTION,
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
    
    @classmethod
    def is_evidence_collection(cls, step_kind: str) -> bool:
        """Check if step kind collects evidence."""
        return step_kind in {
            cls.REQUEST_EVIDENCE,
            cls.REQUEST_MEMORY_EVIDENCE,
            cls.REQUEST_EXECUTION_EVIDENCE,
            cls.REQUEST_IDENTITY_PROJECTION,
            cls.REQUEST_NARRATIVE_PROJECTION,
            cls.COLLECT_THOUGHTS,
        }
    
    @classmethod
    def is_analysis(cls, step_kind: str) -> bool:
        """Check if step kind performs analysis."""
        return step_kind in {
            cls.IDENTIFY_ASSUMPTIONS,
            cls.IDENTIFY_PATTERNS,
            cls.IDENTIFY_CONTRADICTIONS,
            cls.ANALYZE_CAUSES,
            cls.ANALYZE_CONSEQUENCES,
        }
    
    @classmethod
    def is_product_generation(cls, step_kind: str) -> bool:
        """Check if step kind generates reflective products."""
        return step_kind in {
            cls.GENERATE_INSIGHT_CANDIDATES,
            cls.GENERATE_CORRECTION_CANDIDATES,
        }


# =============================================================================
# REFLECTION PLAN - Declarative coordination plan
# =============================================================================

@dataclass(frozen=True, slots=True)
class ReflectionStep:
    """
    One step in a reflection plan.
    
    A step describes what coordination should occur without
    embedding runtime execution details. Implementation belongs
    to capability owners.
    
    PROPERTIES:
        • step_id: Unique identifier within the plan
        • kind: What type of step this is (ReflectionStepKind.*)
        • description: Human-readable explanation
        • requires_evidence: Whether evidence must be collected first
        • produces_products: Whether this step generates products
        • dependency_ids: IDs of steps that must complete first
    """
    
    step_id: str
    """Unique identifier within the plan."""
    
    kind: str  # ReflectionStepKind.*
    """The coordination task for this step."""
    
    description: str = ""
    """Human-readable explanation."""
    
    requires_evidence: bool = False
    """If true, evidence collection must complete first."""
    
    produces_products: bool = False
    """If true, this step generates reflective products."""
    
    dependency_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Step IDs that must complete before this one."""


@dataclass(frozen=True, slots=True)
class ReflectionPlan:
    """
    Immutable declarative plan for reflection coordination.
    
    A plan is a directed acyclic graph (DAG) of steps. Each step
    describes what coordination should occur without runtime details.
    
    PROPERTIES:
        • plan_id: Unique identifier
        • purpose: The purpose this plan serves
        • subject_kind: What type of subject this plan targets
        • steps: All steps in the plan (DAG)
        • start_step_ids: Steps with no dependencies
        • end_step_ids: Steps with no dependents
        • depth: Maximum step dependency chain length
    
    BOUNDEDNESS:
        The plan must be finite and bounded. No infinite loops.
    
    NOT RESPONSIBLE FOR:
        - Executing steps
        - Allocating resources
        - Scheduling coordination
    """
    
    plan_id: str
    """Unique identifier for this plan."""
    
    purpose_kind: str  # ReflectionPurposeKind.*
    """The purpose this plan serves."""
    
    subject_kinds: Tuple[str, ...] = field(default_factory=tuple)
    """Subject kinds this plan targets (empty = all)."""
    
    steps: Tuple[ReflectionStep, ...] = field(default_factory=tuple)
    """All steps in the plan (DAG structure)."""
    
    # Computed properties
    start_step_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Step IDs with no dependencies."""
    
    end_step_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Step IDs with no dependents."""
    
    depth: int = 0
    """Maximum step dependency chain length."""
    
    @classmethod
    def outcome_review_plan(cls, plan_id: str) -> ReflectionPlan:
        """
        Create a standard outcome review plan.
        
        Outcomes are reviewed for alignment with objectives,
        success factors, and failure contributions.
        """
        steps = (
            ReflectionStep(
                step_id="validate_subject",
                kind=ReflectionStepKind.VALIDATE_SUBJECT,
                description="Validate subject identity and availability",
            ),
            ReflectionStep(
                step_id="reconstruct_context",
                kind=ReflectionStepKind.RECONSTRUCT_CONTEXT,
                description="Reconstruct relevant context from projections",
                requires_evidence=False,
                dependency_ids=("validate_subject",),
            ),
            ReflectionStep(
                step_id="collect_evidence",
                kind=ReflectionStepKind.REQUEST_EVIDENCE,
                description="Request outcome and execution evidence",
                requires_evidence=True,
                dependency_ids=("reconstruct_context",),
            ),
            ReflectionStep(
                step_id="analyze_success_factors",
                kind=ReflectionStepKind.ANALYZE_CAUSES,
                description="Identify success factors contributing to outcome",
                produces_products=True,
                dependency_ids=("collect_evidence",),
            ),
            ReflectionStep(
                step_id="analyze_failure_factors",
                kind=ReflectionStepKind.ANALYZE_CONSEQUENCES,
                description="Analyze failure contributions if outcome failed",
                produces_products=True,
                dependency_ids=("collect_evidence",),
            ),
            ReflectionStep(
                step_id="evaluate_products",
                kind=ReflectionStepKind.EVALUATE_REFLECTIVE_PRODUCTS,
                description="Evaluate products for confidence and validity",
                dependency_ids=("analyze_success_factors", "analyze_failure_factors"),
            ),
            ReflectionStep(
                step_id="compose_outcome",
                kind=ReflectionStepKind.COMPOSE_OUTCOME,
                description="Compose terminal outcome from evaluated products",
                dependency_ids=("evaluate_products",),
            ),
            ReflectionStep(
                step_id="prepare_proposals",
                kind=ReflectionStepKind.PREPARE_PROPOSALS,
                description="Prepare follow-up proposals and recommendations",
                dependency_ids=("compose_outcome",),
            ),
        )
        
        return cls._from_steps(plan_id, "outcome_review", steps)
    
    @classmethod
    def assumption_review_plan(cls, plan_id: str) -> ReflectionPlan:
        """
        Create an assumption review plan.
        
        Assumptions are identified and evaluated for their influence
        on activity and outcomes.
        """
        steps = (
            ReflectionStep(
                step_id="validate_subject",
                kind=ReflectionStepKind.VALIDATE_SUBJECT,
                description="Validate subject identity and availability",
            ),
            ReflectionStep(
                step_id="reconstruct_context",
                kind=ReflectionStepKind.RECONSTRUCT_CONTEXT,
                description="Reconstruct context around decision points",
                requires_evidence=False,
                dependency_ids=("validate_subject",),
            ),
            ReflectionStep(
                step_id="identify_assumptions",
                kind=ReflectionStepKind.IDENTIFY_ASSUMPTIONS,
                description="Identify explicit and inferred assumptions",
                produces_products=True,
                dependency_ids=("reconstruct_context",),
            ),
            ReflectionStep(
                step_id="collect_evidence",
                kind=ReflectionStepKind.COLLECT_THOUGHTS,
                description="Gather thoughts supporting and opposing each assumption",
                requires_evidence=True,
                dependency_ids=("identify_assumptions",),
            ),
            ReflectionStep(
                step_id="evaluate_assumptions",
                kind=ReflectionStepKind.EVALUATE_REFLECTIVE_PRODUCTS,
                description="Evaluate assumptions for validity and impact",
                dependency_ids=("collect_evidence",),
            ),
            ReflectionStep(
                step_id="compose_outcome",
                kind=ReflectionStepKind.COMPOSE_OUTCOME,
                description="Compose terminal outcome from assumption analysis",
                dependency_ids=("evaluate_assumptions",),
            ),
        )
        
        return cls._from_steps(plan_id, "assumption_review", steps)
    
    @classmethod
    def pattern_discovery_plan(cls, plan_id: str) -> ReflectionPlan:
        """
        Create a pattern discovery plan.
        
        Patterns are detected across multiple episodes or evidence items.
        """
        steps = (
            ReflectionStep(
                step_id="validate_subject",
                kind=ReflectionStepKind.VALIDATE_SUBJECT,
                description="Validate subject identity and availability",
            ),
            ReflectionStep(
                step_id="collect_evidence",
                kind=ReflectionStepKind.COLLECT_THOUGHTS,
                description="Gather evidence items from multiple episodes",
                requires_evidence=True,
                dependency_ids=("validate_subject",),
            ),
            ReflectionStep(
                step_id="identify_patterns",
                kind=ReflectionStepKind.IDENTIFY_PATTERNS,
                description="Detect patterns across evidence",
                produces_products=True,
                dependency_ids=("collect_evidence",),
            ),
            ReflectionStep(
                step_id="analyze_exceptions",
                kind=ReflectionStepKind.ANALYZE_CONSEQUENCES,
                description="Identify exceptions and edge cases for each pattern",
                produces_products=True,
                dependency_ids=("identify_patterns",),
            ),
            ReflectionStep(
                step_id="validate_patterns",
                kind=ReflectionStepKind.VALIDATE_INSIGHT,
                description="Validate patterns against evidence",
                dependency_ids=("analyze_exceptions",),
            ),
            ReflectionStep(
                step_id="compose_outcome",
                kind=ReflectionStepKind.COMPOSE_OUTCOME,
                description="Compose terminal outcome from pattern analysis",
                dependency_ids=("validate_patterns",),
            ),
        )
        
        return cls._from_steps(plan_id, "pattern_discovery", steps)
    
    @classmethod
    def insight_generation_plan(cls, plan_id: str) -> ReflectionPlan:
        """
        Create an insight generation plan.
        
        Insights are generated from prior activity and evaluated for validity.
        """
        steps = (
            ReflectionStep(
                step_id="reconstruct_context",
                kind=ReflectionStepKind.RECONSTRUCT_CONTEXT,
                description="Reconstruct relevant context",
                requires_evidence=False,
            ),
            ReflectionStep(
                step_id="collect_thoughts",
                kind=ReflectionStepKind.COLLECT_THOUGHTS,
                description="Gather internal thoughts for analysis",
                requires_evidence=True,
                dependency_ids=("reconstruct_context",),
            ),
            ReflectionStep(
                step_id="generate_candidates",
                kind=ReflectionStepKind.GENERATE_INSIGHT_CANDIDATES,
                description="Generate potential insights from thoughts",
                produces_products=True,
                dependency_ids=("collect_thoughts",),
            ),
            ReflectionStep(
                step_id="evaluate_insights",
                kind=ReflectionStepKind.EVALUATE_REFLECTIVE_PRODUCTS,
                description="Evaluate insight candidates for confidence and validity",
                dependency_ids=("generate_candidates",),
            ),
            ReflectionStep(
                step_id="compose_outcome",
                kind=ReflectionStepKind.COMPOSE_OUTCOME,
                description="Compose terminal outcome from validated insights",
                dependency_ids=("evaluate_insights",),
            ),
        )
        
        return cls._from_steps(plan_id, "insight_generation", steps)
    
    @classmethod
    def _from_steps(
        cls,
        plan_id: str,
        purpose_kind: str,
        steps: Tuple[ReflectionStep, ...],
    ) -> ReflectionPlan:
        """
        Create a reflection plan from steps, computing graph properties.
        
        Args:
            plan_id: Unique identifier for the plan
            purpose_kind: The purpose this plan serves
            steps: All steps in the plan
            
        Returns:
            New ReflectionPlan instance with computed properties
        """
        # Build dependency map (step_id -> dependents)
        dependents: dict[str, list[str]] = {s.step_id: [] for s in steps}
        for step in steps:
            for dep_id in step.dependency_ids:
                if dep_id in dependents:
                    dependents[dep_id].append(step.step_id)
        
        # Find start and end steps
        start_step_ids = tuple(
            s.step_id for s in steps if not s.dependency_ids
        )
        end_step_ids = tuple(
            s.step_id for s in steps if not dependents.get(s.step_id, [])
        )
        
        # Compute depth (longest dependency chain)
        depth = cls._compute_depth(steps)
        
        return cls(
            plan_id=plan_id,
            purpose_kind=purpose_kind,
            steps=steps,
            start_step_ids=start_step_ids,
            end_step_ids=end_step_ids,
            depth=depth,
        )
    
    @classmethod
    def _compute_depth(cls, steps: Tuple[ReflectionStep, ...]) -> int:
        """Compute maximum dependency chain length."""
        if not steps:
            return 0
        
        # Build graph for DFS
        dependencies = {s.step_id: s.dependency_ids for s in steps}
        
        memo: dict[str, int] = {}
        
        def dfs(step_id: str) -> int:
            if step_id in memo:
                return memo[step_id]
            
            deps = dependencies.get(step_id, ())
            if not deps:
                memo[step_id] = 1
                return 1
            
            max_depth = max(dfs(dep) for dep in deps)
            memo[step_id] = max_depth + 1
            return memo[step_id]
        
        return max(dfs(s.step_id) for s in steps)


# =============================================================================
# REFLECTION EPISODE - Specialized InternalEpisode profile
# =============================================================================

@dataclass(frozen=True, slots=True)
class ReflectionEpisode:
    """
    Specialized episode profile for reflection coordination.
    
    A ReflectionEpisode IS an InternalEpisode with additional
    reflection-specific metadata. It reuses the core identity,
    lifecycle, and state models without duplication.
    
    PROPERTIES:
        • episode_id: Stable identity (reused from InternalEpisode)
        • revision: Monotonically increasing revision number
        • created_at_utc: When episode was created
        
    REFLECTION-SPECIFIC FIELDS:
        • purpose: Canonical reflection purpose
        • subject: What is being reflected upon
        • scope: Bounded constraints on reflection
        • plan_id: Active reflection plan
        • expected_products: Product kinds expected
        • depth: Current reflection depth (for recursion limits)
        • recursion_lineage: Parent IDs in recursion chain
        • product_count: Number of products generated
        • contradiction_ids: Detected contradictions
        
    NOT RESPONSIBLE FOR:
        - Executing reflection algorithms
        - Allocating runtime resources
        - Scheduling execution
    """
    
    # Identity and lifecycle (reused from InternalEpisode)
    episode_id: str
    """Unique identifier for this episode."""
    
    revision: int = 1
    """Monotonically increasing revision number."""
    
    created_at_utc: str = ""
    """When the episode was created (ISO format string)."""
    
    # Reflection-specific metadata
    purpose: str = "general_reflection"
    """Canonical reflection purpose kind."""
    
    subject_kind: str = "general_experience"
    """Subject kind being reflected upon."""
    
    scope_json: str = "{}"
    """Serialized ReflectionScope as JSON-compatible dict or string reference."""
    
    # Plan and progress
    plan_id: Optional[str] = None
    """Active reflection plan ID."""
    
    expected_products: Tuple[str, ...] = field(default_factory=tuple)
    """Product kinds expected from this reflection."""
    
    depth: int = 1
    """Current reflection depth (for recursion limits)."""
    
    recursion_lineage: Tuple[str, ...] = field(default_factory=tuple)
    """Parent episode IDs in recursion chain (root to parent)."""
    
    # Progress tracking
    product_count: int = 0
    """Number of products generated so far."""
    
    contradiction_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of detected contradictions."""
    
    @classmethod
    def create(
        cls,
        episode_id: str,
        purpose: str,
        subject_kind: str,
        scope_json: str,
        context_id: str,
        plan_id: Optional[str] = None,
        parent_episode_id: Optional[str] = None,
        depth: int = 1,
    ) -> ReflectionEpisode:
        """
        Create a new reflection episode.
        
        Args:
            episode_id: Unique identifier
            purpose: Canonical reflection purpose kind
            subject_kind: Subject kind being reflected upon
            scope_json: Serialized scope constraints
            context_id: Bound context reference
            plan_id: Optional active plan ID
            parent_episode_id: Parent if derived from another
            depth: Current recursion depth
            
        Returns:
            New ReflectionEpisode instance
        """
        lineage = (parent_episode_id,) if parent_episode_id else ()
        
        return cls(
            episode_id=episode_id,
            revision=1,
            purpose=purpose,
            subject_kind=subject_kind,
            scope_json=scope_json,
            plan_id=plan_id,
            depth=depth,
            recursion_lineage=lineage,
        )
    
    def can_accept_product(self, product_kind: str) -> bool:
        """Check if this episode is allowed to accept a given product kind."""
        return not self.expected_products or product_kind in self.expected_products
    
    def has_reached_depth_limit(self, max_depth: int = 3) -> bool:
        """Check if recursion depth limit would be exceeded."""
        return self.depth >= max_depth
    
    def adds_new_evidence_to_lineage(self, new_product_count: int) -> bool:
        """
        Check if this episode adds new evidence compared to its lineage.
        
        For recursive reflection: child must add new evidence or have
        narrower scope than parent.
        """
        # This would check actual product content against parent products
        # Implementation depends on product comparison logic
        return new_product_count > 0
    
    def is_terminal(self) -> bool:
        """Check if this episode has reached a terminal state."""
        # Terminal states are determined by lifecycle in the broader model
        # This is advisory - actual termination happens via transitions
        return False