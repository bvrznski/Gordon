# Narrative Coordination - Canonical Vocabulary
# ==============================================

"""
Canonical enum types and value sets for narrative coordination.

ARCHITECTURAL PRINCIPLES:
    - Immutable enum values
    - Deterministic ordering where applicable
    - Bounded sets (no unbounded expansion)
    - No runtime dependencies
"""

from __future__ import annotations

from typing import Tuple, FrozenSet


# =============================================================================
# NARRATIVE PURPOSE KINDS - Canonical categories of narrative intent
# =============================================================================

class NarrativePurposeKind:
    """
    Canonical purpose kinds for narrative episodes.
    
    Each purpose defines:
        - Expected context requirements
        - Allowed source kinds
        - Factuality restrictions
        - Perspective requirements
        - Completion rules
        - Revision permissions
    """
    
    # Continuity and integration
    AUTOBIOGRAPHICAL_INTEGRATION = "autobiographical_integration"
    """Integrate experiences into self-model continuity."""
    
    EXPERIENCE_INTEGRATION = "experience_integration"
    """Integrate recent experiences into semantic continuity."""
    
    CONVERSATION_CONTINUITY = "conversation_continuity"
    """Maintain conversation thread and participant understanding."""
    
    TASK_CONTINUITY = "task_continuity"
    """Track task progress, decisions, and outcomes."""
    
    COMMITMENT_CONTINUITY = "commitment_continuity"
    """Track commitments, obligations, and their status."""
    
    DECISION_OUTCOME_INTEGRATION = "decision_outcome_integration"
    """Link decisions to their outcomes and consequences."""
    
    # Analysis categories
    FAILURE_INTEGRATION = "failure_integration"
    """Analyze failures and their contributing factors."""
    
    SUCCESS_INTEGRATION = "success_integration"
    """Analyze successes and their contributing factors."""
    
    IDENTITY_RELEVANT_INTEGRATION = "identity_relevant_integration"
    """Integrate experiences relevant to self-model."""
    
    TEMPORAL_SEQUENCE_RECONSTRUCTION = "temporal_sequence_reconstruction"
    """Reconstruct event sequences from fragmented evidence."""
    
    # Interpretive categories
    CAUSAL_INTERPRETATION = "causal_interpretation"
    """Construct causal explanations for events."""
    
    THEMATIC_INTEGRATION = "thematic_integration"
    """Identify and track thematic patterns."""
    
    CONFLICT_RECONCILIATION = "conflict_reconciliation"
    """Reconcile conflicting narratives or evidence."""
    
    NARRATIVE_GAP_ANALYSIS = "narrative_gap_analysis"
    """Identify and characterize gaps in narrative structure."""
    
    # Revision categories
    NARRATIVE_REVISION = "narrative_revision"
    """Revise existing narrative with new evidence."""
    
    # Exploratory categories
    FUTURE_NARRATIVE_EXPLORATION = "future_narrative_exploration"
    """Explore possible future narratives."""
    
    COUNTERFACTUAL_NARRATIVE = "counterfactual_narrative"
    """Construct counterfactual narrative scenarios."""
    
    PARTICIPANT_SPECIFIC_ACCOUNT = "participant_specific_account"
    """Construct account from specific participant perspective."""
    
    # Preparation categories
    WORKSPACE_CANDIDATE_PREPARATION = "workspace_candidate_preparation"
    """Prepare narrative for conscious workspace submission."""
    
    GENERAL_NARRATIVE_COORDINATION = "general_narrative_coordination"
    """General narrative coordination without specific focus."""
    
    @classmethod
    def all_purposes(cls) -> Tuple[str, ...]:
        """Return all valid purpose kinds."""
        return (
            cls.AUTOBIOGRAPHICAL_INTEGRATION,
            cls.EXPERIENCE_INTEGRATION,
            cls.CONVERSATION_CONTINUITY,
            cls.TASK_CONTINUITY,
            cls.COMMITMENT_CONTINUITY,
            cls.DECISION_OUTCOME_INTEGRATION,
            cls.FAILURE_INTEGRATION,
            cls.SUCCESS_INTEGRATION,
            cls.IDENTITY_RELEVANT_INTEGRATION,
            cls.TEMPORAL_SEQUENCE_RECONSTRUCTION,
            cls.CAUSAL_INTERPRETATION,
            cls.THEMATIC_INTEGRATION,
            cls.CONFLICT_RECONCILIATION,
            cls.NARRATIVE_GAP_ANALYSIS,
            cls.NARRATIVE_REVISION,
            cls.FUTURE_NARRATIVE_EXPLORATION,
            cls.COUNTERFACTUAL_NARRATIVE,
            cls.PARTICIPANT_SPECIFIC_ACCOUNT,
            cls.WORKSPACE_CANDIDATE_PREPARATION,
            cls.GENERAL_NARRATIVE_COORDINATION,
        )
    
    @classmethod
    def requires_continuity(cls, purpose: str) -> bool:
        """Check if purpose typically requires continuity tracking."""
        return purpose in {
            cls.CONVERSATION_CONTINUITY,
            cls.TASK_CONTINUITY,
            cls.COMMITMENT_CONTINUITY,
            cls.AUTOBIOGRAPHICAL_INTEGRATION,
        }
    
    @classmethod
    def requires_revision(cls, purpose: str) -> bool:
        """Check if purpose typically involves revision."""
        return purpose in {
            cls.NARRATIVE_REVISION,
            cls.CONFLICT_RECONCILIATION,
            cls.NARRATIVE_GAP_ANALYSIS,
        }


# =============================================================================
# NARRATIVE SUBJECT KINDS - What the narrative is about
# =============================================================================

class NarrativeSubjectKind:
    """
    Canonical subject kinds for narratives.
    
    Each subject kind has distinct context requirements and source patterns.
    """
    
    AGENT = "agent"
    """Narrative about Gordon's own activity."""
    
    PARTICIPANT = "participant"
    """Narrative about a specific participant (not the agent)."""
    
    CONVERSATION = "conversation"
    """Narrative about a conversation thread."""
    
    TASK = "task"
    """Narrative about task execution and outcomes."""
    
    OBJECTIVE = "objective"
    """Narrative about objective pursuit and results."""
    
    COMMITMENT = "commitment"
    """Narrative about commitments and their fulfillment."""
    
    PLAN = "plan"
    """Narrative about plan design, execution, and revision."""
    
    DECISION = "decision"
    """Narrative about a decision point and its context."""
    
    ACTION = "action"
    """Narrative about specific actions taken."""
    
    OUTCOME = "outcome"
    """Narrative about an outcome and its causes."""
    
    FAILURE = "failure"
    """Narrative about a failure event or pattern."""
    
    SUCCESS = "success"
    """Narrative about a success event or pattern."""
    
    EXECUTION_THREAD = "execution_thread"
    """Narrative about an execution thread's semantic path."""
    
    INTERNAL_EPISODE = "internal_episode"
    """Narrative about an internal episode's coordination."""
    
    INTERNAL_THOUGHT = "internal_thought"
    """Narrative about internal thoughts and their relationships."""
    
    RELATIONSHIP = "relationship"
    """Narrative about a relationship or interaction pattern."""
    
    IDENTITY_ASPECT = "identity_aspect"
    """Narrative about an identity-relevant aspect."""
    
    MEMORY_CLUSTER = "memory_cluster"
    """Narrative about related memories."""
    
    TIME_PERIOD = "time_period"
    """Narrative about events in a specific time period."""
    
    PROJECT = "project"
    """Narrative about a project's progress and outcomes."""
    
    SYSTEM_EVOLUTION = "system_evolution"
    """Narrative about system-level changes over time."""
    
    GENERAL_EXPERIENCE = "general_experience"
    """General narrative without specific subject focus."""
    
    @classmethod
    def all_subjects(cls) -> Tuple[str, ...]:
        """Return all valid subject kinds."""
        return (
            cls.AGENT,
            cls.PARTICIPANT,
            cls.CONVERSATION,
            cls.TASK,
            cls.OBJECTIVE,
            cls.COMMITMENT,
            cls.PLAN,
            cls.DECISION,
            cls.ACTION,
            cls.OUTCOME,
            cls.FAILURE,
            cls.SUCCESS,
            cls.EXECUTION_THREAD,
            cls.INTERNAL_EPISODE,
            cls.INTERNAL_THOUGHT,
            cls.RELATIONSHIP,
            cls.IDENTITY_ASPECT,
            cls.MEMORY_CLUSTER,
            cls.TIME_PERIOD,
            cls.PROJECT,
            cls.SYSTEM_EVOLUTION,
            cls.GENERAL_EXPERIENCE,
        )
    
    @classmethod
    def requires_memory_context(cls, subject: str) -> bool:
        """Check if subject typically needs memory context."""
        return subject in {
            cls.MEMORY_CLUSTER,
            cls.INTERNAL_EPISODE,
            cls.INTERNAL_THOUGHT,
            cls.CONVERSATION,
            cls.EXECUTION_THREAD,
            cls.GENERAL_EXPERIENCE,
        }
    
    @classmethod
    def requires_participant_context(cls, subject: str) -> bool:
        """Check if subject typically needs participant context."""
        return subject in {
            cls.CONVERSATION,
            cls.RELATIONSHIP,
            cls.PARTICIPANT,
        }


# =============================================================================
# SOURCE KINDS - Categories of narrative sources
# =============================================================================

class SourceKind:
    """
    Canonical source kinds for narrative evidence.
    
    Sources provide the raw material from which narratives are constructed.
    Every source must include factuality classification and provenance.
    """
    
    MEMORY_RECORD = "memory_record"
    """Record from Memory system."""
    
    EXECUTION_OUTCOME = "execution_outcome"
    """Result of execution activity."""
    
    CONVERSATION_EVENT = "conversation_event"
    """Event from conversation thread."""
    
    ACTION_RESULT = "action_result"
    """Result of an action attempt."""
    
    DECISION_RECORD = "decision_record"
    """Record of a decision and its rationale."""
    
    PLAN_RECORD = "plan_record"
    """Record of plan design or revision."""
    
    OBJECTIVE_RECORD = "objective_record"
    """Record of objective status or progress."""
    
    COMMITMENT_RECORD = "commitment_record"
    """Record of commitment status."""
    
    INTERNAL_EPISODE = "internal_episode"
    """Result from an InternalEpisode."""
    
    INTERNAL_THOUGHT = "internal_thought"
    """Internal thought product."""
    
    REFLECTIVE_PRODUCT = "reflective_product"
    """Product from reflection coordination."""
    
    SIMULATION_PRODUCT = "simulation_product"
    """Product from simulation coordination."""
    
    PREDICTION = "prediction"
    """Predictive model result."""
    
    WORKSPACE_BROADCAST = "workspace_broadcast"
    """Broadcast from conscious workspace."""
    
    EXTERNAL_REPORT = "external_report"
    """Report from external system or user."""
    
    USER_STATEMENT = "user_statement"
    """Statement directly from user."""
    
    SYSTEM_EVENT = "system_event"
    """Event from internal system components."""
    
    UNKNOWN = "unknown"
    """Source kind cannot be determined."""
    
    @classmethod
    def all_source_kinds(cls) -> Tuple[str, ...]:
        """Return all valid source kinds."""
        return (
            cls.MEMORY_RECORD,
            cls.EXECUTION_OUTCOME,
            cls.CONVERSATION_EVENT,
            cls.ACTION_RESULT,
            cls.DECISION_RECORD,
            cls.PLAN_RECORD,
            cls.OBJECTIVE_RECORD,
            cls.COMMITMENT_RECORD,
            cls.INTERNAL_EPISODE,
            cls.INTERNAL_THOUGHT,
            cls.REFLECTIVE_PRODUCT,
            cls.SIMULATION_PRODUCT,
            cls.PREDICTION,
            cls.WORKSPACE_BROADCAST,
            cls.EXTERNAL_REPORT,
            cls.USER_STATEMENT,
            cls.SYSTEM_EVENT,
            cls.UNKNOWN,
        )


# =============================================================================
# FACTUALITY CLASSIFICATION - Evidence quality markers
# =============================================================================

class FactualityClassification:
    """
    Canonical factuality classifications for narrative elements.
    
    Every source, event, relation, and interpretation must preserve
    its factuality classification to prevent confusion between
    observed and constructed content.
    """
    
    OBSERVED = "observed"
    """Directly observed or measured state."""
    
    REPORTED = "reported"
    """Reported by external sources (not independently verified)."""
    
    RECORDED = "recorded"
    """Recorded in system memory with verification."""
    
    INFERRED = "inferred"
    """Inferred from evidence but not directly observed."""
    
    INTERPRETED = "interpreted"
    """Interpretation of observed or recorded content."""
    
    PREDICTED = "predicted"
    """Predicted based on patterns and models."""
    
    SIMULATED = "simulated"
    """Generated through simulation coordination."""
    
    COUNTERFACTUAL = "counterfactual"
    """Generated through counterfactual analysis."""
    
    HYPOTHETICAL = "hypothetical"
    """Hypothetical construct without specific evidence base."""
    
    DISPUTED = "disputed"
    """Content is disputed or contested."""
    
    UNKNOWN = "unknown"
    """Factual status cannot be determined."""
    
    @classmethod
    def all_factuality_classes(cls) -> Tuple[str, ...]:
        """Return all valid factuality classifications."""
        return (
            cls.OBSERVED,
            cls.REPORTED,
            cls.RECORDED,
            cls.INFERRED,
            cls.INTERPRETED,
            cls.PREDICTED,
            cls.SIMULATED,
            cls.COUNTERFACTUAL,
            cls.HYPOTHETICAL,
            cls.DISPUTED,
            cls.UNKNOWN,
        )
    
    @classmethod
    def is_simulated(cls, factuality: str) -> bool:
        """Check if factuality represents simulated content."""
        return factuality in {cls.SIMULATED, cls.COUNTERFACTUAL}
    
    @classmethod
    def is_not_observed(cls, factuality: str) -> bool:
        """Check if factuality is NOT directly observed."""
        return factuality not in {cls.OBSERVED}


# =============================================================================
# NARRATIVE EVENT KINDS - Categories of narrative events
# =============================================================================

class NarrativeEventKind:
    """
    Canonical event kinds for narratives.
    
    Events represent significant occurrences or states in the narrative timeline.
    """
    
    ACTION = "action"
    """A deliberate action taken."""
    
    DECISION = "decision"
    """A decision point or choice made."""
    
    STATE_CHANGE = "state_change"
    """A change in system state."""
    
    OBSERVATION = "observation"
    """An observation or reported event."""
    
    COMMITMENT = "commitment"
    """A commitment being made, modified, or fulfilled."""
    
    OUTCOME = "outcome"
    """The result of an action or set of conditions."""
    
    INTERNAL_EPISODE = "internal_episode"
    """An InternalEpisode completion or transition."""
    
    DISCOVERY = "discovery"
    """A new insight or understanding achieved."""
    
    FAILURE = "failure"
    """A failure event or unexpected outcome."""
    
    SUCCESS = "success"
    """A successful outcome or achievement."""
    
    REPORTED_STATEMENT = "reported_statement"
    """A statement reported by a participant."""
    
    TEMPORARY_EVENT = "temporary_event"
    """An event with temporary duration."""
    
    PERMANENT_EVENT = "permanent_event"
    """An event with lasting consequences."""
    
    @classmethod
    def all_event_kinds(cls) -> Tuple[str, ...]:
        """Return all valid event kinds."""
        return (
            cls.ACTION,
            cls.DECISION,
            cls.STATE_CHANGE,
            cls.OBSERVATION,
            cls.COMMITMENT,
            cls.OUTCOME,
            cls.INTERNAL_EPISODE,
            cls.DISCOVERY,
            cls.FAILURE,
            cls.SUCCESS,
            cls.REPORTED_STATEMENT,
            cls.TEMPORARY_EVENT,
            cls.PERMANENT_EVENT,
        )


# =============================================================================
# NARRATIVE RELATION KINDS - Types of narrative relations
# =============================================================================

class NarrativeRelationKind:
    """
    Canonical relation kinds for narratives.
    
    Relations describe semantic connections between events and states.
    """
    
    # Temporal relations
    TEMPORALLY_PRECEDES = "temporally_precedes"
    """Event occurs before another."""
    
    TEMPORALLY_FOLLOWS = "temporally_follows"
    """Event occurs after another."""
    
    SIMULTANEOUS = "simultaneous"
    """Events occur at the same time."""
    
    OVERLAPS = "overlaps"
    """Events overlap in time."""
    
    # Causal relations
    CAUSES = "causes"
    """Event directly causes another."""
    
    CONTRIBUTES_TO = "contributes_to"
    """Event contributes to another event."""
    
    ENABLES = "enables"
    """Event enables or makes possible another."""
    
    PREVENTS = "prevents"
    """Event prevents another."""
    
    MOTIVATES = "motivates"
    """Event motivates a decision or action."""
    
    EXPLAINS = "explains"
    """Event provides explanation for another."""
    
    # Logical relations
    CONTRADICTS = "contradicts"
    """Events are contradictory."""
    
    SUPPORTS = "supports"
    """Event supports the validity of another."""
    
    CONTINUES = "continues"
    """Event continues or extends a previous pattern."""
    
    RESOLVES = "resolves"
    """Event resolves a previous issue."""
    
    COMPLICATES = "complicates"
    """Event adds complexity to another."""
    
    REFRAMES = "reframes"
    """Event reframes understanding of another."""
    
    DERIVES_FROM = "derives_from"
    """Event derives from or follows logically from another."""
    
    RESPONSE_TO = "response_to"
    """Event is a response to another."""
    
    # State relations
    FULFILLS = "fulfills"
    """Event fulfills a commitment or objective."""
    
    VIOLATES = "violates"
    """Event violates a commitment or norm."""
    
    SUPERSEDES = "supersedes"
    """Event supersedes or replaces a previous state."""
    
    ASSOCIATED_WITH = "associated_with"
    """Events are associated but not directly related."""
    
    UNKNOWN = "unknown"
    """Relation kind cannot be determined."""
    
    @classmethod
    def all_relation_kinds(cls) -> Tuple[str, ...]:
        """Return all valid relation kinds."""
        return (
            cls.TEMPORALLY_PRECEDES,
            cls.TEMPORALLY_FOLLOWS,
            cls.SIMULTANEOUS,
            cls.OVERLAPS,
            cls.CAUSES,
            cls.CONTRIBUTES_TO,
            cls.ENABLES,
            cls.PREVENTS,
            cls.MOTIVATES,
            cls.EXPLAINS,
            cls.CONTRADICTS,
            cls.SUPPORTS,
            cls.CONTINUES,
            cls.RESOLVES,
            cls.COMPLICATES,
            cls.REFRAMES,
            cls.DERIVES_FROM,
            cls.RESPONSE_TO,
            cls.FULFILLS,
            cls.VIOLATES,
            cls.SUPERSEDES,
            cls.ASSOCIATED_WITH,
            cls.UNKNOWN,
        )
    
    @classmethod
    def is_temporal(cls, kind: str) -> bool:
        """Check if relation kind is temporal."""
        return kind in {
            cls.TEMPORALLY_PRECEDES,
            cls.TEMPORALLY_FOLLOWS,
            cls.SIMULTANEOUS,
            cls.OVERLAPS,
        }
    
    @classmethod
    def is_causal(cls, kind: str) -> bool:
        """Check if relation kind is causal."""
        return kind in {
            cls.CAUSES,
            cls.CONTRIBUTES_TO,
            cls.ENABLES,
            cls.PREVENTS,
            cls.MOTIVATES,
            cls.EXPLAINS,
        }


# =============================================================================
# NARRATIVE PERSPECTIVE KINDS - Narrative viewpoints
# =============================================================================

class NarrativePerspectiveKind:
    """
    Canonical perspective kinds for narratives.
    
    Perspective determines available evidence and interpretation limits.
    """
    
    AGENT_FIRST_PERSON = "agent_first_person"
    """Narrative from Gordon's first-person perspective."""
    
    PARTICIPANT = "participant"
    """Narrative from a specific participant's perspective."""
    
    EXTERNAL_OBSERVER = "external_observer"
    """Narrative from an external observer perspective."""
    
    SYSTEM = "system"
    """System-level perspective on events."""
    
    MULTI_PERSPECTIVE = "multi_perspective"
    """Multiple perspectives integrated but kept distinct."""
    
    UNSPECIFIED = "unspecified"
    """Perspective not specified or unknown."""
    
    @classmethod
    def all_perspective_kinds(cls) -> Tuple[str, ...]:
        """Return all valid perspective kinds."""
        return (
            cls.AGENT_FIRST_PERSON,
            cls.PARTICIPANT,
            cls.EXTERNAL_OBSERVER,
            cls.SYSTEM,
            cls.MULTI_PERSPECTIVE,
            cls.UNSPECIFIED,
        )


# =============================================================================
# TEMPORAL RELATION KINDS - Event ordering relations
# =============================================================================

class TemporalRelationKind:
    """
    Canonical temporal relations between events.
    
    These describe how events are ordered in time, including uncertainty.
    """
    
    BEFORE = "before"
    """Event A occurs before event B."""
    
    AFTER = "after"
    """Event A occurs after event B."""
    
    OVERLAPS = "overlaps"
    """Events overlap in time."""
    
    DURING = "during"
    """Event A occurs during event B's duration."""
    
    STARTS = "starts"
    """Event A starts at the same time as event B."""
    
    FINISHES = "finishes"
    """Event A finishes at the same time as event B."""
    
    SIMULTANEOUS = "simultaneous"
    """Events occur simultaneously."""
    
    UNKNOWN = "unknown"
    """Temporal relationship cannot be determined."""
    
    @classmethod
    def all_temporal_relations(cls) -> Tuple[str, ...]:
        """Return all valid temporal relations."""
        return (
            cls.BEFORE,
            cls.AFTER,
            cls.OVERLAPS,
            cls.DURING,
            cls.STARTS,
            cls.FINISHES,
            cls.SIMULTANEOUS,
            cls.UNKNOWN,
        )


# =============================================================================
# NARRATIVE PRODUCT KINDS - Types of narrative products
# =============================================================================

class NarrativeProductKind:
    """
    Canonical product kinds for narratives.
    
    Products are bounded semantic results generated through narrative coordination.
    They should be compatible with InternalThought but remain distinct from
    runtime execution commands.
    """
    
    # Structural products
    NARRATIVE_SEQUENCE = "narrative_sequence"
    """Ordered event sequence."""
    
    EVENT_SUMMARY = "event_summary"
    """Summary of key events."""
    
    CONTINUITY_ACCOUNT = "continuity_account"
    """Account of semantic continuity."""
    
    COMMITMENT_ACCOUNT = "commitment_account"
    """Account of commitments and their status."""
    
    DECISION_OUTCOME_ACCOUNT = "decision_outcome_account"
    """Account linking decisions to outcomes."""
    
    EXPERIENCE_ACCOUNT = "experience_account"
    """Personal experience account."""
    
    THEMATIC_ACCOUNT = "thematic_account"
    """Thematic pattern account."""
    
    # Interpretive products
    MULTI_PERSPECTIVE_ACCOUNT = "multi_perspective_account"
    """Multiple perspectives integrated but distinct."""
    
    NARRATIVE_INTERPRETATION = "narrative_interpretation"
    """Interpretive structure for events."""
    
    # Diagnostic products
    NARRATIVE_GAP_REPORT = "narrative_gap_report"
    """Report on narrative gaps."""
    
    NARRATIVE_CONFLICT_REPORT = "narrative_conflict_report"
    """Report on narrative conflicts."""
    
    NARRATIVE_REVISION_PROPOSAL = "narrative_revision_proposal"
    """Proposal for narrative revision."""
    
    # Exploratory products
    FUTURE_NARRATIVE = "future_narrative"
    """Future-oriented narrative scenario."""
    
    COUNTERFACTUAL_NARRATIVE = "counterfactual_narrative"
    """Counterfactual narrative scenario."""
    
    IDENTITY_RELEVANT_NARRATIVE = "identity_relevant_narrative"
    """Identity-relevant narrative content."""
    
    # Workspace preparation
    WORKSPACE_CANDIDATE = "workspace_candidate"
    """Candidate for conscious workspace submission."""
    
    NO_MEANINGFUL_RESULT = "no_meaningful_result"
    """Narrative coordination completed without meaningful product."""
    
    @classmethod
    def all_product_kinds(cls) -> Tuple[str, ...]:
        """Return all valid product kinds."""
        return (
            cls.NARRATIVE_SEQUENCE,
            cls.EVENT_SUMMARY,
            cls.CONTINUITY_ACCOUNT,
            cls.COMMITMENT_ACCOUNT,
            cls.DECISION_OUTCOME_ACCOUNT,
            cls.EXPERIENCE_ACCOUNT,
            cls.THEMATIC_ACCOUNT,
            cls.MULTI_PERSPECTIVE_ACCOUNT,
            cls.NARRATIVE_INTERPRETATION,
            cls.NARRATIVE_GAP_REPORT,
            cls.NARRATIVE_CONFLICT_REPORT,
            cls.NARRATIVE_REVISION_PROPOSAL,
            cls.FUTURE_NARRATIVE,
            cls.COUNTERFACTUAL_NARRATIVE,
            cls.IDENTITY_RELEVANT_NARRATIVE,
            cls.WORKSPACE_CANDIDATE,
            cls.NO_MEANINGFUL_RESULT,
        )
    
    @classmethod
    def is_structural(cls, kind: str) -> bool:
        """Check if product kind is structural."""
        return kind in {
            cls.NARRATIVE_SEQUENCE,
            cls.EVENT_SUMMARY,
            cls.CONTINUITY_ACCOUNT,
            cls.COMMITMENT_ACCOUNT,
            cls.DECISION_OUTCOME_ACCOUNT,
            cls.EXPERIENCE_ACCOUNT,
            cls.THEMATIC_ACCOUNT,
            cls.MULTI_PERSPECTIVE_ACCOUNT,
        }
    
    @classmethod
    def is_interpretive(cls, kind: str) -> bool:
        """Check if product kind is interpretive."""
        return kind in {
            cls.NARRATIVE_INTERPRETATION,
            cls.FUTURE_NARRATIVE,
            cls.COUNTERFACTUAL_NARRATIVE,
            cls.IDENTITY_RELEVANT_NARRATIVE,
        }
    
    @classmethod
    def is_diagnostic(cls, kind: str) -> bool:
        """Check if product kind is diagnostic."""
        return kind in {
            cls.NARRATIVE_GAP_REPORT,
            cls.NARRATIVE_CONFLICT_REPORT,
            cls.NARRATIVE_REVISION_PROPOSAL,
        }


# =============================================================================
# NARRATIVE OUTCOME KINDS - Terminal results of narrative coordination
# =============================================================================

class NarrativeOutcomeKind:
    """
    Canonical outcome kinds for narrative episodes.
    
    Outcomes represent what the narrative episode produced, not runtime commands.
    """
    
    # Successful outcomes
    NARRATIVE_CONSTRUCTED = "narrative_constructed"
    """Valid narrative was constructed."""
    
    NARRATIVE_REVISED = "narrative_revised"
    """Narrative was revised with new evidence."""
    
    CONTINUITY_ESTABLISHED = "continuity_established"
    """Continuity was established or confirmed."""
    
    CONTINUITY_PARTIAL = "continuity_partial"
    """Partial continuity established."""
    
    GAPS_IDENTIFIED = "gaps_identified"
    """Narrative gaps were identified and documented."""
    
    CONFLICTS_IDENTIFIED = "conflicts_identified"
    """Conflicts were identified and documented."""
    
    THEMES_IDENTIFIED = "themes_identified"
    """Thematic patterns were identified."""
    
    MULTIPLE_INTERPRETATIONS_PRESERVED = "multiple_interpretations_preserved"
    """Multiple valid interpretations preserved."""
    
    IDENTITY_REVIEW_PROPOSED = "identity_review_proposed"
    """Identity review proposed."""
    
    MEMORY_INTEGRATION_PROPOSED = "memory_integration_proposed"
    """Memory integration proposed."""
    
    # Partial outcomes
    PARTIALLY_COMPLETED = "partially_completed"
    """Some narrative steps completed but not all."""
    
    INSUFFICIENT_CONTEXT = "insufficient_context"
    """Context did not meet minimum requirements."""
    
    NO_MEANINGFUL_RESULT = "no_meaningful_result"
    """Narrative coordination completed without meaningful result."""
    
    # Failure states
    FAILED = "failed"
    """Terminated without valid outcome."""
    
    CANCELLED = "cancelled"
    """Terminated before completion."""
    
    EXPIRED = "expired"
    """Terminated due to expiration."""
    
    @classmethod
    def all_outcome_kinds(cls) -> Tuple[str, ...]:
        """Return all valid outcome kinds."""
        return (
            cls.NARRATIVE_CONSTRUCTED,
            cls.NARRATIVE_REVISED,
            cls.CONTINUITY_ESTABLISHED,
            cls.CONTINUITY_PARTIAL,
            cls.GAPS_IDENTIFIED,
            cls.CONFLICTS_IDENTIFIED,
            cls.THEMES_IDENTIFIED,
            cls.MULTIPLE_INTERPRETATIONS_PRESERVED,
            cls.IDENTITY_REVIEW_PROPOSED,
            cls.MEMORY_INTEGRATION_PROPOSED,
            cls.PARTIALLY_COMPLETED,
            cls.INSUFFICIENT_CONTEXT,
            cls.NO_MEANINGFUL_RESULT,
            cls.FAILED,
            cls.CANCELLED,
            cls.EXPIRED,
        )
    
    @classmethod
    def is_success(cls, outcome: str) -> bool:
        """Check if outcome kind represents successful coordination."""
        return outcome in {
            cls.NARRATIVE_CONSTRUCTED,
            cls.NARRATIVE_REVISED,
            cls.CONTINUITY_ESTABLISHED,
            cls.CONTINUITY_PARTIAL,
            cls.GAPS_IDENTIFIED,
            cls.CONFLICTS_IDENTIFIED,
            cls.THEMES_IDENTIFIED,
            cls.MULTIPLE_INTERPRETATIONS_PRESERVED,
            cls.IDENTITY_REVIEW_PROPOSED,
            cls.MEMORY_INTEGRATION_PROPOSED,
        }
    
    @classmethod
    def is_terminal(cls, outcome: str) -> bool:
        """Check if outcome kind represents terminal state."""
        return outcome in {
            cls.NARRATIVE_CONSTRUCTED,
            cls.NARRATIVE_REVISED,
            cls.CONTINUITY_ESTABLISHED,
            cls.CONTINUITY_PARTIAL,
            cls.GAPS_IDENTIFIED,
            cls.CONFLICTS_IDENTIFIED,
            cls.THEMES_IDENTIFIED,
            cls.MULTIPLE_INTERPRETATIONS_PRESERVED,
            cls.IDENTITY_REVIEW_PROPOSED,
            cls.MEMORY_INTEGRATION_PROPOSED,
            cls.PARTIALLY_COMPLETED,
            cls.INSUFFICIENT_CONTEXT,
            cls.NO_MEANINGFUL_RESULT,
            cls.FAILED,
            cls.CANCELLED,
            cls.EXPIRED,
        }


# =============================================================================
# NARRATIVE CONTINUATION KINDS - Advisory recommendations
# =============================================================================

class NarrativeContinuationKind:
    """
    Canonical continuation kinds for narrative episodes.
    
    Continuation recommendations are advisory. They do NOT schedule execution.
    """
    
    COMPLETE = "complete"
    """Narrative coordination completed successfully."""
    
    CONTINUE_CURRENT_ACCOUNT = "continue_current_account"
    """Continue processing current narrative account."""
    
    REQUEST_ADDITIONAL_SOURCES = "request_additional_sources"
    """Request additional sources of evidence."""
    
    REQUEST_CONTEXT_REFRESH = "request_context_refresh"
    """Refresh context binding with updated projections."""
    
    REQUEST_MEMORY_EVIDENCE = "request_memory_evidence"
    """Request memory system evidence."""
    
    REQUEST_PARTICIPANT_PERSPECTIVE = "request_participant_perspective"
    """Request participant perspective projection."""
    
    REQUEST_REFLECTION = "request_reflection"
    """Request reflection coordination."""
    
    REQUEST_SIMULATION = "request_simulation"
    """Request simulation or counterfactual exploration."""
    
    REQUEST_IDENTITY_REVIEW = "request_identity_review"
    """Request identity review coordination."""
    
    RESOLVE_CONFLICT = "resolve_conflict"
    """Resolve identified conflicts before proceeding."""
    
    REVISE_NARRATIVE = "revise_narrative"
    """Revise narrative with new evidence or interpretation."""
    
    WAIT_FOR_EVIDENCE = "wait_for_evidence"
    """Wait for additional evidence to become available."""
    
    SUBMIT_WORKSPACE_CANDIDATE = "submit_workspace_candidate"
    """Submit workspace candidate to conscious workspace."""
    
    REQUEST_EXECUTION_TASK = "request_execution_task"
    """Request an ExecutionTask for persistent coordination."""
    
    SUSPEND = "suspend"
    """Suspend processing, may resume later."""
    
    FAIL = "fail"
    """Mark as failed with error."""
    
    CANCEL = "cancel"
    """Cancel the narrative episode."""
    
    @classmethod
    def all_continuation_kinds(cls) -> Tuple[str, ...]:
        """Return all valid continuation kinds."""
        return (
            cls.COMPLETE,
            cls.CONTINUE_CURRENT_ACCOUNT,
            cls.REQUEST_ADDITIONAL_SOURCES,
            cls.REQUEST_CONTEXT_REFRESH,
            cls.REQUEST_MEMORY_EVIDENCE,
            cls.REQUEST_PARTICIPANT_PERSPECTIVE,
            cls.REQUEST_REFLECTION,
            cls.REQUEST_SIMULATION,
            cls.REQUEST_IDENTITY_REVIEW,
            cls.RESOLVE_CONFLICT,
            cls.REVISE_NARRATIVE,
            cls.WAIT_FOR_EVIDENCE,
            cls.SUBMIT_WORKSPACE_CANDIDATE,
            cls.REQUEST_EXECUTION_TASK,
            cls.SUSPEND,
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
            cls.REQUEST_ADDITIONAL_SOURCES,
            cls.REQUEST_CONTEXT_REFRESH,
            cls.REQUEST_MEMORY_EVIDENCE,
            cls.REQUEST_PARTICIPANT_PERSPECTIVE,
            cls.REQUEST_REFLECTION,
            cls.REQUEST_SIMULATION,
            cls.REQUEST_IDENTITY_REVIEW,
            cls.RESOLVE_CONFLICT,
            cls.REVISE_NARRATIVE,
            cls.WAIT_FOR_EVIDENCE,
            cls.SUBMIT_WORKSPACE_CANDIDATE,
            cls.REQUEST_EXECUTION_TASK,
        }


# =============================================================================
# NARRATIVE GAP KINDS - Types of narrative gaps
# =============================================================================

class NarrativeGapKind:
    """
    Canonical gap kinds for narratives.
    
    Gaps represent missing or unclear elements in the narrative structure.
    """
    
    MISSING_EVENT = "missing_event"
    """An event is missing between known events."""
    
    MISSING_CAUSE = "missing_cause"
    """Cause of an event is unknown."""
    
    MISSING_CONSEQUENCE = "missing_consequence"
    """Consequence of an event is unknown."""
    
    MISSING_MOTIVATION = "missing_motivation"
    """Motivation for a decision or action is unknown."""
    
    MISSING_PARTICIPANT_PERSPECTIVE = "missing_participant_perspective"
    """Participant perspective is unavailable."""
    
    TEMPORAL_GAP = "temporal_gap"
    """Time period with no known events."""
    
    MISSING_SOURCE = "missing_source"
    """Source of information is unavailable."""
    
    UNRESOLVED_COMMITMENT = "unresolved_commitment"
    """Commitment status is unclear."""
    
    UNEXPLAINED_CHANGE = "unexplained_change"
    """State change without known cause."""
    
    UNKNOWN = "unknown"
    """Gap type cannot be determined."""
    
    @classmethod
    def all_gap_kinds(cls) -> Tuple[str, ...]:
        """Return all valid gap kinds."""
        return (
            cls.MISSING_EVENT,
            cls.MISSING_CAUSE,
            cls.MISSING_CONSEQUENCE,
            cls.MISSING_MOTIVATION,
            cls.MISSING_PARTICIPANT_PERSPECTIVE,
            cls.TEMPORAL_GAP,
            cls.MISSING_SOURCE,
            cls.UNRESOLVED_COMMITMENT,
            cls.UNEXPLAINED_CHANGE,
            cls.UNKNOWN,
        )


# =============================================================================
# NARRATIVE CONFLICT KINDS - Types of narrative conflicts
# =============================================================================

class NarrativeConflictKind:
    """
    Canonical conflict kinds for narratives.
    
    Conflicts represent irreconcilable or disputed elements in the narrative.
    """
    
    SOURCE_CONFLICT = "source_conflict"
    """Conflicting sources provide different information."""
    
    EVENT_CONFLICT = "event_conflict"
    """Events are reported differently across sources."""
    
    TEMPORAL_CONFLICT = "temporal_conflict"
    """Conflicting temporal orderings."""
    
    CAUSAL_CONFLICT = "causal_conflict"
    """Conflicting causal explanations."""
    
    PERSPECTIVE_CONFLICT = "perspective_conflict"
    """Different participant perspectives cannot be merged."""
    
    IDENTITY_CONFLICT = "identity_conflict"
    """Conflict with identity model or self-concept."""
    
    MEMORY_CONFLICT = "memory_conflict"
    """Conflicting memory records."""
    
    INTERPRETATION_CONFLICT = "interpretation_conflict"
    """Conflicting interpretations of same events."""
    
    FACTUALITY_CONFLICT = "factuality_conflict"
    """Conflicting factuality classifications."""
    
    COMMITMENT_CONFLICT = "commitment_conflict"
    """Conflicting commitments or obligations."""
    
    UNKNOWN = "unknown"
    """Conflict type cannot be determined."""
    
    @classmethod
    def all_conflict_kinds(cls) -> Tuple[str, ...]:
        """Return all valid conflict kinds."""
        return (
            cls.SOURCE_CONFLICT,
            cls.EVENT_CONFLICT,
            cls.TEMPORAL_CONFLICT,
            cls.CAUSAL_CONFLICT,
            cls.PERSPECTIVE_CONFLICT,
            cls.IDENTITY_CONFLICT,
            cls.MEMORY_CONFLICT,
            cls.INTERPRETATION_CONFLICT,
            cls.FACTUALITY_CONFLICT,
            cls.COMMITMENT_CONFLICT,
            cls.UNKNOWN,
        )


# =============================================================================
# NARRATIVE CONTINUITY ASSESSMENT KINDS
# =============================================================================

class NarrativeContinuityKind:
    """
    Canonical continuity classification kinds.
    """
    
    CONTINUOUS = "continuous"
    """Full temporal and semantic continuity."""
    
    MOSTLY_CONTINUOUS = "mostly_continuous"
    """Mostly continuous with minor gaps."""
    
    PARTIALLY_CONTINUOUS = "partially_continuous"
    """Partial continuity with significant gaps."""
    
    FRAGMENTED = "fragmented"
    """Fragmented events with limited connections."""
    
    DISCONNECTED = "disconnected"
    """Events with no discernible connections."""
    
    UNKNOWN = "unknown"
    """Continuity cannot be determined."""
    
    @classmethod
    def all_continuity_kinds(cls) -> Tuple[str, ...]:
        """Return all valid continuity kinds."""
        return (
            cls.CONTINUOUS,
            cls.MOSTLY_CONTINUOUS,
            cls.PARTIALLY_CONTINUOUS,
            cls.FRAGMENTED,
            cls.DISCONNECTED,
            cls.UNKNOWN,
        )


# =============================================================================
# NARRATIVE COHERENCE ASSESSMENT KINDS
# =============================================================================

class NarrativeCoherenceKind:
    """
    Canonical coherence classification kinds.
    """
    
    COHERENT = "coherent"
    """Internally consistent narrative."""
    
    MOSTLY_COHERENT = "mostly_coherent"
    """Mostly consistent with minor issues."""
    
    PARTIALLY_COHERENT = "partially_coherent"
    """Partial consistency with significant issues."""
    
    INCOHERENT = "incoherent"
    """Inconsistent or contradictory."""
    
    UNDETERMINED = "undetermined"
    """Cannot determine coherence."""
    
    @classmethod
    def all_coherence_kinds(cls) -> Tuple[str, ...]:
        """Return all valid coherence kinds."""
        return (
            cls.COHERENT,
            cls.MOSTLY_COHERENT,
            cls.PARTIALLY_COHERENT,
            cls.INCOHERENT,
            cls.UNDETERMINED,
        )


# =============================================================================
# NARRATIVE COMPLETENESS KINDS
# =============================================================================

class NarrativeCompletenessKind:
    """
    Canonical completeness classification kinds.
    """
    
    COMPLETE = "complete"
    """All required elements present."""
    
    SUFFICIENT = "sufficient"
    """Sufficient for the purpose, some elements missing."""
    
    PARTIAL = "partial"
    """Partial coverage of required elements."""
    
    INSUFFICIENT = "insufficient"
    """Insufficient elements to meet purpose."""
    
    INVALID = "invalid"
    """Cannot be evaluated due to invalid structure."""
    
    @classmethod
    def all_completeness_kinds(cls) -> Tuple[str, ...]:
        """Return all valid completeness kinds."""
        return (
            cls.COMPLETE,
            cls.SUFFICIENT,
            cls.PARTIAL,
            cls.INSUFFICIENT,
            cls.INVALID,
        )