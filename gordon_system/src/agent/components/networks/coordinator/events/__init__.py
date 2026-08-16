# Gordon Cognitive Architecture - Phase 4.11.6
# ===========================================

"""
Cognitive Event Model (CEM) - Semantic History of Cognition

This module defines the canonical semantic architecture for representing,
tracking, and querying cognitive events in Gordon.

COGNITIVE EVENT MODEL OVERVIEW
==============================

The Cognitive Event Model serves as Gordon's semantic history system.
It records **what cognition did**, independently of:

* Implementation language;
* Execution engine;
* Transport protocol;
* Runtime scheduler;

Unlike logging systems that record implementation activity, the CEM records
**meaningful changes in cognition**.

COGNITIVE EVENT MODEL OWNERSHIP
===============================

The Event Model owns:

* event identity;
* event revisions;
* event taxonomy;
* event kinds;
* event streams;
* event timelines;
* event aggregation;
* event episodes;
* event intervals;
* event causation;
* event correlation;
* event lineage;
* event indexes;
* event replay;
* event querying;
* event validation;
* event serialization;
* event findings;
* event limitations;
* event provenance.

It does NOT own:

* runtime execution;
* scheduler state;
* transport;
* logging;
* debugging;
* storage;
* cognitive computation;
* graph construction;
* protocol communication.

ARCHITECTURAL PRINCIPLES
========================
1. Events are immutable once published
2. Revisions create new events, not mutations
3. Event identity is semantic, not runtime-derived
4. Causation and correlation must be explicit
5. Provenance is never lost
6. Replay reconstructs what happened, not how
7. Determinism is preserved
8. Semantic ownership is maintained

EVENT TAXONOMY
==============
The model supports the following event kinds:

Lifecycle Events:
* NETWORK_ACTIVATED / NETWORK_DEACTIVATED
* GOAL_CREATED / GOAL_COMPLETED
* TASK_CREATED / TASK_COMPLETED
* PLAN_STARTED / PLAN_COMPLETED

Cognitive Events:
* DECISION_CREATED / DECISION_SELECTED
* PREDICTION_CREATED / PREDICTION_UPDATED
* REWARD_ESTIMATED / REWARD_OBSERVED
* SALIENCE_CHANGED / ATTENTION_SHIFTED

Memory Events:
* WORKSPACE_ADMISSION / WORKSPACE_EVICTION
* MEMORY_ENCODED / MEMORY_RETRIEVED
* MEMORY_CONSOLIDATED

Meta-Cognitive Events:
* REFLECTION_STARTED / REFLECTION_COMPLETED
* LEARNING_STARTED / LEARNING_COMPLETED
* SYNCHRONIZATION_STARTED / SYNCHRONIZATION_COMPLETED

Error/Transition Events:
* BARRIER_BLOCKED / BARRIER_RELEASED
* TRANSITION_STARTED / TRANSITION_COMPLETED
* FAILURE_DETECTED / FAILURE_RECOVERED
* CONFLICT_DETECTED / CONFLICT_RESOLVED

Observation Events:
* OBSERVATION_RECORDED

Importance Levels:
* CRITICAL, HIGH, NORMAL, LOW, BACKGROUND

Duration Types:
* INSTANTANEOUS - Single point in semantic time
* INTERVAL - Has start and end events
* OPEN_INTERVAL - Ongoing interval

TIMELINE SCOPES
===============
* GLOBAL - All events across all networks
* NETWORK - Events from a specific network
* GOAL - Events related to a goal
* TASK - Events related to a task
* EPISODE - Coherent cognitive experiences
* DOMAIN - Domain-specific events
* REFLECTION - Reflection sessions

DETERMINISM INVARIANTS
======================
- Equivalent semantic inputs produce equivalent event identities
- Event ordering preserves semantic time, not wall-clock
- Replay reconstructs semantic history deterministically
- No randomness in identity generation
- No runtime memory addresses in identities

ARCHITECTURAL LAWS
==================
EVENT-LAW-001: Every Cognitive Event possesses stable semantic identity
EVENT-LAW-002: Event identity is independent from runtime execution
EVENT-LAW-003: Published events are immutable (revisions create new events)
EVENT-LAW-004: Causation must be explicit (no inference)
EVENT-LAW-005: Correlation never implies causation
EVENT-LAW-006: Provenance is never lost
EVENT-LAW-007: Historical events remain inspectable
EVENT-LAW-008: Event construction remains deterministic

IMPORT SAFETY
=============
This package is import-safe:
- No filesystem access during import
- No network access during import
- No model loading during import
- No runtime initialization during import
- No random identity generation during import
- No wall-clock acquisition during import

All construction is deterministic given identical semantic inputs.
"""

__all__ = [
    # Core enums - Phase 4.11.6 Part 2
    "CognitiveEventKind",
    "CognitiveEventStatus",
    "EventImportance",
    "EventDurationKind",
    
    # Identity models - Phase 4.11.6 Part 2
    "CognitiveEventIdentity",
    "CognitiveEventRevisionIdentity",
    
    # Revision models - Phase 4.11.6 Part 2
    "CognitiveEventRevision",
    "RevisionKind",
    
    # Duration models - Phase 4.11.6 Part 2
    "EventDuration",
    "EventIntervalReference",
    
    # Core event model - Phase 4.11.6 Part 2
    "CognitiveEvent",
    "SemanticTimeReference",
    
    # Stream models - Phase 4.11.6 Part 2
    "CognitiveEventStreamIdentity",
    "CognitiveEventStream",
    
    # Timeline models - Phase 4.11.6 Part 2
    "CognitiveTimelineScope",
    "CognitiveTimelineIdentity",
    "CognitiveTimeline",
    
    # Episode models - Phase 4.11.6 Part 2
    "CognitiveEpisodeIdentity",
    "CognitiveEpisodeKind",
    "CognitiveEpisode",
    
    # Aggregation models - Phase 4.11.6 Part 2
    "EventAggregationIdentity",
    "EventAggregation",
    
    # Correlation models - Phase 4.11.6 Part 2
    "EventCorrelationIdentity",
    "EventCorrelation",
    
    # Causation models - Phase 4.11.6 Part 2
    "EventCausation",
    
    # Lineage models - Phase 4.11.6 Part 2
    "EventLineage",
    
    # Index types - Phase 4.11.6 Part 2
    "EventIndexKey",
    
    # Replay models - Phase 4.11.6 Part 2
    "CognitiveReplayRequest",
    "CognitiveReplayResult",
    "ReplayScope",
    
    # Query models - Phase 4.11.6 Part 2
    "CognitiveEventQueryKind",
    "CognitiveEventQuery",
    "CognitiveEventQueryResult",
    
    # Validation models - Phase 4.11.6 Part 2
    "ValidationFindingCode",
    "ValidationFinding",
    "ValidationResult",
    "CognitiveEventValidationEngine",
    
    # Serialization models - Phase 4.11.6 Part 2
    "CognitiveEventSerializer",
    
    # Main engine - Phase 4.11.6 Part 3
    "CognitiveEventEngine",
    "CognitiveEventRequest",
    "CognitiveEventResult",
]

# =============================================================================
# CORE ENUMS - Phase 4.11.6 Part 2
# =============================================================================

from .kind import (
    CognitiveEventKind,
)

from .status import (
    CognitiveEventStatus,
)

from .importance import (
    EventImportance,
)

from .duration import (
    EventDurationKind,
    EventIntervalReference,
)

# =============================================================================
# IDENTITY MODELS - Phase 4.11.6 Part 2
# =============================================================================

from .identity import (
    SemanticTimeReference,
    CognitiveEventIdentity,
    CognitiveEventRevisionIdentity,
    CognitiveEventStreamIdentity,
    CognitiveTimelineIdentity,
    CognitiveEpisodeIdentity,
    EventAggregationIdentity,
    EventCorrelationIdentity,
)

# =============================================================================
# REVISION MODELS - Phase 4.11.6 Part 2
# =============================================================================

from .revision import (
    RevisionKind,
    CognitiveEventRevision,
)

# =============================================================================
# DURATION MODELS - Phase 4.11.6 Part 2
# =============================================================================

from .duration import (
    EventDuration,
)

# =============================================================================
# CORE EVENT MODEL - Phase 4.11.6 Part 2
# =============================================================================

from .event import (
    CognitiveEvent,
)

# =============================================================================
# STREAM MODELS - Phase 4.11.6 Part 2
# =============================================================================

from .stream import (
    CognitiveEventStreamIdentity,
    CognitiveEventStream,
    GlobalCognitiveEventStream,
)

# =============================================================================
# TIMELINE MODELS - Phase 4.11.6 Part 2
# =============================================================================

from .timeline import (
    CognitiveTimelineScope,
    CognitiveTimelineIdentity,
    CognitiveTimeline,
)

# =============================================================================
# EPISODE MODELS - Phase 4.11.6 Part 2
# =============================================================================

from .episode import (
    CognitiveEpisodeKind,
    CognitiveEpisodeIdentity,
    CognitiveEpisode,
)

# =============================================================================
# AGGREGATION MODELS - Phase 4.11.6 Part 2
# =============================================================================

from .aggregation import (
    EventAggregationIdentity,
    EventAggregation,
)

# =============================================================================
# CORRELATION MODELS - Phase 4.11.6 Part 2
# =============================================================================

from .correlation import (
    EventCorrelationIdentity,
    EventCorrelation,
)

# =============================================================================
# CAUSATION MODELS - Phase 4.11.6 Part 2
# =============================================================================

from .causation import (
    EventCausation,
)

# =============================================================================
# LINEAGE MODELS - Phase 4.11.6 Part 2
# =============================================================================

from .lineage import (
    EventLineage,
)

# =============================================================================
# INDEX TYPES - Phase 4.11.6 Part 2
# =============================================================================

from .indexes import (
    EventIndexKey,
)

# =============================================================================
# REPLAY MODELS - Phase 4.11.6 Part 2
# =============================================================================

from .replay import (
    ReplayScope,
    CognitiveReplayRequest,
    CognitiveReplayResult,
)

# =============================================================================
# QUERY MODELS - Phase 4.11.6 Part 2
# =============================================================================

from .query import (
    CognitiveEventQueryKind,
    CognitiveEventQuery,
    CognitiveEventQueryResult,
)

# =============================================================================
# VALIDATION MODELS - Phase 4.11.6 Part 2
# =============================================================================

from .validation import (
    ValidationFindingCode,
    ValidationFinding,
    ValidationResult,
    CognitiveEventValidationEngine,
)

# =============================================================================
# SERIALIZATION MODELS - Phase 4.11.6 Part 2
# =============================================================================

from .serialization import (
    CognitiveEventSerializer,
)

# =============================================================================
# MAIN ENGINE - Phase 4.11.6 Part 3
# =============================================================================

from .engine import (
    CognitiveEventEngine,
    CognitiveEventRequest,
    CognitiveEventResult,
)