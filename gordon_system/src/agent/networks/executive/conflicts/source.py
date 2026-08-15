# Executive Conflict Source Types
# ================================

"""
Types for representing conflict sources - the systems or structures that
contribute evidence, requirements, or conditions to an executive conflict.

A conflict source reference preserves ownership and authority information
without embedding the full object.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class ExecutiveConflictSourceCategory:
    """
    Categories of sources that may contribute to executive conflicts.
    
    Each category represents a different source domain that can provide
    input, evidence, or constraints relevant to conflict assessment.
    """
    
    EXECUTIVE_STATE = "executive_state"
    """Executive state changes."""
    
    EXECUTIVE_CONTEXT = "executive_context"
    """Executive context projections."""
    
    EXECUTIVE_PROGRAM = "executive_program"
    """Executive Programs."""
    
    EXECUTIVE_TASK_SET = "executive_task_set"
    """Executive Task Sets."""
    
    GOAL_COORDINATION = "goal_coordination"
    """Goal coordination from Phase 4.4.4."""
    
    COMMITMENT_COORDINATION = "commitment_coordination"
    """Commitment coordination from Phase 4.4.4."""
    
    PRIORITY_COORDINATION = "priority_coordination"
    """Priority coordination from Phase 4.4.4."""
    
    ALERTING_NETWORK = "alerting_network"
    """Alerting network projections."""
    
    FOCUSED_NETWORK = "focusing_network"
    """Focusing network projections."""
    
    DEFAULT_NETWORK = "default_network"
    """Default Network products."""
    
    MOTIVATION = "motivation"
    """Motivation state projections."""
    
    WORKING_MEMORY = "working_memory"
    """Working Memory state projections."""
    
    WORKSPACE = "workspace"
    """Workspace admission projections."""
    
    PLANNING = "planning"
    """Planning network products (plans, strategies)."""
    
    REASONING = "reasoning"
    """Reasoning network products (conclusions, deductions)."""
    
    DECISION = "decision"
    """Decision network products (requirements, candidates)."""
    
    ACTION_SELECTION = "action_selection"
    """Action Selection network products (candidates, constraints)."""
    
    ACTION_OUTCOME = "action_outcome"
    """Action execution outcomes."""
    
    PREDICTION = "prediction"
    """Predictive model outputs."""
    
    OBSERVATION = "observation"
    """Observed environmental data."""
    
    MONITORING = "monitoring"
    """Monitoring system results."""
    
    EVALUATION = "evaluation"
    """Evaluation network assessments."""
    
    POLICY = "policy"
    """Policy requirements and prohibitions."""
    
    SECURITY = "security"
    """Security constraints and permissions."""
    
    COMMUNICATION = "communication"
    """Communication state projections."""
    
    EXTERNAL_SYSTEM = "external_system"
    """External system inputs or decisions."""
    
    USER = "user"
    """User requests or guidance."""
    
    UNKNOWN = "unknown"
    """Unknown source category."""
    
    @classmethod
    def all_categories(cls) -> Tuple[str, ...]:
        """Return all source categories as a tuple."""
        return (
            cls.EXECUTIVE_STATE,
            cls.EXECUTIVE_CONTEXT,
            cls.EXECUTIVE_PROGRAM,
            cls.EXECUTIVE_TASK_SET,
            cls.GOAL_COORDINATION,
            cls.COMMITMENT_COORDINATION,
            cls.PRIORITY_COORDINATION,
            cls.ALERTING_NETWORK,
            cls.FOCUSED_NETWORK,
            cls.DEFAULT_NETWORK,
            cls.MOTIVATION,
            cls.WORKING_MEMORY,
            cls.WORKSPACE,
            cls.PLANNING,
            cls.REASONING,
            cls.DECISION,
            cls.ACTION_SELECTION,
            cls.ACTION_OUTCOME,
            cls.PREDICTION,
            cls.OBSERVATION,
            cls.MONITORING,
            cls.EVALUATION,
            cls.POLICY,
            cls.SECURITY,
            cls.COMMUNICATION,
            cls.EXTERNAL_SYSTEM,
            cls.USER,
            cls.UNKNOWN,
        )


@dataclass(frozen=True)
class ExecutiveConflictSourceReference:
    """
    Reference to a source system contributing to an executive conflict.
    
    This does NOT transfer ownership of the source. It merely references
    and attributes the contribution for traceability and provenance.
    """
    
    category: str  # ExecutiveConflictSourceCategory value
    """The category of this source."""
    
    reference_id: str
    """Reference ID to the external system or product."""
    
    source_owner: str = "unknown"
    """Owner of the source system."""
    
    source_authority: str = "executive_network_internal"
    """Authority level for this source."""
    
    revision: int = 1
    """Revision of the source when conflict was assessed."""
    
    contribution_kind: str = "evidence"
    """Kind of contribution (evidence, constraint, requirement, etc.)."""
    
    factuality_class: str = "factual"
    """Classification of how factual this source representation is."""
    
    confidence_class: str = "unknown"
    """Confidence in the source's reliability."""
    
    privacy_classification: str = "internal"
    """Privacy classification of this source reference."""
    
    provenance_acquired_at_utc: float = 0.0
    """When this source was acquired for conflict assessment."""
    
    @classmethod
    def from_program(
        cls,
        program_id: str,
        revision: int = 1,
    ) -> "ExecutiveConflictSourceReference":
        """Create a source reference to an ExecutiveProgram."""
        return cls(
            category=ExecutiveConflictSourceCategory.EXECUTIVE_PROGRAM,
            reference_id=program_id,
            source_owner="executive_network",
            revision=revision,
            contribution_kind="constraint",
            factuality_class="factual",
            confidence_class="high",
        )
    
    @classmethod
    def from_task_set(
        cls,
        task_set_id: str,
        revision: int = 1,
    ) -> "ExecutiveConflictSourceReference":
        """Create a source reference to an ExecutiveTaskSet."""
        return cls(
            category=ExecutiveConflictSourceCategory.EXECUTIVE_TASK_SET,
            reference_id=task_set_id,
            source_owner="executive_network",
            revision=revision,
            contribution_kind="requirement",
            factuality_class="factual",
            confidence_class="high",
        )
    
    @classmethod
    def from_policy(
        cls,
        policy_id: str,
        revision: int = 1,
    ) -> "ExecutiveConflictSourceReference":
        """Create a source reference to a Policy."""
        return cls(
            category=ExecutiveConflictSourceCategory.POLICY,
            reference_id=policy_id,
            source_owner="policy_system",
            revision=revision,
            contribution_kind="prohibition",
            factuality_class="factual",
            confidence_class="high",
        )
    
    @classmethod
    def from_security(
        cls,
        security_id: str,
        revision: int = 1,
    ) -> "ExecutiveConflictSourceReference":
        """Create a source reference to Security constraints."""
        return cls(
            category=ExecutiveConflictSourceCategory.SECURITY,
            reference_id=security_id,
            source_owner="security_system",
            revision=revision,
            contribution_kind="constraint",
            factuality_class="factual",
            confidence_class="high",
        )


__all__: Tuple[str, ...] = (
    "ExecutiveConflictSourceCategory",
    "ExecutiveConflictSourceReference",
)