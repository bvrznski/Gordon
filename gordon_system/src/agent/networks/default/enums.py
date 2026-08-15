# Default Network Enums
# =====================

"""
Canonical enum definitions for the DefaultNetwork.

These enums provide typed semantic categories without embedding any behavior.
All values are frozen to ensure deterministic behavior and prevent runtime mutation.

PHASE 4.3.12: Runtime-Neutral Enumerations
"""

from __future__ import annotations


# =============================================================================
# DEFAULT NETWORK PURPOSES
# =============================================================================

class DefaultNetworkPurpose:
    """
    Canonical purpose categories for Default Network coordination.
    
    Each purpose determines:
        - Valid paths
        - Valid subject types
        - Required context
        - Expected outputs
        - Allowed external requests
        - Maximum local steps
        - Completion conditions
        - Continuation vocabulary
    
    DO NOT use unrestricted strings for canonical purpose values.
    """
    
    # Core coordination purposes
    GENERATE_INTERNAL_THOUGHT = "generate_internal_thought"
    """Generate new internally generated semantic cognition."""
    
    CONTINUE_INTERNAL_EPISODE = "continue_internal_episode"
    """Continue an existing internal episode progression."""
    
    COORDINATE_REFLECTION = "coordinate_reflection"
    """Coordinate bounded reflection processing."""
    
    COORDINATE_SIMULATION = "coordinate_simulation"
    """Coordinate bounded simulation coordination."""
    
    COORDINATE_COUNTERFACTUAL = "coordinate_counterfactual"
    """Coordinate bounded counterfactual analysis."""
    
    COORDINATE_NARRATIVE = "coordinate_narrative"
    """Coordinate bounded narrative integration."""
    
    INTEGRATE_IDENTITY = "integrate_identity"
    """Coordinate identity integration processing."""
    
    INTEGRATE_MEMORY = "integrate_memory"
    """Coordinate memory integration processing."""
    
    INTEGRATE_PREDICTION = "integrate_prediction"
    """Coordinate predictive integration processing."""
    
    PREPARE_WORKSPACE_CANDIDATE = "prepare_workspace_candidate"
    """Prepare workspace candidate submission."""
    
    REVIEW_INTERNAL_CONTEXT = "review_internal_context"
    """Review and assess internal context state."""
    
    INTEGRATE_EXTERNAL_RESULT = "integrate_external_result"
    """Integrate externally supplied capability result."""
    
    RESOLVE_INTERNAL_CONFLICT = "resolve_internal_conflict"
    """Resolve semantic conflicts in internal cognition."""
    
    ASSESS_INTERNAL_CONTINUATION = "assess_internal_continuation"
    """Assess and recommend continuation strategy."""
    
    GENERAL_INTERNAL_COGNITION = "general_internal_cognition"
    """General internal cognition coordination."""
    
    @classmethod
    def all_purposes(cls) -> tuple[str, ...]:
        """Return all valid purpose values as a tuple."""
        return (
            cls.GENERATE_INTERNAL_THOUGHT,
            cls.CONTINUE_INTERNAL_EPISODE,
            cls.COORDINATE_REFLECTION,
            cls.COORDINATE_SIMULATION,
            cls.COORDINATE_COUNTERFACTUAL,
            cls.COORDINATE_NARRATIVE,
            cls.INTEGRATE_IDENTITY,
            cls.INTEGRATE_MEMORY,
            cls.INTEGRATE_PREDICTION,
            cls.PREPARE_WORKSPACE_CANDIDATE,
            cls.REVIEW_INTERNAL_CONTEXT,
            cls.INTEGRATE_EXTERNAL_RESULT,
            cls.RESOLVE_INTERNAL_CONFLICT,
            cls.ASSESS_INTERNAL_CONTINUATION,
            cls.GENERAL_INTERNAL_COGNITION,
        )
    
    @classmethod
    def is_valid_purpose(cls, value: str) -> bool:
        """Check if a string is a valid purpose value."""
        return value in cls.all_purposes()


# =============================================================================
# DEFAULT NETWORK PATHS
# =============================================================================

class DefaultNetworkPath:
    """
    Canonical path identifiers for internal semantic coordination.
    
    A path identifies a semantic coordination approach, NOT:
        - An operating system thread
        - A runtime route
        - A queue destination
        - A provider selection
    
    The requested path may be absent; the network then deterministically
    infers a permitted path from purpose, subject, context, and configuration.
    """
    
    THOUGHT_GENERATION = "thought_generation"
    """Thought generation coordination path."""
    
    REFLECTION = "reflection"
    """Reflection processing path."""
    
    SIMULATION = "simulation"
    """Simulation coordination path."""
    
    COUNTERFACTUAL = "counterfactual"
    """Counterfactual analysis path."""
    
    NARRATIVE = "narrative"
    """Narrative integration path."""
    
    IDENTITY = "identity"
    """Identity integration path."""
    
    MEMORY = "memory"
    """Memory integration path."""
    
    PREDICTIVE = "predictive"
    """Predictive integration path."""
    
    WORKSPACE = "workspace"
    """Workspace candidate preparation path."""
    
    CONTEXT_REVIEW = "context_review"
    """Internal context review path."""
    
    COMPOSITE = "composite"
    """Composite multi-path coordination."""
    
    @classmethod
    def all_paths(cls) -> tuple[str, ...]:
        """Return all valid path values as a tuple."""
        return (
            cls.THOUGHT_GENERATION,
            cls.REFLECTION,
            cls.SIMULATION,
            cls.COUNTERFACTUAL,
            cls.NARRATIVE,
            cls.IDENTITY,
            cls.MEMORY,
            cls.PREDICTIVE,
            cls.WORKSPACE,
            cls.CONTEXT_REVIEW,
            cls.COMPOSITE,
        )
    
    @classmethod
    def is_valid_path(cls, value: str) -> bool:
        """Check if a string is a valid path value."""
        return value in cls.all_paths()
    
    @classmethod
    def get_runtime_neutral_description(cls, path: str) -> str:
        """Get a runtime-neutral description of a path."""
        descriptions = {
            cls.THOUGHT_GENERATION: "Bounded internally generated thought production",
            cls.REFLECTION: "Bounded self-referential processing coordination",
            cls.SIMULATION: "Bounded prospective scenario coordination",
            cls.COUNTERFACTUAL: "Bounded what-if analysis coordination",
            cls.NARRATIVE: "Bounded story continuity integration",
            cls.IDENTITY: "Bounded self-model coherence assessment",
            cls.MEMORY: "Bounded associative knowledge coordination",
            cls.PREDICTIVE: "Bounded expectation evaluation coordination",
            cls.WORKSPACE: "Bounded candidate submission preparation",
            cls.CONTEXT_REVIEW: "Bounded context state assessment",
            cls.COMPOSITE: "Bounded multi-path semantic progression",
        }
        return descriptions.get(path, f"Unknown path: {path}")


# =============================================================================
# DEFAULT NETWORK SUBJECTS
# =============================================================================

class DefaultNetworkSubject:
    """
    Canonical subject categories for Default Network coordination.
    
    A subject identifies what internal cognitive phenomenon is being processed.
    """
    
    UNRESOLVED_CONTRADICTION = "unresolved_contradiction"
    """Processing of conflicting semantic information."""
    
    MISSING_EVIDENCE = "missing_evidence"
    """Coordination requiring additional evidence."""
    
    GOAL_RELEVANCE = "goal_relevance"
    """Goal-related internal processing."""
    
    NARRATIVE_GAP = "narrative_gap"
    """Narrative continuity coordination."""
    
    IDENTITY_CONFLICT = "identity_conflict"
    """Identity coherence assessment."""
    
    PREDICTION_ERROR = "prediction_error"
    """Expectation violation evaluation."""
    
    MEMORY_ASSOCIATION = "memory_association"
    """Memory-driven associative processing."""
    
    SIMULATION_REQUEST = "simulation_request"
    """Simulation scenario coordination."""
    
    WORKSPACE_CANDIDATE = "workspace_candidate"
    """Workspace submission candidate preparation."""
    
    CONTEXT_REVIEW_REQUEST = "context_review_request"
    """Context state assessment request."""
    
    @classmethod
    def all_subjects(cls) -> tuple[str, ...]:
        """Return all valid subject values as a tuple."""
        return (
            cls.UNRESOLVED_CONTRADICTION,
            cls.MISSING_EVIDENCE,
            cls.GOAL_RELEVANCE,
            cls.NARRATIVE_GAP,
            cls.IDENTITY_CONFLICT,
            cls.PREDICTION_ERROR,
            cls.MEMORY_ASSOCIATION,
            cls.SIMULATION_REQUEST,
            cls.WORKSPACE_CANDIDATE,
            cls.CONTEXT_REVIEW_REQUEST,
        )
    
    @classmethod
    def is_valid_subject(cls, value: str) -> bool:
        """Check if a string is a valid subject value."""
        return value in cls.all_subjects()


# =============================================================================
# DEFAULT NETWORK SCOPE
# =============================================================================

class DefaultNetworkScope:
    """
    Canonical scope categories for Default Network coordination.
    
    Scope defines the breadth of the internal cognitive undertaking.
    """
    
    NARROW = "narrow"
    """Single focused semantic task."""
    
    MODERATE = "moderate"
    """Moderate complexity coordination."""
    
    BROAD = "broad"
    """Multi-faceted internal coordination."""
    
    COMPLEX = "complex"
    """Highly complex multi-path coordination."""
    
    @classmethod
    def all_scopes(cls) -> tuple[str, ...]:
        """Return all valid scope values as a tuple."""
        return (cls.NARROW, cls.MODERATE, cls.BROAD, cls.COMPLEX)
    
    @classmethod
    def is_valid_scope(cls, value: str) -> bool:
        """Check if a string is a valid scope value."""
        return value in cls.all_scopes()


# =============================================================================
# DEFAULT NETWORK PRODUCT KINDS
# =============================================================================

class DefaultNetworkProductKind:
    """
    Canonical product kinds produced by the Default Network.
    
    Each kind corresponds to one specialized subsystem's output.
    """
    
    INTERNAL_THOUGHT = "internal_thought"
    """Generated internal thought."""
    
    REFLECTION_PRODUCT = "reflection_product"
    """Reflection coordination outcome."""
    
    SIMULATION_PRODUCT = "simulation_product"
    """Simulation coordination outcome."""
    
    COUNTERFACTUAL_PRODUCT = "counterfactual_product"
    """Counterfactual analysis product."""
    
    NARRATIVE_PRODUCT = "narrative_product"
    """Narrative integration product."""
    
    IDENTITY_PRODUCT = "identity_product"
    """Identity integration product."""
    
    MEMORY_INTEGRATION_PRODUCT = "memory_integration_product"
    """Memory integration outcome."""
    
    PREDICTIVE_INTEGRATION_PRODUCT = "predictive_integration_product"
    """Predictive integration outcome."""
    
    WORKSPACE_CANDIDATE_PREPARED = "workspace_candidate_prepared"
    """Workspace candidate preparation result."""
    
    CONTEXT_REVIEW_PRODUCT = "context_review_product"
    """Context review outcome."""
    
    @classmethod
    def all_kinds(cls) -> tuple[str, ...]:
        """Return all valid product kind values as a tuple."""
        return (
            cls.INTERNAL_THOUGHT,
            cls.REFLECTION_PRODUCT,
            cls.SIMULATION_PRODUCT,
            cls.COUNTERFACTUAL_PRODUCT,
            cls.NARRATIVE_PRODUCT,
            cls.IDENTITY_PRODUCT,
            cls.MEMORY_INTEGRATION_PRODUCT,
            cls.PREDICTIVE_INTEGRATION_PRODUCT,
            cls.WORKSPACE_CANDIDATE_PREPARED,
            cls.CONTEXT_REVIEW_PRODUCT,
        )
    
    @classmethod
    def is_valid_kind(cls, value: str) -> bool:
        """Check if a string is a valid product kind value."""
        return value in cls.all_kinds()


# =============================================================================
# DEFAULT NETWORK OUTCOME KINDS
# =============================================================================

class DefaultNetworkOutcomeKind:
    """
    Canonical outcome kinds for Default Network results.
    
    Outcome represents the result of one bounded semantic progression.
    """
    
    THOUGHTS_GENERATED = "thoughts_generated"
    """Internal thoughts were generated."""
    
    REFLECTION_COORDINATED = "reflection_coordinated"
    """Reflection coordination completed."""
    
    SIMULATION_COORDINATED = "simulation_coordinated"
    """Simulation coordination completed."""
    
    COUNTERFACTUAL_COORDINATED = "counterfactual_coordinated"
    """Counterfactual analysis completed."""
    
    NARRATIVE_COORDINATED = "narrative_coordinated"
    """Narrative integration completed."""
    
    IDENTITY_INTEGRATED = "identity_integrated"
    """Identity integration completed."""
    
    MEMORY_INTEGRATED = "memory_integrated"
    """Memory integration completed."""
    
    PREDICTIONS_INTEGRATED = "predictions_integrated"
    """Predictive integration completed."""
    
    WORKSPACE_CANDIDATE_PREPARED = "workspace_candidate_prepared"
    """Workspace candidate prepared."""
    
    COMPOSITE_PROGRESS = "composite_progress"
    """Composite multi-path progress made."""
    
    PARTIAL_PROGRESS = "partial_progress"
    """Partial semantic progression achieved."""
    
    WAITING_FOR_EXTERNAL_RESULT = "waiting_for_external_result"
    """Awaiting externally supplied capability result."""
    
    WAITING_FOR_CONTEXT = "waiting_for_context"
    """Waiting for additional context."""
    
    NO_MEANINGFUL_RESULT = "no_meaningful_result"
    """No meaningful semantic progression occurred."""
    
    INSUFFICIENT_CONTEXT = "insufficient_context"
    """Context was insufficient to proceed."""
    
    INVALID_INPUT = "invalid_input"
    """Input validation failed."""
    
    UNRESOLVED = "unresolved"
    """Semantic issue remains unresolved."""
    
    FAILED = "failed"
    """Processing terminated with failure."""
    
    CANCELLED = "cancelled"
    """Processing was cancelled."""
    
    EXPIRED = "expired"
    """Processing expired due to time or context validity."""
    
    @classmethod
    def all_kinds(cls) -> tuple[str, ...]:
        """Return all valid outcome kind values as a tuple."""
        return (
            cls.THOUGHTS_GENERATED,
            cls.REFLECTION_COORDINATED,
            cls.SIMULATION_COORDINATED,
            cls.COUNTERFACTUAL_COORDINATED,
            cls.NARRATIVE_COORDINATED,
            cls.IDENTITY_INTEGRATED,
            cls.MEMORY_INTEGRATED,
            cls.PREDICTIONS_INTEGRATED,
            cls.WORKSPACE_CANDIDATE_PREPARED,
            cls.COMPOSITE_PROGRESS,
            cls.PARTIAL_PROGRESS,
            cls.WAITING_FOR_EXTERNAL_RESULT,
            cls.WAITING_FOR_CONTEXT,
            cls.NO_MEANINGFUL_RESULT,
            cls.INSUFFICIENT_CONTEXT,
            cls.INVALID_INPUT,
            cls.UNRESOLVED,
            cls.FAILED,
            cls.CANCELLED,
            cls.EXPIRED,
        )
    
    @classmethod
    def is_valid_kind(cls, value: str) -> bool:
        """Check if a string is a valid outcome kind value."""
        return value in cls.all_kinds()


# =============================================================================
# DEFAULT NETWORK CONTINUATION KINDS
# =============================================================================

class DefaultNetworkContinuationKind:
    """
    Canonical continuation kinds for Default Network recommendations.
    
    Continuation is advisory - it does not schedule or execute anything.
    """
    
    COMPLETE = "complete"
    """Current episode completed successfully."""
    
    CONTINUE_CURRENT_EPISODE = "continue_current_episode"
    """Continue processing current episode."""
    
    REQUEST_EXTERNAL_RESULT = "request_external_result"
    """Request externally supplied capability result."""
    
    REQUEST_CONTEXT_REFRESH = "request_context_refresh"
    """Refresh internal context."""
    
    REQUEST_ADDITIONAL_EVIDENCE = "request_additional_evidence"
    """Acquire additional evidence."""
    
    REQUEST_REFLECTION = "request_reflection"
    """Initiate reflection processing."""
    
    REQUEST_SIMULATION = "request_simulation"
    """Initiate simulation coordination."""
    
    REQUEST_COUNTERFACTUAL = "request_counterfactual"
    """Initiate counterfactual analysis."""
    
    REQUEST_NARRATIVE = "request_narrative"
    """Initiate narrative integration."""
    
    REQUEST_IDENTITY_REVIEW = "request_identity_review"
    """Review identity state."""
    
    REQUEST_MEMORY_INTEGRATION = "request_memory_integration"
    """Integrate memory content."""
    
    REQUEST_PREDICTIVE_INTEGRATION = "request_predictive_integration"
    """Integrate predictive content."""
    
    REQUEST_WORKSPACE_INTEGRATION = "request_workspace_integration"
    """Integrate workspace candidates."""
    
    WAIT_FOR_EXTERNAL_RESULT = "wait_for_external_result"
    """Wait for externally supplied result."""
    
    SUSPEND = "suspend"
    """Suspend current episode progression."""
    
    FAIL = "fail"
    """Mark processing as failed."""
    
    CANCEL = "cancel"
    """Cancel the current request."""
    
    @classmethod
    def all_kinds(cls) -> tuple[str, ...]:
        """Return all valid continuation kind values as a tuple."""
        return (
            cls.COMPLETE,
            cls.CONTINUE_CURRENT_EPISODE,
            cls.REQUEST_EXTERNAL_RESULT,
            cls.REQUEST_CONTEXT_REFRESH,
            cls.REQUEST_ADDITIONAL_EVIDENCE,
            cls.REQUEST_REFLECTION,
            cls.REQUEST_SIMULATION,
            cls.REQUEST_COUNTERFACTUAL,
            cls.REQUEST_NARRATIVE,
            cls.REQUEST_IDENTITY_REVIEW,
            cls.REQUEST_MEMORY_INTEGRATION,
            cls.REQUEST_PREDICTIVE_INTEGRATION,
            cls.REQUEST_WORKSPACE_INTEGRATION,
            cls.WAIT_FOR_EXTERNAL_RESULT,
            cls.SUSPEND,
            cls.FAIL,
            cls.CANCEL,
        )
    
    @classmethod
    def is_valid_kind(cls, value: str) -> bool:
        """Check if a string is a valid continuation kind value."""
        return value in cls.all_kinds()


# =============================================================================
# EXTERNAL REQUEST CATEGORIES
# =============================================================================

class DefaultNetworkExternalRequestCategory:
    """
    Canonical external request categories.
    
    These represent the types of external computation that may be requested.
    The network produces requests but NEVER executes them directly.
    """
    
    REFLECTION_CAPABILITY = "reflection_capability"
    """Reflection processing capability."""
    
    SIMULATION_CAPABILITY = "simulation_capability"
    """Simulation coordination capability."""
    
    IMAGINATION_CAPABILITY = "imagination_capability"
    """Imagination or creative generation capability."""
    
    WORLD_MODEL = "world_model"
    """World model query or inference capability."""
    
    REASONING_CAPABILITY = "reasoning_capability"
    """Logical reasoning capability."""
    
    NARRATIVE_CAPABILITY = "narrative_capability"
    """Narrative integration capability."""
    
    IDENTITY_CAPABILITY = "identity_capability"
    """Identity projection capability."""
    
    MEMORY_PROJECTION = "memory_projection"
    """Memory projection capability."""
    
    PREDICTIVE_CAPABILITY = "predictive_capability"
    """Predictive inference capability."""
    
    OBSERVATION_PROJECTION = "observation_projection"
    """Observation projection capability."""
    
    WORKSPACE_ADMISSION = "workspace_admission"
    """Workspace admission decision capability."""
    
    SECURITY_REVIEW = "security_review"
    """Security review capability."""
    
    DISCLOSURE_REVIEW = "disclosure_review"
    """Disclosure review capability."""
    
    EXECUTIVE_REVIEW = "executive_review"
    """Executive review capability."""
    
    ATTENTION_REVIEW = "attention_review"
    """Attention review capability."""
    
    OTHER_CAPABILITY = "other_capability"
    """Other capability type."""
    
    @classmethod
    def all_categories(cls) -> tuple[str, ...]:
        """Return all valid external request category values as a tuple."""
        return (
            cls.REFLECTION_CAPABILITY,
            cls.SIMULATION_CAPABILITY,
            cls.IMAGINATION_CAPABILITY,
            cls.WORLD_MODEL,
            cls.REASONING_CAPABILITY,
            cls.NARRATIVE_CAPABILITY,
            cls.IDENTITY_CAPABILITY,
            cls.MEMORY_PROJECTION,
            cls.PREDICTIVE_CAPABILITY,
            cls.OBSERVATION_PROJECTION,
            cls.WORKSPACE_ADMISSION,
            cls.SECURITY_REVIEW,
            cls.DISCLOSURE_REVIEW,
            cls.EXECUTIVE_REVIEW,
            cls.ATTENTION_REVIEW,
            cls.OTHER_CAPABILITY,
        )
    
    @classmethod
    def is_valid_category(cls, value: str) -> bool:
        """Check if a string is a valid external request category."""
        return value in cls.all_categories()


# =============================================================================
# DEFAULT NETWORK STATE REVISION
# =============================================================================

class DefaultNetworkStateRevision:
    """
    State revision tracking for Default Network.
    
    Revisions ensure deterministic replay and idempotent processing.
    Each state update produces a new revision number.
    """
    
    INITIAL = 1
    """Initial state revision."""
    
    @classmethod
    def next_revision(cls, current: int) -> int:
        """Compute the next revision number after incrementing."""
        return current + 1


# =============================================================================
# PROVENANCE SOURCES
# =============================================================================

class DefaultNetworkProvenanceSource:
    """
    Canonical sources of provenance for semantic products.
    
    Provenance tracks origin without embedding runtime references.
    """
    
    DEFAULT_NETWORK = "default_network"
    """Produced by the Default Network."""
    
    INTERNAL_CONTEXT = "internal_context"
    """Derived from internal context analysis."""
    
    MEMORY_PROJECTION = "memory_projection"
    """Derived from memory projection analysis."""
    
    IDENTITY_PROJECTION = "identity_projection"
    """Derived from identity projection analysis."""
    
    NARRATIVE_PROJECTION = "narrative_projection"
    """Derived from narrative projection analysis."""
    
    PREDICTIVE_PROJECTION = "predictive_projection"
    """Derived from predictive projection analysis."""
    
    EXTERNAL_CAPABILITY_RESULT = "external_capability_result"
    """Result from externally supplied capability."""
    
    @classmethod
    def all_sources(cls) -> tuple[str, ...]:
        """Return all valid provenance source values as a tuple."""
        return (
            cls.DEFAULT_NETWORK,
            cls.INTERNAL_CONTEXT,
            cls.MEMORY_PROJECTION,
            cls.IDENTITY_PROJECTION,
            cls.NARRATIVE_PROJECTION,
            cls.PREDICTIVE_PROJECTION,
            cls.EXTERNAL_CAPABILITY_RESULT,
        )