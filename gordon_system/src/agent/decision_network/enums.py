# Gordon Cognitive Architecture - Phase 4.5.1
# ===========================================

"""
Action Semantic Enumerations

These enumerations define semantic categories for Actions without any
executable behavior or runtime state.

All values are string constants that must remain stable across versions.
No algorithmic meaning should be attached to enum values.
"""

from enum import Enum, auto


# =============================================================================
# ACTION KINDS - Semantic categories of operations
# =============================================================================

class ActionKind(Enum):
    """
    High-level semantic categories for Actions.
    
    These classify the fundamental nature of the operation. Each kind
    represents a coherent semantic category that cuts across different
    domains and execution mechanisms.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Informational operations (read-only, no state change)
    OBSERVATIONAL = "observational"
    """Observe or inspect without modification."""
    
    INFORMATIONAL = "informational"
    """Gather information without necessarily storing it."""
    
    VALIDATION = "validation"
    """Verify properties or conditions."""
    
    COMPARISON = "comparison"
    """Compare states or values."""
    
    # Computational operations
    COMPUTATIONAL = "computational"
    """Perform computation or reasoning."""
    
    CALCULATION = "calculation"
    """Mathematical or logical calculation."""
    
    REASONING = "reasoning"
    """Logical inference or deduction."""
    
    ANALYSIS = "analysis"
    """Break down into components for understanding."""
    
    # Transformation operations (modify existing state)
    TRANSFORMATIONAL = "transformational"
    """Modify existing state while preserving identity."""
    
    MODIFICATION = "modification"
    """Change properties of an existing target."""
    
    UPDATE = "update"
    """Update existing information or configuration."""
    
    TRANSFER = "transfer"
    """Move from one location or form to another."""
    
    # Creation operations
    CREATION = "creation"
    """Create new entities or state."""
    
    CONSTRUCTION = "construction"
    """Build new structures or compositions."""
    
    GENERATION = "generation"
    """Generate new content or artifacts."""
    
    ACQUISITION = "acquisition"
    """Acquire new resources or capabilities."""
    
    # Removal operations
    REMOVAL = "removal"
    """Remove existing entities or state."""
    
    DELETION = "deletion"
    """Delete information or artifacts."""
    
    DESTRUCTION = "destruction"
    """Destroy physical or logical entities."""
    
    REVERSION = "reversion"
    """Revert to a previous state."""
    
    # Communication operations
    COMMUNICATIVE = "communicative"
    """Exchange information with other systems."""
    
    NOTIFICATION = "notification"
    """Send notifications or alerts."""
    
    REQUEST = "request"
    """Request services or information."""
    
    PROMPT = "prompt"
    """Prompt external input or confirmation."""
    
    # Delegation operations
    DELEGATIVE = "delegative"
    """Delegate work to other components."""
    
    ASSIGNMENT = "assignment"
    """Assign tasks or responsibilities."""
    
    REFERRAL = "referral"
    """Refer to another authority or component."""
    
    # Resource operations
    RESOURCE = "resource"
    """Manage resources."""
    
    ALLOCATION = "allocation"
    """Allocate resources to purposes."""
    
    DEALLOCATION = "deallocation"
    """Release allocated resources."""
    
    ACQUISITION_RESOURCE = "acquisition_resource"
    """Acquire new resources."""
    
    # Memory operations
    MEMORY = "memory"
    """Manage working or long-term memory."""
    
    RETRIEVAL = "retrieval"
    """Retrieve stored information."""
    
    PERSISTENCE = "persistence"
    """Persist state to storage."""
    
    CLEARING = "clearing"
    """Clear memory or cache."""
    
    # Workspace operations
    WORKSPACE = "workspace"
    """Manage workspace artifacts and context."""
    
    ADMISSION = "admission"
    """Admit new artifacts to workspace."""
    
    REJECTION = "rejection"
    """Reject artifacts from workspace."""
    
    REFACTORING = "refactoring"
    """Reorganize workspace structure."""
    
    # Configuration operations
    CONFIGURATION = "configuration"
    """Change configuration or settings."""
    
    ENABLING = "enabling"
    """Enable features or capabilities."""
    
    DISABLING = "disabling"
    """Disable features or capabilities."""
    
    RECONFIGURATION = "reconfiguration"
    """Reconfigure existing setup."""
    
    # Control operations
    CONTROL = "control"
    """Control execution flow or behavior."""
    
    STARTING = "starting"
    """Start processes or activities."""
    
    STOPPING = "stopping"
    """Stop processes or activities."""
    
    SUSPENDING = "suspending"
    """Suspend temporarily."""
    
    RESUMING = "resuming"
    """Resume suspended operations."""
    
    # Recovery operations
    RECOVERY = "recovery"
    """Recover from failure or error."""
    
    ROLLBACK = "rollback"
    """Rollback to previous state."""
    
    COMPENSATION = "compensation"
    """Compensate for effects of another action."""
    
    MITIGATION = "mitigation"
    """Mitigate negative effects."""
    
    RESTORATION = "restoration"
    """Restore from backup or snapshot."""
    
    # Security-sensitive operations
    SECURITY_SENSITIVE = "security_sensitive"
    """Security-critical operations."""
    
    AUTHORIZATION = "authorization"
    """Grant or modify authorization."""
    
    AUTHENTICATION = "authentication"
    """Authenticate credentials."""
    
    AUDITING = "auditing"
    """Create audit records."""
    
    ENCRYPTION = "encryption"
    """Encrypt data."""
    
    DECRYPTION = "decryption"
    """Decrypt data."""
    
    # External interaction
    EXTERNAL_INTERACTION = "external_interaction"
    """Interact with external systems."""
    
    API_CALL = "api_call"
    """Invoke external API."""
    
    NETWORK_REQUEST = "network_request"
    """Make network request."""
    
    DATABASE_QUERY = "database_query"
    """Query database."""
    
    # General operations
    GENERAL = "general"
    """General-purpose operation."""
    
    WAITING = "waiting"
    """Wait for condition or timeout."""
    
    SYNCHRONIZATION = "synchronization"
    """Synchronize with other operations."""
    
    MONITORING = "monitoring"
    """Monitor system state."""
    
    LOGGING = "logging"
    """Log information."""
    
    # Unknown / undetermined
    UNKNOWN = "unknown"
    """Operation kind is unknown or undetermined."""
    
    @property
    def is_informational(self) -> bool:
        """Check if this kind is informational (read-only)."""
        return self in (
            ActionKind.OBSERVATIONAL,
            ActionKind.INFORMATIONAL,
            ActionKind.VALIDATION,
            ActionKind.COMPARISON,
        )
    
    @property
    def is_transformative(self) -> bool:
        """Check if this kind transforms state."""
        return self in (
            ActionKind.TRANSFORMATIONAL,
            ActionKind.MODIFICATION,
            ActionKind.UPDATE,
            ActionKind.TRANSFER,
        )
    
    @property
    def is_creation(self) -> bool:
        """Check if this kind creates new state."""
        return self in (
            ActionKind.CREATION,
            ActionKind.CONSTRUCTION,
            ActionKind.GENERATION,
            ActionKind.ACQUISITION,
        )
    
    @property
    def is_destructive(self) -> bool:
        """Check if this kind removes state."""
        return self in (
            ActionKind.REMOVAL,
            ActionKind.DELETION,
            ActionKind.DESTRUCTION,
            ActionKind.REVERSION,
        )


# =============================================================================
# ACTION PURPOSE - Why the action exists
# =============================================================================

class ActionPurpose(Enum):
    """
    The purpose or intent of an Action.
    
    Purpose describes why the operation is needed in semantic terms,
    not how it accomplishes that goal.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # Information purposes
    OBSERVE = "observe"
    """Observe or monitor state."""
    
    INSPECT = "inspect"
    """Inspect structure or composition."""
    
    READ = "read"
    """Read data or content."""
    
    ACQUIRE_INFORMATION = "acquire_information"
    """Acquire information for later use."""
    
    # Validation purposes
    VALIDATE = "validate"
    """Validate properties or conditions."""
    
    COMPARE = "compare"
    """Compare states or values."""
    
    CHECK = "check"
    """Check conditions or requirements."""
    
    # Transformation purposes
    TRANSFORM = "transform"
    """Transform data or state."""
    
    CREATE = "create"
    """Create new entities."""
    
    MODIFY = "modify"
    """Modify existing entities."""
    
    REMOVE = "remove"
    """Remove entities."""
    
    MOVE = "move"
    """Move from one location to another."""
    
    COPY = "copy"
    """Copy data or artifacts."""
    
    # Communication purposes
    COMMUNICATE = "communicate"
    """Communicate information."""
    
    NOTIFICATION = "notification"
    """Send notification."""
    
    REQUEST = "request"
    """Request service or information."""
    
    QUERY = "query"
    """Query for information."""
    
    # Delegation purposes
    DELEGATE = "delegate"
    """Delegate work to other components."""
    
    REQUEST_AUTHORIZATION = "request_authorization"
    """Request authorization."""
    
    AUTHENTICATE = "authenticate"
    """Authenticate credentials."""
    
    # Resource purposes
    RESERVE = "reserve"
    """Reserve resources."""
    
    RELEASE = "release"
    """Release reserved resources."""
    
    ALLOCATE = "allocate"
    """Allocate resources."""
    
    DEALLOCATE = "deallocate"
    """Deallocate resources."""
    
    # Monitoring and control purposes
    MONITOR = "monitor"
    """Monitor system state."""
    
    RECOVER = "recover"
    """Recover from failure."""
    
    COMPENSATE = "compensate"
    """Compensate for effects."""
    
    ROLLBACK = "rollback"
    """Rollback to previous state."""
    
    # Temporal purposes
    WAIT = "wait"
    """Wait for condition or timeout."""
    
    SYNCHRONIZE = "synchronize"
    """Synchronize with other operations."""
    
    PERSIST = "persist"
    """Persist state."""
    
    RETRIEVE = "retrieve"
    """Retrieve stored information."""
    
    INDEX = "index"
    """Index for later retrieval."""
    
    ARCHIVE = "archive"
    """Archive data or artifacts."""
    
    # General purposes
    GENERAL = "general"
    """General operation purpose."""
    
    UNKNOWN = "unknown"
    """Purpose is unknown or undetermined."""
    
    @property
    def is_informational(self) -> bool:
        """Check if purpose is information-focused."""
        return self in (
            ActionPurpose.OBSERVE,
            ActionPurpose.INSPECT,
            ActionPurpose.READ,
            ActionPurpose.ACQUIRE_INFORMATION,
            ActionPurpose.VALIDATE,
            ActionPurpose.COMPARE,
            ActionPurpose.CHECK,
            ActionPurpose.RETRIEVE,
            ActionPurpose.QUERY,
        )
    
    @property
    def is_mutating(self) -> bool:
        """Check if purpose involves state mutation."""
        return self in (
            ActionPurpose.TRANSFORM,
            ActionPurpose.CREATE,
            ActionPurpose.MODIFY,
            ActionPurpose.REMOVE,
            ActionPurpose.MOVE,
            ActionPurpose.COPY,
            ActionPurpose.ALLOCATE,
            ActionPurpose.DEALLOCATE,
        )


# =============================================================================
# ACTION MODALITY - State change behavior
# =============================================================================

class ActionModality(Enum):
    """
    The modality or state change behavior of an Action.
    
    Modality describes the expected effect on system state, independent
    of the specific mechanism used to achieve that effect.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    OBSERVE_ONLY = "observe_only"
    """No state change, observation only."""
    
    READ_ONLY = "read_only"
    """Read access, no modification."""
    
    STATE_PRESERVING = "state_preserving"
    """Preserves existing state while producing effects."""
    
    STATE_MODIFYING = "state_modifying"
    """Modifies existing state."""
    
    STATE_CREATING = "state_creating"
    """Creates new state or entities."""
    
    STATE_DELETING = "state_deleting"
    """Deletes or removes state."""
    
    COMMUNICATIVE = "communicative"
    """Transmits information without local state change."""
    
    RESOURCE_ACQUIRING = "resource_acquiring"
    """Acquires resources or capabilities."""
    
    RESOURCE_RELEASING = "resource_releasing"
    """Releases resources or capabilities."""
    
    CONTROL_TRANSFERRING = "control_transferring"
    """Transfers control or authority."""
    
    AUTHORITY_CHANGING = "authority_changing"
    """Changes authorization or authority."""
    
    IRREVERSIBLE = "irreversible"
    """Fundamentally irreversible operation."""
    
    UNKNOWN = "unknown"
    """Modality is unknown or undetermined."""
    
    @property
    def is_read_only(self) -> bool:
        """Check if modality is read-only (no state change)."""
        return self in (
            ActionModality.OBSERVE_ONLY,
            ActionModality.READ_ONLY,
        )
    
    @property
    def is_state_changing(self) -> bool:
        """Check if modality changes state."""
        return self in (
            ActionModality.STATE_MODIFYING,
            ActionModality.STATE_CREATING,
            ActionModality.STATE_DELETING,
        )
    
    @property
    def is_mutating(self) -> bool:
        """Check if modality involves mutation."""
        return not self.is_read_only


# =============================================================================
# ACTION GRANULARITY - Operational scope
# =============================================================================

class ActionGranularity(Enum):
    """
    The granularity or scope of an Action.
    
    Granularity describes whether the action represents a single semantic
    operation, multiple operations, or a composite reference.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    ATOMIC_SEMANTIC_OPERATION = "atomic_semantic_operation"
    """Single atomic semantic operation."""
    
    SINGLE_TARGET_OPERATION = "single_target_operation"
    """Operation on one target entity."""
    
    MULTI_TARGET_OPERATION = "multi_target_operation"
    """Operation on multiple ordered targets."""
    
    BATCH_OPERATION = "batch_operation"
    """Batch operation across many similar targets."""
    
    COMPOSITE_OPERATION_REFERENCE = "composite_operation_reference"
    """Reference to composite behavior (not the composition itself)."""
    
    OPEN_ENDED_OPERATION = "open_ended_operation"
    """Operation with potentially unbounded scope or duration."""
    
    UNKNOWN = "unknown"
    """Granularity is unknown or undetermined."""
    
    @property
    def is_bounded(self) -> bool:
        """Check if operation has bounded scope."""
        return self in (
            ActionGranularity.ATOMIC_SEMANTIC_OPERATION,
            ActionGranularity.SINGLE_TARGET_OPERATION,
            ActionGranularity.MULTI_TARGET_OPERATION,
            ActionGranularity.BATCH_OPERATION,
        )


# =============================================================================
# ACTION HORIZON - Temporal persistence expectations
# =============================================================================

class ActionHorizon(Enum):
    """
    The temporal persistence horizon for an Action.
    
    Horizon describes how long the semantic effect or relevance of the
    action is expected to persist, not runtime duration.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    IMMEDIATE = "immediate"
    """Valid until next evaluation cycle."""
    
    NEAR_TERM = "near_term"
    """Valid for minutes to hours."""
    
    TASK_BOUND = "task_bound"
    """Valid within current task scope."""
    
    SESSION_BOUND = "session_bound"
    """Valid for current session."""
    
    PROGRAM_BOUND = "program_bound"
    """Valid for program execution lifetime."""
    
    PERSISTENT_EFFECT = "persistent_effect"
    """Effect intended to persist indefinitely."""
    
    UNKNOWN = "unknown"
    """Horizon is unknown or undetermined."""
    
    @property
    def is_temporary(self) -> bool:
        """Check if horizon indicates temporary effect."""
        return self in (
            ActionHorizon.IMMEDIATE,
            ActionHorizon.NEAR_TERM,
            ActionHorizon.TASK_BOUND,
            ActionHorizon.SESSION_BOUND,
        )


# =============================================================================
# ACTION REVERSIBILITY KINDS
# =============================================================================

class ActionReversibilityKind(Enum):
    """
    Categories of reversibility for Actions.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    FULLY_REVERSIBLE = "fully_reversible"
    """Can be fully reversed to prior state."""
    
    REVERSIBLE_WITH_PRECONDITIONS = "reversible_with_preconditions"
    """Reversal possible when specific conditions are met."""
    
    COMPENSATABLE = "compensatable"
    """Can be compensated for (not necessarily restored)."""
    
    PARTIALLY_REVERSIBLE = "partially_reversible"
    """Only partial reversal possible."""
    
    PRACTICALLY_IRREVERSIBLE = "practically_irreversible"
    """Effectively irreversible in practice."""
    
    IRREVERSIBLE = "irreversible"
    """Fundamentally irreversible operation."""
    
    UNKNOWN = "unknown"
    """Reversibility is unknown or undetermined."""


# =============================================================================
# ACTION IDEMPOTENCY KINDS
# =============================================================================

class ActionIdempotencyKind(Enum):
    """
    Categories of idempotency for Actions.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    IDEMPOTENT = "idempotent"
    """Multiple identical executions produce same result as single execution."""
    
    IDEMPOTENT_WITH_KEY = "idempotent_with_key"
    """Idempotent when provided with an idempotency key."""
    
    CONDITIONALLY_IDEMPOTENT = "conditionally_idempotent"
    """Idempotent only under specific conditions."""
    
    NON_IDEMPOTENT = "non_idempotent"
    """Execution may have different effects each invocation."""
    
    UNKNOWN = "unknown"
    """Idempotency is unknown or undetermined."""


# =============================================================================
# ACTION ATOMICITY KINDS
# =============================================================================

class ActionAtomicityKind(Enum):
    """
    Categories of atomicity for Actions.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    SEMANTICALLY_ATOMIC = "semantically_atomic"
    """Semantically indivisible operation."""
    
    TRANSACTIONALLY_ATOMIC = "transactionally_atomic"
    """Atomically executed within transactional context."""
    
    PARTIALLY_ATOMIC = "partially_atomic"
    """Part of larger atomic operation."""
    
    MULTI_STAGE = "multi_stage"
    """Multi-stage operation with clear boundaries."""
    
    NOT_ATOMIC = "not_atomic"
    """Not an atomic operation."""
    
    UNKNOWN = "unknown"
    """Atomicity is unknown or undetermined."""


# =============================================================================
# ACTION RISK KINDS
# =============================================================================

class ActionRiskKind(Enum):
    """
    Categories of risk associated with Actions.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    DATA_LOSS = "data_loss"
    """Potential for data loss or corruption."""
    
    DATA_CORRUPTION = "data_corruption"
    """Potential for data corruption."""
    
    PRIVACY = "privacy"
    """Privacy exposure risk."""
    
    SECURITY = "security"
    """Security vulnerability or breach."""
    
    AUTHORITY = "authority"
    """Authority escalation or violation."""
    
    POLICY = "policy"
    """Policy violation."""
    
    RESOURCE = "resource"
    """Resource exhaustion or waste."""
    
    AVAILABILITY = "availability"
    """Service availability impact."""
    
    PERFORMANCE = "performance"
    """Performance degradation."""
    
    TEMPORAL = "temporal"
    """Temporal ordering issues."""
    
    TARGET = "target"
    """Target-specific risks."""
    
    IRREVERSIBILITY = "irreversibility"
    """Irreversible effect risk."""
    
    ROLLBACK_FAILURE = "rollback_failure"
    """Rollback may fail."""
    
    COMPENSATION_FAILURE = "compensation_failure"
    """Compensation may fail."""
    
    EXTERNAL_DEPENDENCY = "external_dependency"
    """Dependency on external system."""
    
    COMMUNICATION = "communication"
    """Communication failure risk."""
    
    USER_IMPACT = "user_impact"
    """User-facing impact."""
    
    ARCHITECTURAL = "architectural"
    """Architectural integrity risk."""
    
    UNKNOWN = "unknown"
    """Risk kind is unknown or undetermined."""


# =============================================================================
# ACTION RISK SEVERITY
# =============================================================================

class ActionRiskSeverity(Enum):
    """
    Severity levels for identified risks.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    TRIVIAL = "trivial"
    """Negligible impact, easily recoverable."""
    
    LOW = "low"
    """Minor impact, manageable risk."""
    
    MEDIUM = "medium"
    """Moderate impact, requires consideration."""
    
    HIGH = "high"
    """Significant impact, needs careful review."""
    
    CRITICAL = "critical"
    """Severe impact, likely unacceptable."""
    
    UNKNOWN = "unknown"
    """Severity is unknown or undetermined."""


# =============================================================================
# ACTION LIFECYCLE STATES - Semantic position in existence
# =============================================================================

class ActionLifecycleState(Enum):
    """
    States in the semantic lifecycle of an Action.
    
    Lifecycle states describe where the Action is in its existence from
    a semantic perspective, NOT runtime progress or execution state.
    
    Runtime-neutral: Yes
    Executable: No
    
    IMPORTANT: This excludes runtime execution states like "RUNNING",
               "SUCCEEDED", "FAILED" - those belong to Execution monitoring.
    """
    
    # Pre-semantic states (not yet valid)
    DRAFT = "draft"
    """Initial formulation, not yet valid for consideration."""
    
    PROPOSED = "proposed"
    """Proposed for consideration but not validated."""
    
    CANDIDATE = "candidate"
    """Valid candidate for selection."""
    
    # Normalized states (ready for evaluation)
    NORMALIZED = "normalized"
    """Semantic structure is normalized and validated."""
    
    VALIDATED = "validated"
    """Preconditions and constraints have been checked."""
    
    ELIGIBLE = "eligible"
    """Meets all eligibility criteria for selection."""
    
    INELIGIBLE = "ineligible"
    """Does not meet eligibility criteria."""
    
    # Evaluated states
    EVALUATED = "evaluated"
    """Has been evaluated by Action Selection capability."""
    
    SELECTABLE = "selectable"
    """Ready to be selected by Action Selection."""
    
    # Post-selection states (selected but not executed)
    SELECTED = "selected"
    """Selected for execution (but not yet executed)."""
    
    # Authorization states
    AUTHORIZATION_PENDING = "authorization_pending"
    """Authorization review required before execution."""
    
    AUTHORIZED = "authorized"
    """Authorized for execution."""
    
    AUTHORIZATION_DENIED = "authorized_denied"
    """Authorization denied."""
    
    # Execution preparation states
    EXECUTION_REVIEW_PENDING = "execution_review_pending"
    """Execution review pending."""
    
    EXECUTION_READY = "execution_ready"
    """Ready to be executed."""
    
    # Terminal/invalidated states
    STALE = "stale"
    """No longer current due to context changes."""
    
    INVALIDATED = "invalidated"
    """Invalidated by external event or condition."""
    
    SUPERSEDED = "superseded"
    """Superseded by another Action."""
    
    EXPIRED = "expired"
    """Expired by time constraint."""
    
    CANCELLED = "cancelled"
    """Cancelled before execution."""
    
    REJECTED = "rejected"
    """Rejected during selection or evaluation."""
    
    TERMINAL_REFERENCE = "terminal_reference"
    """Reference to a terminal action (for history)."""
    
    UNKNOWN = "unknown"
    """Lifecycle state is unknown or undetermined."""


# =============================================================================
# ACTION PRECONDITION KINDS
# =============================================================================

class ActionPreconditionKind(Enum):
    """
    Categories of preconditions for Actions.
    
    Runtime-neutral: Yes
    Executable: No
    
    Preconditions are semantic propositions that must hold before execution.
    They do not evaluate themselves - they are descriptions.
    """
    
    TARGET_EXISTS = "target_exists"
    """Target entity must exist."""
    
    TARGET_REVISION_MATCHES = "target_revision_matches"
    """Target must be at specific revision."""
    
    TARGET_STATE_MATCHES = "target_state_matches"
    """Target state must match expected value."""
    
    CAPABILITY_AVAILABLE = "capability_available"
    """Required capability must be available."""
    
    RESOURCE_AVAILABLE = "resource_available"
    """Required resource must be available."""
    
    AUTHORITY_VALID = "authority_valid"
    """Authority must be valid."""
    
    POLICY_COMPATIBLE = "policy_compatible"
    """Action must be compatible with Policy."""
    
    SECURITY_COMPATIBLE = "security_compatible"
    """Action must be compatible with Security rules."""
    
    CONTEXT_CURRENT = "context_current"
    """Context must be current."""
    
    DEPENDENCY_SATISFIED = "dependency_satisfied"
    """Dependencies must be satisfied."""
    
    PLAN_STEP_READY = "plan_step_ready"
    """Plan step must be ready for execution."""
    
    DECISION_ACTIVE = "decision_active"
    """Governing Decision must be active."""
    
    COMMITMENT_ACTIVE = "commitment_active"
    """Commitment must be active."""
    
    PRIVACY_SCOPE_VALID = "privacy_scope_valid"
    """Privacy scope must be valid."""
    
    USER_CONFIRMATION_PRESENT = "user_confirmation_present"
    """User confirmation must be present."""
    
    EXTERNAL_APPROVAL_PRESENT = "external_approval_present"
    """External approval must be present."""
    
    IDEMPOTENCY_KEY_AVAILABLE = "idempotency_key_available"
    """Idempotency key required and available."""
    
    ROLLBACK_AVAILABLE = "rollback_available"
    """Rollback mechanism must be available."""
    
    GENERAL = "general"
    """General semantic proposition."""
    
    UNKNOWN = "unknown"
    """Precondition kind is unknown or undetermined."""


# =============================================================================
# ACTION PRECONDITION STATUS
# =============================================================================

class ActionPreconditionStatus(Enum):
    """
    Status values for precondition evaluation.
    
    Runtime-neutral: Yes
    Executable: No
    
    These are semantic projections, not live evaluations.
    """
    
    SATISFIED = "satisfied"
    """All conditions are met."""
    
    SATISFIED_WITH_CONDITIONS = "satisfied_with_conditions"
    """Met but with specific conditions or limitations."""
    
    UNSATISFIED = "unsatisfied"
    """Conditions not met."""
    
    UNKNOWN = "unknown"
    """Cannot determine status without live evaluation."""
    
    STALE = "stale"
    """May have been satisfied previously but context has changed."""
    
    NOT_APPLICABLE = "not_applicable"
    """Precondition does not apply in current context."""
    
    REQUIRES_VALIDATION = "requires_validation"
    """Requires external validation before use."""
    
    REQUIRES_AUTHORITY = "requires_authority"
    """Requires authority review."""
    
    REQUIRES_POLICY_REVIEW = "requires_policy_review"
    """Requires Policy review."""
    
    REQUIRES_SECURITY_REVIEW = "requires_security_review"
    """Requires Security review."""


# =============================================================================
# ACTION EFFECT KINDS
# =============================================================================

class ActionEffectKind(Enum):
    """
    Categories of intended Effects for Actions.
    
    Runtime-neutral: Yes
    Executable: No
    
    Intended effects describe what the Action is designed to produce,
    not proof that it occurred.
    """
    
    INFORMATION_ACQUIRED = "information_acquired"
    """Information was acquired."""
    
    STATE_OBSERVED = "state_observed"
    """State was observed."""
    
    STATE_CREATED = "state_created"
    """New state was created."""
    
    STATE_MODIFIED = "state_modified"
    """Existing state was modified."""
    
    STATE_REMOVED = "state_removed"
    """State was removed."""
    
    STATE_MOVED = "state_moved"
    """State was moved."""
    
    STATE_COPIED = "state_copied"
    """State was copied."""
    
    MESSAGE_EMITTED = "message_emitted"
    """Message was emitted."""
    
    RESOURCE_RESERVED = "resource_reserved"
    """Resource was reserved."""
    
    RESOURCE_RELEASED = "resource_released"
    """Resource was released."""
    
    CAPABILITY_ACTIVATED = "capability_activated"
    """Capability was activated."""
    
    CAPABILITY_DEACTIVATED = "capability_deactivated"
    """Capability was deactivated."""
    
    CONFIGURATION_CHANGED = "configuration_changed"
    """Configuration was changed."""
    
    AUTHORITY_REQUESTED = "authority_requested"
    """Authority request was made."""
    
    ATTENTION_REQUESTED = "attention_requested"
    """Attention was requested."""
    
    MEMORY_REQUESTED = "memory_requested"
    """Memory allocation or retrieval requested."""
    
    WORKSPACE_ADMISSION_REQUESTED = "workspace_admission_requested"
    """Workspace admission was requested."""
    
    RECOVERY_REQUESTED = "recovery_requested"
    """Recovery action was requested."""
    
    NO_STATE_CHANGE = "no_state_change"
    """No state change intended."""
    
    UNKNOWN = "unknown"
    """Effect kind is unknown or undetermined."""


# =============================================================================
# ACTION SIDE EFFECT KINDS
# =============================================================================

class ActionSideEffectKind(Enum):
    """
    Categories of Side Effects for Actions.
    
    Runtime-neutral: Yes
    Executable: No
    
    Side Effects are possible secondary consequences, not the primary purpose.
    """
    
    RESOURCE_CONSUMPTION = "resource_consumption"
    """Consumes resources."""
    
    CACHE_CHANGE = "cache_change"
    """Affects cache state."""
    
    AUDIT_ENTRY = "audit_entry"
    """Creates audit record."""
    
    EXTERNAL_NOTIFICATION = "external_notification"
    """Triggers external notification."""
    
    TARGET_METADATA_CHANGE = "target_metadata_change"
    """Changes target metadata."""
    
    LATENCY = "latency"
    """Introduces latency."""
    
    LOCK_ACQUISITION = "lock_acquisition"
    """Acquires lock."""
    
    TEMPORARY_UNAVAILABILITY = "temporary_unavailability"
    """Causes temporary unavailability."""
    
    PRIVACY_EXPOSURE = "privacy_exposure"
    """Exposes privacy information."""
    
    SECURITY_SURFACE_CHANGE = "security_surface_change"
    """Changes security surface area."""
    
    USER_VISIBLE_CHANGE = "user_visible_change"
    """Visible to user."""
    
    PERSISTENT_STORAGE_CHANGE = "persistent_storage_change"
    """Affects persistent storage."""
    
    UNKNOWN = "unknown"
    """Side effect kind is unknown or undetermined."""


# =============================================================================
# ACTION EFFECT RELATION
# =============================================================================

class ActionEffectRelation(Enum):
    """
    Relationships between Effects.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    CAUSES = "causes"
    """Direct causal relationship."""
    
    MAY_CAUSE = "may_cause"
    """Potential causal relationship."""
    
    ENABLES = "enables"
    """Enables subsequent effect or action."""
    
    DISABLES = "disables"
    """Disables subsequent effect or action."""
    
    INVALIDATES = "invalidates"
    """Invalidates other action or state."""
    
    PRESERVES = "preserves"
    """Preserves existing state."""
    
    COMPENSATES_FOR = "compensates_for"
    """Compensates for another effect."""
    
    REVERSES = "reverses"
    """Reverses previous effect."""
    
    CONFLICTS_WITH = "conflicts_with"
    """Conflicts with another effect."""
    
    DEPENDS_ON = "depends_on"
    """Depends on another effect."""
    
    UNKNOWN = "unknown"
    """Effect relation is unknown or undetermined."""


# =============================================================================
# ACTION REQUIREMENT KIND
# =============================================================================

class ActionRequirementKind(Enum):
    """
    Categories of requirements for Actions.
    
    Runtime-neutral: Yes
    Executable: No
    
    Requirements describe what must be available but do not allocate it.
    """
    
    CAPABILITY = "capability"
    """Requires specific capability."""
    
    RESOURCE = "resource"
    """Requires resource allocation."""
    
    AUTHORITY = "authority"
    """Requires authority."""
    
    POLICY_REVIEW = "policy_review"
    """Policy review required."""
    
    SECURITY_REVIEW = "security_review"
    """Security review required."""
    
    TARGET_ACCESS = "target_access"
    """Must be able to access target."""
    
    TARGET_LOCK = "target_lock"
    """Must acquire lock on target."""
    
    NETWORK_ACCESS = "network_access"
    """Requires network access."""
    
    FILESYSTEM_ACCESS = "filesystem_access"
    """Requires filesystem access."""
    
    MEMORY_ACCESS = "memory_access"
    """Requires memory access."""
    
    WORKSPACE_ACCESS = "workspace_access"
    """Requires workspace access."""
    
    COMMUNICATION_CHANNEL = "communication_channel"
    """Requires communication channel."""
    
    USER_CONFIRMATION = "user_confirmation"
    """User confirmation required."""
    
    PLAN_REFERENCE = "plan_reference"
    """Plan reference required."""
    
    REASONING_REFERENCE = "reasoning_reference"
    """Reasoning reference required."""
    
    MONITORING = "monitoring"
    """Monitoring required."""
    
    ROLLBACK_SUPPORT = "rollback_support"
    """Rollback support must be available."""
    
    COMPENSATION_SUPPORT = "compensation_support"
    """Compensation support must be available."""
    
    AUDIT_SUPPORT = "audit_support"
    """Audit support required."""
    
    PRIVACY_SUPPORT = "privacy_support"
    """Privacy support required."""
    
    GENERAL = "general"
    """General requirement."""
    
    UNKNOWN = "unknown"
    """Requirement kind is unknown or undetermined."""


# =============================================================================
# ACTION CONSTRAINT KIND
# =============================================================================

class ActionConstraintKind(Enum):
    """
    Categories of constraints on Actions.
    
    Runtime-neutral: Yes
    Executable: No
    
    Constraints are conditions that must hold, often from external sources.
    """
    
    DECISION = "decision"
    """Governed by specific Decision."""
    
    GOAL = "goal"
    """Must align with Goal."""
    
    COMMITMENT = "commitment"
    """Must respect Commitment."""
    
    STRATEGY = "strategy"
    """Must follow Strategy."""
    
    PLAN = "plan"
    """Must conform to Plan."""
    
    POLICY = "policy"
    """Policy constraint."""
    
    SECURITY = "security"
    """Security rule."""
    
    AUTHORITY = "authority"
    """Authority requirement."""
    
    TARGET = "target"
    """Target-specific constraint."""
    
    CAPABILITY = "capability"
    """Capability requirement or limitation."""
    
    RESOURCE = "resource"
    """Resource constraint."""
    
    TEMPORAL = "temporal"
    """Temporal constraint (deadline, etc.)."""
    
    PRIVACY = "privacy"
    """Privacy constraint."""
    
    DISCLOSURE = "disclosure"
    """Disclosure scope constraint."""
    
    REVERSIBILITY = "reversibility"
    """Reversibility requirement."""
    
    IDEMPOTENCY = "idempotency"
    """Idempotency requirement."""
    
    ROLLBACK = "rollback"
    """Rollback requirement."""
    
    COMPENSATION = "compensation"
    """Compensation requirement."""
    
    SIDE_EFFECT = "side_effect"
    """Side effect constraint."""
    
    OUTCOME = "outcome"
    """Outcome expectation constraint."""
    
    EXECUTION_ENVIRONMENT = "execution_environment"
    """Execution environment constraint."""
    
    GENERAL = "general"
    """General constraint."""
    
    UNKNOWN = "unknown"
    """Constraint kind is unknown or undetermined."""


# =============================================================================
# ACTION DEPENDENCY KIND
# =============================================================================

class ActionDependencyKind(Enum):
    """
    Categories of dependencies between Actions.
    
    Runtime-neutral: Yes
    Executable: No
    
    Dependencies are semantic relationships, not runtime futures.
    """
    
    REQUIRES_ACTION = "requires_action"
    """Requires another action to complete first."""
    
    REQUIRES_PLAN_STEP = "requires_plan_step"
    """Requires specific plan step completion."""
    
    REQUIRES_DECISION = "requires_decision"
    """Requires Decision to be active."""
    
    REQUIRES_COMMITMENT = "requires_commitment"
    """Requires Commitment to be active."""
    
    REQUIRES_CAPABILITY = "requires_capability"
    """Requires capability to be available."""
    
    REQUIRES_RESOURCE = "requires_resource"
    """Requires resource to be available."""
    
    REQUIRES_AUTHORITY = "requires_authority"
    """Requires authority to be valid."""
    
    REQUIRES_POLICY_REVIEW = "requires_policy_review"
    """Policy review required before dependency satisfied."""
    
    REQUIRES_SECURITY_REVIEW = "requires_security_review"
    """Security review required before dependency satisfied."""
    
    REQUIRES_CONTEXT = "requires_context"
    """Requires specific context to be current."""
    
    REQUIRES_TARGET_REVISION = "requires_target_revision"
    """Target must be at expected revision."""
    
    REQUIRES_EVIDENCE = "requires_evidence"
    """Requires evidence to be available."""
    
    PRECEDES_ACTION = "precedes_action"
    """Must precede another action in sequence."""
    
    FOLLOWS_ACTION = "follows_action"
    """Must follow another action in sequence."""
    
    CONFLICTS_WITH_ACTION = "conflicts_with_action"
    """Conflicts with another action."""
    
    INVALIDATES_ACTION = "invalidates_action"
    """Invalidates another action."""
    
    ENABLES_ACTION = "enables_action"
    """Enables another action."""
    
    UNKNOWN = "unknown"
    """Dependency kind is unknown or undetermined."""


__all__ = [
    # Kinds
    "ActionKind",
    "ActionPurpose",
    "ActionModality",
    "ActionGranularity",
    "ActionHorizon",
    # Safety semantics
    "ActionReversibilityKind",
    "ActionIdempotencyKind",
    "ActionAtomicityKind",
    "ActionRiskKind",
    "ActionRiskSeverity",
    # Lifecycle
    "ActionLifecycleState",
    # Preconditions and postconditions
    "ActionPreconditionKind",
    "ActionPreconditionStatus",
    # Effects
    "ActionEffectKind",
    "ActionSideEffectKind",
    "ActionEffectRelation",
    # Requirements and constraints
    "ActionRequirementKind",
    "ActionConstraintKind",
    "ActionDependencyKind",
]