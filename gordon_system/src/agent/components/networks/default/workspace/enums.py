# Workspace Integration Enums
# ============================

"""
Canonical enum definitions for workspace integration.

ARCHITECTURAL PRINCIPLES:
    - All enums are simple string constants
    - No runtime dependencies
    - Deeply immutable
"""

from __future__ import annotations


# =============================================================================
# WORKSPACE INTEGRATION PURPOSE KINDS
# =============================================================================

class WorkspaceIntegrationPurposeKind:
    """
    Canonical purpose kinds for workspace integration episodes.
    
    Each purpose kind determines what operations are valid, what source
    products may be used, and what output is expected.
    """
    
    PREPARE_CANDIDATE = "prepare_candidate"
    """Prepare a new workspace candidate from internal content."""
    
    REVISE_CANDIDATE = "revise_candidate"
    """Revise an existing workspace candidate."""
    
    RESUBMIT_CANDIDATE = "resubmit_candidate"
    """Resubmit a previously submitted candidate with modifications."""
    
    WITHDRAW_CANDIDATE = "withdraw_candidate"
    """Propose withdrawal of an existing candidate."""
    
    MERGE_CANDIDATES = "merge_candidates"
    """Merge multiple candidates into one."""
    
    SPLIT_CANDIDATE = "split_candidate"
    """Split a candidate into multiple candidates."""
    
    DEDUPLICATE_CANDIDATES = "deduplicate_candidates"
    """Analyze and resolve duplicate candidates."""
    
    ASSESS_CANDIDATE_VALUE = "assess_candidate_value"
    """Assess the value of an existing candidate."""
    
    ASSESS_CANDIDATE_DISCLOSURE = "assess_candidate_disclosure"
    """Assess disclosure requirements for a candidate."""
    
    ASSESS_CANDIDATE_AUDIENCE = "assess_candidate_audience"
    """Assess audience recommendations for a candidate."""
    
    ASSESS_CANDIDATE_CONFLICT = "assess_candidate_conflict"
    """Identify conflicts involving a candidate."""
    
    PROCESS_ADMISSION_DECISION = "process_admission_decision"
    """Process external admission decision feedback."""
    
    PROCESS_REJECTION = "process_rejection"
    """Process rejection feedback for a candidate."""
    
    PROCESS_DEFERRAL = "process_deferral"
    """Process deferral feedback for a candidate."""
    
    PROCESS_REVISION_REQUEST = "process_revision_request"
    """Process revision request from external authority."""
    
    PROCESS_BROADCAST_FEEDBACK = "process_broadcast_feedback"
    """Process broadcast result feedback."""
    
    PROCESS_CONSUMPTION_FEEDBACK = "process_consumption_feedback"
    """Process consumption feedback."""
    
    PREPARE_EXECUTIVE_REVIEW_CANDIDATE = "prepare_executive_review_candidate"
    """Prepare candidate requiring Executive review."""
    
    PREPARE_ATTENTION_REVIEW_CANDIDATE = "prepare_attention_review_candidate"
    """Prepare candidate requiring attention assessment."""
    
    PREPARE_GENERAL_WORKSPACE_CANDIDATE = "prepare_general_workspace_candidate"
    """General workspace candidate preparation."""


# =============================================================================
# WORKSPACE INTEGRATION SUBJECT KINDS
# =============================================================================

class WorkspaceIntegrationSubjectKind:
    """
    Canonical subject kinds for workspace integration episodes.
    
    Each subject kind represents what is being proposed to the workspace.
    """
    
    INTERNAL_THOUGHT = "internal_thought"
    """An internally generated thought."""
    
    REFLECTIVE_PRODUCT = "reflective_product"
    """A product from reflection coordination."""
    
    SIMULATION_PRODUCT = "simulation_product"
    """A product from simulation coordination."""
    
    COUNTERFACTUAL_PRODUCT = "counterfactual_product"
    """A counterfactual simulation product."""
    
    NARRATIVE_PRODUCT = "narrative_product"
    """A narrative integration product."""
    
    IDENTITY_PRODUCT = "identity_product"
    """An identity integration product."""
    
    MEMORY_PRODUCT = "memory_product"
    """A memory integration product."""
    
    PREDICTIVE_PRODUCT = "predictive_product"
    """A predictive integration product."""
    
    INTERNAL_EPISODE = "internal_episode"
    """An internal episode summary or outcome."""
    
    CONCERN = "concern"
    """An internally generated concern."""
    
    CONTRADICTION = "contradiction"
    """A detected contradiction."""
    
    QUESTION = "question"
    """An important question for review."""
    
    INSIGHT = "insight"
    """A validated insight."""
    
    RISK = "risk"
    """A risk forecast or concern."""
    
    OPPORTUNITY = "opportunity"
    """An opportunity forecast."""
    
    GOAL_PROPOSAL = "goal_proposal"
    """A proposed goal for review."""
    
    COMMITMENT_REVIEW = "commitment_review"
    """A commitment requiring review."""
    
    AUTHORITY_REVIEW = "authority_review"
    """An authority requirement for review."""
    
    SYSTEM_CONDITION = "system_condition"
    """Important system state or condition."""
    
    GENERAL_INTERNAL_CONTENT = "general_internal_content"
    """General internal semantic content."""


# =============================================================================
# WORKSPACE SOURCE PRODUCT KINDS
# =============================================================================

class WorkspaceSourceProductKind:
    """
    Canonical source product kinds that may be referenced by workspace candidates.
    
    Every source reference must preserve origin information without embedding
    live objects.
    """
    
    INTERNAL_THOUGHT = "internal_thought"
    """An InternalThought instance."""
    
    REFLECTION = "reflection"
    """A reflection coordination product."""
    
    SIMULATION = "simulation"
    """A simulation coordination product."""
    
    COUNTERFACTUAL = "counterfactual"
    """A counterfactual coordination product."""
    
    NARRATIVE = "narrative"
    """A narrative integration product."""
    
    IDENTITY = "identity"
    """An identity integration product."""
    
    MEMORY = "memory"
    """A memory integration product."""
    
    PREDICTION = "prediction"
    """A predictive integration product."""
    
    EXECUTION_OUTCOME = "execution_outcome"
    """An execution outcome."""
    
    OBSERVATION = "observation"
    """An external or internal observation."""
    
    ATTENTION_ASSESSMENT = "attention_assessment"
    """An attention assessment result."""
    
    OTHER_NETWORK_PRODUCT = "other_network_product"
    """A product from another network."""
    
    UNKNOWN = "unknown"
    """Unknown or unspecified source."""


# =============================================================================
# WORKSPACE CANDIDATE KINDS
# =============================================================================

class WorkspaceCandidateKind:
    """
    Canonical workspace candidate kinds.
    
    Each kind represents a category of semantic content that may be proposed
    for workspace admission.
    """
    
    INSIGHT = "insight"
    """A validated insight."""
    
    CONTRADICTION = "contradiction"
    """A detected contradiction between beliefs or facts."""
    
    QUESTION = "question"
    """An important question requiring review."""
    
    CONCERN = "concern"
    """An internally generated concern."""
    
    RISK = "risk"
    """A risk forecast or concern."""
    
    OPPORTUNITY = "opportunity"
    """An opportunity forecast."""
    
    PREDICTION = "prediction"
    """A predictive statement."""
    
    PREDICTION_ERROR = "prediction_error"
    """A prediction that did not match observed outcomes."""
    
    EXPECTATION_VIOLATION = "expectation_violation"
    """Expected outcome was not achieved."""
    
    SIMULATION_RESULT = "simulation_result"
    """A simulation or prospective analysis result."""
    
    COUNTERFACTUAL_RESULT = "counterfactual_result"
    """A counterfactual analysis result."""
    
    NARRATIVE_DISCONTINUITY = "narrative_discontinuity"
    """A break in narrative continuity."""
    
    IDENTITY_CONFLICT = "identity_conflict"
    """A conflict in identity commitments or values."""
    
    MEMORY_CONFLICT = "memory_conflict"
    """A conflict between memory projections."""
    
    MEMORY_GAP = "memory_gap"
    """An important missing information gap."""
    
    GOAL_PROPOSAL = "goal_proposal"
    """A proposed goal for commitment."""
    
    PLAN_REVIEW_PROPOSAL = "plan_review_proposal"
    """A proposal to review or revise a plan."""
    
    COMMITMENT_REVIEW_PROPOSAL = "commitment_review_proposal"
    """A proposal to review commitments."""
    
    AUTHORITY_REVIEW_REQUEST = "authority_review_request"
    """A request for authority review."""
    
    CAPABILITY_LIMITATION = "capability_limitation"
    """Identified capability limitation."""
    
    SYSTEM_LIMITATION = "system_limitation"
    """Identified system-level limitation."""
    
    INTERNAL_STATE_CHANGE = "internal_state_change"
    """Significant internal state change."""
    
    EXECUTIVE_REVIEW_ITEM = "executive_review_item"
    """Item requiring Executive review."""
    
    ATTENTION_REVIEW_ITEM = "attention_review_item"
    """Item requiring attention assessment."""
    
    GENERAL_SEMANTIC_CONTENT = "general_semantic_content"
    """General semantic content without specific classification."""


# =============================================================================
# WORKSPACE CANDIDATE PURPOSE
# =============================================================================

class WorkspaceCandidatePurpose:
    """
    Canonical purposes for workspace candidates.
    
    Purpose defines why the candidate is being proposed, not what it contains.
    """
    
    INFORM = "inform"
    """Inform workspace consumers of information."""
    
    WARN = "warn"
    """Warn about a potential issue or risk."""
    
    REQUEST_REVIEW = "request_review"
    """Request review by consumers."""
    
    REQUEST_DECISION = "request_decision"
    """Request a decision from consumers."""
    
    REQUEST_CLARIFICATION = "request_clarification"
    """Request clarification or additional information."""
    
    REQUEST_EVIDENCE = "request_evidence"
    """Request additional evidence be gathered."""
    
    REQUEST_COORDINATION = "request_coordination"
    """Request coordination across systems."""
    
    SURFACE_CONFLICT = "surface_conflict"
    """Surface a conflict for resolution."""
    
    SURFACE_GAP = "surface_gap"
    """Surface an important gap in knowledge or understanding."""
    
    SURFACE_RISK = "surface_risk"
    """Surface a potential risk."""
    
    SURFACE_OPPORTUNITY = "surface_opportunity"
    """Surface an opportunity for consideration."""
    
    PROPOSE_GOAL = "propose_goal"
    """Propose a new goal."""
    
    PROPOSE_TASK = "propose_task"
    """Propose a new task or action."""
    
    PROPOSE_REVISION = "propose_revision"
    """Propose revision of existing content."""
    
    SUPPORT_ACTIVE_WORK = "support_active_work"
    """Support currently active work."""
    
    SUPPORT_FUTURE_WORK = "support_future_work"
    """Support future work or planning."""
    
    PRESERVE_TEMPORARY_AVAILABILITY = "preserve_temporary_availability"
    """Preserve content temporarily in workspace."""
    
    GENERAL_AVAILABILITY = "general_availability"
    """Make content generally available."""


# =============================================================================
# WORKSPACE AUDIENCE KINDS
# =============================================================================

class WorkspaceAudienceKind:
    """
    Canonical audience kinds for workspace candidate recommendations.
    
    These are advisory recommendations only. They do not perform routing.
    """
    
    EXECUTIVE = "executive"
    """Executive decision-makers."""
    
    ATTENTION = "attention"
    """Attention and focus mechanisms."""
    
    ALERTING = "alerting"
    """Alerting systems."""
    
    FOCUSING = "focusing"
    """Focusing mechanisms."""
    
    WORKING_MEMORY = "working_memory"
    """Working memory systems."""
    
    PLANNING = "planning"
    """Planning systems."""
    
    REASONING = "reasoning"
    """Reasoning systems."""
    
    REFLECTION = "reflection"
    """Reflection systems."""
    
    MEMORY = "memory"
    """Memory systems."""
    
    NARRATIVE = "narrative"
    """Narrative integration systems."""
    
    IDENTITY = "identity"
    """Identity integration systems."""
    
    PREDICTION = "prediction"
    """Prediction systems."""
    
    MONITORING = "monitoring"
    """Monitoring systems."""
    
    CONVERSATION = "conversation"
    """Conversation and communication systems."""
    
    EXECUTION = "execution"
    """Execution systems."""
    
    SYSTEM_DIAGNOSTICS = "system_diagnostics"
    """System diagnostics and debugging."""
    
    AUTHORIZED_GENERAL_CONSUMERS = "authorized_general_consumers"
    """Authorized general consumers."""


# =============================================================================
# WORKSPACE ACCESS CLASSIFICATIONS
# =============================================================================

class WorkspaceAccessClassification:
    """
    Canonical access classifications for workspace candidates.
    
    Access classification is advisory. The workspace and security authorities
    enforce actual access control.
    """
    
    INTERNAL_GENERAL = "internal_general"
    """General internal availability."""
    
    INTERNAL_RESTRICTED = "internal_restricted"
    """Restricted internal availability."""
    
    EXECUTIVE_ONLY = "executive_only"
    """Executive authority only."""
    
    ATTENTION_ONLY = "attention_only"
    """Attention mechanism only."""
    
    IDENTITY_RESTRICTED = "identity_restricted"
    """Identity authority restricted."""
    
    MEMORY_RESTRICTED = "memory_restricted"
    """Memory authority restricted."""
    
    SECURITY_RESTRICTED = "security_restricted"
    """Security authority restricted."""
    
    PARTICIPANT_SCOPED = "participant_scoped"
    """Scoped to specific participants."""
    
    TASK_SCOPED = "task_scoped"
    """Scoped to specific tasks."""
    
    THREAD_SCOPED = "thread_scoped"
    """Scoped to specific threads."""
    
    DIAGNOSTIC_ONLY = "diagnostic_only"
    """Diagnostic systems only."""
    
    NON_DISCLOSABLE = "non_disclosable"
    """Non-disclosable content."""


# =============================================================================
# WORKSPACE DISCLOSURE CLASSIFICATIONS
# =============================================================================

class WorkspaceDisclosureClassification:
    """
    Canonical disclosure classifications for workspace candidates.
    
    Disclosure classification determines external disclosability. Internal
    availability does not imply external disclosability.
    """
    
    INTERNAL_ONLY = "internal_only"
    """Internal only, no external disclosure."""
    
    EXTERNALLY_RENDERABLE_AFTER_REVIEW = "externally_renderable_after_review"
    """May be externally rendered after review."""
    
    PARTICIPANT_SCOPED = "participant_scoped"
    """Disclosable to participants in scope."""
    
    USER_DISCLOSABLE = "user_disclosable"
    """Disclosable to users."""
    
    DEVELOPER_DISCLOSABLE = "developer_disclosable"
    """Disclosable to developers."""
    
    CONFIDENTIAL = "confidential"
    """Confidential internal use only."""
    
    SECURITY_SENSITIVE = "security_sensitive"
    """Security-sensitive content."""
    
    IDENTITY_SENSITIVE = "identity_sensitive"
    """Identity-sensitive content."""
    
    MEMORY_SENSITIVE = "memory_sensitive"
    """Memory-sensitive content."""
    
    PROHIBITED_FROM_EXTERNAL_DISCLOSURE = "prohibited_from_external_disclosure"
    """External disclosure prohibited."""


# =============================================================================
# WORKSPACE CANDIDATE LIFETIME CLASSIFICATIONS
# =============================================================================

class WorkspaceCandidateLifetime:
    """
    Canonical lifetime classifications for workspace candidates.
    
    Lifetime is advisory. External authorities enforce actual lifecycle.
    """
    
    TRANSIENT = "transient"
    """Very short-lived, may be discarded immediately after review."""
    
    CYCLE_BOUND = "cycle_bound"
    """Valid only for the current ExecutionCycle."""
    
    EPISODE_BOUND = "episode_bound"
    """Valid for the duration of an InternalEpisode."""
    
    THREAD_BOUND = "thread_bound"
    """Valid for the duration of a Thread."""
    
    OBJECTIVE_BOUND = "objective_bound"
    """Valid until objective completion or change."""
    
    EVENT_BOUND = "event_bound"
    """Valid for a specific event window."""
    
    TIME_BOUND = "time_bound"
    """Valid for a specific time period."""
    
    UNTIL_REVIEWED = "until_reviewed"
    """Valid until reviewed by consumers."""
    
    UNTIL_RESOLVED = "until_resolved"
    """Valid until issue is resolved."""
    
    UNTIL_SUPERSEDED = "until_superseded"
    """Valid until superseded by newer content."""
    
    PERSISTENCE_REVIEW_REQUIRED = "persistence_review_required"
    """Requires explicit review for persistence beyond transient state."""


# =============================================================================
# WORKSPACE PERSISTENCE RECOMMENDATIONS
# =============================================================================

class WorkspacePersistenceRecommendation:
    """
    Canonical persistence recommendations for workspace candidates.
    
    Persistence is advisory. Memory authority determines actual storage.
    """
    
    DO_NOT_PERSIST = "do_not_persist"
    """Do not persist beyond transient state."""
    
    PRESERVE_TRANSIENTLY = "preserve_transiently"
    """Preserve temporarily in transient storage."""
    
    PRESERVE_UNTIL_CONSUMED = "preserve_until_consumed"
    """Preserve until consumed by authorized consumers."""
    
    PRESERVE_UNTIL_RESOLVED = "preserve_until_resolved"
    """Preserve until related issue is resolved."""
    
    PRESERVE_UNTIL_SUPERSEDED = "preserve_until_superseded"
    """Preserve until superseded by newer content."""
    
    PROPOSE_MEMORY_RETENTION = "propose_memory_retention"
    """Propose for long-term memory retention."""
    
    REVIEW_REQUIRED = "review_required"
    """Requires explicit review before persistence."""


# =============================================================================
# WORKSPACE CANDIDATE CONFLICT KINDS
# =============================================================================

class ConflictKind:
    """
    Canonical conflict kinds between workspace candidates.
    """
    
    CONTENT_CONFLICT = "content_conflict"
    """Conflicting semantic content."""
    
    FACTUALITY_CONFLICT = "factuality_conflict"
    """Conflicting factuality assessments."""
    
    PURPOSE_CONFLICT = "purpose_conflict"
    """Incompatible purposes."""
    
    AUDIENCE_CONFLICT = "audience_conflict"
    """Conflicting audience recommendations."""
    
    DISCLOSURE_CONFLICT = "disclosure_conflict"
    """Conflicting disclosure classifications."""
    
    ACCESS_CONFLICT = "access_conflict"
    """Conflicting access classifications."""
    
    LIFETIME_CONFLICT = "lifetime_conflict"
    """Conflicting lifetime requirements."""
    
    SOURCE_CONFLICT = "source_conflict"
    """Incompatible source origins."""
    
    REVISION_CONFLICT = "revision_conflict"
    """Conflicting revision states."""
    
    PRIORITY_CONFLICT = "priority_conflict"
    """Conflicting priority recommendations."""
    
    POLICY_CONFLICT = "policy_conflict"
    """Policy violation conflict."""
    
    SECURITY_CONFLICT = "security_conflict"
    """Security concern conflict."""
    
    UNKNOWN = "unknown"
    """Unknown or unspecified conflict kind."""


# =============================================================================
# WORKSPACE CANDIDATE DUPLICATE ASSESSMENT KINDS
# =============================================================================

class DuplicateAssessmentKind:
    """
    Canonical duplicate assessment kinds for workspace candidates.
    """
    
    DISTINCT = "distinct"
    """Candidates are distinct."""
    
    RELATED = "related"
    """Related but not duplicates."""
    
    POSSIBLE_DUPLICATE = "possible_duplicate"
    """May be a duplicate, needs verification."""
    
    PROBABLE_DUPLICATE = "probable_duplicate"
    """Likely a duplicate."""
    
    REVISION_OF_EXISTING = "revision_of_existing"
    """A revision of an existing candidate."""
    
    SUPERSEDES_EXISTING = "supersedes_existing"
    """Supersedes an existing candidate."""


# =============================================================================
# WORKSPACE ADMISSION DECISION KINDS
# =============================================================================

class WorkspaceAdmissionDecisionKind:
    """
    Canonical admission decision kinds from workspace authority.
    """
    
    ACCEPT = "accept"
    """Candidate accepted."""
    
    ACCEPT_WITH_CONSTRAINTS = "accept_with_constraints"
    """Candidate accepted with constraints."""
    
    REJECT = "reject"
    """Candidate rejected."""
    
    DEFER = "defer"
    """Admission deferred to later time."""
    
    REQUEST_REVISION = "request_revision"
    """Revision requested before resubmission."""
    
    REQUEST_MORE_EVIDENCE = "request_more_evidence"
    """Additional evidence required."""
    
    DUPLICATE_OF_EXISTING = "duplicate_of_existing"
    """Candidate is duplicate of existing workspace content."""
    
    CONFLICT_WITH_EXISTING = "conflict_with_existing"
    """Candidate conflicts with existing workspace content."""
    
    CAPACITY_UNAVAILABLE = "capacity_unavailable"
    """Workspace capacity unavailable."""
    
    ACCESS_DENIED = "access_denied"
    """Access denied for requested classification."""
    
    DISCLOSURE_RESTRICTED = "disclosure_restricted"
    """Disclosure restrictions prevent admission."""
    
    EXPIRED = "expired"
    """Candidate has expired."""
    
    WITHDRAWN = "withdrawn"
    """Candidate was withdrawn by proposer."""


# =============================================================================
# WORKSPACE INTEGRATION OUTCOME KINDS
# =============================================================================

class WorkspaceIntegrationOutcomeKind:
    """
    Canonical outcome kinds for workspace integration episodes.
    """
    
    CANDIDATE_PREPARED = "candidate_prepared"
    """Workspace candidate prepared."""
    
    SUBMISSION_PROPOSED = "submission_proposed"
    """Submission proposal created."""
    
    CANDIDATE_ACCEPTED_EXTERNALLY = "candidate_accepted_externally"
    """Candidate accepted by external authority."""
    
    CANDIDATE_ACCEPTED_WITH_CONSTRAINTS_EXTERNALLY = "candidate_accepted_with_constraints_externally"
    """Candidate accepted with constraints by external authority."""
    
    CANDIDATE_REJECTED_EXTERNALLY = "candidate_rejected_externally"
    """Candidate rejected by external authority."""
    
    CANDIDATE_DEFERRED_EXTERNALLY = "candidate_deferred_externally"
    """Admission deferred by external authority."""
    
    CANDIDATE_REVISION_REQUESTED_EXTERNALLY = "candidate_revision_requested_externally"
    """Revision requested by external authority."""
    
    CANDIDATE_REVISED = "candidate_revised"
    """Candidate revised based on feedback."""
    
    CANDIDATE_WITHDRAWAL_PROPOSED = "candidate_withdrawal_proposed"
    """Withdrawal proposal created."""
    
    DUPLICATE_IDENTIFIED = "duplicate_identified"
    """Duplicate candidate identified."""
    
    CONFLICT_IDENTIFIED = "conflict_identified"
    """Conflict identified."""
    
    BROADCAST_FEEDBACK_PROCESSED = "broadcast_feedback_processed"
    """Broadcast feedback processed."""
    
    CONSUMPTION_FEEDBACK_PROCESSED = "consumption_feedback_processed"
    """Consumption feedback processed."""
    
    PARTIALLY_COMPLETED = "partially_completed"
    """Episode partially completed with some products."""
    
    INSUFFICIENT_CONTEXT = "insufficient_context"
    """Insufficient context to proceed."""
    
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    """Insufficient evidence for candidate."""
    
    NO_MEANINGFUL_RESULT = "no_meaningful_result"
    """No meaningful result produced."""
    
    UNRESOLVED = "unresolved"
    """Episode ended without resolution."""
    
    FAILED = "failed"
    """Episode failed."""
    
    CANCELLED = "cancelled"
    """Episode cancelled."""
    
    EXPIRED = "expired"
    """Episode expired before completion."""


# =============================================================================
# WORKSPACE INTEGRATION CONTINUATION KINDS
# =============================================================================

class WorkspaceIntegrationContinuationKind:
    """
    Canonical continuation recommendations for workspace integration episodes.
    """
    
    COMPLETE = "complete"
    """Episode completed successfully."""
    
    CONTINUE_CANDIDATE_PREPARATION = "continue_candidate_preparation"
    """Continue preparing candidate."""
    
    REQUEST_CONTEXT_REFRESH = "request_context_refresh"
    """Request context refresh."""
    
    REQUEST_ADDITIONAL_EVIDENCE = "request_additional_evidence"
    """Request additional evidence be gathered."""
    
    REQUEST_SOURCE_PRODUCT_REFRESH = "request_source_product_refresh"
    """Request source product refresh."""
    
    REQUEST_DISCLOSURE_REVIEW = "request_disclosure_review"
    """Request disclosure classification review."""
    
    REQUEST_SECURITY_REVIEW = "request_security_review"
    """Request security review."""
    
    REQUEST_EXECUTIVE_REVIEW = "request_executive_review"
    """Request Executive review."""
    
    REQUEST_ATTENTION_REVIEW = "request_attention_review"
    """Request attention assessment review."""
    
    REQUEST_CANDIDATE_REVISION = "request_candidate_revision"
    """Request candidate revision."""
    
    REQUEST_CANDIDATE_SPLIT = "request_candidate_split"
    """Request candidate be split."""
    
    REQUEST_CANDIDATE_MERGE = "request_candidate_merge"
    """Request candidate merge."""
    
    WAIT_FOR_ADMISSION_DECISION = "wait_for_admission_decision"
    """Wait for external admission decision."""
    
    WAIT_FOR_WORKSPACE_FEEDBACK = "wait_for_workspace_feedback"
    """Wait for workspace feedback."""
    
    PREPARE_RESUBMISSION = "prepare_resubmission"
    """Prepare resubmission after revision."""
    
    PREPARE_WITHDRAWAL = "prepare_withdrawal"
    """Prepare withdrawal proposal."""
    
    SUSPEND = "suspend"
    """Suspend episode temporarily."""
    
    FAIL = "fail"
    """Episode should fail."""
    
    CANCEL = "cancel"
    """Episode should be cancelled."""


# =============================================================================
# WORKSPACE COORDINATION STEP KINDS
# =============================================================================

class WorkspaceCoordinationStepKind:
    """
    Canonical coordination step kinds for workspace integration plans.
    """
    
    VALIDATE_CONTEXT = "validate_context"
    """Validate bound context."""
    
    VALIDATE_SUBJECT = "validate_subject"
    """Validate subject references."""
    
    VALIDATE_SOURCE_PRODUCTS = "validate_source_products"
    """Validate source product references."""
    
    NORMALIZE_SOURCE_OWNERSHIP = "normalize_source_ownership"
    """Normalize source ownership information."""
    
    NORMALIZE_SOURCE_REVISION = "normalize_source_revision"
    """Normalize source revision information."""
    
    NORMALIZE_FACTUALITY = "normalize_factuality"
    """Normalize factuality assessments."""
    
    NORMALIZE_PROVENANCE = "normalize_provenance"
    """Normalize provenance records."""
    
    EXTRACT_CANDIDATE_CONTENT = "extract_candidate_content"
    """Extract candidate semantic content."""
    
    CLASSIFY_CANDIDATE = "classify_candidate"
    """Classify candidate kind and purpose."""
    
    ASSESS_VALUE = "assess_value"
    """Assess candidate value."""
    
    ASSESS_RELEVANCE = "assess_relevance"
    """Assess candidate relevance."""
    
    ASSESS_URGENCY = "assess_urgency"
    """Assess candidate urgency."""
    
    ASSESS_IMPORTANCE = "assess_importance"
    """Assess candidate importance."""
    
    ASSESS_NOVELTY = "assess_novelty"
    """Assess candidate novelty."""
    
    ASSESS_CONFIDENCE = "assess_confidence"
    """Assess candidate confidence."""
    
    ASSESS_RISK = "assess_risk"
    """Assess candidate risk."""
    
    RECOMMEND_AUDIENCE = "recommend_audience"
    """Recommend candidate audience."""
    
    RECOMMEND_ACCESS = "recommend_access"
    """Recommend candidate access classification."""
    
    RECOMMEND_DISCLOSURE = "recommend_disclosure"
    """Recommend candidate disclosure classification."""
    
    RECOMMEND_LIFETIME = "recommend_lifetime"
    """Recommend candidate lifetime."""
    
    ASSESS_CAPACITY_COST = "assess_capacity_cost"
    """Assess capacity cost of candidate."""
    
    DETECT_DUPLICATES = "detect_duplicates"
    """Detect duplicate candidates."""
    
    DETECT_CONFLICTS = "detect_conflicts"
    """Detect conflicts involving candidate."""
    
    PREPARE_COMPETITION_PROJECTION = "prepare_competition_projection"
    """Prepare competition projection."""
    
    VALIDATE_CANDIDATE = "validate_candidate"
    """Validate candidate structure and constraints."""
    
    PREPARE_SUBMISSION = "prepare_submission"
    """Prepare submission proposal."""
    
    PROCESS_ADMISSION_DECISION = "process_admission_decision"
    """Process admission decision feedback."""
    
    PROCESS_REJECTION = "process_rejection"
    """Process rejection feedback."""
    
    PROCESS_DEFERRAL = "process_deferral"
    """Process deferral feedback."""
    
    PROCESS_REVISION_REQUEST = "process_revision_request"
    """Process revision request."""
    
    PROCESS_BROADCAST_FEEDBACK = "process_broadcast_feedback"
    """Process broadcast feedback."""
    
    PROCESS_CONSUMPTION_FEEDBACK = "process_consumption_feedback"
    """Process consumption feedback."""
    
    PREPARE_REVISION = "prepare_revision"
    """Prepare candidate revision proposal."""
    
    PREPARE_WITHDRAWAL = "prepare_withdrawal"
    """Prepare candidate withdrawal proposal."""
    
    COMPOSE_OUTCOME = "compose_outcome"
    """Compose final outcome."""