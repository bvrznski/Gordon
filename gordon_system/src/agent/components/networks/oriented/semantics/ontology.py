# Oriented Network Semantic Ontology
# ===================================

"""
Canonical Ontology for the Oriented Network (Phase 4.7.2)

This module defines all primary semantic concepts belonging to the Oriented Network.

ARCHITECTURAL PRINCIPLES:
    - Every concept has exactly one canonical definition
    - Ownership is explicit and immutable for each concept
    - Relationships are typed and explicit
    - Semantic hierarchy is acyclic
    - No implementation-dependent semantics

SEMANTIC LAWS (See laws.py):
    ORIENTED-SEMANTIC-LAW-013: Every semantic concept has exactly one canonical definition
    ORIENTED-SEMANTIC-LAW-014: Every semantic concept has exactly one architectural owner
    ORIENTED-SEMANTIC-LAW-037: Semantic hierarchy shall remain acyclic
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from gordon_system.src.agent.components.networks.oriented.semantics.laws import SemanticLaw


# =============================================================================
# OWNER TYPES
# =============================================================================

class OwnerType(Enum):
    """
    Types of ownership for semantic concepts.
    
    Every concept must have exactly one owner type.
    The Oriented Network only owns orientation semantics.
    All other cognitive artifacts are externally authoritative.
    """
    ORIENTED_NETWORK = "oriented_network"
    """Owned by the Oriented Network (orientation semantics)"""
    
    GOAL_SYSTEM = "goal_system"
    """Owned by Goal System (Goals remain externally authoritative)"""
    
    EXECUTIVE = "executive"
    """Owned by Executive Network"""
    
    PLANNING = "planning"
    """Owned by Planning subsystem"""
    
    DECISION_NETWORK = "decision_network"
    """Owned by Decision Network"""
    
    WORKSPACE = "workspace"
    """Owned by Workspace Network"""
    
    WORKING_MEMORY = "working_memory"
    """Owned by Working Memory subsystem"""
    
    ATTENTION = "attention"
    """Owned by Attention Network"""
    
    STRATEGY = "strategy"
    """Owned by Strategy subsystem"""
    
    COGNITIVE_ARTIFACT = "cognitive_artifact"
    """External cognitive artifact (not owned by any subsystem)"""


# =============================================================================
# OWNERSHIP MODEL
# =============================================================================

@dataclass(frozen=True)
class OwnershipModel:
    """
    Explicit ownership specification for a semantic concept.
    
    This model defines what each concept:
        - Owns (controls directly)
        - References (points to but doesn't control)
        - Consumes (uses from other subsystems)
        - Produces (creates as output)
        - Requests (asks other subsystems for)
        - Observes (monitors without controlling)
        - Coordinates (manages interactions between)
    
    This prevents ownership leakage and maintains architectural boundaries.
    """
    owns: Tuple[str, ...] = field(default_factory=tuple)
    """What this concept directly controls or owns"""
    
    references: Tuple[str, ...] = field(default_factory=tuple)
    """What this concept points to (external authoritative entities)"""
    
    consumes: Tuple[str, ...] = field(default_factory=tuple)
    """What this concept uses from other subsystems"""
    
    produces: Tuple[str, ...] = field(default_factory=tuple)
    """What this concept creates or outputs"""
    
    requests: Tuple[str, ...] = field(default_factory=tuple)
    """What this concept asks other subsystems for"""
    
    observes: Tuple[str, ...] = field(default_factory=tuple)
    """What this concept monitors without controlling"""
    
    coordinates: Tuple[str, ...] = field(default_factory=tuple)
    """What this concept coordinates interactions between"""
    
    never_owns: Tuple[str, ...] = field(default_factory=tuple)
    """What this concept never owns (architectural prohibition)"""
    
    never_implements: Tuple[str, ...] = field(default_factory=tuple)
    """What this concept never implements (deferred to other subsystems)"""


# =============================================================================
# SEMANTIC LIFECYCLE
# =============================================================================

class SemanticLifecycle(Enum):
    """
    Lifecycle states for semantic concepts.
    
    This is the semantic lifecycle, not a runtime state machine.
    It describes when and how concepts become relevant or inactive.
    """
    POTENTIAL = "potential"
    """Concept exists as potential but not yet engaged"""
    
    ACTIVE = "active"
    """Concept is currently part of orientation"""
    
    INACTIVE = "inactive"
    """Concept was active but is no longer oriented toward"""
    
    SUSPENDED = "suspended"
    """Concept temporarily suspended (may be restored)"""
    
    COMPLETED = "completed"
    """Concept has been satisfied or fulfilled"""
    
    FAILED = "failed"
    """Concept could not be satisfied"""


# =============================================================================
# CANONICAL SEMANTIC CONCEPTS
# =============================================================================

# -----------------------------------------------------------------------------
# ORIENTATION ROOT CONCEPTS
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class Orientation:
    """
    Canonical definition of Orientation.
    
    Orientation is the semantic relationship between the cognitive agent and
    the entities currently regarded as intentionally relevant.
    
    KEY PRINCIPLES:
        - Orientation does not imply execution
        - Orientation does not imply planning
        - Orientation does not imply commitment
        - Orientation merely defines what cognition is presently organized around
        
    OWNERSHIP:
        - Owns: orientation semantics, identity, context
        - References: Goals, Objectives, Tasks, Constraints
        - Never owns: runtime execution, planning, decisions
        
    ARCHITECTURAL ROLE:
        Primary semantic foundation of the Oriented Network.
        
    SEMANTIC DIMENSIONS:
        - Goal Orientation: toward active Goals
        - Objective Orientation: toward operational objectives
        - Task Orientation: toward executable Tasks
        - Mission Orientation: toward overarching Missions
        - Context Orientation: surrounding cognitive context
        - Constraint Orientation: awareness of limitations
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-SEMANTIC-LAW-001: Orientation is semantic, not runtime process
        ORIENTED-SEMANTIC-LAW-002: Orientation never implies execution
        ORIENTED-SEMANTIC-LAW-003: Orientation never implies planning
        ORIENTED-SEMANTIC-LAW-006: Orientation possesses stable semantic identity
    """
    name: str = "Orientation"
    canonical_definition: str = (
        "The semantic relationship between the cognitive agent and "
        "the entities currently regarded as intentionally relevant."
    )
    owner_type: OwnerType = OwnerType.ORIENTED_NETWORK
    owner_name: str = "Oriented Network"
    
    # Semantic dimensions
    goal_orientation_enabled: bool = True
    objective_orientation_enabled: bool = True
    task_orientation_enabled: bool = True
    mission_orientation_enabled: bool = True
    context_orientation_enabled: bool = True
    constraint_orientation_enabled: bool = True
    
    lifecycle_semantics: SemanticLifecycle = SemanticLifecycle.ACTIVE


@dataclass(frozen=True)
class Intent:
    """
    Canonical definition of Intent.
    
    Intent is deliberate cognitive commitment to orient toward certain entities.
    
    KEY PRINCIPLES:
        - Intent establishes orientation through deliberate commitment
        - Intent does not guarantee execution
        - Intent may be maintained across reasoning episodes
        
    SEMANTIC RELATIONSHIPS:
        - Intent → Orientation: intent establishes orientation
        - Intent → Goal: intentional goal orientation
        - Intent → Mission: mission-oriented intention
        
    OWNERSHIP:
        - Owns: intentional commitment state
        - References: targeted entities (Goals, Missions)
        - Never owns: runtime execution of intentions
        
    SEMANTIC HIERARCHY:
        Intent ↓ Orientation ↓ Engagement ↓ Continuation
    """
    name: str = "Intent"
    canonical_definition: str = (
        "Intentional orientation established through deliberate cognitive "
        "commitment rather than passive perception."
    )
    owner_type: OwnerType = OwnerType.ORIENTED_NETWORK
    owner_name: str = "Oriented Network"


@dataclass(frozen=True)
class Purpose:
    """
    Canonical definition of Purpose.
    
    Purpose represents the highest-level semantic orientation toward a final aim
    or ultimate cognitive objective.
    
    KEY PRINCIPLES:
        - Purpose is the foundation of all intentional orientation
        - Purpose provides ultimate semantic justification
        - All other concepts ultimately serve purpose
        
    SEMANTIC HIERARCHY (Acyclic):
        Purpose ↓
            Mission ↓
                Goal ↓
                    Objective ↓
                        Task
                        
    OWNERSHIP:
        - Owns: ultimate orientation aim
        - References: all subordinate concepts
        - Never owns: implementation of means to ends
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-SEMANTIC-LAW-017: Purpose exists at higher semantic level than Mission
        ORIENTED-SEMANTIC-LAW-038: Semantic ownership shall never overlap
    """
    name: str = "Purpose"
    canonical_definition: str = (
        "The highest-level semantic orientation toward a final aim or "
        "ultimate cognitive objective that provides ultimate justification."
    )
    owner_type: OwnerType = OwnerType.ORIENTED_NETWORK
    owner_name: str = "Oriented Network"


@dataclass(frozen=True)
class Mission:
    """
    Canonical definition of Mission.
    
    Mission is a major orientation toward achieving a significant cognitive objective
    that contributes to Purpose.
    
    KEY PRINCIPLES:
        - Mission organizes Goals around a common higher-level aim
        - Mission provides semantic cohesion across Goal systems
        - Missions are externally authoritative
        
    SEMANTIC HIERARCHY:
        Purpose ↓
            Mission ↓ (this)
                Goal ↓
                    Objective ↓
                        Task
                        
    OWNERSHIP:
        - Owns: semantic organization of related Goals
        - References: constituent Goals, contributes to Purpose
        - Never owns: Goal implementation or runtime execution
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-SEMANTIC-LAW-018: Mission exists at higher level than Goal
        ORIENTED-SEMANTIC-LAW-023: Goals contribute toward Missions
    """
    name: str = "Mission"
    canonical_definition: str = (
        "A major orientation toward achieving a significant cognitive objective "
        "that contributes to Purpose and organizes related Goals."
    )
    owner_type: OwnerType = OwnerType.GOAL_SYSTEM
    owner_name: str = "Goal System"


@dataclass(frozen=True)
class Goal:
    """
    Canonical definition of Goal.
    
    Goal is an actively oriented cognitive target that requires specific cognitive work
    to achieve. Goals remain externally authoritative and externally owned.
    
    KEY PRINCIPLES:
        - Goal represents intentional orientation toward a target state
        - Goal may be active, suspended, completed, or failed
        - Orientation may reference Goals without owning them
        
    SEMANTIC HIERARCHY:
        Purpose ↓
            Mission ↓
                Goal ↓ (this)
                    Objective ↓
                        Task
                        
    OWNERSHIP:
        - Owns: none (externally owned)
        - References: Objectives, Tasks that contribute to goal achievement
        - Never owns: implementation of strategies to achieve goal
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-SEMANTIC-LAW-007: Goals remain externally authoritative
        ORIENTED-SEMANTIC-LAW-019: Goals organize Objectives
        ORIENTED-SEMANTIC-LAW-023: Goals contribute toward Missions
    """
    name: str = "Goal"
    canonical_definition: str = (
        "An actively oriented cognitive target that requires specific cognitive work "
        "to achieve. Remains externally authoritative and externally owned."
    )
    owner_type: OwnerType = OwnerType.GOAL_SYSTEM
    owner_name: str = "Goal System"


@dataclass(frozen=True)
class Objective:
    """
    Canonical definition of Objective.
    
    Objective is an intermediate cognitive target that contributes to Goal achievement.
    Objectives remain externally authoritative and are decomposed from Goals.
    
    KEY PRINCIPLES:
        - Objective represents a step toward achieving a Goal
        - Objectives are organized by their parent Goal
        - Objectives may be decomposed into Tasks
        
    SEMANTIC HIERARCHY:
        Purpose ↓
            Mission ↓
                Goal ↓
                    Objective ↓ (this)
                        Task
                        
    OWNERSHIP:
        - Owns: none (externally owned)
        - References: parent Goal, constituent Tasks
        - Never owns: runtime execution of tasks
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-SEMANTIC-LAW-008: Objectives remain externally authoritative
        ORIENTED-SEMANTIC-LAW-020: Objectives organize Tasks
        ORIENTED-SEMANTIC-LAW-024: Objectives contribute toward Goals
    """
    name: str = "Objective"
    canonical_definition: str = (
        "An intermediate cognitive target that contributes to Goal achievement. "
        "Remains externally authoritative and is decomposed from Goals."
    )
    owner_type: OwnerType = OwnerType.GOAL_SYSTEM
    owner_name: str = "Goal System"


@dataclass(frozen=True)
class Task:
    """
    Canonical definition of Task.
    
    Task is an executable cognitive unit derived from Objectives. Tasks remain
    externally owned and are the basis for runtime execution.
    
    KEY PRINCIPLES:
        - Task represents orientation toward an executable cognitive action
        - Tasks are derived from Objectives
        - Tasks may be scheduled, executed, and completed
        
    SEMANTIC HIERARCHY:
        Purpose ↓
            Mission ↓
                Goal ↓
                    Objective ↓
                        Task ↓ (this)
                        
    OWNERSHIP:
        - Owns: none (externally owned)
        - References: parent Objective, required Constraints
        - Never owns: runtime execution
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-SEMANTIC-LAW-009: Tasks remain externally authoritative
        ORIENTED-SEMANTIC-LAW-021: Tasks contribute toward Objectives
    """
    name: str = "Task"
    canonical_definition: str = (
        "An executable cognitive unit derived from Objectives. "
        "Remains externally owned and is the basis for runtime execution."
    )
    owner_type: OwnerType = OwnerType.GOAL_SYSTEM
    owner_name: str = "Goal System"


@dataclass(frozen=True)
class Constraint:
    """
    Canonical definition of Constraint.
    
    Constraint represents a limitation or condition that affects current orientation.
    Constraints remain externally authoritative and influence orientation semantics.
    
    KEY PRINCIPLES:
        - Constraint affects what cognition can achieve
        - Constraints may limit available options
        - Orientation adapts to constraints without owning them
        
    SEMANTIC RELATIONSHIPS:
        - Constraint → Orientation: influences current orientation
        - Constraint → Objective: constrains achievable objectives
        - Constraint → Task: constrains executable tasks
        
    OWNERSHIP:
        - Owns: none (externally authoritative)
        - References: context, affected orientation targets
        - Never owns: runtime execution or constraint enforcement
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-SEMANTIC-LAW-026: Constraints influence Orientation
    """
    name: str = "Constraint"
    canonical_definition: str = (
        "A limitation or condition that affects current orientation. "
        "Remains externally authoritative and influences orientation semantics."
    )
    owner_type: OwnerType = OwnerType.COGNITIVE_ARTIFACT
    owner_name: str = "External Context"


@dataclass(frozen=True)
class Dependency:
    """
    Canonical definition of Dependency.
    
    Dependency represents a semantic relationship where one concept requires
    another concept to achieve its purpose.
    
    KEY PRINCIPLES:
        - Dependency is a semantic requirement, not a runtime dependency
        - Dependencies may be satisfied or unsatisfied
        - Orientation considers dependencies without owning them
        
    SEMANTIC RELATIONSHIPS:
        - Dependency → Target: requires target for completion
        - Dependency → Task: task depends on another task/objective
        - Dependency → Constraint: constraint affects dependencies
        
    OWNERSHIP:
        - Owns: none (semantic relationship)
        - References: dependent concept, required dependency
        - Never owns: implementation of dependency resolution
        
    SEMANTIC HIERARCHY:
        Dependency is a relationship type, not part of the main hierarchy
    """
    name: str = "Dependency"
    canonical_definition: str = (
        "A semantic relationship where one concept requires another to achieve "
        "its purpose. Represents requirement without runtime implementation."
    )
    owner_type: OwnerType = OwnerType.COGNITIVE_ARTIFACT
    owner_name: str = "Semantic Model"


@dataclass(frozen=True)
class Requirement:
    """
    Canonical definition of Requirement.
    
    Requirement is a condition or capability that must be satisfied for orientation
    to proceed successfully.
    
    KEY PRINCIPIVES:
        - Requirement represents necessary conditions for orientation
        - Requirements may be explicit or implicit
        - Orientation validates requirements without owning them
        
    SEMANTIC RELATIONSHIPS:
        - Requirement → Constraint: constraint may satisfy requirement
        - Requirement → Objective: objective requires certain capabilities
        - Requirement → Task: task has specific requirements
        
    OWNERSHIP:
        - Owns: none (external condition)
        - References: satisfied constraints, affected orientation
        - Never owns: implementation of requirements
        
    SEMANTIC HIERARCHY:
        Requirement is a relationship type, not part of the main hierarchy
    """
    name: str = "Requirement"
    canonical_definition: str = (
        "A condition or capability that must be satisfied for orientation "
        "to proceed successfully."
    )
    owner_type: OwnerType = OwnerType.COGNITIVE_ARTIFACT
    owner_name: str = "External Context"


@dataclass(frozen=True)
class Expectation:
    """
    Canonical definition of Expectation.
    
    Expectation represents the anticipated outcome or state that orientation targets.
    
    KEY PRINCIPLES:
        - Expectation is semantic anticipation, not probabilistic prediction
        - Expectations guide orientation toward desired outcomes
        - Orientation maintains expectations without owning them
        
    SEMANTIC RELATIONSHIPS:
        - Expectation → Goal: goal implies specific expectation
        - Expectation → Task: task has expected outcome
        - Expectation → Progress: progress measured against expectation
        
    OWNERSHIP:
        - Owns: none (semantic anticipation)
        - References: targeted outcomes, orientation targets
        - Never owns: prediction or estimation mechanisms
        
    SEMANTIC HIERARCHY:
        Expectation is a relationship type
    """
    name: str = "Expectation"
    canonical_definition: str = (
        "The anticipated outcome or state that orientation targets. "
        "Semantic anticipation, not probabilistic prediction."
    )
    owner_type: OwnerType = OwnerType.COGNITIVE_ARTIFACT
    owner_name: str = "Semantic Model"


@dataclass(frozen=True)
class Commitment:
    """
    Canonical definition of Commitment.
    
    Commitment represents a semantic strengthening of orientation toward a target.
    Once committed, orientation persists unless explicitly disengaged.
    
    KEY PRINCIPLES:
        - Commitment is semantic, not runtime execution
        - Commitment enables persistence across reasoning episodes
        - Orientation may be committed or uncommitted
        
    SEMANTIC RELATIONSHIPS:
        - Commitment → Goal: strengthens orientation toward goal
        - Commitment → Objective: reinforces objective orientation
        - Commitment → Continuation: enables persistence
        
    OWNERSHIP:
        - Owns: commitment state (semantic)
        - References: committed targets, disengagement triggers
        - Never owns: execution or runtime persistence
        
    SEMANTIC HIERARCHY:
        Commitment is a relationship modifier type
    """
    name: str = "Commitment"
    canonical_definition: str = (
        "A semantic strengthening of orientation toward a target. "
        "Enables persistence across reasoning episodes without runtime execution."
    )
    owner_type: OwnerType = OwnerType.ORIENTED_NETWORK
    owner_name: str = "Oriented Network"


@dataclass(frozen=True)
class Continuation:
    """
    Canonical definition of Continuation.
    
    Continuation represents the maintenance of orientation across multiple reasoning
    episodes or decision boundaries.
    
    KEY PRINCIPLES:
        - Continuation preserves semantic identity over time
        - Continuation enables sustained orientation
        - Orientation may continue, be interrupted, or restored
        
    SEMANTIC RELATIONSHIPS:
        - Continuation → Commitment: commitment enables continuation
        - Continuation → Suspension: suspension preserves for restoration
        - Continuation → Restoration: restoration continues suspended orientation
        
    OWNERSHIP:
        - Owns: continuation state (semantic)
        - References: continuing targets, interruption points
        - Never owns: runtime persistence mechanisms
        
    SEMANTIC HIERARCHY:
        Continuation is a lifecycle modifier type
    """
    name: str = "Continuation"
    canonical_definition: str = (
        "The maintenance of orientation across multiple reasoning episodes "
        "or decision boundaries. Preserves semantic identity over time."
    )
    owner_type: OwnerType = OwnerType.ORIENTED_NETWORK
    owner_name: str = "Oriented Network"


@dataclass(frozen=True)
class Interruption:
    """
    Canonical definition of Interruption.
    
    Interruption represents the temporary cessation of active orientation toward a target,
    without termination or completion. Interruption may be followed by restoration.
    
    KEY PRINCIPLES:
        - Interruption does not necessarily terminate orientation
        - Interruption preserves semantic identity for potential restoration
        - Orientation may be resumed after interruption
        
    SEMANTIC RELATIONSHIPS:
        - Interruption → Continuation: interrupting continuation creates suspension
        - Interruption → Restoration: restoration follows interruption
        - Interruption → Suspension: interruption creates suspended state
        
    OWNERSHIP:
        - Owns: interruption state (semantic)
        - References: interrupted targets, restoration capability
        - Never owns: runtime interruption mechanisms
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-SEMANTIC-LAW-034: Interruption does not necessarily terminate Orientation
        ORIENTED-SEMANTIC-LAW-036: Replacement preserves semantic lineage
    """
    name: str = "Interruption"
    canonical_definition: str = (
        "The temporary cessation of active orientation toward a target, "
        "without termination. May be followed by restoration."
    )
    owner_type: OwnerType = OwnerType.ORIENTED_NETWORK
    owner_name: str = "Oriented Network"


@dataclass(frozen=True)
class Suspension:
    """
    Canonical definition of Suspension.
    
    Suspension represents the preservation of semantic identity during interruption,
    enabling potential future restoration. Suspension is an intermediate state
    between active orientation and terminated or restored orientation.
    
    KEY PRINCIPLES:
        - Suspension preserves semantic identity
        - Suspension enables restoration of previous orientation
        - Suspension is not termination
        
    SEMANTIC RELATIONSHIPS:
        - Suspension → Interruption: interruption creates suspension
        - Suspension → Restoration: suspension enables restoration
        - Suspension → Continuation: restored continuation continues from suspension
        
    OWNERSHIP:
        - Owns: suspended state (semantic)
        - References: suspended targets, restoration context
        - Never owns: runtime suspension mechanisms
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-SEMANTIC-LAW-035: Suspension preserves semantic identity
        ORIENTED-SEMANTIC-LAW-036: Replacement preserves semantic lineage
    """
    name: str = "Suspension"
    canonical_definition: str = (
        "The preservation of semantic identity during interruption, "
        "enabling potential future restoration."
    )
    owner_type: OwnerType = OwnerType.ORIENTED_NETWORK
    owner_name: str = "Oriented Network"


@dataclass(frozen=True)
class Restoration:
    """
    Canonical definition of Restoration.
    
    Restoration represents the resumption of orientation toward a previously
    interrupted or suspended target. Restoration may continue from where
    orientation was suspended.
    
    KEY PRINCIPLES:
        - Restoration continues from interruption state
        - Restoration preserves semantic continuity
        - Orientation may be fully restored or partially resumed
        
    SEMANTIC RELATIONSHIPS:
        - Restoration → Suspension: restoration follows suspension
        - Restoration → Continuation: restoration enables continuation
        - Restoration → Interruption: restoration responds to interruption
        
    OWNERSHIP:
        - Owns: restoration state (semantic)
        - References: restored targets, context for continuation
        - Never owns: runtime restoration mechanisms
        
    SEMANTIC HIERARCHY:
        Restoration is a lifecycle modifier type
    """
    name: str = "Restoration"
    canonical_definition: str = (
        "The resumption of orientation toward a previously interrupted or "
        "suspended target. May continue from where orientation was suspended."
    )
    owner_type: OwnerType = OwnerType.ORIENTED_NETWORK
    owner_name: str = "Oriented Network"


@dataclass(frozen=True)
class Context:
    """
    Canonical definition of Context.
    
    Context represents the surrounding cognitive environment that shapes current
    orientation. Context influences but does not determine orientation semantics.
    
    KEY PRINCIPLES:
        - Context surrounds and influences orientation
        - Context is external to orientation itself
        - Orientation adapts to context without being owned by it
        
    SEMANTIC RELATIONSHIPS:
        - Context → Orientation: influences current orientation
        - Context → Goal: context may affect goal relevance
        - Context → Constraint: context provides constraints
        
    OWNERSHIP:
        - Owns: none (external environment)
        - References: influencing factors, affected orientation
        - Never owns: semantic orientation
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-SEMANTIC-LAW-025: Context influences Orientation
        INV-026: Context never owns Orientation
    """
    name: str = "Context"
    canonical_definition: str = (
        "The surrounding cognitive environment that shapes current orientation. "
        "Influences but does not determine orientation semantics."
    )
    owner_type: OwnerType = OwnerType.COGNITIVE_ARTIFACT
    owner_name: str = "External Environment"


@dataclass(frozen=True)
class Scope:
    """
    Canonical definition of Scope.
    
    Scope represents the boundaries of current orientation - what is included and
    what is excluded from intentional focus.
    
    KEY PRINCIPLES:
        - Scope defines inclusiveness and exclusiveness of orientation
        - Scope may be broad or narrow, deep or shallow
        - Scope is semantic, not runtime boundary
        
    SEMANTIC RELATIONSHIPS:
        - Scope → Orientation: defines the boundaries of orientation
        - Scope → Goal: scope determines which goals are included
        - Scope → Context: scope is constrained by context
        
    OWNERSHIP:
        - Owns: none (semantic boundary)
        - References: included targets, excluded items
        - Never owns: runtime boundary enforcement
        
    SEMANTIC HIERARCHY:
        Scope is a boundary type
    """
    name: str = "Scope"
    canonical_definition: str = (
        "The boundaries of current orientation - what is included and "
        "what is excluded from intentional focus."
    )
    owner_type: OwnerType = OwnerType.COGNITIVE_ARTIFACT
    owner_name: str = "Semantic Model"


@dataclass(frozen=True)
class Horizon:
    """
    Canonical definition of Horizon.
    
    Horizon represents the temporal and conceptual reach of current orientation -
    how far ahead and how broadly orientation considers possibilities and outcomes.
    
    KEY PRINCIPLES:
        - Horizon defines the temporal extent of orientation
        - Horizon may be short-term or long-term
        - Horizon shapes strategic versus tactical orientation
        
    SEMANTIC RELATIONSHIPS:
        - Horizon → Orientation: determines temporal extent of focus
        - Horizon → Goal: horizon affects goal selection and planning
        - Horizon → Progress: horizon defines what counts as progress
        
    OWNERSHIP:
        - Owns: none (temporal boundary)
        - References: future possibilities, past context
        - Never owns: runtime temporal mechanisms
        
    SEMANTIC HIERARCHY:
        Horizon is a temporal boundary type
    """
    name: str = "Horizon"
    canonical_definition: str = (
        "The temporal and conceptual reach of current orientation. "
        "Determines how far ahead orientation considers possibilities."
    )
    owner_type: OwnerType = OwnerType.COGNITIVE_ARTIFACT
    owner_name: str = "Semantic Model"


@dataclass(frozen=True)
class Priority:
    """
    Canonical definition of Priority.
    
    Priority represents the relative importance or urgency of one orientation
    target compared to others. Priority affects which orientations receive
    cognitive resources first.
    
    KEY PRINCIPLES:
        - Priority is relative ordering of importance
        - Priority may be absolute or comparative
        - Priority influences resource allocation requests
        
    SEMANTIC RELATIONSHIPS:
        - Priority → Goal: determines goal selection order
        - Priority → Objective: affects which objectives are pursued first
        - Priority → Task: influences task execution order
        
    OWNERSHIP:
        - Owns: none (ordering relationship)
        - References: ordered orientation targets, comparison basis
        - Never owns: runtime scheduling based on priority
        
    SEMANTIC HIERARCHY:
        Priority is an ordering type
    """
    name: str = "Priority"
    canonical_definition: str = (
        "The relative importance or urgency of one orientation target "
        "compared to others. Affects cognitive resource allocation."
    )
    owner_type: OwnerType = OwnerType.COGNITIVE_ARTIFACT
    owner_name: str = "Semantic Model"


@dataclass(frozen=True)
class Progress:
    """
    Canonical definition of Progress.
    
    Progress represents semantic advancement toward orientation targets.
    Progress is not execution percentage but semantic movement toward completion.
    
    KEY PRINCIPLES:
        - Progress measures semantic advancement, not runtime progress
        - Progress may be qualitative or quantitative
        - Progress guides continued orientation
        
    SEMANTIC RELATIONSHIPS:
        - Progress → Goal: advancement toward goal achievement
        - Progress → Objective: movement toward objective completion
        - Progress → Task: advancement in task execution state
        
    OWNERSHIP:
        - Owns: none (measurement relationship)
        - References: current state, target state, gap analysis
        - Never owns: runtime progress tracking mechanisms
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-SEMANTIC-LAW-030: Progress represents semantic advancement,
            not execution percentage
    """
    name: str = "Progress"
    canonical_definition: str = (
        "Semantic advancement toward orientation targets. "
        "Not execution percentage but semantic movement toward completion."
    )
    owner_type: OwnerType = OwnerType.COGNITIVE_ARTIFACT
    owner_name: str = "Semantic Model"


@dataclass(frozen=True)
class Completion:
    """
    Canonical definition of Completion.
    
    Completion represents semantic satisfaction of an orientation target.
    When a target is completed, orientation may shift to new targets or terminate.
    
    KEY PRINCIPLES:
        - Completion is semantic satisfaction, not runtime termination
        - Completed orientation may trigger new orientation
        - Completion enables continuation toward other targets
        
    SEMANTIC RELATIONSHIPS:
        - Completion → Goal: goal achievement
        - Completion → Objective: objective fulfillment
        - Completion → Task: task completion state
        
    OWNERSHIP:
        - Owns: none (state relationship)
        - References: satisfied target, next orientation targets
        - Never owns: runtime termination mechanisms
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-SEMANTIC-LAW-031: Completion represents semantic satisfaction
    """
    name: str = "Completion"
    canonical_definition: str = (
        "Semantic satisfaction of an orientation target. "
        "Not runtime termination but semantic fulfillment."
    )
    owner_type: OwnerType = OwnerType.COGNITIVE_ARTIFACT
    owner_name: str = "Semantic Model"


@dataclass(frozen=True)
class Alignment:
    """
    Canonical definition of Alignment.
    
    Alignment represents the semantic consistency between orientation targets
    and other cognitive elements. Alignment evaluates whether targets are
    mutually supportive or conflicting.
    
    KEY PRINCIPLES:
        - Alignment evaluates semantic consistency, not runtime coordination
        - Alignment may be positive (supportive) or negative (conflicting)
        - Orientation requires alignment for coherence
        
    SEMANTIC RELATIONSHIPS:
        - Alignment → Goal: mutual support with other goals
        - Alignment → Objective: consistency with related objectives
        - Alignment → Constraint: compatibility with existing constraints
        
    OWNERSHIP:
        - Owns: none (evaluation relationship)
        - References: evaluated targets, alignment basis
        - Never owns: runtime coordination mechanisms
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-SEMANTIC-LAW-028: Alignment evaluates semantic consistency
    """
    name: str = "Alignment"
    canonical_definition: str = (
        "Semantic consistency between orientation targets and other cognitive elements. "
        "Evaluates whether targets are mutually supportive or conflicting."
    )
    owner_type: OwnerType = OwnerType.COGNITIVE_ARTIFACT
    owner_name: str = "Semantic Model"


@dataclass(frozen=True)
class Confidence:
    """
    Canonical definition of Confidence.
    
    Confidence represents semantic belief in the achievement of orientation targets.
    Confidence is not probabilistic inference but semantic conviction based on
    available information and constraints.
    
    KEY PRINCIPLES:
        - Confidence is semantic belief, not probabilistic inference
        - Confidence may be high or low based on available evidence
        - Confidence influences continuation versus interruption
        
    SEMANTIC RELATIONSHIPS:
        - Confidence → Goal: belief in goal achievement
        - Confidence → Objective: conviction about objective fulfillment
        - Confidence → Task: certainty about task success
        
    OWNERSHIP:
        - Owns: none (semantic evaluation)
        - References: evidence, constraints, target properties
        - Never owns: probabilistic inference mechanisms
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-SEMANTIC-LAW-030: Confidence expresses semantic belief,
            not probabilistic inference
    """
    name: str = "Confidence"
    canonical_definition: str = (
        "Semantic belief in the achievement of orientation targets. "
        "Not probabilistic inference but semantic conviction based on information."
    )
    owner_type: OwnerType = OwnerType.COGNITIVE_ARTIFACT
    owner_name: str = "Semantic Model"


@dataclass(frozen=True)
class Risk:
    """
    Canonical definition of Risk.
    
    Risk represents the potential for orientation failure or incomplete achievement.
    Risk assesses what may prevent successful orientation toward targets.
    
    KEY PRINCIPLES:
        - Risk assesses potential failures
        - Risk may be mitigated through constraint awareness
        - Risk influences orientation strength and continuation
        
    SEMANTIC RELATIONSHIPS:
        - Risk → Goal: threat to goal achievement
        - Risk → Objective: obstacle to objective completion
        - Risk → Constraint: constraints may increase or decrease risk
        
    OWNERSHIP:
        - Owns: none (assessment relationship)
        - References: potential failure modes, constraint context
        - Never owns: risk mitigation implementation
        
    SEMANTIC HIERARCHY:
        Risk is an assessment type
    """
    name: str = "Risk"
    canonical_definition: str = (
        "The potential for orientation failure or incomplete achievement. "
        "Assesses what may prevent successful orientation toward targets."
    )
    owner_type: OwnerType = OwnerType.COGNITIVE_ARTIFACT
    owner_name: str = "Semantic Model"


@dataclass(frozen=True)
class Recovery:
    """
    Canonical definition of Recovery.
    
    Recovery represents the restoration of semantic continuity after interruption,
    failure, or other disruption. Recovery preserves orientation identity where possible.
    
    KEY PRINCIPLES:
        - Recovery preserves semantic continuity
        - Recovery may be partial or full
        - Recovery enables continuation after disruption
        
    SEMANTIC RELATIONSHURES:
        - Recovery → Interruption: recovery follows interruption
        - Recovery → Failure: recovery from failed orientation
        - Recovery → Restoration: recovery enables restoration
        
    OWNERSHIP:
        - Owns: none (restoration relationship)
        - References: disrupted state, recovery path, continuation
        - Never owns: runtime recovery mechanisms
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-SEMANTIC-LAW-033: Recovery preserves semantic continuity whenever possible
    """
    name: str = "Recovery"
    canonical_definition: str = (
        "The restoration of semantic continuity after interruption or failure. "
        "Preserves orientation identity where possible."
    )
    owner_type: OwnerType = OwnerType.COGNITIVE_ARTIFACT
    owner_name: str = "Semantic Model"


@dataclass(frozen=True)
class Failure:
    """
    Canonical definition of Failure.
    
    Failure represents semantic inability to satisfy orientation toward a target.
    Failure is not runtime error but semantic termination when achievement is impossible.
    
    KEY PRINCIPLES:
        - Failure represents semantic inability, not runtime error
        - Failure may be partial or complete
        - Failure triggers recovery or new orientation
        
    SEMANTIC RELATIONSHIPS:
        - Failure → Goal: goal cannot be achieved
        - Failure → Objective: objective cannot be fulfilled
        - Failure → Recovery: failure may trigger recovery attempts
        
    OWNERSHIP:
        - Owns: none (state relationship)
        - References: failed target, failure reason, recovery options
        - Never owns: runtime error handling mechanisms
        
    SEMANTIC LAW COMPLIANCE:
        ORIENTED-SEMANTIC-LAW-032: Failure represents semantic inability to satisfy Orientation
    """
    name: str = "Failure"
    canonical_definition: str = (
        "Semantic inability to satisfy orientation toward a target. "
        "Not runtime error but semantic termination when achievement is impossible."
    )
    owner_type: OwnerType = OwnerType.COGNITIVE_ARTIFACT
    owner_name: str = "Semantic Model"


# =============================================================================
# CANONICAL ONTOLOGY COLLECTION
# =============================================================================

@dataclass(frozen=True)
class CanonicalOntology:
    """
    The complete canonical ontology of the Oriented Network.
    
    This collection contains all primary semantic concepts and their relationships.
    Every concept follows the architectural principles established in Phase 4.7.2.
    
    ARCHITECTURAL LAWS:
        - ORIENTED-SEMANTIC-LAW-001 through ORIENTED-SEMANTIC-LAW-040
        - INV-001 through INV-030 (Semantic Invariants)
        
    ONTOLOGY STRUCTURE:
        Orientation Root Concepts:
            - Orientation, Intent
            
        Semantic Hierarchy:
            - Purpose → Mission → Goal → Objective → Task
            
        State and Lifecycle:
            - Commitment, Continuation, Interruption, Suspension, Restoration
            
        Boundary and Context:
            - Context, Scope, Horizon
            
        Evaluation and Relationship:
            - Priority, Progress, Completion, Alignment, Confidence, Risk
            - Recovery, Failure
            
        Requirement and Constraint:
            - Constraint, Dependency, Requirement, Expectation
            
    SEMANTIC OWNERSHIP:
        All concepts have explicit ownership (OwnerType enum).
        The Oriented Network only owns orientation semantics.
        All other concepts remain externally authoritative.
    """
    
    # Orientation Root Concepts
    ORIENTATION: Orientation = field(default_factory=Orientation)
    INTENT: Intent = field(default_factory=Intent)
    
    # Semantic Hierarchy - Top to Bottom
    PURPOSE: Purpose = field(default_factory=Purpose)
    MISSION: Mission = field(default_factory=Mission)
    GOAL: Goal = field(default_factory=Goal)
    OBJECTIVE: Objective = field(default_factory=Objective)
    TASK: Task = field(default_factory=Task)
    
    # State and Lifecycle
    COMMITMENT: Commitment = field(default_factory=Commitment)
    CONTINUATION: Continuation = field(default_factory=Continuation)
    INTERRUPTION: Interruption = field(default_factory=Interruption)
    SUSPENSION: Suspension = field(default_factory=Suspension)
    RESTORATION: Restoration = field(default_factory=Restoration)
    
    # Boundary and Context
    CONTEXT: Context = field(default_factory=Context)
    SCOPE: Scope = field(default_factory=Scope)
    HORIZON: Horizon = field(default_factory=Horizon)
    
    # Evaluation and Relationship
    PRIORITY: Priority = field(default_factory=Priority)
    PROGRESS: Progress = field(default_factory=Progress)
    COMPLETION: Completion = field(default_factory=Completion)
    ALIGNMENT: Alignment = field(default_factory=Alignment)
    CONFIDENCE: Confidence = field(default_factory=Confidence)
    RISK: Risk = field(default_factory=Risk)
    RECOVERY: Recovery = field(default_factory=Recovery)
    FAILURE: Failure = field(default_factory=Failure)
    
    # Requirement and Constraint
    CONSTRAINT: Constraint = field(default_factory=Constraint)
    DEPENDENCY: Dependency = field(default_factory=Dependency)
    REQUIREMENT: Requirement = field(default_factory=Requirement)
    EXPECTATION: Expectation = field(default_factory=Expectation)
    
    @property
    def all_concepts(self) -> list:
        """Return all canonical concepts."""
        return [
            self.ORIENTATION,
            self.INTENT,
            self.PURPOSE,
            self.MISSION,
            self.GOAL,
            self.OBJECTIVE,
            self.TASK,
            self.COMMITMENT,
            self.CONTINUATION,
            self.INTERRUPTION,
            self.SUSPENSION,
            self.RESTORATION,
            self.CONTEXT,
            self.SCOPE,
            self.HORIZON,
            self.PRIORITY,
            self.PROGRESS,
            self.COMPLETION,
            self.ALIGNMENT,
            self.CONFIDENCE,
            self.RISK,
            self.RECOVERY,
            self.FAILURE,
            self.CONSTRAINT,
            self.DEPENDENCY,
            self.REQUIREMENT,
            self.EXPECTATION,
        ]
    
    def get_concept_by_name(self, name: str) -> Optional:
        """Get a concept by its canonical name."""
        for concept in self.all_concepts:
            if concept.name == name:
                return concept
        return None


# Singleton instance of the canonical ontology
CANONICAL_ONTOLOGY = CanonicalOntology()

__all__ = [
    # Owner types
    "OwnerType",
    
    # Ownership model
    "OwnershipModel",
    
    # Lifecycle states
    "SemanticLifecycle",
    
    # All canonical concepts
    "Orientation",
    "Intent",
    "Purpose",
    "Mission",
    "Goal",
    "Objective",
    "Task",
    "Constraint",
    "Dependency",
    "Requirement",
    "Expectation",
    "Commitment",
    "Continuation",
    "Interruption",
    "Suspension",
    "Restoration",
    "Context",
    "Scope",
    "Horizon",
    "Priority",
    "Progress",
    "Completion",
    "Alignment",
    "Confidence",
    "Risk",
    "Recovery",
    "Failure",
    
    # Ontology collection
    "CanonicalOntology",
    "CANONICAL_ONTOLOGY",
]