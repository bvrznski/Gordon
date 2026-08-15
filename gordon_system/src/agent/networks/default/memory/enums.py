# Memory Integration - Canonical Enums
# =====================================

"""
Canonical enum types and value sets for memory integration coordination.

ARCHITECTURAL PRINCIPLES:
    - Immutable enum values (frozen dataclasses, class constants)
    - Deterministic ordering where applicable
    - Bounded sets (no unbounded expansion)
    - No runtime dependencies (pure semantic definitions)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


# =============================================================================
# MEMORY KINDS - Canonical categories of memory records
# =============================================================================

class MemoryKind:
    """
    Canonical kinds of memory records.
    
    These define the type of information stored, not how it is retrieved or
    where it is persisted.
    """
    
    EPISODIC = "episodic"
    """Memory of specific events or experiences."""
    
    SEMANTIC = "semantic"
    """General knowledge and concepts (not tied to specific events)."""
    
    AUTOBIOGRAPHICAL = "autobiographical"
    """Self-relevant memories that contribute to identity."""
    
    PROCEDURAL = "procedural"
    """Skills, habits, and procedure-based knowledge."""
    
    WORKING_MEMORY_REFERENCE = "working_memory_reference"
    """Reference to content in Working Memory (not the content itself)."""
    
    PROSPECTIVE = "prospective"
    """Memories of intended future actions or events."""
    
    ASSOCIATIVE = "associative"
    """Memory records primarily defined by associations with other records."""
    
    RELATIONAL = "relational"
    """Records describing relationships between entities."""
    
    CONTEXTUAL = "contextual"
    """Context information that frames other memories."""
    
    SYSTEM_HISTORY = "system_history"
    """System-level operation history (not user experience)."""
    
    EXTERNAL_KNOWLEDGE_REFERENCE = "external_knowledge_reference"
    """Reference to external knowledge sources."""
    
    UNKNOWN = "unknown"
    """Memory kind cannot be determined or is unspecified."""
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid memory kinds."""
        return (
            cls.EPISODIC,
            cls.SEMANTIC,
            cls.AUTOBIOGRAPHICAL,
            cls.PROCEDURAL,
            cls.WORKING_MEMORY_REFERENCE,
            cls.PROSPECTIVE,
            cls.ASSOCIATIVE,
            cls.RELATIONAL,
            cls.CONTEXTUAL,
            cls.SYSTEM_HISTORY,
            cls.EXTERNAL_KNOWLEDGE_REFERENCE,
            cls.UNKNOWN,
        )
    
    @classmethod
    def is_certain(cls, kind: str) -> bool:
        """Check if memory kind represents certain (not speculative) content."""
        return kind not in {cls.PROSPECTIVE, cls.ASSOCIATIVE}
    
    @classmethod
    def requires_subjects(cls, kind: str) -> bool:
        """Check if memory kind typically has subject references."""
        return kind in {
            cls.EPISODIC,
            cls.AUTOBIOGRAPHICAL,
            cls.PROCEDURAL,
            cls.WORKING_MEMORY_REFERENCE,
        }


# =============================================================================
# FACTUALITY CLASSES - Evidence of truth status
# =============================================================================

class FactualityClass:
    """
    Canonical factuality classifications for memory records.
    
    Factuality is independent from confidence. A highly confident simulated
    event remains counterfactual.
    """
    
    OBSERVED = "observed"
    """Recorded as having occurred in reality (direct observation)."""
    
    RECORDED = "recorded"
    """Documented through external means (e.g., logs, notes)."""
    
    REPORTED = "reported"
    """Reported by another source (secondhand information)."""
    
    INFERRED = "inferred"
    """Deductively or inductively concluded from other evidence."""
    
    INTERPRETED = "interpreted"
    """Subjective interpretation of events or data."""
    
    PREDICTED = "predicted"
    """Future-oriented projection based on current knowledge."""
    
    SIMULATED = "simulated"
    """Generated through simulation (not observed)."""
    
    COUNTERFACTUAL = "counterfactual"
    """Hypothetical alternative to actual events."""
    
    HYPOTHETICAL = "hypothetical"
    """Speculative possibility without current evidence."""
    
    DISPUTED = "disputed"
    """Contention exists about this record's accuracy."""
    
    SUPERSEDED = "superseded"
    """Replaced by a more accurate or complete record."""
    
    UNKNOWN = "unknown"
    """Factuality cannot be determined."""
    
    @classmethod
    def all_classes(cls) -> Tuple[str, ...]:
        """Return all valid factuality classes."""
        return (
            cls.OBSERVED,
            cls.RECORDED,
            cls.REPORTED,
            cls.INFERRED,
            cls.INTERPRETED,
            cls.PREDICTED,
            cls.SIMULATED,
            cls.COUNTERFACTUAL,
            cls.HYPOTHETICAL,
            cls.DISPUTED,
            cls.SUPERSEDED,
            cls.UNKNOWN,
        )
    
    @classmethod
    def is_factual(cls, factuality: str) -> bool:
        """Check if factuality class represents factual (not speculative) content."""
        return factuality in {
            cls.OBSERVED,
            cls.RECORDED,
            cls.REPORTED,
        }
    
    @classmethod
    def is_speculative(cls, factuality: str) -> bool:
        """Check if factuality class represents speculative content."""
        return factuality in {
            cls.PREDICTED,
            cls.SIMULATED,
            cls.COUNTERFACTUAL,
            cls.HYPOTHETICAL,
        }
    
    @classmethod
    def is_disputed(cls, factuality: str) -> bool:
        """Check if factuality class represents potentially contested content."""
        return factuality in {
            cls.DISPUTED,
            cls.INTERPRETED,
            cls.INFERRED,
        }


# =============================================================================
# SOURCE AUTHORITY - Origin of memory records
# =============================================================================

class SourceAuthority:
    """
    Canonical authority classifications for memory record sources.
    
    Authority is independent from confidence. A source may be highly authoritative
    but still produce incorrect information.
    """
    
    MEMORY_AUTHORITY = "memory_authority"
    """Source is the canonical Memory Capability."""
    
    EXECUTION_RECORD = "execution_record"
    """Record comes from ExecutionThread or execution history."""
    
    USER_REPORT = "user_report"
    """Information directly reported by user."""
    
    DEVELOPER_DECLARATION = "developer_declaration"
    """Explicit declaration by system developer."""
    
    SYSTEM_OBSERVATION = "system_observation"
    """System observation of its own state or behavior."""
    
    EXTERNAL_SOURCE = "external_source"
    """Information from external systems or services."""
    
    INTERNAL_INFERENCE = "internal_inference"
    """Concluded through internal processing."""
    
    NARRATIVE_INTERPRETATION = "narrative_interpretation"
    """Interpretation from narrative coordination."""
    
    REFLECTION_RESULT = "reflection_result"
    """Result from reflection coordination."""
    
    SIMULATION_RESULT = "simulation_result"
    """Result from simulation or counterfactual generation."""
    
    PREDICTION_RESULT = "prediction_result"
    """Result from predictive coordination."""
    
    UNKNOWN = "unknown"
    """Source authority cannot be determined."""
    
    @classmethod
    def all_authorities(cls) -> Tuple[str, ...]:
        """Return all valid source authorities."""
        return (
            cls.MEMORY_AUTHORITY,
            cls.EXECUTION_RECORD,
            cls.USER_REPORT,
            cls.DEVELOPER_DECLARATION,
            cls.SYSTEM_OBSERVATION,
            cls.EXTERNAL_SOURCE,
            cls.INTERNAL_INFERENCE,
            cls.NARRATIVE_INTERPRETATION,
            cls.REFLECTION_RESULT,
            cls.SIMULATION_RESULT,
            cls.PREDICTION_RESULT,
            cls.UNKNOWN,
        )
    
    @classmethod
    def is_direct(cls, authority: str) -> bool:
        """Check if source is direct (not inferred or interpreted)."""
        return authority in {
            cls.MEMORY_AUTHORITY,
            cls.EXECUTION_RECORD,
            cls.USER_REPORT,
            cls.SYSTEM_OBSERVATION,
            cls.DEVELOPER_DECLARATION,
        }
    
    @classmethod
    def is_indirect(cls, authority: str) -> bool:
        """Check if source is indirect (inferred or interpreted)."""
        return authority in {
            cls.INTERNAL_INFERENCE,
            cls.NARRATIVE_INTERPRETATION,
            cls.REFLECTION_RESULT,
            cls.SIMULATION_RESULT,
            cls.PREDICTION_RESULT,
        }


# =============================================================================
# MEMORY INTEGRATION PURPOSE KINDS - Canonical categories of memory integration
# =============================================================================

class MemoryIntegrationPurposeKind:
    """
    Canonical purpose kinds for memory integration episodes.
    
    Each purpose defines:
        - Required memory kinds
        - Expected product types
        - Completion rules
        - Scope limits
    """
    
    # Context and general integration
    CONTEXT_ENRICHMENT = "context_enrichment"
    """Enrich current context with relevant memories."""
    
    GENERAL_MEMORY_INTEGRATION = "general_memory_integration"
    """General memory coordination without specific focus."""
    
    # Memory kind-specific
    EPISODIC_INTEGRATION = "episodic_integration"
    """Integrate episodic memory records."""
    
    SEMANTIC_INTEGRATION = "semantic_integration"
    """Integrate semantic knowledge."""
    
    AUTOBIOGRAPHICAL_INTEGRATION = "autobiographical_integration"
    """Integrate self-relevant memories."""
    
    RECENT_EXPERIENCE_INTEGRATION = "recent_experience_integration"
    """Integrate recent experiences into broader context."""
    
    # Relationship coordination
    MEMORY_ASSOCIATION = "memory_association"
    """Identify associations between memory records."""
    
    MEMORY_LINKAGE = "memory_linkage"
    """Establish structural links between memories."""
    
    MEMORY_CLUSTERING = "memory_clustering"
    """Group related memories into clusters."""
    
    # Defect analysis
    MEMORY_CONFLICT_ANALYSIS = "memory_conflict_analysis"
    """Analyze contradictions in memory records."""
    
    MEMORY_GAP_ANALYSIS = "memory_gap_analysis"
    """Identify missing or incomplete information."""
    
    MEMORY_DUPLICATION_ANALYSIS = "memory_duplication_analysis"
    """Detect potential duplicate records."""
    
    MEMORY_INCONSISTENCY_ANALYSIS = "memory_inconsistency_analysis"
    """Identify inconsistencies within or across records."""
    
    # Proposal generation
    RETRIEVAL_CUE_GENERATION = "retrieval_cue_generation"
    """Generate proposals for improved future retrieval."""
    
    CONSOLIDATION_CANDIDATE_GENERATION = "consolidation_candidate_generation"
    """Propose opportunities for memory consolidation."""
    
    ABSTRACTION_CANDIDATE_GENERATION = "abstraction_candidate_generation"
    """Propose generalized semantic representations."""
    
    MEMORY_UPDATE_REVIEW = "memory_update_review"
    """Review potential updates to memory records."""
    
    MEMORY_CORRECTION_REVIEW = "memory_correction_review"
    """Review proposed corrections to memory."""
    
    # Integration with other coordination
    IDENTITY_MEMORY_INTEGRATION = "identity_memory_integration"
    """Integrate memories relevant to Identity."""
    
    NARRATIVE_MEMORY_INTEGRATION = "narrative_memory_integration"
    """Integrate memories into Narrative structure."""
    
    REFLECTION_MEMORY_SUPPORT = "reflection_memory_support"
    """Provide memory evidence for reflection."""
    
    SIMULATION_MEMORY_SUPPORT = "simulation_memory_support"
    """Provide memory grounding for simulations."""
    
    PREDICTION_MEMORY_SUPPORT = "prediction_memory_support"
    """Provide historical context for predictions."""
    
    WORKSPACE_MEMORY_PREPARATION = "workspace_memory_preparation"
    """Prepare memories for workspace consideration."""
    
    @classmethod
    def all_purposes(cls) -> Tuple[str, ...]:
        """Return all valid purpose kinds."""
        return (
            cls.CONTEXT_ENRICHMENT,
            cls.GENERAL_MEMORY_INTEGRATION,
            cls.EPISODIC_INTEGRATION,
            cls.SEMANTIC_INTEGRATION,
            cls.AUTOBIOGRAPHICAL_INTEGRATION,
            cls.RECENT_EXPERIENCE_INTEGRATION,
            cls.MEMORY_ASSOCIATION,
            cls.MEMORY_LINKAGE,
            cls.MEMORY_CLUSTERING,
            cls.MEMORY_CONFLICT_ANALYSIS,
            cls.MEMORY_GAP_ANALYSIS,
            cls.MEMORY_DUPLICATION_ANALYSIS,
            cls.MEMORY_INCONSISTENCY_ANALYSIS,
            cls.RETRIEVAL_CUE_GENERATION,
            cls.CONSOLIDATION_CANDIDATE_GENERATION,
            cls.ABSTRACTION_CANDIDATE_GENERATION,
            cls.MEMORY_UPDATE_REVIEW,
            cls.MEMORY_CORRECTION_REVIEW,
            cls.IDENTITY_MEMORY_INTEGRATION,
            cls.NARRATIVE_MEMORY_INTEGRATION,
            cls.REFLECTION_MEMORY_SUPPORT,
            cls.SIMULATION_MEMORY_SUPPORT,
            cls.PREDICTION_MEMORY_SUPPORT,
            cls.WORKSPACE_MEMORY_PREPARATION,
        )
    
    @classmethod
    def requires_factual(cls, purpose: str) -> bool:
        """Check if purpose typically requires factual (not speculative) memories."""
        return purpose in {
            cls.CONTEXT_ENRICHMENT,
            cls.IDENTITY_MEMORY_INTEGRATION,
            cls.NARRATIVE_MEMORY_INTEGRATION,
            cls.MEMORY_CORRECTION_REVIEW,
        }
    
    @classmethod
    def allows_speculative(cls, purpose: str) -> bool:
        """Check if purpose may include speculative content."""
        return purpose in {
            cls.SIMULATION_MEMORY_SUPPORT,
            cls.PREDICTION_MEMORY_SUPPORT,
            cls.ABSTRACTION_CANDIDATE_GENERATION,
        }
    
    @classmethod
    def produces_proposals(cls, purpose: str) -> bool:
        """Check if purpose typically produces proposals."""
        return purpose in {
            cls.RETRIEVAL_CUE_GENERATION,
            cls.CONSOLIDATION_CANDIDATE_GENERATION,
            cls.ABSTRACTION_CANDIDATE_GENERATION,
            cls.MEMORY_UPDATE_REVIEW,
            cls.MEMORY_CORRECTION_REVIEW,
        }


# =============================================================================
# MEMORY INTEGRATION SUBJECT KINDS - What is being integrated
# =============================================================================

class MemoryIntegrationSubjectKind:
    """
    Canonical subject kinds for memory integration episodes.
    
    Each subject defines what the integration episode is addressing.
    """
    
    INTERNAL_CONTEXT = "internal_context"
    """Memory relevant to current InternalContext."""
    
    INTERNAL_EPISODE = "internal_episode"
    """Memory related to a specific InternalEpisode."""
    
    INTERNAL_THOUGHT = "internal_thought"
    """Memory that supports or relates to an internal thought."""
    
    EXECUTION_THREAD = "execution_thread"
    """Memory from or relevant to an ExecutionThread."""
    
    EXECUTION_CYCLE = "execution_cycle"
    """Memory from one finite semantic progression."""
    
    CONVERSATION = "conversation"
    """Memory from a conversation thread."""
    
    TASK = "task"
    """Memory related to a specific task or objective."""
    
    OBJECTIVE = "objective"
    """Memory relevant to achieving an objective."""
    
    DECISION = "decision"
    """Memory supporting or resulting from a decision."""
    
    ACTION = "action"
    """Memory of actions taken and their outcomes."""
    
    OUTCOME = "outcome"
    """Memory of outcome results and evaluations."""
    
    FAILURE = "failure"
    """Memory related to failures or unexpected results."""
    
    SUCCESS = "success"
    """Memory related to successful outcomes."""
    
    REFLECTIVE_PRODUCT = "reflective_product"
    """Memory supporting a reflective product."""
    
    SIMULATION_PRODUCT = "simulation_product"
    """Memory grounding for simulation products."""
    
    NARRATIVE_PRODUCT = "narrative_product"
    """Memory used in narrative construction."""
    
    IDENTITY_PRODUCT = "identity_product"
    """Memory relevant to identity state."""
    
    PREDICTION = "prediction"
    """Memory relevant to a prediction."""
    
    CONCERN = "concern"
    """Memory related to identified concerns."""
    
    MEMORY_CLUSTER = "memory_cluster"
    """Memory related to a proposed or existing cluster."""
    
    MEMORY_RECORD = "memory_record"
    """Specific memory record being reviewed."""
    
    TIME_PERIOD = "time_period"
    """Memory within a specific time range."""
    
    RELATIONSHIP = "relationship"
    """Memory describing a relationship between entities."""
    
    PROJECT = "project"
    """Memory related to a project or long-term effort."""
    
    GENERAL_EXPERIENCE = "general_experience"
    """General experience without specific subject focus."""
    
    @classmethod
    def all_subjects(cls) -> Tuple[str, ...]:
        """Return all valid subject kinds."""
        return (
            cls.INTERNAL_CONTEXT,
            cls.INTERNAL_EPISODE,
            cls.INTERNAL_THOUGHT,
            cls.EXECUTION_THREAD,
            cls.EXECUTION_CYCLE,
            cls.CONVERSATION,
            cls.TASK,
            cls.OBJECTIVE,
            cls.DECISION,
            cls.ACTION,
            cls.OUTCOME,
            cls.FAILURE,
            cls.SUCCESS,
            cls.REFLECTIVE_PRODUCT,
            cls.SIMULATION_PRODUCT,
            cls.NARRATIVE_PRODUCT,
            cls.IDENTITY_PRODUCT,
            cls.PREDICTION,
            cls.CONCERN,
            cls.MEMORY_CLUSTER,
            cls.MEMORY_RECORD,
            cls.TIME_PERIOD,
            cls.RELATIONSHIP,
            cls.PROJECT,
            cls.GENERAL_EXPERIENCE,
        )
    
    @classmethod
    def requires_episodic(cls, subject: str) -> bool:
        """Check if subject typically needs episodic memory."""
        return subject in {
            cls.INTERNAL_EPISODE,
            cls.EXECUTION_THREAD,
            cls.CONVERSATION,
            cls.ACTION,
            cls.FAILURE,
            cls.SUCCESS,
            cls.SIMULATION_PRODUCT,
            cls.NARRATIVE_PRODUCT,
            cls.MEMORY_RECORD,
            cls.TIME_PERIOD,
        }
    
    @classmethod
    def requires_semantic(cls, subject: str) -> bool:
        """Check if subject typically needs semantic memory."""
        return subject in {
            cls.INTERNAL_CONTEXT,
            cls.TASK,
            cls.OBJECTIVE,
            cls.DECISION,
            cls.PREDICTION,
            cls.MEMORY_CLUSTER,
            cls.RELATIONSHIP,
            cls.PROJECT,
        }


# =============================================================================
# RECONSTRUCTION CLASSIFICATION - How memory was obtained
# =============================================================================

class ReconstructionClassification:
    """
    Canonical classifications for how memory content was derived.
    
    These distinguish between direct records and reconstructed representations.
    """
    
    DIRECT_RECORD = "direct_record"
    """Original record as stored."""
    
    SUMMARIZED_RECORD = "summarized_record"
    """Condensed version of original record."""
    
    RECONSTRUCTED_RECORD = "reconstructed_record"
    """Rebuilt from partial evidence (not original)."""
    
    INFERRED_RECONSTRUCTION = "inferred_reconstruction"
    """Reconstruction based on inference and pattern matching."""
    
    HYPOTHETICAL_RECONSTRUCTION = "hypothetical_reconstruction"
    """Reconstruction based on hypothetical scenarios."""
    
    @classmethod
    def all_classifications(cls) -> Tuple[str, ...]:
        """Return all valid reconstruction classifications."""
        return (
            cls.DIRECT_RECORD,
            cls.SUMMARIZED_RECORD,
            cls.RECONSTRUCTED_RECORD,
            cls.INFERRED_RECONSTRUCTION,
            cls.HYPOTHETICAL_RECONSTRUCTION,
        )
    
    @classmethod
    def is_original(cls, classification: str) -> bool:
        """Check if reconstruction classification represents original content."""
        return classification in {
            cls.DIRECT_RECORD,
            cls.SUMMARIZED_RECORD,
        }
    
    @classmethod
    def is_reconstructed(cls, classification: str) -> bool:
        """Check if reconstruction classification represents reconstructed content."""
        return classification in {
            cls.RECONSTRUCTED_RECORD,
            cls.INFERRED_RECONSTRUCTION,
            cls.HYPOTHETICAL_RECONSTRUCTION,
        }


# =============================================================================
# MEMORY PROPOSAL OPERATIONS - What a proposal intends to do
# =============================================================================

class ProposalOperation:
    """
    Canonical operations for memory proposals.
    
    Each operation describes the intended effect on authoritative Memory.
    """
    
    ADD_RECORD = "add_record"
    """Propose adding a new record."""
    
    ADD_LINK = "add_link"
    """Propose adding a structural link between records."""
    
    ADD_SUMMARY = "add_summary"
    """Propose adding or updating a summary."""
    
    ADD_RETRIEVAL_CUE = "add_retrieval_cue"
    """Propose adding a retrieval cue (indexing aid)."""
    
    ADD_PROVENANCE = "add_provenance"
    """Propose adding provenance information."""
    
    ADD_CONFLICT = "add_conflict"
    """Propose recording a conflict."""
    
    ADD_UNCERTAINTY = "add_uncertainty"
    """Propose marking uncertainty on a record."""
    
    REVISE_CONFIDENCE = "revise_confidence"
    """Propose revising confidence level."""
    
    REVISE_FACTUALITY = "revise_factuality"
    """Propose revising factuality classification."""
    
    MARK_SUPERSEDED = "mark_superseded"
    """Propose marking record as superseded."""
    
    MERGE_CANDIDATES = "merge_candidates"
    """Propose merging duplicate candidates."""
    
    SPLIT_CANDIDATE = "split_candidate"
    """Propose splitting a merged candidate."""
    
    CORRECT_REFERENCE = "correct_reference"
    """Propose correcting a reference."""
    
    ARCHIVE_CANDIDATE = "archive_candidate"
    """Propose archiving for retention review."""
    
    DEEMPHASIZE_CANDIDATE = "deemphasize_candidate"
    """Propose reducing retrieval priority."""
    
    @classmethod
    def all_operations(cls) -> Tuple[str, ...]:
        """Return all valid proposal operations."""
        return (
            cls.ADD_RECORD,
            cls.ADD_LINK,
            cls.ADD_SUMMARY,
            cls.ADD_RETRIEVAL_CUE,
            cls.ADD_PROVENANCE,
            cls.ADD_CONFLICT,
            cls.ADD_UNCERTAINTY,
            cls.REVISE_CONFIDENCE,
            cls.REVISE_FACTUALITY,
            cls.MARK_SUPERSEDED,
            cls.MERGE_CANDIDATES,
            cls.SPLIT_CANDIDATE,
            cls.CORRECT_REFERENCE,
            cls.ARCHIVE_CANDIDATE,
            cls.DEEMPHASIZE_CANDIDATE,
        )
    
    @classmethod
    def requires_authority(cls, operation: str) -> bool:
        """Check if operation requires authoritative Memory change."""
        return True  # All proposals ultimately require authority approval


# =============================================================================
# ASSOCIATION KINDS - How memories relate semantically
# =============================================================================

class AssociationKind:
    """
    Canonical association kinds between memory records.
    
    Associations describe semantic relationships, not causal or logical truth.
    """
    
    SEMANTIC_SIMILARITY = "semantic_similarity"
    """Memories share similar concepts or topics."""
    
    TEMPORAL_PROXIMITY = "temporal_proximity"
    """Memories occurred close in time."""
    
    CAUSAL_HYPOTHESIS = "causal_hypothesis"
    """One memory may have caused another (not confirmed)."""
    
    SHARED_SUBJECT = "shared_subject"
    """Both memories involve the same subject."""
    
    SHARED_OBJECTIVE = "shared_objective"
    """Both memories relate to the same objective."""
    
    SHARED_PARTICIPANT = "shared_participant"
    """Both memories involve the same participant."""
    
    SHARED_CONTEXT = "shared_context"
    """Both memories share contextual elements."""
    
    SHARED_OUTCOME = "shared_outcome"
    """Both memories have similar outcomes."""
    
    NARRATIVE_LINK = "narrative_link"
    """Linked in a narrative structure."""
    
    IDENTITY_LINK = "identity_link"
    """Relevant to Identity continuity."""
    
    CONTRAST = "contrast"
    """Memories contrast or differ significantly."""
    
    ANALOGY = "analogy"
    """One memory is analogous to the other."""
    
    GENERALIZATION = "generalization"
    """One memory represents a generalization of the other."""
    
    SPECIALIZATION = "specialization"
    """One memory is a specialization of the other."""
    
    SUPPORTS = "supports"
    """One memory supports the validity of the other."""
    
    CONTRADICTS = "contradicts"
    """Memories contradict each other."""
    
    REFINES = "refines"
    """One memory refines or adds detail to the other."""
    
    SUPERSEDES = "supersedes"
    """One memory supersedes the other."""
    
    UNKNOWN = "unknown"
    """Association kind cannot be determined."""
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid association kinds."""
        return (
            cls.SEMANTIC_SIMILARITY,
            cls.TEMPORAL_PROXIMITY,
            cls.CAUSAL_HYPOTHESIS,
            cls.SHARED_SUBJECT,
            cls.SHARED_OBJECTIVE,
            cls.SHARED_PARTICIPANT,
            cls.SHARED_CONTEXT,
            cls.SHARED_OUTCOME,
            cls.NARRATIVE_LINK,
            cls.IDENTITY_LINK,
            cls.CONTRAST,
            cls.ANALOGY,
            cls.GENERALIZATION,
            cls.SPECIALIZATION,
            cls.SUPPORTS,
            cls.CONTRADICTS,
            cls.REFINES,
            cls.SUPERSEDES,
            cls.UNKNOWN,
        )
    
    @classmethod
    def is_symmetric(cls, kind: str) -> bool:
        """Check if association kind is bidirectional."""
        return kind in {
            cls.SEMANTIC_SIMILARITY,
            cls.TEMPORAL_PROXIMITY,
            cls.SHARED_SUBJECT,
            cls.SHARED_OBJECTIVE,
            cls.SHARED_PARTICIPANT,
            cls.SHARED_CONTEXT,
            cls.CONTRAST,
            cls.ANALOGY,
        }
    
    @classmethod
    def is_supportive(cls, kind: str) -> bool:
        """Check if association kind is supportive."""
        return kind in {
            cls.SEMANTIC_SIMILARITY,
            cls.NARRATIVE_LINK,
            cls.IDENTITY_LINK,
            cls.SUPPORTS,
            cls.GENERALIZATION,
            cls.REFINES,
            cls.SHARED_SUBJECT,
            cls.SHARED_OBJECTIVE,
            cls.SHARED_PARTICIPANT,
            cls.SHARED_CONTEXT,
        }
    
    @classmethod
    def is_contrary(cls, kind: str) -> bool:
        """Check if association kind indicates conflict."""
        return kind in {
            cls.CONTRADICTS,
            cls.CONTRAST,
        }


# =============================================================================
# CONFLICT KINDS - Types of memory conflicts
# =============================================================================

class ConflictKind:
    """
    Canonical conflict kinds between memory records.
    
    A conflict represents incompatible claims that cannot both be true.
    """
    
    SOURCE_CONFLICT = "source_conflict"
    """Records claim different sources for the same event."""
    
    FACTUALITY_CONFLICT = "factuality_conflict"
    """Records have incompatible factuality classifications."""
    
    TEMPORAL_CONFLICT = "temporal_conflict"
    """Records have incompatible temporal relationships."""
    
    EVENT_CONFLICT = "event_conflict"
    """Records describe different events as occurring."""
    
    SEMANTIC_CONFLICT = "semantic_conflict"
    """Records make semantically incompatible claims."""
    
    NARRATIVE_CONFLICT = "narrative_conflict"
    """Records contradict in narrative structure or interpretation."""
    
    IDENTITY_CONFLICT = "identity_conflict"
    """Records conflict on Identity-relevant information."""
    
    PREDICTION_CONFLICT = "prediction_conflict"
    """Conflicting predictions about the same outcome."""
    
    REVISION_CONFLICT = "revision_conflict"
    """Different revision histories for what should be same record."""
    
    RELATIONSHIP_CONFLICT = "relationship_conflict"
    """Conflicts in relationship claims between records."""
    
    AUTHORITY_CONFLICT = "authority_conflict"
    """Conflicting source authority determinations."""
    
    UNKNOWN = "unknown"
    """Conflict kind cannot be determined."""
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid conflict kinds."""
        return (
            cls.SOURCE_CONFLICT,
            cls.FACTUALITY_CONFLICT,
            cls.TEMPORAL_CONFLICT,
            cls.EVENT_CONFLICT,
            cls.SEMANTIC_CONFLICT,
            cls.NARRATIVE_CONFLICT,
            cls.IDENTITY_CONFLICT,
            cls.PREDICTION_CONFLICT,
            cls.REVISION_CONFLICT,
            cls.RELATIONSHIP_CONFLICT,
            cls.AUTHORITY_CONFLICT,
            cls.UNKNOWN,
        )
    
    @classmethod
    def requires_resolution(cls, kind: str) -> bool:
        """Check if conflict kind typically requires resolution."""
        return kind in {
            cls.FACTUALITY_CONFLICT,
            cls.SEMANTIC_CONFLICT,
            cls.EVENT_CONFLICT,
        }


# =============================================================================
# GAP KINDS - Types of memory gaps
# =============================================================================

class GapKind:
    """
    Canonical gap kinds in memory coverage.
    
    A gap represents missing information that would improve understanding.
    """
    
    MISSING_EVENT = "missing_event"
    """An event is expected but not recorded."""
    
    MISSING_CONTEXT = "missing_context"
    """Context needed to understand a record is missing."""
    
    MISSING_SOURCE = "missing_source"
    """Source of information cannot be identified."""
    
    MISSING_OUTCOME = "missing_outcome"
    """Outcome of an action or decision is unknown."""
    
    MISSING_RELATION = "missing_relation"
    """Relationship between entities is unclear."""
    
    MISSING_TEMPORAL_LINK = "missing_temporal_link"
    """Temporal ordering of events is unclear."""
    
    MISSING_PARTICIPANT = "missing_participant"
    """Participant in an event is not identified."""
    
    MISSING_IDENTITY_LINK = "missing_identity_link"
    """Identity-relevant connection cannot be made."""
    
    MISSING_NARRATIVE_LINK = "missing_narrative_link"
    """Narrative connection between events is unclear."""
    
    MISSING_PROVENANCE = "missing_provenance"
    """Provenance information cannot be determined."""
    
    MISSING_REVISION = "missing_revision"
    """Revision history cannot be established."""
    
    UNKNOWN = "unknown"
    """Gap kind cannot be determined."""
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid gap kinds."""
        return (
            cls.MISSING_EVENT,
            cls.MISSING_CONTEXT,
            cls.MISSING_SOURCE,
            cls.MISSING_OUTCOME,
            cls.MISSING_RELATION,
            cls.MISSING_TEMPORAL_LINK,
            cls.MISSING_PARTICIPANT,
            cls.MISSING_IDENTITY_LINK,
            cls.MISSING_NARRATIVE_LINK,
            cls.MISSING_PROVENANCE,
            cls.MISSING_REVISION,
            cls.UNKNOWN,
        )
    
    @classmethod
    def indicates_completeness_issue(cls, kind: str) -> bool:
        """Check if gap kind indicates record incompleteness."""
        return kind in {
            cls.MISSING_EVENT,
            cls.MISSING_CONTEXT,
            cls.MISSING_SOURCE,
            cls.MISSING_OUTCOME,
        }


# =============================================================================
# CONSOLIDATION KINDS - Types of memory consolidation proposals
# =============================================================================

class ConsolidationKind:
    """
    Canonical consolidation kinds for memory records.
    
    Consolidation transforms multiple records into more efficient representations.
    """
    
    EPISODE_SUMMARY = "episode_summary"
    """Consolidate an episode into a summary."""
    
    SEMANTIC_EXTRACTION = "semantic_extraction"
    """Extract general knowledge from specific instances."""
    
    AUTOBIOGRAPHICAL_LINK = "autobiographical_link"
    """Link self-relevant memories for continuity."""
    
    PATTERN_CONSOLIDATION = "pattern_consolidation"
    """Consolidate recurring patterns into a single representation."""
    
    PROCEDURAL_EXTRACTION = "procedural_extraction"
    """Extract procedural knowledge from episodic instances."""
    
    MEMORY_CLUSTER = "memory_cluster"
    """Create or refine a memory cluster."""
    
    DUPLICATE_REDUCTION = "duplicate_reduction"
    """Reduce duplicate or near-duplicate records."""
    
    NARRATIVE_SUMMARY = "narrative_summary"
    """Consolidate narrative elements into cohesive structure."""
    
    IDENTITY_RELEVANT_SUMMARY = "identity_relevant_summary"
    """Consolidate identity-relevant information."""
    
    RETRIEVAL_INDEX_CANDIDATE = "retrieval_index_candidate"
    """Propose record as indexing candidate for faster retrieval."""
    
    UNKNOWN = "unknown"
    """Consolidation kind cannot be determined."""
    
    @classmethod
    def all_kinds(cls) -> Tuple[str, ...]:
        """Return all valid consolidation kinds."""
        return (
            cls.EPISODE_SUMMARY,
            cls.SEMANTIC_EXTRACTION,
            cls.AUTOBIOGRAPHICAL_LINK,
            cls.PATTERN_CONSOLIDATION,
            cls.PROCEDURAL_EXTRACTION,
            cls.MEMORY_CLUSTER,
            cls.DUPLICATE_REDUCTION,
            cls.NARRATIVE_SUMMARY,
            cls.IDENTITY_RELEVANT_SUMMARY,
            cls.RETRIEVAL_INDEX_CANDIDATE,
            cls.UNKNOWN,
        )
    
    @classmethod
    def may_lose_information(cls, kind: str) -> bool:
        """Check if consolidation kind may result in information loss."""
        return kind not in {
            cls.MEMORY_CLUSTER,
            cls.RETRIEVAL_INDEX_CANDIDATE,
        }