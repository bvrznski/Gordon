# Oriented Network State Composition Types - Phase 4.7.4
# =======================================================

"""
Canonical state composition types for the Oriented Network.

ARCHITECTURAL PRINCIPLES:
    - Deeply immutable (frozen dataclasses)
    - No runtime dependencies
    - Semantic-only representation
    - Versionable and serializable
    - Repository-independent

STATE HIERARCHY:
    OrientedNetworkState (canonical root)
        ├── OrientationState
        ├── GoalState
        ├── ObjectiveState
        ├── TaskState
        ├── ContextState
        ├── ConstraintState
        ├── AssessmentState
        ├── RelationshipState
        ├── RequirementState

COMPOSITION PRINCIPLES:
    - State composes immutable Content references (never duplicates)
    - Composition is explicitly typed and validated
    - No cyclic composition graphs
    - Acyclic state hierarchy
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple, Optional
from enum import Enum

from gordon_system.src.agent.components.networks.oriented.content.base import (
    BaseContent,
    ContentIdentity,
)
from gordon_system.src.agent.components.networks.oriented.state.metadata import (
    StateMetadata,
)


# =============================================================================
# STATE TYPES ENUM
# =============================================================================

class StateType(Enum):
    """
    Canonical state type tags for categorization.
    
    Used for semantic validation and routing without runtime dependencies.
    """
    
    ORIENTED_NETWORK = "oriented_network"
    """Root OrientedNetworkState"""
    
    ORIENTATION = "orientation"
    """OrientationState - current orientation representation"""
    
    GOAL = "goal"
    """GoalState - goal references and context"""
    
    OBJECTIVE = "objective"
    """ObjectiveState - objective references and context"""
    
    TASK = "task"
    """TaskState - task references and context"""
    
    CONTEXT = "context"
    """ContextState - semantic surroundings"""
    
    CONSTRAINT = "constraint"
    """ConstraintState - boundary conditions"""
    
    ASSESSMENT = "assessment"
    """AssessmentState - evaluation summary"""
    
    RELATIONSHIP = "relationship"
    """RelationshipState - explicit connections"""
    
    REQUIREMENT = "requirement"
    """RequirementState - semantic necessities"""


# =============================================================================
# CANONICAL ORIENTED NETWORK STATE
# =============================================================================

@dataclass(frozen=True)
class OrientedNetworkState:
    """
    The canonical immutable snapshot of the Oriented Network.
    
    SEMANTIC ROLE:
        - Represents one semantic condition of the network at a point in time
        - Composes references to Content objects (never duplicates)
        - Never owns runtime behavior, scheduling, or execution
        
    COMPOSITION INVARIANTS:
        ON-INV-001: State is deeply immutable
        ON-INV-002: State composes references only (no duplication)
        ON-INV-003: Composition graph remains acyclic
        ON-INV-004: No runtime resources owned
        
    NOT RESPONSIBLE FOR:
        - Runtime execution
        - Scheduling or coordination
        - Planning or reasoning
        - State transitions (produced by external systems)
        
    STATE LAWS:
        ORIENTED-STATE-LAW-001 through 040 apply
    """
    
    # Identity and metadata
    state_id: str = "oriented_network_initial"
    """Unique identifier for this state instance"""
    
    revision: int = 1
    """Current semantic revision number"""
    
    version: int = 1
    """Schema version for compatibility"""
    
    authority: str = "oriented_network"
    """Source of authority"""
    
    owner: str = "oriented_network"
    """Architectural owner"""
    
    # Metadata container
    metadata: StateMetadata = field(default_factory=StateMetadata)
    """Combined state metadata (identity, provenance, lineage)"""
    
    # Orientation content reference
    orientation_state_id: Optional[str] = None
    """ID of current orientation Content"""
    
    # References to external state (Content references, not ownership)
    goal_references: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of referenced Goal Content"""
    
    objective_references: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of referenced Objective Content"""
    
    task_references: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of referenced Task Content"""
    
    mission_references: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of referenced Mission Content"""
    
    # Context content references
    context_state_id: Optional[str] = None
    """ID of current Context Content"""
    
    constraint_state_id: Optional[str] = None
    """ID of current Constraint Content"""
    
    assessment_state_id: Optional[str] = None
    """ID of current Assessment Content"""
    
    relationship_state_id: Optional[str] = None
    """ID of current Relationship Content"""
    
    requirement_state_id: Optional[str] = None
    """ID of current Requirement Content"""
    
    @classmethod
    def initial(cls) -> OrientedNetworkState:
        """
        Return the initial state for a new Oriented Network.
        
        Returns:
            An OrientedNetworkState with default empty values.
        """
        return cls(
            state_id="oriented_network_initial",
            revision=1,
            version=1,
            authority="oriented_network",
            owner="oriented_network",
            metadata=StateMetadata.create(state_id="oriented_network_initial"),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Return a dictionary representation of the state."""
        return {
            "state_id": self.state_id,
            "revision": self.revision,
            "version": self.version,
            "authority": self.authority,
            "owner": self.owner,
            "metadata": self.metadata.to_dict(),
            "orientation_state_id": self.orientation_state_id,
            "goal_references": list(self.goal_references),
            "objective_references": list(self.objective_references),
            "task_references": list(self.task_references),
            "mission_references": list(self.mission_references),
            "context_state_id": self.context_state_id,
            "constraint_state_id": self.constraint_state_id,
            "assessment_state_id": self.assessment_state_id,
            "relationship_state_id": self.relationship_state_id,
            "requirement_state_id": self.requirement_state_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OrientedNetworkState:
        """Create state from a dictionary representation."""
        return cls(
            state_id=data["state_id"],
            revision=data.get("revision", 1),
            version=data.get("version", 1),
            authority=data.get("authority", "oriented_network"),
            owner=data.get("owner", "oriented_network"),
            metadata=StateMetadata.from_dict(data.get("metadata", {})),
            orientation_state_id=data.get("orientation_state_id"),
            goal_references=tuple(data.get("goal_references", [])),
            objective_references=tuple(data.get("objective_references", [])),
            task_references=tuple(data.get("task_references", [])),
            mission_references=tuple(data.get("mission_references", [])),
            context_state_id=data.get("context_state_id"),
            constraint_state_id=data.get("constraint_state_id"),
            assessment_state_id=data.get("assessment_state_id"),
            relationship_state_id=data.get("relationship_state_id"),
            requirement_state_id=data.get("requirement_state_id"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        """
        Validate state structure.
        
        Returns:
            (is_valid, list_of_errors) tuple
        """
        errors = []
        
        if not self.state_id:
            errors.append("state_id is required")
        
        if self.revision < 1:
            errors.append("revision must be >= 1")
        
        if self.version < 1:
            errors.append("version must be >= 1")
        
        return len(errors) == 0, tuple(errors)
    
    def get_provenance(self) -> Dict[str, Any]:
        """Get provenance information."""
        return self.metadata.provenance.to_dict()
    
    def get_lineage(self) -> Tuple[str, ...]:
        """Get lineage (ancestral chain)."""
        lineage = []
        if self.metadata.lineage.root_state_id:
            lineage.append(self.metadata.lineage.root_state_id)
        if self.metadata.lineage.parent_state_id:
            lineage.append(self.metadata.lineage.parent_state_id)
        if self.metadata.lineage.previous_state_id:
            lineage.append(self.metadata.lineage.previous_state_id)
        lineage.extend(self.metadata.lineage.related_state_ids)
        return tuple(lineage)


# =============================================================================
# ORIENTATION STATE
# =============================================================================

@dataclass(frozen=True)
class OrientationState:
    """
    State representing the orientation component of the Oriented Network.
    
    SEMANTIC ROLE:
        - Represents current, desired, and candidate orientations
        - References orientation Content (never owns it directly)
        
    COMPOSITION INVARIANTS:
        OS-INV-001: Immutable representation
        OS-INV-002: References external orientation Content
    """
    
    state_id: str = "orientation_initial"
    """Unique identifier"""
    
    current_orientation_id: Optional[str] = None
    """ID of current Orientation Content"""
    
    desired_orientation_id: Optional[str] = None
    """ID of desired Orientation Content"""
    
    candidate_orientation_id: Optional[str] = None
    """ID of candidate Orientation Content"""
    
    historical_orientation_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of historical orientation references"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "current_orientation_id": self.current_orientation_id,
            "desired_orientation_id": self.desired_orientation_id,
            "candidate_orientation_id": self.candidate_orientation_id,
            "historical_orientation_ids": list(self.historical_orientation_ids),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OrientationState:
        return cls(
            state_id=data["state_id"],
            current_orientation_id=data.get("current_orientation_id"),
            desired_orientation_id=data.get("desired_orientation_id"),
            candidate_orientation_id=data.get("candidate_orientation_id"),
            historical_orientation_ids=tuple(data.get("historical_orientation_ids", [])),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.state_id:
            errors.append("state_id is required")
        return len(errors) == 0, tuple(errors)
    
    @classmethod
    def initial(cls) -> OrientationState:
        return cls(state_id="orientation_initial")


# =============================================================================
# GOAL STATE
# =============================================================================

@dataclass(frozen=True)
class GoalState:
    """
    State representing goal-related references.
    
    SEMANTIC ROLE:
        - References Goals (owned by Goal System, not owned here)
        - Never owns Goal implementations
        
    COMPOSITION INVARIANTS:
        GS-INV-001: Immutable references only
    """
    
    state_id: str = "goal_initial"
    """Unique identifier"""
    
    active_goal_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of active goals (external references)"""
    
    suspended_goal_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of suspended goals"""
    
    completed_goal_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of completed goals"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "active_goal_ids": list(self.active_goal_ids),
            "suspended_goal_ids": list(self.suspended_goal_ids),
            "completed_goal_ids": list(self.completed_goal_ids),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> GoalState:
        return cls(
            state_id=data["state_id"],
            active_goal_ids=tuple(data.get("active_goal_ids", [])),
            suspended_goal_ids=tuple(data.get("suspended_goal_ids", [])),
            completed_goal_ids=tuple(data.get("completed_goal_ids", [])),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.state_id:
            errors.append("state_id is required")
        return len(errors) == 0, tuple(errors)
    
    @classmethod
    def initial(cls) -> GoalState:
        return cls(state_id="goal_initial")


# =============================================================================
# OBJECTIVE STATE
# =============================================================================

@dataclass(frozen=True)
class ObjectiveState:
    """
    State representing objective-related references.
    
    SEMANTIC ROLE:
        - References Objectives (owned by external system)
        
    COMPOSITION INVARIANTS:
        OBS-INV-001: Immutable references only
    """
    
    state_id: str = "objective_initial"
    """Unique identifier"""
    
    active_objective_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of active objectives (external references)"""
    
    suspended_objective_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of suspended objectives"""
    
    completed_objective_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of completed objectives"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "active_objective_ids": list(self.active_objective_ids),
            "suspended_objective_ids": list(self.suspended_objective_ids),
            "completed_objective_ids": list(self.completed_objective_ids),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ObjectiveState:
        return cls(
            state_id=data["state_id"],
            active_objective_ids=tuple(data.get("active_objective_ids", [])),
            suspended_objective_ids=tuple(data.get("suspended_objective_ids", [])),
            completed_objective_ids=tuple(data.get("completed_objective_ids", [])),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.state_id:
            errors.append("state_id is required")
        return len(errors) == 0, tuple(errors)
    
    @classmethod
    def initial(cls) -> ObjectiveState:
        return cls(state_id="objective_initial")


# =============================================================================
# TASK STATE
# =============================================================================

@dataclass(frozen=True)
class TaskState:
    """
    State representing task-related references.
    
    SEMANTIC ROLE:
        - References Tasks (owned by external system)
        
    COMPOSITION INVARIANTS:
        TS-INV-001: Immutable references only
    """
    
    state_id: str = "task_initial"
    """Unique identifier"""
    
    active_task_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of active tasks (external references)"""
    
    suspended_task_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of suspended tasks"""
    
    completed_task_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of completed tasks"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "active_task_ids": list(self.active_task_ids),
            "suspended_task_ids": list(self.suspended_task_ids),
            "completed_task_ids": list(self.completed_task_ids),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TaskState:
        return cls(
            state_id=data["state_id"],
            active_task_ids=tuple(data.get("active_task_ids", [])),
            suspended_task_ids=tuple(data.get("suspended_task_ids", [])),
            completed_task_ids=tuple(data.get("completed_task_ids", [])),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.state_id:
            errors.append("state_id is required")
        return len(errors) == 0, tuple(errors)
    
    @classmethod
    def initial(cls) -> TaskState:
        return cls(state_id="task_initial")


# =============================================================================
# CONTEXT STATE
# =============================================================================

@dataclass(frozen=True)
class ContextState:
    """
    State representing the context component.
    
    SEMANTIC ROLE:
        - References Context Content (semantic surroundings)
        
    COMPOSITION INVARIANTS:
        CS-INV-001: Immutable references only
    """
    
    state_id: str = "context_initial"
    """Unique identifier"""
    
    mission_context_id: Optional[str] = None
    """ID of Mission Context Content"""
    
    goal_context_id: Optional[str] = None
    """ID of Goal Context Content"""
    
    objective_context_id: Optional[str] = None
    """ID of Objective Context Content"""
    
    task_context_id: Optional[str] = None
    """ID of Task Context Content"""
    
    operational_context_id: Optional[str] = None
    """ID of Operational Context Content"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "mission_context_id": self.mission_context_id,
            "goal_context_id": self.goal_context_id,
            "objective_context_id": self.objective_context_id,
            "task_context_id": self.task_context_id,
            "operational_context_id": self.operational_context_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ContextState:
        return cls(
            state_id=data["state_id"],
            mission_context_id=data.get("mission_context_id"),
            goal_context_id=data.get("goal_context_id"),
            objective_context_id=data.get("objective_context_id"),
            task_context_id=data.get("task_context_id"),
            operational_context_id=data.get("operational_context_id"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.state_id:
            errors.append("state_id is required")
        return len(errors) == 0, tuple(errors)
    
    @classmethod
    def initial(cls) -> ContextState:
        return cls(state_id="context_initial")


# =============================================================================
# CONSTRAINT STATE
# =============================================================================

@dataclass(frozen=True)
class ConstraintState:
    """
    State representing constraints.
    
    SEMANTIC ROLE:
        - References Constraint Content (boundary conditions)
        
    COMPOSITION INVARIANTS:
        CrS-INV-001: Immutable references only
    """
    
    state_id: str = "constraint_initial"
    """Unique identifier"""
    
    active_constraint_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of active constraints (external references)"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "active_constraint_ids": list(self.active_constraint_ids),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConstraintState:
        return cls(
            state_id=data["state_id"],
            active_constraint_ids=tuple(data.get("active_constraint_ids", [])),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.state_id:
            errors.append("state_id is required")
        return len(errors) == 0, tuple(errors)
    
    @classmethod
    def initial(cls) -> ConstraintState:
        return cls(state_id="constraint_initial")


# =============================================================================
# ASSESSMENT STATE
# =============================================================================

@dataclass(frozen=True)
class AssessmentState:
    """
    State representing assessment summary.
    
    SEMANTIC ROLE:
        - References Assessment Content (evaluations and observations)
        
    COMPOSITION INVARIANTS:
        AS-INV-001: Immutable references only
    """
    
    state_id: str = "assessment_initial"
    """Unique identifier"""
    
    progress_assessment_id: Optional[str] = None
    """ID of Progress Assessment Content"""
    
    alignment_assessment_id: Optional[str] = None
    """ID of Alignment Assessment Content"""
    
    confidence_assessment_id: Optional[str] = None
    """ID of Confidence Assessment Content"""
    
    risk_assessment_id: Optional[str] = None
    """ID of Risk Assessment Content"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "progress_assessment_id": self.progress_assessment_id,
            "alignment_assessment_id": self.alignment_assessment_id,
            "confidence_assessment_id": self.confidence_assessment_id,
            "risk_assessment_id": self.risk_assessment_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> AssessmentState:
        return cls(
            state_id=data["state_id"],
            progress_assessment_id=data.get("progress_assessment_id"),
            alignment_assessment_id=data.get("alignment_assessment_id"),
            confidence_assessment_id=data.get("confidence_assessment_id"),
            risk_assessment_id=data.get("risk_assessment_id"),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.state_id:
            errors.append("state_id is required")
        return len(errors) == 0, tuple(errors)
    
    @classmethod
    def initial(cls) -> AssessmentState:
        return cls(state_id="assessment_initial")


# =============================================================================
# RELATIONSHIP STATE
# =============================================================================

@dataclass(frozen=True)
class RelationshipState:
    """
    State representing explicit semantic relationships.
    
    SEMANTIC ROLE:
        - References Relationship Content (semantic connections)
        
    COMPOSITION INVARIANTS:
        RS-INV-001: Immutable references only
    """
    
    state_id: str = "relationship_initial"
    """Unique identifier"""
    
    goal_relationship_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Goal Relationship Content"""
    
    objective_relationship_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Objective Relationship Content"""
    
    task_relationship_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Task Relationship Content"""
    
    dependency_relationship_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Dependency Relationship Content"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "goal_relationship_ids": list(self.goal_relationship_ids),
            "objective_relationship_ids": list(self.objective_relationship_ids),
            "task_relationship_ids": list(self.task_relationship_ids),
            "dependency_relationship_ids": list(self.dependency_relationship_ids),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RelationshipState:
        return cls(
            state_id=data["state_id"],
            goal_relationship_ids=tuple(data.get("goal_relationship_ids", [])),
            objective_relationship_ids=tuple(data.get("objective_relationship_ids", [])),
            task_relationship_ids=tuple(data.get("task_relationship_ids", [])),
            dependency_relationship_ids=tuple(data.get("dependency_relationship_ids", [])),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.state_id:
            errors.append("state_id is required")
        return len(errors) == 0, tuple(errors)
    
    @classmethod
    def initial(cls) -> RelationshipState:
        return cls(state_id="relationship_initial")


# =============================================================================
# REQUIREMENT STATE
# =============================================================================

@dataclass(frozen=True)
class RequirementState:
    """
    State representing requirements.
    
    SEMANTIC ROLE:
        - References Requirement Content (semantic necessities)
        
    COMPOSITION INVARIANTS:
        RQ-INV-001: Immutable references only
    """
    
    state_id: str = "requirement_initial"
    """Unique identifier"""
    
    attention_requirement_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Attention Requirement Content"""
    
    workspace_requirement_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Workspace Requirement Content"""
    
    planning_requirement_ids: Tuple[str, ...] = field(default_factory=tuple)
    """IDs of Planning Requirement Content"""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "state_id": self.state_id,
            "attention_requirement_ids": list(self.attention_requirement_ids),
            "workspace_requirement_ids": list(self.workspace_requirement_ids),
            "planning_requirement_ids": list(self.planning_requirement_ids),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RequirementState:
        return cls(
            state_id=data["state_id"],
            attention_requirement_ids=tuple(data.get("attention_requirement_ids", [])),
            workspace_requirement_ids=tuple(data.get("workspace_requirement_ids", [])),
            planning_requirement_ids=tuple(data.get("planning_requirement_ids", [])),
        )
    
    def validate(self) -> Tuple[bool, Tuple[str, ...]]:
        errors = []
        if not self.state_id:
            errors.append("state_id is required")
        return len(errors) == 0, tuple(errors)
    
    @classmethod
    def initial(cls) -> RequirementState:
        return cls(state_id="requirement_initial")


# =============================================================================
# STATE SNAPSHOT TYPES
# =============================================================================

@dataclass(frozen=True)
class CurrentState:
    """
    Represents the current semantic snapshot of a state.
    
    SEMANTIC ROLE:
        - Captures the present condition
        - Never represents runtime execution
        
    COMPOSITION INVARIANTS:
        CSN-INV-001: Immutable representation
    """
    
    state_id: str
    """ID of the current state"""
    
    timestamp: Optional[int] = None
    """Optional logical timestamp (not wall-clock)"""
    
    @classmethod
    def create(cls, state_id: str, timestamp: Optional[int] = None) -> CurrentState:
        return cls(state_id=state_id, timestamp=timestamp)


@dataclass(frozen=True)
class HistoricalState:
    """
    Represents a historical semantic snapshot.
    
    SEMANTIC ROLE:
        - Captures past conditions for reference
        - Never modifies history
        
    COMPOSITION INVARIANTS:
        HS-INV-001: Immutable representation
    """
    
    state_id: str
    """ID of the historical state"""
    
    revision: int = 1
    """Revision at that point in time"""
    
    @classmethod
    def create(cls, state_id: str, revision: int = 1) -> HistoricalState:
        return cls(state_id=state_id, revision=revision)


@dataclass(frozen=True)
class CandidateState:
    """
    Represents a candidate future state.
    
    SEMANTIC ROLE:
        - Captures potential conditions
        - Never guarantees execution
        
    COMPOSITION INVARIANTS:
        CAND-INV-001: Immutable representation
    """
    
    state_id: str
    """ID of the candidate state"""
    
    confidence: float = 0.0
    """Confidence in this state being realized"""
    
    @classmethod
    def create(cls, state_id: str, confidence: float = 0.0) -> CandidateState:
        return cls(state_id=state_id, confidence=confidence)


@dataclass(frozen=True)
class SuspendedState:
    """
    Represents a suspended (paused) semantic snapshot.
    
    SEMANTIC ROLE:
        - Captures paused conditions for later resumption
        - Never executes while suspended
        
    COMPOSITION INVARIANTS:
        SS-INV-001: Immutable representation
    """
    
    state_id: str
    """ID of the suspended state"""
    
    suspended_at_revision: int = 1
    """Revision when suspension occurred"""
    
    @classmethod
    def create(cls, state_id: str, suspended_at_revision: int = 1) -> SuspendedState:
        return cls(state_id=state_id, suspended_at_revision=suspended_at_revision)


@dataclass(frozen=True)
class RecoveredState:
    """
    Represents a recovered semantic snapshot.
    
    SEMANTIC ROLE:
        - Captures restored conditions
        - Never modifies recovery history
        
    COMPOSITION INVARIANTS:
        RS-INV-001: Immutable representation
    """
    
    state_id: str
    """ID of the recovered state"""
    
    from_state_id: Optional[str] = None
    """ID of the state it was recovered from (if any)"""
    
    @classmethod
    def create(cls, state_id: str, from_state_id: Optional[str] = None) -> RecoveredState:
        return cls(state_id=state_id, from_state_id=from_state_id)


@dataclass(frozen=True)
class ReferenceState:
    """
    Represents a reference (canonical) semantic snapshot.
    
    SEMANTIC ROLE:
        - Captures authoritative conditions for comparison
        - Never executes or modifies
        
    COMPOSITION INVARIANTS:
        REF-INV-001: Immutable representation
    """
    
    state_id: str
    """ID of the reference state"""
    
    canonical: bool = True
    """Whether this is the canonical reference"""
    
    @classmethod
    def create(cls, state_id: str, canonical: bool = True) -> ReferenceState:
        return cls(state_id=state_id, canonical=canonical)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "StateType",
    # Canonical hierarchy
    "OrientedNetworkState",
    "OrientationState",
    "GoalState",
    "ObjectiveState",
    "TaskState",
    "ContextState",
    "ConstraintState",
    "AssessmentState",
    "RelationshipState",
    "RequirementState",
    # Snapshot types
    "CurrentState",
    "HistoricalState",
    "CandidateState",
    "SuspendedState",
    "RecoveredState",
    "ReferenceState",
]