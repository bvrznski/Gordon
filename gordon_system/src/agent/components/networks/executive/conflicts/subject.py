# Executive Conflict Subject Types
# =================================

"""
Types for representing conflict subjects - the executive entities that are
involved in or affected by a conflict.

A conflict subject is any semantic structure whose state, requirements,
or relationships contribute to or are impacted by an executive conflict.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveConflictSubjectKind:
    """
    Kinds of conflict subjects that may be involved in executive conflicts.
    
    Each kind represents a different type of semantic structure that can
    participate in or cause a conflict.
    """
    
    EXECUTIVE_PROGRAM = "executive_program"
    """An active ExecutiveProgram."""
    
    EXECUTIVE_TASK_SET = "executive_task_set"
    """An active ExecutiveTaskSet."""
    
    GOAL = "goal"
    """A goal (from the executive goal system)."""
    
    COMMITMENT = "commitment"
    """A commitment (from the executive commitment system)."""
    
    PRIORITY_ASSESSMENT = "priority_assessment"
    """A priority assessment (from the priorities system)."""
    
    RULE = "rule"
    """A rule or constraint."""
    
    CONSTRAINT = "constraint"
    """A binding constraint."""
    
    ASSUMPTION = "assumption"
    """An assumption underlying executive planning."""
    
    HYPOTHESIS = "hypothesis"
    """A hypothesis being evaluated by reasoning."""
    
    STRATEGY = "strategy"
    """An active strategy or approach."""
    
    PLAN = "plan"
    """A plan (from the Planning network)."""
    
    REASONING_PRODUCT = "reasoning_product"
    """A product of Reasoning processes."""
    
    DECISION_REQUIREMENT = "decision_requirement"
    """A decision requirement from the Decision network."""
    
    DECISION_CANDIDATE = "decision_candidate"
    """A candidate solution for a decision."""
    
    ACTION_CANDIDATE = "action_candidate"
    """An admissible action candidate."""
    
    EXPECTED_OUTCOME = "expected_outcome"
    """Expected outcome of a plan or action."""
    
    OBSERVED_OUTCOME = "observed_outcome"
    """Actual observed outcome from execution."""
    
    PREDICTION = "prediction"
    """A predictive model output."""
    
    OBSERVATION = "observation"
    """An observation from the environment."""
    
    FOCUS_TARGET = "focus_target"
    """Current focus target (from Focusing network)."""
    
    MOTIVATIONAL_STATE = "motivational_state"
    """Motivation state projection."""
    
    WORKING_MEMORY_REQUIREMENT = "working_memory_requirement"
    """Working memory content requirement."""
    
    WORKSPACE_ITEM = "workspace_item"
    """Workspace admission item."""
    
    POLICY = "policy"
    """Policy requirement or rule."""
    
    SECURITY_REQUIREMENT = "security_requirement"
    """Security constraint or permission."""
    
    CAPABILITY_REQUIREMENT = "capability_requirement"
    """Required capability for execution."""
    
    RESOURCE_PROJECTION = "resource_projection"
    """Resource availability projection."""
    
    AUTHORITY_DECISION = "authority_decision"
    """Authority decision (from external authority)."""
    
    COMMUNICATION_REQUIREMENT = "communication_requirement"
    """Communication or information flow requirement."""
    
    GENERAL_EXECUTIVE_CONDITION = "general_executive_condition"
    """A general executive condition not fitting other categories."""
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all subject kind values as a tuple."""
        return (
            cls.EXECUTIVE_PROGRAM,
            cls.EXECUTIVE_TASK_SET,
            cls.GOAL,
            cls.COMMITMENT,
            cls.PRIORITY_ASSESSMENT,
            cls.RULE,
            cls.CONSTRAINT,
            cls.ASSUMPTION,
            cls.HYPOTHESIS,
            cls.STRATEGY,
            cls.PLAN,
            cls.REASONING_PRODUCT,
            cls.DECISION_REQUIREMENT,
            cls.DECISION_CANDIDATE,
            cls.ACTION_CANDIDATE,
            cls.EXPECTED_OUTCOME,
            cls.OBSERVED_OUTCOME,
            cls.PREDICTION,
            cls.OBSERVATION,
            cls.FOCUS_TARGET,
            cls.MOTIVATIONAL_STATE,
            cls.WORKING_MEMORY_REQUIREMENT,
            cls.WORKSPACE_ITEM,
            cls.POLICY,
            cls.SECURITY_REQUIREMENT,
            cls.CAPABILITY_REQUIREMENT,
            cls.RESOURCE_PROJECTION,
            cls.AUTHORITY_DECISION,
            cls.COMMUNICATION_REQUIREMENT,
            cls.GENERAL_EXECUTIVE_CONDITION,
        )


@dataclass(frozen=True)
class ExecutiveConflictSubject:
    """
    A subject involved in a conflict - the semantic entity that has conflicting
    or competing conditions.
    
    Every subject preserves its source identity, owner, revision, factuality,
    privacy, and provenance even though it is referenced, not embedded.
    """
    
    kind: str  # ExecutiveConflictSubjectKind value
    """The type of this subject."""
    
    reference_id: str
    """Reference ID to the external semantic entity."""
    
    source_owner: str = "unknown"
    """Owner of the source system that owns this subject."""
    
    source_authority: str = "executive_network_internal"
    """Authority level for this subject."""
    
    revision: int = 1
    """Revision of the subject when conflict was assessed."""
    
    factuality_class: str = "factual"
    """Classification of how factual this representation is."""
    
    confidence_class: str = "unknown"
    """Confidence in the subject's state or requirements."""
    
    privacy_classification: str = "internal"
    """Privacy classification of this subject reference."""
    
    provenance_acquired_at_utc: float = 0.0
    """When this subject was acquired for conflict assessment."""
    
    @classmethod
    def from_program(
        cls,
        program_id: str,
        revision: int = 1,
    ) -> "ExecutiveConflictSubject":
        """Create a subject reference to an ExecutiveProgram."""
        return cls(
            kind=ExecutiveConflictSubjectKind.EXECUTIVE_PROGRAM,
            reference_id=program_id,
            source_owner="executive_network",
            revision=revision,
            factuality_class="factual",
            confidence_class="high",
        )
    
    @classmethod
    def from_task_set(
        cls,
        task_set_id: str,
        revision: int = 1,
    ) -> "ExecutiveConflictSubject":
        """Create a subject reference to an ExecutiveTaskSet."""
        return cls(
            kind=ExecutiveConflictSubjectKind.EXECUTIVE_TASK_SET,
            reference_id=task_set_id,
            source_owner="executive_network",
            revision=revision,
            factuality_class="factual",
            confidence_class="high",
        )
    
    @classmethod
    def from_goal(
        cls,
        goal_id: str,
        revision: int = 1,
    ) -> "ExecutiveConflictSubject":
        """Create a subject reference to a Goal."""
        return cls(
            kind=ExecutiveConflictSubjectKind.GOAL,
            reference_id=goal_id,
            source_owner="executive_network",
            revision=revision,
            factuality_class="factual",
            confidence_class="unknown",
        )
    
    @classmethod
    def from_commitment(
        cls,
        commitment_id: str,
        revision: int = 1,
    ) -> "ExecutiveConflictSubject":
        """Create a subject reference to a Commitment."""
        return cls(
            kind=ExecutiveConflictSubjectKind.COMMITMENT,
            reference_id=commitment_id,
            source_owner="executive_network",
            revision=revision,
            factuality_class="factual",
            confidence_class="unknown",
        )


__all__: Tuple[str, ...] = (
    "ExecutiveConflictSubjectKind",
    "ExecutiveConflictSubject",
)