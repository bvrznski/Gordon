# Reflection Coordination - Canonical Vocabulary
# ===============================================

"""
Canonical enum types and value sets for reflection coordination.

ARCHITECTURAL PRINCIPLES:
    - Immutable enum values
    - Deterministic ordering where applicable
    - Bounded sets (no unbounded expansion)
    - No runtime dependencies
"""

from __future__ import annotations

from typing import Tuple, FrozenSet


# =============================================================================
# REFLECTION PURPOSE KINDS - Canonical categories of reflection intent
# =============================================================================

class ReflectionPurposeKind:
    """
    Canonical purpose kinds for reflection episodes.
    
    Each purpose defines:
        - Expected context requirements
        - Allowed product kinds
        - Completion rules
        - Recursion limits
        - Required confidence thresholds
    """
    
    # Experience and outcome review
    EXPERIENCE_REVIEW = "experience_review"
    """Review past experience to derive insights."""
    
    OUTCOME_REVIEW = "outcome_review"
    """Evaluate outcomes against objectives."""
    
    FAILURE_REVIEW = "failure_review"
    """Analyze failures to identify causes and lessons."""
    
    SUCCESS_REVIEW = "success_review"
    """Examine successes to understand contributing factors."""
    
    # Analysis categories
    ASSUMPTION_REVIEW = "assumption_review"
    """Identify and evaluate assumptions influencing activity."""
    
    PATTERN_DISCOVERY = "pattern_discovery"
    """Detect recurring patterns in semantic activity."""
    
    CONTRADICTION_ANALYSIS = "contradiction_analysis"
    """Examine contradictions for underlying tensions."""
    
    # Product generation
    INSIGHT_GENERATION = "insight_generation"
    """Generate new insights from prior activity."""
    
    # Review categories
    DECISION_REVIEW = "decision_review"
    """Review decisions and their rationales."""
    
    PLAN_REVIEW = "plan_review"
    """Evaluate plan execution against original design."""
    
    BEHAVIOR_REVIEW = "behavior_review"
    """Examine behavioral patterns and their consequences."""
    
    SELF_EVALUATION = "self_evaluation"
    """Assess internal consistency and performance."""
    
    # Integration categories
    IDENTITY_REVIEW = "identity_review"
    """Review identity tensions and continuity."""
    
    NARRATIVE_REVIEW = "narrative_review"
    """Examine narrative coherence and gaps."""
    
    MEMORY_INTEGRATION_REVIEW = "memory_integration_review"
    """Review memory integration quality and completeness."""
    
    POLICY_REVIEW = "policy_review"
    """Evaluate policy effectiveness and consistency."""
    
    ARCHITECTURE_REVIEW = "architecture_review"
    """Assess architectural decisions and alignment."""
    
    # General reflection
    GENERAL_REFLECTION = "general_reflection"
    """General internal review without specific focus."""
    
    @classmethod
    def all_purposes(cls) -> Tuple[str, ...]:
        """Return all valid purpose kinds."""
        return (
            cls.EXPERIENCE_REVIEW,
            cls.OUTCOME_REVIEW,
            cls.FAILURE_REVIEW,
            cls.SUCCESS_REVIEW,
            cls.ASSUMPTION_REVIEW,
            cls.PATTERN_DISCOVERY,
            cls.CONTRADICTION_ANALYSIS,
            cls.INSIGHT_GENERATION,
            cls.DECISION_REVIEW,
            cls.PLAN_REVIEW,
            cls.BEHAVIOR_REVIEW,
            cls.SELF_EVALUATION,
            cls.IDENTITY_REVIEW,
            cls.NARRATIVE_REVIEW,
            cls.MEMORY_INTEGRATION_REVIEW,
            cls.POLICY_REVIEW,
            cls.ARCHITECTURE_REVIEW,
            cls.GENERAL_REFLECTION,
        )
    
    @classmethod
    def requires_insights(cls, purpose: str) -> bool:
        """Check if purpose typically produces insights."""
        return purpose in {
            cls.EXPERIENCE_REVIEW,
            cls.FAILURE_REVIEW,
            cls.INSIGHT_GENERATION,
            cls.SELF_EVALUATION,
        }
    
    @classmethod
    def requires_patterns(cls, purpose: str) -> bool:
        """Check if purpose typically discovers patterns."""
        return purpose in {
            cls.PATTERN_DISCOVERY,
            cls.BEHAVIOR_REVIEW,
        }
    
    @classmethod
    def requires_assumptions(cls, purpose: str) -> bool:
        """Check if purpose typically identifies assumptions."""
        return purpose in {
            cls.ASSUMPTION_REVIEW,
            cls.DECISION_REVIEW,
        }


# =============================================================================
# REFLECTION SUBJECT KINDS - What is being reflected upon
# =============================================================================

class ReflectionSubjectKind:
    """
    Canonical subject kinds for reflection.
    
    Each subject kind has distinct context requirements and evidence sources.
    """
    
    EXECUTION_THREAD = "execution_thread"
    """Reflect on an ExecutionThread's semantic continuity."""
    
    EXECUTION_CYCLE = "execution_cycle"
    """Reflect on one finite semantic progression."""
    
    TASK = "task"
    """Reflect on a specific task or objective."""
    
    PLAN = "plan"
    """Reflect on a plan's design and execution."""
    
    DECISION = "decision"
    """Reflect on a decision and its rationale."""
    
    OUTCOME = "outcome"
    """Reflect on an outcome's alignment with objectives."""
    
    FAILURE = "failure"
    """Reflect on a failure or unexpected result."""
    
    SUCCESS = "success"
    """Reflect on a successful outcome."""
    
    ACTION = "action"
    """Reflect on specific actions taken."""
    
    CONVERSATION = "conversation"
    """Reflect on a conversation's content and structure."""
    
    INTERNAL_EPISODE = "internal_episode"
    """Reflect on an InternalEpisode's coordination."""
    
    INTERNAL_THOUGHT = "internal_thought"
    """Reflect on internal thoughts and their relationships."""
    
    MEMORY = "memory"
    """Reflect on memory content and integration."""
    
    IDENTITY_STATE = "identity_state"
    """Reflect on identity state and consistency."""
    
    NARRATIVE = "narrative"
    """Reflect on narrative structure and continuity."""
    
    POLICY = "policy"
    """Reflect on policy constraints and effectiveness."""
    
    ARCHITECTURE = "architecture"
    """Reflect on architectural decisions and alignment."""
    
    BEHAVIOR_PATTERN = "behavior_pattern"
    """Reflect on behavioral patterns over time."""
    
    CONTRADICTION = "contradiction"
    """Reflect on detected contradictions."""
    
    GENERAL_EXPERIENCE = "general_experience"
    """General reflection without specific subject focus."""
    
    @classmethod
    def all_subjects(cls) -> Tuple[str, ...]:
        """Return all valid subject kinds."""
        return (
            cls.EXECUTION_THREAD,
            cls.EXECUTION_CYCLE,
            cls.TASK,
            cls.PLAN,
            cls.DECISION,
            cls.OUTCOME,
            cls.FAILURE,
            cls.SUCCESS,
            cls.ACTION,
            cls.CONVERSATION,
            cls.INTERNAL_EPISODE,
            cls.INTERNAL_THOUGHT,
            cls.MEMORY,
            cls.IDENTITY_STATE,
            cls.NARRATIVE,
            cls.POLICY,
            cls.ARCHITECTURE,
            cls.BEHAVIOR_PATTERN,
            cls.CONTRADICTION,
            cls.GENERAL_EXPERIENCE,
        )
    
    @classmethod
    def requires_memory_context(cls, subject: str) -> bool:
        """Check if subject typically needs memory context."""
        return subject in {
            cls.MEMORY,
            cls.INTERNAL_EPISODE,
            cls.INTERNAL_THOUGHT,
            cls.NARRATIVE,
            cls.IDENTITY_STATE,
            cls.CONVERSATION,
            cls.GENERAL_EXPERIENCE,
        }
    
    @classmethod
    def requires_execution_context(cls, subject: str) -> bool:
        """Check if subject typically needs execution context."""
        return subject in {
            cls.EXECUTION_THREAD,
            cls.EXECUTION_CYCLE,
            cls.TASK,
            cls.ACTION,
            cls.DECISION,
            cls.PLAN,
            cls.OUTCOME,
            cls.FAILURE,
            cls.SUCCESS,
        }


# =============================================================================
# REFLECTION DEPTH - Bounded exploration levels
# =============================================================================

class ReflectionDepth:
    """
    Canonical depth levels for reflection.
    
    Depth affects context breadth, evidence limits, and expected product counts.
    It does NOT determine runtime duration or token count.
    """
    
    SURFACE = "surface"
    """Shallow reflection with minimal evidence review."""
    
    STANDARD = "standard"
    """Normal depth reflection with balanced evidence."""
    
    DEEP = "deep"
    """Thorough reflection with extensive evidence review."""
    
    COMPREHENSIVE = "comprehensive"
    """Most thorough reflection with maximum evidence review."""
    
    @classmethod
    def all_depths(cls) -> Tuple[str, ...]:
        """Return all valid depth levels."""
        return (cls.SURFACE, cls.STANDARD, cls.DEEP, cls.COMPREHENSIVE)
    
    @classmethod
    def context_budget(cls, depth: str) -> int:
        """Get recommended maximum evidence items for depth level."""
        budgets = {
            cls.SURFACE: 25,
            cls.STANDARD: 100,
            cls.DEEP: 250,
            cls.COMPREHENSIVE: 500,
        }
        return budgets.get(depth, 100)
    
    @classmethod
    def confidence_requirement(cls, depth: str) -> float:
        """Get recommended minimum confidence threshold for depth level."""
        thresholds = {
            cls.SURFACE: 0.3,
            cls.STANDARD: 0.5,
            cls.DEEP: 0.7,
            cls.COMPREHENSIVE: 0.8,
        }
        return thresholds.get(depth, 0.5)
    
    @classmethod
    def max_products(cls, depth: str) -> int:
        """Get recommended maximum products for depth level."""
        limits = {
            cls.SURFACE: 5,
            cls.STANDARD: 15,
            cls.DEEP: 30,
            cls.COMPREHENSIVE: 50,
        }
        return limits.get(depth, 15)


# =============================================================================
# REFLECTION PRODUCT KINDS - Types of reflective products
# =============================================================================

class ReflectiveProductKind:
    """
    Canonical kinds of reflective products.
    
    Products are bounded semantic results generated through reflection.
    They should be compatible with InternalThought but remain distinct
    from runtime execution commands.
    """
    
    # Core product types
    INSIGHT = "insight"
    """Validated insight about prior activity."""
    
    PATTERN = "pattern"
    """Detected pattern across evidence items."""
    
    ASSUMPTION = "assumption"
    """Explicit or inferred assumption influencing activity."""
    
    CONTRADICTION = "contradiction"
    """Detected contradiction or inconsistency."""
    
    CAUSE_HYPOTHESIS = "cause_hypothesis"
    """Proposed causal explanation (not yet validated)."""
    
    CONSEQUENCE_ANALYSIS = "consequence_analysis"
    """Analysis of outcomes and their implications."""
    
    LESSON = "lesson"
    """Extracted lesson from experience."""
    
    # Proposal types
    CORRECTION_PROPOSAL = "correction_proposal"
    """Proposed correction to prior activity."""
    
    IMPROVEMENT_PROPOSAL = "improvement_proposal"
    """Proposed improvement or optimization."""
    
    QUESTION = "question"
    """Open question requiring further investigation."""
    
    UNCERTAINTY = "uncertainty"
    """Identified uncertainty that remains unresolved."""
    
    KNOWLEDGE_GAP = "knowledge_gap"
    """Gap in available knowledge or evidence."""
    
    # Quality assessment
    SUCCESS_FACTOR = "success_factor"
    """Factor contributing to success."""
    
    FAILURE_FACTOR = "failure_factor"
    """Factor contributing to failure."""
    
    RISK = "risk"
    """Identified risk or potential issue."""
    
    # Follow-up types
    FOLLOW_UP_TOPIC = "follow_up_topic"
    """Topic recommended for follow-up investigation."""
    
    NO_MEANINGFUL_RESULT = "no_meaningful_result"
    """Reflection completed without meaningful products."""
    
    @classmethod
    def all_product_kinds(cls) -> Tuple[str, ...]:
        """Return all valid product kinds."""
        return (
            cls.INSIGHT,
            cls.PATTERN,
            cls.ASSUMPTION,
            cls.CONTRADICTION,
            cls.CAUSE_HYPOTHESIS,
            cls.CONSEQUENCE_ANALYSIS,
            cls.LESSON,
            cls.CORRECTION_PROPOSAL,
            cls.IMPROVEMENT_PROPOSAL,
            cls.QUESTION,
            cls.UNCERTAINTY,
            cls.KNOWLEDGE_GAP,
            cls.SUCCESS_FACTOR,
            cls.FAILURE_FACTOR,
            cls.RISK,
            cls.FOLLOW_UP_TOPIC,
            cls.NO_MEANINGFUL_RESULT,
        )
    
    @classmethod
    def is_hypothesis(cls, product_kind: str) -> bool:
        """Check if product kind represents a hypothesis (not yet validated)."""
        return product_kind in {
            cls.CAUSE_HYPOTHESIS,
            cls.QUESTION,
            cls.KNOWLEDGE_GAP,
        }
    
    @classmethod
    def is_proposal(cls, product_kind: str) -> bool:
        """Check if product kind represents an actionable proposal."""
        return product_kind in {
            cls.CORRECTION_PROPOSAL,
            cls.IMPROVEMENT_PROPOSAL,
            cls.FOLLOW_UP_TOPIC,
        }


# =============================================================================
# REFLECTION OUTCOME KINDS - Terminal results of reflection
# =============================================================================

class ReflectionOutcomeKind:
    """
    Canonical outcome kinds for reflection episodes.
    
    Outcomes represent what the reflection episode produced, not runtime commands.
    """
    
    # Successful outcomes
    INSIGHTS_PRODUCED = "insights_produced"
    """Valid insights were generated."""
    
    PATTERNS_IDENTIFIED = "patterns_identified"
    """Patterns were discovered in evidence."""
    
    CONTRADICTIONS_IDENTIFIED = "contradictions_identified"
    """Contradictions were detected and recorded."""
    
    ASSUMPTIONS_IDENTIFIED = "assumptions_identified"
    """Material assumptions were identified."""
    
    CORRECTION_PROPOSED = "correction_proposed"
    """A correction was proposed."""
    
    IMPROVEMENT_PROPOSED = "improvement_proposed"
    """An improvement was proposed."""
    
    FOLLOW_UP_REQUIRED = "follow_up_required"
    """Follow-up activities are recommended."""
    
    # Partial outcomes
    PARTIALLY_COMPLETED = "partially_completed"
    """Some reflection steps completed but not all."""
    
    INSUFFICIENT_CONTEXT = "insufficient_context"
    """Context did not meet minimum requirements."""
    
    NO_MEANINGFUL_RESULT = "no_meaningful_result"
    """Reflection completed but produced no meaningful result."""
    
    # Failure states
    FAILED = "failed"
    """Terminated without valid outcome."""
    
    CANCELLED = "cancelled"
    """Terminated before completion."""
    
    EXPIRED = "expired"
    """Terminated due to expiration."""
    
    @classmethod
    def all_outcomes(cls) -> Tuple[str, ...]:
        """Return all valid outcome kinds."""
        return (
            cls.INSIGHTS_PRODUCED,
            cls.PATTERNS_IDENTIFIED,
            cls.CONTRADICTIONS_IDENTIFIED,
            cls.ASSUMPTIONS_IDENTIFIED,
            cls.CORRECTION_PROPOSED,
            cls.IMPROVEMENT_PROPOSED,
            cls.FOLLOW_UP_REQUIRED,
            cls.PARTIALLY_COMPLETED,
            cls.INSUFFICIENT_CONTEXT,
            cls.NO_MEANINGFUL_RESULT,
            cls.FAILED,
            cls.CANCELLED,
            cls.EXPIRED,
        )
    
    @classmethod
    def is_success(cls, outcome: str) -> bool:
        """Check if outcome kind represents successful reflection."""
        return outcome in {
            cls.INSIGHTS_PRODUCED,
            cls.PATTERNS_IDENTIFIED,
            cls.CONTRADICTIONS_IDENTIFIED,
            cls.ASSUMPTIONS_IDENTIFIED,
            cls.CORRECTION_PROPOSED,
            cls.IMPROVEMENT_PROPOSED,
            cls.FOLLOW_UP_REQUIRED,
        }
    
    @classmethod
    def is_terminal(cls, outcome: str) -> bool:
        """Check if outcome kind represents terminal state."""
        return outcome in {
            cls.INSIGHTS_PRODUCED,
            cls.PATTERNS_IDENTIFIED,
            cls.CONTRADICTIONS_IDENTIFIED,
            cls.ASSUMPTIONS_IDENTIFIED,
            cls.CORRECTION_PROPOSED,
            cls.IMPROVEMENT_PROPOSED,
            cls.FOLLOW_UP_REQUIRED,
            cls.PARTIALLY_COMPLETED,
            cls.INSUFFICIENT_CONTEXT,
            cls.NO_MEANINGFUL_RESULT,
            cls.FAILED,
            cls.CANCELLED,
            cls.EXPIRED,
        }


# =============================================================================
# REFLECTION CONTINUATION KINDS - Advisory recommendations
# =============================================================================

class ReflectionContinuationKind:
    """
    Canonical continuation kinds for reflection episodes.
    
    Continuation recommendations are advisory. They do NOT schedule execution.
    """
    
    COMPLETE = "complete"
    """Reflection completed successfully."""
    
    CONTINUE_WITH_CURRENT_CONTEXT = "continue_with_current_context"
    """Continue processing with current context and plan."""
    
    REQUEST_CONTEXT_REFRESH = "request_context_refresh"
    """Refresh context binding with updated projections."""
    
    WAIT_FOR_EVIDENCE = "wait_for_evidence"
    """Wait for additional evidence to become available."""
    
    WAIT_FOR_CAPABILITY = "wait_for_capability"
    """Wait for capability result."""
    
    SUSPEND = "suspend"
    """Suspend processing, may resume later."""
    
    DERIVE_CHILD_EPISODE = "derive_child_episode"
    """Create a child episode for related work."""
    
    REQUEST_SIMULATION = "request_simulation"
    """Request simulation or counterfactual exploration."""
    
    REQUEST_COUNTERFACTUAL = "request_counterfactual"
    """Request counterfactual analysis."""
    
    REQUEST_IDENTITY_REVIEW = "request_identity_review"
    """Request identity review coordination."""
    
    REQUEST_NARRATIVE_REVIEW = "request_narrative_review"
    """Request narrative review coordination."""
    
    SUBMIT_WORKSPACE_CANDIDATE = "submit_workspace_candidate"
    """Submit workspace candidate to conscious workspace."""
    
    REQUEST_EXECUTION_TASK = "request_execution_task"
    """Request an ExecutionTask for persistent coordination."""
    
    FAIL = "fail"
    """Mark as failed with error."""
    
    CANCEL = "cancel"
    """Cancel the reflection episode."""
    
    @classmethod
    def all_continuation_kinds(cls) -> Tuple[str, ...]:
        """Return all valid continuation kinds."""
        return (
            cls.COMPLETE,
            cls.CONTINUE_WITH_CURRENT_CONTEXT,
            cls.REQUEST_CONTEXT_REFRESH,
            cls.WAIT_FOR_EVIDENCE,
            cls.WAIT_FOR_CAPABILITY,
            cls.SUSPEND,
            cls.DERIVE_CHILD_EPISODE,
            cls.REQUEST_SIMULATION,
            cls.REQUEST_COUNTERFACTUAL,
            cls.REQUEST_IDENTITY_REVIEW,
            cls.REQUEST_NARRATIVE_REVIEW,
            cls.SUBMIT_WORKSPACE_CANDIDATE,
            cls.REQUEST_EXECUTION_TASK,
            cls.FAIL,
            cls.CANCEL,
        )
    
    @classmethod
    def is_terminal(cls, kind: str) -> bool:
        """Check if continuation kind represents terminal state."""
        return kind in {
            cls.COMPLETE,
            cls.FAIL,
            cls.CANCEL,
        }
    
    @classmethod
    def requires_external_action(cls, kind: str) -> bool:
        """Check if continuation kind requires external coordination."""
        return kind in {
            cls.REQUEST_CONTEXT_REFRESH,
            cls.WAIT_FOR_EVIDENCE,
            cls.WAIT_FOR_CAPABILITY,
            cls.DERIVE_CHILD_EPISODE,
            cls.REQUEST_SIMULATION,
            cls.REQUEST_COUNTERFACTUAL,
            cls.REQUEST_IDENTITY_REVIEW,
            cls.REQUEST_NARRATIVE_REVIEW,
            cls.SUBMIT_WORKSPACE_CANDIDATE,
            cls.REQUEST_EXECUTION_TASK,
        }


# =============================================================================
# RECURSION RULES - Constraints on recursive reflection
# =============================================================================

class RecursionRule:
    """
    Rules governing recursive reflection (reflection upon reflection).
    
    Recursive reflection is allowed only under strict limits.
    """
    
    REQUIRE_NEW_EVIDENCE = "require_new_evidence"
    """Child must have at least one new evidence item."""
    
    REQUIRE_NARROWER_SCOPE = "require_narrower_scope"
    """Child scope must be narrower than parent scope."""
    
    REQUIRE_DISTINCT_PURPOSE = "require_distinct_purpose"
    """Child purpose must be distinct from parent purpose."""
    
    REQUIRE_INDEPENDENT_VALIDATION = "require_independent_validation"
    """Child must use independent validation criteria."""
    
    MAXIMUM_DEPTH = "maximum_depth"
    """Maximum reflection depth allowed."""
    
    MAXIMUM_DESCENDANTS = "maximum_descendants"
    """Maximum descendant episodes allowed."""
    
    MAXIMUM_NO_RESULT_SEQUENCE = "maximum_no_result_sequence"
    """Maximum consecutive no-result reflections before attenuation."""
