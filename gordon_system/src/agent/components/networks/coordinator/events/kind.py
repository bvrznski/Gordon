# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Event Kind Enumeration - Taxonomy of Cognitive Occurrences

This module defines the canonical taxonomy of cognitive event kinds in Gordon.
Each event kind represents a meaningful semantic occurrence in cognition.

EVENT KIND PRINCIPLES
=====================
1. Each event has exactly one canonical Event Kind
2. Event kinds represent semantic cognitive occurrences
3. Event kinds remain implementation-independent
4. Equivalent occurrences map to equivalent Event Kinds
5. Unknown kinds remain explicit

COGNITIVE EVENT KINDS
=====================

Lifecycle Events (Network & System):
- NETWORK_ACTIVATED: A cognitive network becomes active
- NETWORK_DEACTIVATED: A cognitive network becomes inactive
- NETWORK_DEGRADED: A cognitive network operates with reduced capacity
- NETWORK_RECOVERED: A degraded network returns to full capacity

Goal & Task Events:
- GOAL_CREATED: A new goal is established in cognition
- GOAL_UPDATED: Existing goal parameters change
- GOAL_COMPLETED: Goal achievement is recognized
- TASK_CREATED: A task is initiated for goal execution
- TASK_COMPLETED: Task completion is recognized

Planning Events:
- PLAN_STARTED: Planning process begins
- PLAN_REVISED: Plan is modified based on new information
- PLAN_COMPLETED: Planning concludes with final plan selection

Decision Events:
- DECISION_CREATED: A decision option is generated
- DECISION_SELECTED: One option is chosen as the decision
- DECISION_REJECTED: A decision option is discarded
- DECISION_EXECUTED: The selected decision begins execution

Prediction Events:
- PREDICTION_CREATED: A new prediction about future state
- PREDICTION_UPDATED: Prediction parameters or confidence changes
- PREDICTION_CONFIRMED: Prediction matches observed outcome
- PREDICTION_REJECTED: Prediction significantly deviates from observation

Reward Events:
- REWARD_ESTIMATED: Expected reward value is calculated
- REWARD_OBSERVED: Actual reward is experienced
- REWARD_UPDATED: Reward value estimate is revised

Salience & Attention Events:
- SALIENCE_CHANGED: Relative importance of a stimulus changes
- ATTENTION_SHIFTED: Focal attention moves to new target

Workspace Events (Memory Management):
- WORKSPACE_ADMISSION: Information admitted to working memory
- WORKSPACE_EVICTION: Information removed from working memory

Memory Events:
- MEMORY_ENCODED: Experience is stored in long-term memory
- MEMORY_RETRIEVED: Stored information is accessed
- MEMORY_CONSOLIDATED: Memory is strengthened/stabilized

Meta-Cognitive Events:
- REFLECTION_STARTED: Introspective reflection begins
- REFLECTION_COMPLETED: Reflection concludes with insights
- LEARNING_STARTED: Learning process initiates
- LEARNING_COMPLETED: Learning episode concludes
- SYNCHRONIZATION_STARTED: Network synchronization begins
- SYNCHRONIZATION_COMPLETED: Synchronization achieves consensus

Transition Events:
- BARRIER_BLOCKED: A constraint blocks progress
- BARRIER_RELEASED: A constraint no longer applies
- TRANSITION_STARTED: State transition begins
- TRANSITION_COMPLETED: State change finishes

Error/Recovery Events:
- FAILURE_DETECTED: An error or failure condition identified
- FAILURE_RECOVERED: System returns to normal operation after failure
- CONFLICT_DETECTED: Contradictory information or options found
- CONFLICT_RESOLVED: Conflict is resolved through reasoning

Observation Events:
- OBSERVATION_RECORDED: External observation is registered

UNKNOWN: Catch-all for unrecognized event kinds

EVENT KIND CATEGORIES
=====================

1. Lifecycle Events (Network & System):
   - Network activation/deactivation states
   - System component availability transitions

2. Goal & Task Events:
   - Goal lifecycle from creation to completion
   - Task execution tracking

3. Planning Events:
   - Plan generation and revision
   - Alternative evaluation

4. Decision Events:
   - Option generation, selection, rejection
   - Execution commitment

5. Prediction Events:
   - Future state estimation
   - Prediction validation

6. Reward Events:
   - Value estimation
   - Expected vs. actual reward comparison

7. Salience & Attention Events:
   - Relevance assessment
   - Focal attention shifts

8. Workspace Events:
   - Working memory content management
   - Information admission/eviction

9. Memory Events:
   - Encoding, retrieval, consolidation
   - Long-term storage operations

10. Meta-Cognitive Events:
    - Reflection on cognitive process
    - Learning from experience
    - Network synchronization

11. Transition Events:
    - State boundaries
    - Barrier state changes

12. Error/Recovery Events:
    - Problem detection
    - Resolution tracking

13. Observation Events:
    - External input registration

SEMANTIC PROPERTIES
===================
- Event kinds are immutable once defined
- New event kinds may be added but never removed
- Kind identification is deterministic from semantic content
- No runtime information affects kind classification
"""

from enum import Enum, unique


@unique
class CognitiveEventKind(Enum):
    """
    Canonical enumeration of cognitive event kinds.
    
    Every cognitive occurrence maps to exactly one Event Kind.
    The same semantic occurrence always produces the same kind.
    
    EVENT KIND LAWS (KIND-LAW)
    --------------------------
    KIND-LAW-001: Every event possesses exactly one canonical Event Kind
    KIND-LAW-002: Event kinds represent semantic cognitive occurrences
    KIND-LAW-003: Event kinds remain implementation-independent
    KIND-LAW-004: Equivalent occurrences map to equivalent Event Kinds
    KIND-LAW-005: Unknown kinds remain explicit
    KIND-LAW-006: Event kind evolution preserves compatibility
    KIND-LAW-007: Kind ownership remains explicit
    KIND-LAW-008: Classification remains deterministic
    """
    
    # =============================================================================
    # NETWORK LIFECYCLE EVENTS
    # =============================================================================
    
    NETWORK_ACTIVATED = "network_activated"
    """A cognitive network becomes active and available for coordination."""
    
    NETWORK_DEACTIVATED = "network_deactivated"
    """A cognitive network becomes inactive and unavailable."""
    
    NETWORK_DEGRADED = "network_degraded"
    """A cognitive network operates with reduced capacity or degraded performance."""
    
    NETWORK_RECOVERED = "network_recovered"
    """A previously degraded network returns to full operational capacity."""
    
    # =============================================================================
    # GOAL & TASK EVENTS
    # =============================================================================
    
    GOAL_CREATED = "goal_created"
    """A new goal is established in cognition, initiating goal-directed behavior."""
    
    GOAL_UPDATED = "goal_updated"
    """Existing goal parameters, constraints, or priority change."""
    
    GOAL_COMPLETED = "goal_completed"
    """Goal achievement is recognized; goal is satisfied or abandoned."""
    
    TASK_CREATED = "task_created"
    """A task is initiated for execution to advance a goal."""
    
    TASK_COMPLETED = "task_completed"
    """Task completion is recognized and verified."""
    
    # =============================================================================
    # PLANNING EVENTS
    # =============================================================================
    
    PLAN_STARTED = "plan_started"
    """Planning process begins, initiating candidate generation."""
    
    PLAN_REVISED = "plan_revised"
    """Plan is modified based on new information or changed circumstances."""
    
    PLAN_COMPLETED = "plan_completed"
    """Planning concludes with final plan selection and commitment."""
    
    # =============================================================================
    # DECISION EVENTS
    # =============================================================================
    
    DECISION_CREATED = "decision_created"
    """A decision option is generated as a candidate for selection."""
    
    DECISION_SELECTED = "decision_selected"
    """One option is chosen as the definitive decision."""
    
    DECISION_REJECTED = "decision_rejected"
    """A decision option is discarded during evaluation."""
    
    DECISION_EXECUTED = "decision_executed"
    """The selected decision begins execution in action space."""
    
    # =============================================================================
    # PREDICTION EVENTS
    # =============================================================================
    
    PREDICTION_CREATED = "prediction_created"
    """A new prediction about future state or outcome is generated."""
    
    PREDICTION_UPDATED = "prediction_updated"
    """Prediction parameters, confidence, or precision changes."""
    
    PREDICTION_CONFIRMED = "prediction_confirmed"
    """Prediction matches observed outcome within expected tolerance."""
    
    PREDICTION_REJECTED = "prediction_rejected"
    """Prediction significantly deviates from observation (prediction error)."""
    
    # =============================================================================
    # REWARD EVENTS
    # =============================================================================
    
    REWARD_ESTIMATED = "reward_estimated"
    """Expected reward value is calculated based on prediction and policy."""
    
    REWARD_OBSERVED = "reward_observed"
    """Actual reward is experienced as an external outcome."""
    
    REWARD_UPDATED = "reward_updated"
    """Reward value estimate is revised based on new information."""
    
    # =============================================================================
    # SALIENCE & ATTENTION EVENTS
    # =============================================================================
    
    SALIENCE_CHANGED = "salience_changed"
    """Relative importance or relevance of a stimulus changes."""
    
    ATTENTION_SHIFTED = "attention_shifted"
    """Focal attention moves from current target to new target."""
    
    # =============================================================================
    # WORKSPACE (MEMORY MANAGEMENT) EVENTS
    # =============================================================================
    
    WORKSPACE_ADMISSION = "workspace_admission"
    """Information is admitted into working memory for active processing."""
    
    WORKSPACE_EVICTION = "workspace_eviction"
    """Information is removed from working memory to free capacity."""
    
    # =============================================================================
    # MEMORY EVENTS
    # =============================================================================
    
    MEMORY_ENCODED = "memory_encoded"
    """Experience is encoded and stored in long-term memory."""
    
    MEMORY_RETRIEVED = "memory_retrieved"
    """Stored information is accessed and brought into working memory."""
    
    MEMORY_CONSOLIDATED = "memory_consolidated"
    """Memory is strengthened, stabilized, or integrated with existing knowledge."""
    
    # =============================================================================
    # META-COGNITIVE EVENTS
    # =============================================================================
    
    REFLECTION_STARTED = "reflection_started"
    """Introspective reflection begins; cognition examines its own processes."""
    
    REFLECTION_COMPLETED = "reflection_completed"
    """Reflection concludes with insights or learning outcomes."""
    
    LEARNING_STARTED = "learning_started"
    """Learning process initiates to acquire new capabilities or knowledge."""
    
    LEARNING_COMPLETED = "learning_completed"
    """Learning episode concludes with capability acquisition."""
    
    SYNCHRONIZATION_STARTED = "synchronization_started"
    """Network synchronization process begins."""
    
    SYNCHRONIZATION_COMPLETED = "synchronization_completed"
    """Synchronization achieves consensus among participating networks."""
    
    # =============================================================================
    # TRANSITION EVENTS
    # =============================================================================
    
    BARRIER_BLOCKED = "barrier_blocked"
    """A constraint or barrier prevents progress toward a goal."""
    
    BARRIER_RELEASED = "barrier_released"
    """A previously blocking constraint no longer applies."""
    
    TRANSITION_STARTED = "transition_started"
    """State transition begins, moving from one cognitive state to another."""
    
    TRANSITION_COMPLETED = "transition_completed"
    """State change finishes successfully; new stable state established."""
    
    # =============================================================================
    # ERROR / RECOVERY EVENTS
    # =============================================================================
    
    FAILURE_DETECTED = "failure_detected"
    """An error condition or failure is identified in cognition or execution."""
    
    FAILURE_RECOVERED = "failure_recovered"
    """System returns to normal operation after detecting a failure."""
    
    CONFLICT_DETECTED = "conflict_detected"
    """Contradictory information, options, or constraints are found."""
    
    CONFLICT_RESOLVED = "conflict_resolved"
    """Conflict is resolved through reasoning or priority evaluation."""
    
    # =============================================================================
    # OBSERVATION EVENTS
    # =============================================================================
    
    OBSERVATION_RECORDED = "observation_recorded"
    """External observation from environment is registered in cognition."""
    
    # =============================================================================
    # FALLBACK FOR UNRECOGNIZED KINDS
    # =============================================================================
    
    UNKNOWN = "unknown"
    """Fallback for unrecognized or invalid event kinds."""


def get_event_kind_from_name(name: str) -> "CognitiveEventKind":
    """
    Convert a string name to its corresponding CognitiveEventKind.
    
    This function provides deterministic mapping from string identifiers
    to enum values. It is used during deserialization and query operations.
    
    Args:
        name: The string identifier of the event kind
        
    Returns:
        The corresponding CognitiveEventKind enum value
        
    Raises:
        ValueError: If no matching event kind is found
    """
    try:
        return CognitiveEventKind(name)
    except ValueError:
        raise ValueError(
            f"Unknown event kind name: '{name}'. "
            f"Valid kinds: {[kind.value for kind in CognitiveEventKind]}"
        )


def get_event_kind_name(kind: "CognitiveEventKind") -> str:
    """
    Convert a CognitiveEventKind to its string identifier.
    
    This function provides the canonical string representation of an event kind,
    used for serialization and external communication.
    
    Args:
        kind: The CognitiveEventKind enum value
        
    Returns:
        The string identifier of the event kind
    """
    return kind.value


def parse_event_kind_from_string(s: str) -> "CognitiveEventKind":
    """
    Parse an event kind from various string representations.
    
    Accepts both canonical names and common aliases for flexibility.
    This function enables interoperability with external systems that
    may use different naming conventions.
    
    Args:
        s: The string to parse (case-insensitive)
        
    Returns:
        The corresponding CognitiveEventKind enum value
        
    Raises:
        ValueError: If the string cannot be parsed as a valid event kind
    """
    if not isinstance(s, str):
        raise TypeError(f"Expected string, got {type(s).__name__}")
    
    s_lower = s.lower().strip()
    
    # Direct lookup from canonical names
    try:
        return CognitiveEventKind(s_lower.replace("_", " ").title().replace(" ", "_"))
    except ValueError:
        pass
    
    # Try direct value lookup
    for kind in CognitiveEventKind:
        if kind.value == s_lower or kind.name.lower() == s_lower:
            return kind
    
    raise ValueError(
        f"Cannot parse '{s}' as a valid event kind. "
        f"Valid kinds: {[kind.value for kind in CognitiveEventKind]}"
    )