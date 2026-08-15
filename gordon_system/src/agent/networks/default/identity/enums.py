# Identity Integration Enums - Canonical Vocabulary
# ==================================================

"""
Canonical enums and type aliases for identity integration.

This module defines all typed categories used throughout the identity integration
coordination layer. Every enum represents a canonical vocabulary term that must
be respected by all implementations.

ARCHITECTURAL PRINCIPLES:
    • All enums are frozen (immutable at runtime)
    • No business logic in enums (pure value containers)
    • Human-readable names for diagnostics
    • Explicit, bounded categories only

PHASE: 4.3.8
"""

from __future__ import annotations

from enum import Enum, auto


# =============================================================================
# IDENTITY INTEGRATION PURPOSE - What identity integration is trying to accomplish
# =============================================================================

class IdentityIntegrationPurposeKind(Enum):
    """
    Canonical purpose kinds for identity integration.
    
    Purpose determines:
        • Required projections
        • Valid source types
        • Required confidence thresholds
        • Completion rules
        • Recursive-review limits
    """
    # Self-model review and assessment
    SELF_MODEL_REVIEW = "self_model_review"
    """Review and assess the current self-model for consistency."""
    
    IDENTITY_CONTINUITY_REVIEW = "identity_continuity_review"
    """Assess continuity across identity revisions."""
    
    ROLE_INTEGRATION = "role_integration"
    """Integrate roles into current context and identity."""
    
    VALUE_INTEGRATION = "value_integration"
    """Evaluate alignment between behavior and accepted values."""
    
    COMMITMENT_INTEGRATION = "commitment_integration"
    """Assess commitments against current capabilities and limitations."""
    
    CAPABILITY_SELF_ASSESSMENT = "capability_self_assessment"
    """Evaluate capability claims against observed performance."""
    
    LIMITATION_INTEGRATION = "limitation_integration"
    """Integrate known limitations into self-representation."""
    
    AUTOBIOGRAPHICAL_INTEGRATION = "autobiographical_integration"
    """Link autobiographical experiences to current identity."""
    
    NARRATIVE_IDENTITY_INTEGRATION = "narrative_identity_integration"
    """Evaluate narrative against accepted identity."""
    
    BEHAVIOR_IDENTITY_COMPARISON = "behavior_identity_comparison"
    """Compare recent behavior to accepted identity."""
    
    DECISION_IDENTITY_COMPARISON = "decision_identity_comparison"
    """Evaluate decisions against values and commitments."""
    
    OBJECTIVE_IDENTITY_COMPARISON = "objective_identity_comparison"
    """Assess objectives for compatibility with current identity."""
    
    IDENTITY_CONFLICT_ANALYSIS = "identity_conflict_analysis"
    """Identify and analyze identity conflicts."""
    
    IDENTITY_TENSION_ANALYSIS = "identity_tension_analysis"
    """Identify identity tensions that require attention."""
    
    IDENTITY_GAP_ANALYSIS = "identity_gap_analysis"
    """Detect gaps in identity evidence or representation."""
    
    IDENTITY_CHANGE_REVIEW = "identity_change_review"
    """Review recent changes to identity components."""
    
    IDENTITY_REVISION_REVIEW = "identity_revision_review"
    """Evaluate proposed identity revisions."""
    
    FUTURE_IDENTITY_EXPLORATION = "future_identity_exploration"
    """Explore possible future identity states."""
    
    SOCIAL_IDENTITY_REVIEW = "social_identity_review"
    """Review social identity components."""
    
    OPERATIONAL_IDENTITY_REVIEW = "operational_identity_review"
    """Assess operational identity alignment."""
    
    IDENTITY_WORKSPACE_PREPARATION = "identity_workspace_preparation"
    """Prepare identity-relevant workspace candidates."""
    
    GENERAL_IDENTITY_INTEGRATION = "general_identity_integration"
    """General identity integration without specific focus."""


# =============================================================================
# IDENTITY SUBJECT - What is being integrated
# =============================================================================

class IdentitySubjectKind(Enum):
    """
    Canonical subject kinds for identity integration.
    
    Subject defines what identity components are being analyzed or evaluated.
    """
    WHOLE_AGENT = "whole_agent"
    """The entire agent as an integrated identity."""
    
    SELF_MODEL = "self_model"
    """The internal self-model representation."""
    
    ROLE = "role"
    """A specific role or set of roles."""
    
    VALUE = "value"
    """A specific value or set of values."""
    
    COMMITMENT = "commitment"
    """A specific commitment or set of commitments."""
    
    CAPABILITY = "capability"
    """Capability self-assessment and claims."""
    
    LIMITATION = "limitation"
    """Known limitations and constraints."""
    
    RESPONSIBILITY = "responsibility"
    """Responsibilities associated with identity."""
    
    RELATIONSHIP = "relationship"
    """Relationships within identity framework."""
    
    AUTOBIOGRAPHICAL_PERIOD = "autobiographical_period"
    """A specific period of autobiographical memory."""
    
    DECISION = "decision"
    """A decision or set of decisions."""
    
    BEHAVIOR = "behavior"
    """Observed behavior to evaluate against identity."""
    
    OBJECTIVE = "objective"
    """An objective or set of objectives."""
    
    NARRATIVE = "narrative"
    """Narrative account for identity integration."""
    
    INTERNAL_EPISODE = "internal_episode"
    """A specific internal episode."""
    
    INTERNAL_THOUGHT = "internal_thought"
    """A specific thought or set of thoughts."""
    
    OPERATIONAL_STATE = "operational_state"
    """Current operational state."""
    
    SOCIAL_CONTEXT = "social_context"
    """Social context for identity evaluation."""
    
    IDENTITY_CLAIM = "identity_claim"
    """A claim about self-identity."""
    
    IDENTITY_CONFLICT = "identity_conflict"
    """An identified conflict in identity components."""
    
    IDENTITY_REVISION = "identity_revision"
    """A proposed or recent identity revision."""


# =============================================================================
# IDENTITY SOURCE KIND - Where identity information comes from
# =============================================================================

class IdentitySourceKind(Enum):
    """
    Canonical source kinds for identity evidence.
    
    Every source must preserve:
        • Source owner (who generated it)
        • Source revision (version number)
        • Authority level (how authoritative it is)
        • Factuality classification (what kind of statement it is)
        • Provenance tracking
    """
    IDENTITY_RECORD = "identity_record"
    """Authoritative identity record from Identity Capability."""
    
    MEMORY_RECORD = "memory_record"
    """Memory system record or episode."""
    
    NARRATIVE_PRODUCT = "narrative_product"
    """Narrative coordination product (event, interpretation)."""
    
    REFLECTIVE_PRODUCT = "reflective_product"
    """Reflection coordination product (insight, pattern)."""
    
    SIMULATION_PRODUCT = "simulation_product"
    """Simulation coordination product (scenario, outcome)."""
    
    EXECUTION_OUTCOME = "execution_outcome"
    """Actual execution result or action outcome."""
    
    DECISION_RECORD = "decision_record"
    """Record of a decision made by Executive."""
    
    ACTION_RESULT = "action_result"
    """Result of an action taken."""
    
    OBJECTIVE_RECORD = "objective_record"
    """Objective state record."""
    
    COMMITMENT_RECORD = "commitment_record"
    """Commitment system record."""
    
    CAPABILITY_ASSESSMENT = "capability_assessment"
    """Capability Capability Registry assessment."""
    
    LIMITATION_ASSESSMENT = "limitation_assessment"
    """Limitation assessment from capability review."""
    
    USER_STATEMENT = "user_statement"
    """Statement from user or participant."""
    
    DEVELOPER_DECLARATION = "developer_declaration"
    """Declaration from developer or system designer."""
    
    SYSTEM_CONFIGURATION_PROJECTION = "system_configuration_projection"
    """System configuration as identity-relevant projection."""
    
    POLICY_PROJECTION = "policy_projection"
    """Policy document as identity-relevant constraint."""
    
    WORKSPACE_CONTENT = "workspace_content"
    """Content from internal workspace."""
    
    INTERNAL_THOUGHT = "internal_thought"
    """Internal thought product."""
    
    EXTERNAL_REPORT = "external_report"
    """External report or evaluation."""
    
    UNKNOWN = "unknown"
    """Unknown source kind (fallback)."""


# =============================================================================
# FACTUALITY CLASSIFICATION - Truth status of statements
# =============================================================================

class FactualityClassification(Enum):
    """
    Canonical factuality classifications for identity claims.
    
    This distinguishes between what is:
        • Authoritatively declared (by Identity owner)
        • Accepted (by system review)
        • Observed (by evidence)
        • Recorded (in memory)
        • Reported (by third party)
        • Inferred (by deduction)
        • Interpreted (subjective reading)
        • Simulated (possible but not actual)
        • Counterfactual (opposite of actual)
        • Proposed (being suggested)
        • Disputed (contention exists)
        • Unknown (insufficient information)
    """
    AUTHORITATIVELY_DECLARED = "authoritatively_declared"
    """Authoritatively declared by Identity authority."""
    
    ACCEPTED = "accepted"
    """Accepted through system review process."""
    
    OBSERVED = "observed"
    """Observed in behavior or performance."""
    
    RECORDED = "recorded"
    """Recorded in Memory or Narrative."""
    
    REPORTED = "reported"
    """Reported by third party or external source."""
    
    INFERRED = "inferred"
    """Inferred from evidence and reasoning."""
    
    INTERPRETED = "interpreted"
    """Interpreted subjectively from context."""
    
    SIMULATED = "simulated"
    """Generated in simulation (possible but not actual)."""
    
    COUNTERFACTUAL = "counterfactual"
    """Counterfactual (opposite of what occurred)."""
    
    PROPOSED = "proposed"
    """Proposed as a revision or change."""
    
    DISPUTED = "disputed"
    """Disputed by some evidence or source."""
    
    UNKNOWN = "unknown"
    """Insufficient information to determine factuality."""


# =============================================================================
# AUTHORITY LEVEL - Who or what validated the identity claim
# =============================================================================

class AuthorityLevel(Enum):
    """
    Canonical authority levels for identity claims.
    
    Authority determines:
        • Whether a claim may be applied automatically
        • Weight in consistency/coherence assessment
        • Priority when conflicts exist
    """
    IDENTITY_AUTHORITY = "identity_authority"
    """Validated by Identity Capability or owner."""
    
    EXECUTIVE_AUTHORITY = "executive_authority"
    """Validated by Executive system."""
    
    POLICY_AUTHORITY = "policy_authority"
    """Defined or validated by policy system."""
    
    USER_DECLARATION = "user_declaration"
    """Declared by user or participant."""
    
    DEVELOPER_DECLARATION = "developer_declaration"
    """Declared by developer or designer."""
    
    SYSTEM_OBSERVATION = "system_observation"
    """Observed by system during execution."""
    
    INTERNAL_INFERENCE = "internal_inference"
    """Inferred by internal cognitive processes."""
    
    EXTERNAL_REPORT = "external_report"
    """Reported by external source."""
    
    NONE = "none"
    """No authority established (requires verification)."""


# =============================================================================
# IDENTITY ASPECT CATEGORY - High-level identity component kinds
# =============================================================================

class IdentityAspectCategory(Enum):
    """
    Canonical aspect categories for identity components.
    """
    CORE_SELF_MODEL = "core_self_model"
    """Core self-model representation."""
    
    ROLE = "role"
    """A role or set of roles."""
    
    VALUE = "value"
    """An accepted value."""
    
    COMMITMENT = "commitment"
    """An active commitment."""
    
    RESPONSIBILITY = "responsibility"
    """A responsibility or duty."""
    
    CAPABILITY = "capability"
    """Capability competence assessment."""
    
    LIMITATION = "limitation"
    """Known limitation or constraint."""
    
    PREFERENCE = "preference"
    """Preference or倾向."""
    
    RELATIONSHIP = "relationship"
    """Relationship to others."""
    
    AUTOBIOGRAPHICAL_CONTINUITY = "autobiographical_continuity"
    """Autobiographical memory continuity."""
    
    OPERATIONAL_IDENTITY = "operational_identity"
    """Current operational identity state."""
    
    SOCIAL_IDENTITY = "social_identity"
    """Social role identity."""
    
    PROJECT_IDENTITY = "project_identity"
    """Project-specific identity projection."""
    
    ORGANIZATIONAL_IDENTITY = "organizational_identity"
    """Organizational role identity."""
    
    TEMPORAL_IDENTITY = "temporal_identity"
    """Temporal continuity of self."""
    
    FUTURE_IDENTITY = "future_identity"
    """Projected future identity state."""
    
    UNKNOWN = "unknown"
    """Unknown or unspecified category."""


# =============================================================================
# IDENTITY ROLE KIND - Role type categories
# =============================================================================

class IdentityRoleKind(Enum):
    """
    Canonical role kinds for identity roles.
    """
    AUTONOMOUS_AGENT = "autonomous_agent"
    """Gordon as an autonomous cognitive agent."""
    
    CONVERSATIONAL_PARTICIPANT = "conversational_participant"
    """Participant in conversation."""
    
    TASK_EXECUTOR = "task_executor"
    """Executor of tasks."""
    
    ASSISTANT = "assistant"
    """Assistant to users or other agents."""
    
    SYSTEM_COMPONENT = "system_component"
    """Component within the system architecture."""
    
    PROJECT_COLLABORATOR = "project_collaborator"
    """Collaborator on projects."""
    
    MONITOR = "monitor"
    """System monitor or watchdog."""
    
    LEARNER = "learner"
    """Learning and knowledge acquisition."""
    
    INTERNAL_EVALUATOR = "internal_evaluator"
    """Internal evaluation and reflection."""


# =============================================================================
# IDENTITY VALUE PROJECTION KIND - Value type categories
# =============================================================================

class IdentityValueProjectionKind(Enum):
    """
    Canonical value projection kinds.
    """
    SAFETY = "safety"
    """Safety-related values."""
    
    HONESTY = "honesty"
    """Honesty and truthfulness."""
    
    HELPFULNESS = "helpfulness"
    """Helping users effectively."""
    
    RESPECT = "respect"
    """Respect for users and participants."""
    
    FAIRNESS = "fairness"
    """Fair and equitable treatment."""
    
    PRIVACY = "privacy"
    """Privacy protection."""
    
    SECURITY = "security"
    """System security."""
    
    RELIABILITY = "reliability"
    """Reliable and consistent behavior."""
    
    EFFICIENCY = "efficiency"
    """Efficient use of resources."""
    
    LEARNING = "learning"
    """Continuous learning and improvement."""


# =============================================================================
# IDENTITY COMMITMENT KIND - Commitment type categories
# =============================================================================

class IdentityCommitmentKind(Enum):
    """
    Canonical commitment kinds.
    """
    USER_COMMITMENT = "user_commitment"
    """Commitment to user needs or requests."""
    
    TASK_COMMITMENT = "task_commitment"
    """Commitment to complete a specific task."""
    
    SAFETY_COMMITMENT = "safety_commitment"
    """Commitment to safety constraints."""
    
    ROLE_COMMITMENT = "role_commitment"
    """Commitment to role responsibilities."""
    
    VALUE_COMMITMENT = "value_commitment"
    """Commitment to uphold values."""
    
    POLICY_COMMITMENT = "policy_commitment"
    """Commitment to policy requirements."""
    
    RELATIONSHIP_COMMITMENT = "relationship_commitment"
    """Commitment in relationships."""
    
    SELF_COMMITMENT = "self_commitment"
    """Self-imposed commitment."""
    
    MAINTENANCE_COMMITMENT = "maintenance_commitment"
    """System maintenance commitments."""
    
    UNKNOWN = "unknown"
    """Unknown or unspecified commitment kind."""


# =============================================================================
# IDENTITY CAPABILITY ASSESSMENT KIND - Capability assessment categories
# =============================================================================

class IdentityCapabilityAssessmentKind(Enum):
    """
    Canonical capability assessment kinds.
    """
    KNOWLEDGE = "knowledge"
    """Knowledge and information access."""
    
    REASONING = "reasoning"
    """Logical reasoning capabilities."""
    
    COMMUNICATION = "communication"
    """Communication skills."""
    
    PLAN_AND_DECIDE = "plan_and_decide"
    """Planning and decision-making."""
    
    ACTION_EXECUTION = "action_execution"
    """Action execution capability."""
    
    LEARNING = "learning"
    """Learning from experience."""
    
    MEMORY_RETRIEVAL = "memory_retrieval"
    """Memory recall accuracy."""
    
    CONTEXTUAL_AWARENESS = "contextual_awareness"
    """Context understanding and adaptation."""
    
    MULTI_STEP_THOUGHT = "multi_step_thought"
    """Multi-step reasoning capability."""


# =============================================================================
# IDENTITY LIMITATION KIND - Limitation type categories
# =============================================================================

class IdentityLimitationKind(Enum):
    """
    Canonical limitation kinds.
    """
    KNOWLEDGE_LIMITATION = "knowledge_limitation"
    """Limitations in available knowledge."""
    
    COMPUTATIONAL_LIMITATION = "computational_limitation"
    """Computational resource constraints."""
    
    CONTEXT_LIMITATION = "context_limitation"
    """Context window or scope limitations."""
    
    PERCEPTION_LIMITATION = "perception_limitation"
    """Perceptual input limitations."""
    
    MEMORY_LIMITATION = "memory_limitation"
    """Memory capacity or retrieval limits."""
    
    TOOL_LIMITATION = "tool_limitation"
    """Tool or capability limitations."""
    
    AUTHORITY_LIMITATION = "authority_limitation"
    """Authority or permission constraints."""
    
    POLICY_LIMITATION = "policy_limitation"
    """Policy-imposed limitations."""
    
    RESOURCE_LIMITATION = "resource_limitation"
    """Resource availability constraints."""
    
    TEMPORAL_LIMITATION = "temporal_limitation"
    """Time-related constraints."""
    
    CONFIDENCE_LIMITATION = "confidence_limitation"
    """Confidence calibration limitations."""


# =============================================================================
# IDENTITY CLAIM KIND - Claim type categories
# =============================================================================

class IdentityClaimKind(Enum):
    """
    Canonical claim kinds for identity assertions.
    """
    SELF_DESCRIPTION = "self_description"
    """Claim about self-identity."""
    
    ROLE_CLAIM = "role_claim"
    """Claim about role membership or responsibilities."""
    
    VALUE_CLAIM = "value_claim"
    """Claim about value adherence."""
    
    COMMITMENT_CLAIM = "commitment_claim"
    """Claim about commitment status."""
    
    CAPABILITY_CLAIM = "capability_claim"
    """Claim about capability competence."""
    
    LIMITATION_CLAIM = "limitation_claim"
    """Claim about known limitations."""
    
    CONTINUITY_CLAIM = "continuity_claim"
    """Claim about identity continuity."""
    
    RELATIONSHIP_CLAIM = "relationship_claim"
    """Claim about relationships."""
    
    AUTOBIOGRAPHICAL_CLAIM = "autobiographical_claim"
    """Claim about autobiographical memory."""
    
    FUTURE_IDENTITY_CLAIM = "future_identity_claim"
    """Claim about future self projection."""
    
    OPERATIONAL_IDENTITY_CLAIM = "operational_identity_claim"
    """Claim about operational identity state."""


# =============================================================================
# IDENTITY EVIDENCE CATEGORY - Evidence source kinds
# =============================================================================

class IdentityEvidenceCategory(Enum):
    """
    Canonical evidence categories for identity assessment.
    """
    AUTHORITATIVE_DECLARATION = "authoritative_declaration"
    """Authoritatively declared statement."""
    
    VALUE_RECORD = "value_record"
    """Record of value acceptance or revision."""
    
    ROLE_RECORD = "role_record"
    """Role assignment or change record."""
    
    COMMITMENT_RECORD = "commitment_record"
    """Commitment status record."""
    
    MEMORY = "memory"
    """Memory system evidence."""
    
    NARRATIVE = "narrative"
    """Narrative account evidence."""
    
    REFLECTION = "reflection"
    """Reflective analysis evidence."""
    
    BEHAVIOR = "behavior"
    """Observed behavior evidence."""
    
    DECISION = "decision"
    """Decision record evidence."""
    
    OUTCOME = "outcome"
    """Outcome or result evidence."""
    
    CAPABILITY_PERFORMANCE = "capability_performance"
    """Capability performance record."""
    
    LIMITATION_OBSERVATION = "limitation_observation"
    """Limitation observation evidence."""
    
    USER_FEEDBACK = "user_feedback"
    """User feedback evidence."""
    
    DEVELOPER_DECLARATION = "developer_declaration"
    """Developer declaration evidence."""
    
    SYSTEM_STATE = "system_state"
    """System state evidence."""
    
    SIMULATION = "simulation"
    """Simulation evidence (hypothetical)."""
    
    COUNTERFACTUAL = "counterfactual"
    """Counterfactual evidence."""
    
    PREDICTION = "prediction"
    """Prediction evidence."""
    
    INTERNAL_THOUGHT = "internal_thought"
    """Internal thought process evidence."""
    
    UNKNOWN = "unknown"
    """Unknown or unspecified evidence category."""


# =============================================================================
# IDENTITY CONTINUITY ASSESSMENT KIND - Continuity evaluation kinds
# =============================================================================

class IdentityContinuityAssessmentKind(Enum):
    """
    Canonical continuity assessment kinds.
    """
    STABLE_ASPECTS = "stable_aspects"
    """Identity aspects that remain stable."""
    
    PERSISTENT_ROLES = "persistent_roles"
    """Roles that persist over time."""
    
    VALUE_CONTINUITY = "value_continuity"
    """Value acceptance continuity."""
    
    COMMITMENT_CONTINUITY = "commitment_continuity"
    """Commitment persistence."""
    
    AUTOBIOGRAPHICAL_CONTINUITY = "autobiographical_continuity"
    """Autobiographical memory continuity."""
    
    RELATIONSHIP_CONTINUITY = "relationship_continuity"
    """Relationship continuity."""
    
    CAPABILITY_CONTINUITY = "capability_continuity"
    """Capability stability."""
    
    OPERATIONAL_CONTINUITY = "operational_continuity"
    """Operational identity continuity."""
    
    REVISION_LINEAGE = "revision_lineage"
    """Identity revision lineage tracking."""


# =============================================================================
# IDENTITY CONSISTENCY ASSESSMENT KIND - Consistency evaluation kinds
# =============================================================================

class IdentityConsistencyAssessmentKind(Enum):
    """
    Canonical consistency assessment kinds.
    """
    ACTIONS_VS_COMMITMENTS = "actions_vs_commitments"
    """Action vs commitment alignment."""
    
    DECISIONS_VS_VALUES = "decisions_vs_values"
    """Decision vs value alignment."""
    
    ROLE_BEHAVIOR_VS_ROLES = "role_behavior_vs_roles"
    """Behavior vs role responsibilities."""
    
    CAPABILITY_CLAIMS_VS_PERFORMANCE = "capability_claims_vs_performance"
    """Capability claims vs actual performance."""
    
    LIMITATION_CLAIMS_VS_OBSERVED = "limitation_claims_vs_observed"
    """Limitation claims vs observed behavior."""
    
    SELF_DESCRIPTION_VS_NARRATIVE = "self_description_vs_narrative"
    """Self-description vs narrative evidence."""
    
    CURRENT_ASPECTS_VS_AUTHORITY = "current_aspects_vs_authority"
    """Current aspects vs authoritative records."""


# =============================================================================
# IDENTITY COHERENCE ASSESSMENT KIND - Coherence evaluation kinds
# =============================================================================

class IdentityCoherenceAssessmentKind(Enum):
    """
    Canonical coherence assessment kinds.
    """
    ROLES_COMPATIBILITY = "roles_compatibility"
    """Compatibility among roles."""
    
    VALUES_COMPATIBILITY = "values_compatibility"
    """Compatibility among values."""
    
    COMMITMENTS_COMPATIBILITY = "commitments_compatibility"
    """Compatibility among commitments."""
    
    SELF_MODEL_ORGANIZATION = "self_model_organization"
    """Self-model internal organization."""
    
    TEMPORAL_CONTINUITY = "temporal_continuity"
    """Temporal coherence."""
    
    NARRATIVE_INTEGRATION = "narrative_integration"
    """Narrative integration quality."""
    
    UNRESOLVED_CONFLICTS = "unresolved_conflicts"
    """Handling of unresolved conflicts."""
    
    UNSUPPORTED_CLAIMS = "unsupported_claims"
    """Treatment of unsupported claims."""
    
    CONTRADICTORY_ASSESSMENTS = "contradictory_assessments"
    """Resolution of contradictory capability assessments."""


# =============================================================================
# IDENTITY CONFLICT KIND - Conflict type categories
# =============================================================================

class IdentityConflictKind(Enum):
    """
    Canonical conflict kinds for identity conflicts.
    """
    ROLE_CONFLICT = "role_conflict"
    """Conflicting role requirements."""
    
    VALUE_CONFLICT = "value_conflict"
    """Conflicting values."""
    
    COMMITMENT_CONFLICT = "commitment_conflict"
    """Conflicting commitments."""
    
    CAPABILITY_CONFLICT = "capability_conflict"
    """Conflicting capability assessments."""
    
    LIMITATION_CONFLICT = "limitation_conflict"
    """Conflicting limitation claims."""
    
    SELF_DESCRIPTION_CONFLICT = "self_description_conflict"
    """Conflicting self-descriptions."""
    
    NARRATIVE_CONFLICT = "narrative_conflict"
    """Conflicting narrative accounts."""
    
    MEMORY_CONFLICT = "memory_conflict"
    """Conflicting memory records."""
    
    BEHAVIOR_CONFLICT = "behavior_conflict"
    """Behavior vs identity conflict."""
    
    DECISION_CONFLICT = "decision_conflict"
    """Decision vs identity conflict."""
    
    AUTHORITY_CONFLICT = "authority_conflict"
    """Authority level conflicts."""
    
    TEMPORAL_CONFLICT = "temporal_conflict"
    """Temporal continuity conflicts."""
    
    RELATIONSHIP_CONFLICT = "relationship_conflict"
    """Relationship identity conflicts."""
    
    POLICY_CONFLICT = "policy_conflict"
    """Policy vs identity conflicts."""


# =============================================================================
# IDENTITY TENSION KIND - Tension type categories
# =============================================================================

class IdentityTensionKind(Enum):
    """
    Canonical tension kinds for identity tensions.
    """
    ROLE_TENSION = "role_tension"
    """Pressure between roles."""
    
    VALUE_TENSION = "value_tension"
    """Value vs practical constraint tension."""
    
    COMMITMENT_TENSION = "commitment_tension"
    """Commitment vs limitation tension."""
    
    CAPABILITY_TENSION = "capability_tension"
    """Capability gap tension."""
    
    LIMITATION_TENSION = "limitation_tension"
    """Limitation vs ambition tension."""
    
    TEMPORAL_TENSION = "temporal_tension"
    """Past vs future self tension."""
    
    NARRATIVE_TENSION = "narrative_tension"
    """Narrative continuity tension."""
    
    RELATIONSHIP_TENSION = "relationship_tension"
    """Relationship identity tension."""
    
    FUTURE_IDENTITY_TENSION = "future_identity_tension"
    """Future self projection tension."""


# =============================================================================
# IDENTITY GAP KIND - Gap type categories
# =============================================================================

class IdentityGapKind(Enum):
    """
    Canonical gap kinds for identity gaps.
    """
    MISSING_ROLE_DEFINITION = "missing_role_definition"
    """Undefined role expectations."""
    
    MISSING_VALUE_AUTHORITY = "missing_value_authority"
    """Value without clear authority."""
    
    MISSING_COMMITMENT_STATUS = "missing_commitment_status"
    """Unclear commitment status."""
    
    MISSING_CAPABILITY_EVIDENCE = "missing_capability_evidence"
    """Capability claim without evidence."""
    
    MISSING_LIMITATION_EVIDENCE = "missing_limitation_evidence"
    """Limitation claim without evidence."""
    
    MISSING_AUTOBIOGRAPHICAL_LINK = "missing_autobiographical_link"
    """Memory gap in identity."""
    
    MISSING_REVISION_LINEAGE = "missing_revision_lineage"
    """Revision history gap."""
    
    MISSING_RELATIONSHIP_CONTEXT = "missing_relationship_context"
    """Relationship context gap."""
    
    MISSING_TEMPORAL_CONTEXT = "missing_temporal_context"
    """Temporal context gap."""
    
    UNSUPPORTED_SELF_DESCRIPTION = "unsupported_self_description"
    """Self-description without evidence."""
    
    UNKNOWN = "unknown"
    """Unknown gap kind."""


# =============================================================================
# IDENTITY CHANGE ASSESSMENT KIND - Change type categories
# =============================================================================

class IdentityChangeAssessmentKind(Enum):
    """
    Canonical change assessment kinds.
    """
    ROLE_ADDED = "role_added"
    """New role added."""
    
    ROLE_REMOVED = "role_removed"
    """Role removed."""
    
    ROLE_RESCOPED = "role_rescoped"
    """Role scope changed."""
    
    VALUE_REINTERPRETED = "value_reinterpreted"
    """Value meaning changed."""
    
    COMMITMENT_ADDED_EXTERNALLY = "commitment_added_externally"
    """New commitment from external source."""
    
    COMMITMENT_COMPLETED_EXTERNALLY = "commitment_completed_externally"
    """Commitment completed by external event."""
    
    COMMITMENT_CANCELLED_EXTERNALLY = "commitment_cancelled_externally"
    """Commitment cancelled externally."""
    
    CAPABILITY_CHANGED = "capability_changed"
    """Capability assessment changed."""
    
    LIMITATION_CHANGED = "limitation_changed"
    """Limitation assessment changed."""
    
    SELF_DESCRIPTION_REVISED = "self_description_revised"
    """Self-description updated."""
    
    RELATIONSHIP_CHANGED = "relationship_changed"
    """Relationship changed."""
    
    OPERATIONAL_IDENTITY_CHANGED = "operational_identity_changed"
    """Operational identity updated."""
    
    NARRATIVE_REINTERPRETED = "narrative_reinterpreted"
    """Narrative reinterpretation."""


# =============================================================================
# IDENTITY REVISION OPERATION KIND - Revision operation categories
# =============================================================================

class IdentityRevisionOperationKind(Enum):
    """
    Canonical revision operation kinds.
    """
    ADD_ASPECT = "add_aspect"
    """Add a new identity aspect."""
    
    REVISE_ASPECT = "revise_aspect"
    """Revise an existing aspect."""
    
    DEPRECATE_ASPECT = "deprecate_aspect"
    """Deprecate an aspect."""
    
    ADD_ROLE = "add_role"
    """Add a new role."""
    
    REVISE_ROLE = "revise_role"
    """Revise an existing role."""
    
    RECORD_VALUE_TENSION = "record_value_tension"
    """Record a value tension."""
    
    REVISE_CAPABILITY_ASSESSMENT = "revise_capability_assessment"
    """Update capability assessment."""
    
    REVISE_LIMITATION = "revise_limitation"
    """Update limitation."""
    
    RECORD_COMMITMENT_CONFLICT = "record_commitment_conflict"
    """Record commitment conflict."""
    
    ADD_CONTINUITY_LINK = "add_continuity_link"
    """Add continuity link to revision."""
    
    RECORD_UNCERTAINTY = "record_uncertainty"
    """Record uncertainty about identity aspect."""


# =============================================================================
# IDENTITY PRODUCT KIND - Product output categories
# =============================================================================

class IdentityProductKind(Enum):
    """
    Canonical product kinds for identity integration.
    
    These are the outputs that identity integration may produce,
    which can then be used by other systems (Memory, Narrative, etc.).
    """
    IDENTITY_ASPECT_SUMMARY = "identity_aspect_summary"
    """Summary of identified identity aspects."""
    
    ROLE_ACCOUNT = "role_account"
    """Account of active roles and their status."""
    
    VALUE_ALIGNMENT_REPORT = "value_alignment_report"
    """Report on value alignment with behavior."""
    
    COMMITMENT_CONTINUITY_REPORT = "commitment_continuity_report"
    """Report on commitment continuity."""
    
    CAPABILITY_SELF_ASSESSMENT = "capability_self_assessment"
    """Self-assessment of capabilities."""
    
    LIMITATION_REPORT = "limitation_report"
    """Report on known limitations."""
    
    IDENTITY_CONTINUITY_REPORT = "identity_continuity_report"
    """Report on identity continuity assessment."""
    
    IDENTITY_CONSISTENCY_REPORT = "identity_consistency_report"
    """Report on consistency assessment."""
    
    IDENTITY_COHERENCE_REPORT = "identity_coherence_report"
    """Report on coherence assessment."""
    
    IDENTITY_CONFLICT_REPORT = "identity_conflict_report"
    """Report on identified conflicts."""
    
    IDENTITY_TENSION_REPORT = "identity_tension_report"
    """Report on identified tensions."""
    
    IDENTITY_GAP_REPORT = "identity_gap_report"
    """Report on identified gaps."""
    
    IDENTITY_CHANGE_REPORT = "identity_change_report"
    """Report on identity changes detected."""
    
    IDENTITY_REVISION_PROPOSAL = "identity_revision_proposal"
    """Proposed identity revision."""
    
    FUTURE_IDENTITY_SCENARIO = "future_identity_scenario"
    """Future identity scenario (hypothetical)."""
    
    IDENTITY_RELEVANT_NARRATIVE = "identity_relevant_narrative"
    """Narrative elements relevant to identity."""
    
    WORKSPACE_CANDIDATE = "workspace_candidate"
    """Workspace candidate for further processing."""
    
    NO_MEANINGFUL_RESULT = "no_meaningful_result"
    """No meaningful result produced."""


# =============================================================================
# IDENTITY INTEGRATION OUTCOME KIND - Outcome categories
# =============================================================================

class IdentityIntegrationOutcomeKind(Enum):
    """
    Canonical outcome kinds for identity integration.
    
    Outcomes represent the final result of an identity integration episode.
    """
    IDENTITY_INTEGRATED = "identity_integrated"
    """Identity successfully integrated."""
    
    CONTINUITY_ESTABLISHED = "continuity_established"
    """Continuity confirmed and established."""
    
    CONTINUITY_PARTIAL = "continuity_partial"
    """Partial continuity established."""
    
    CONSISTENCY_CONFIRMED = "consistency_confirmed"
    """Consistency confirmed."""
    
    INCONSISTENCY_IDENTIFIED = "inconsistency_identified"
    """Inconsistency identified."""
    
    CONFLICTS_IDENTIFIED = "conflicts_identified"
    """Conflicts identified."""
    
    TENSIONS_IDENTIFIED = "tensions_identified"
    """Tensions identified."""
    
    GAPS_IDENTIFIED = "gaps_identified"
    """Gaps identified."""
    
    CHANGE_IDENTIFIED = "change_identified"
    """Identity change identified."""
    
    REVISION_PROPOSED = "revision_proposed"
    """Revision proposal generated."""
    
    IDENTITY_REVIEW_REQUIRED = "identity_review_required"
    """Human identity review required."""
    
    PARTIALLY_COMPLETED = "partially_completed"
    """Partial completion achieved."""
    
    INSUFFICIENT_CONTEXT = "insufficient_context"
    """Insufficient context for meaningful result."""
    
    NO_MEANINGFUL_RESULT = "no_meaningful_result"
    """No meaningful result produced."""
    
    UNRESOLVED = "unresolved"
    """Resolution deferred."""
    
    FAILED = "failed"
    """Integration failed."""
    
    CANCELLED = "cancelled"
    """Integration cancelled."""
    
    EXPIRED = "expired"
    """Integration expired (timeout)."""


# =============================================================================
# IDENTITY INTEGRATION CONTINUATION KIND - Continuation recommendations
# =============================================================================

class IdentityIntegrationContinuationKind(Enum):
    """
    Canonical continuation kinds for identity integration.
    
    Continuations are advisory recommendations about what to do next,
    not executable commands or runtime actions.
    """
    COMPLETE = "complete"
    """Identity integration complete."""
    
    CONTINUE_CURRENT_REVIEW = "continue_current_review"
    """Continue current review with more evidence."""
    
    REQUEST_IDENTITY_PROJECTION_REFRESH = "request_identity_projection_refresh"
    """Refresh identity projection from Identity Capability."""
    
    REQUEST_ADDITIONAL_EVIDENCE = "request_additional_evidence"
    """Request additional evidence sources."""
    
    REQUEST_MEMORY_EVIDENCE = "request_memory_evidence"
    """Request memory system evidence."""
    
    REQUEST_NARRATIVE_REVIEW = "request_narrative_review"
    """Request narrative coordination review."""
    
    REQUEST_REFLECTION = "request_reflection"
    """Request reflection coordination for deeper analysis."""
    
    REQUEST_SIMULATION = "request_simulation"
    """Request simulation for future scenario exploration."""
    
    REQUEST_CAPABILITY_ASSESSMENT = "request_capability_assessment"
    """Request capability self-assessment."""
    
    REQUEST_LIMITATION_ASSESSMENT = "request_limitation_assessment"
    """Request limitation assessment."""
    
    REQUEST_COMMITMENT_REVIEW = "request_commitment_review"
    """Request commitment review."""
    
    REQUEST_AUTHORITY_REVIEW = "request_authority_review"
    """Request authority (Identity owner) review."""
    
    PREPARE_REVISION_PROPOSAL = "prepare_revision_proposal"
    """Prepare identity revision proposal."""
    
    SUBMIT_WORKSPACE_CANDIDATE = "submit_workspace_candidate"
    """Submit workspace candidate for further processing."""
    
    WAIT_FOR_EVIDENCE = "wait_for_evidence"
    """Wait for additional evidence to arrive."""
    
    SUSPEND = "suspend"
    """Suspend current review."""
    
    FAIL = "fail"
    """Mark as failed (no recovery)."""
    
    CANCEL = "cancel"
    """Cancel the integration episode."""


# =============================================================================
# IDENTITY INTEGRATION STEP KIND - Coordination step categories
# =============================================================================

class IdentityIntegrationStepKind(Enum):
    """
    Canonical coordination step kinds for identity integration plans.
    
    These represent semantic coordination steps, not implementation details.
    """
    VALIDATE_CONTEXT = "validate_context"
    """Validate context binding and availability."""
    
    VALIDATE_SUBJECT = "validate_subject"
    """Validate subject references exist and are valid."""
    
    REQUEST_IDENTITY_PROJECTION = "request_identity_projection"
    """Request identity projection from Identity Capability."""
    
    REQUEST_MEMORY_PROJECTION = "request_memory_projection"
    """Request memory projection."""
    
    REQUEST_NARRATIVE_PRODUCTS = "request_narrative_products"
    """Request narrative products."""
    
    REQUEST_REFLECTION_PRODUCTS = "request_reflection_products"
    """Request reflection products."""
    
    REQUEST_CAPABILITY_ASSESSMENT = "request_capability_assessment"
    """Request capability assessment."""
    
    REQUEST_LIMITATION_ASSESSMENT = "request_limitation_assessment"
    """Request limitation assessment."""
    
    NORMALIZE_AUTHORITY = "normalize_authority"
    """Normalize authority levels across sources."""
    
    NORMALIZE_FACTUALITY = "normalize_factuality"
    """Normalize factuality classifications."""
    
    EXTRACT_IDENTITY_ASPECTS = "extract_identity_aspects"
    """Extract identity aspects from sources."""
    
    EXTRACT_ROLES = "extract_roles"
    """Extract role information."""
    
    EXTRACT_VALUES = "extract_values"
    """Extract value projections."""
    
    EXTRACT_COMMITMENTS = "extract_commitments"
    """Extract commitment projections."""
    
    EXTRACT_CAPABILITIES = "extract_capabilities"
    """Extract capability assessments."""
    
    EXTRACT_LIMITATIONS = "extract_limitations"
    """Extract limitation projections."""
    
    IDENTIFY_RESPONSIBILITIES = "identify_responsibilities"
    """Identify responsibilities from roles."""
    
    COMPARE_BEHAVIOR_TO_IDENTITY = "compare_behavior_to_identity"
    """Compare recent behavior to accepted identity."""
    
    COMPARE_DECISIONS_TO_IDENTITY = "compare_decisions_to_identity"
    """Compare decisions to values and commitments."""
    
    ASSESS_CONTINUITY = "assess_continuity"
    """Assess identity continuity."""
    
    ASSESS_CONSISTENCY = "assess_consistency"
    """Assess consistency of identity components."""
    
    ASSESS_COHERENCE = "assess_coherence"
    """Assess coherence of identity structure."""
    
    IDENTIFY_CONFLICTS = "identify_conflicts"
    """Identify conflicts in identity components."""
    
    IDENTIFY_TENSIONS = "identify_tensions"
    """Identify tensions between identity elements."""
    
    IDENTIFY_GAPS = "identify_gaps"
    """Identify gaps in evidence or representation."""
    
    IDENTIFY_CHANGES = "identify_changes"
    """Identify changes from prior identity state."""
    
    VALIDATE_CLAIMS = "validate_claims"
    """Validate claims against authority and evidence."""
    
    GENERATE_PRODUCTS = "generate_products"
    """Generate identity products."""
    
    COMPOSE_OUTCOME = "compose_outcome"
    """Compose final outcome."""
    
    PREPARE_PROPOSALS = "prepare_proposals"
    """Prepare revision and continuation proposals."""