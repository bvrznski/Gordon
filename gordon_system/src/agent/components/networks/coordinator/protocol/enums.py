# Gordon Cognitive Architecture - Phase 4.11.5
# ===========================================

"""
Cognitive Coordination Protocol (CCP) Enums
===========================================

This module defines the semantic enumerations used by CCP for:
- Message kinds
- Payload kinds  
- Visibility scopes
- Publication statuses
- Acknowledgement kinds
- Negotiation statuses
- Synchronization statuses
- Lifecycle states

All enums are immutable and deterministic.
"""

from __future__ import annotations

from enum import Enum, unique


# =============================================================================
# CCP MESSAGE KINDS - The canonical taxonomy of semantic communication
# =============================================================================

@unique
class CCPMessageKind(Enum):
    """
    Canonical message kinds for the Cognitive Coordination Protocol.
    
    Every cognitive network communicates through exactly one of these message kinds.
    
    INVENTORY-LAW-001: All message kinds are declared here
    INVENTORY-LAW-002: No runtime-defined message kinds exist
    """
    # --- PROJECTIONS ---
    PROJECTION_PUBLICATION = "projection_publication"
    """Network projection publication (e.g., reward, prediction, salience)"""
    
    STATE_PUBLICATION = "state_publication"
    """Completed coordination state publication"""
    
    # --- CAPABILITIES ---
    CAPABILITY_ADVERTISEMENT = "capability_advertisement"
    """Network capability advertisement"""
    
    CAPABILITY_WITHDRAWAL = "capability_withdrawal"
    """Network capability withdrawal"""
    
    # --- REQUIREMENTS ---
    REQUIREMENT_DECLARATION = "requirement_declaration"
    """Network requirement declaration"""
    
    REQUIREMENT_WITHDRAWAL = "requirement_withdrawal"
    """Network requirement withdrawal"""
    
    # --- SUBSCRIPTIONS ---
    SUBSCRIPTION_DECLARATION = "subscription_declaration"
    """Subscription declaration (who wants what)"""
    
    SUBSCRIPTION_REVISION = "subscription_revision"
    """Subscription revision"""
    
    SUBSCRIPTION_WITHDRAWAL = "subscription_withdrawal"
    """Subscription withdrawal"""
    
    # --- ACKNOWLEDGEMENTS ---
    ACKNOWLEDGEMENT = "acknowledgement"
    """Generic acknowledgement of a message"""
    
    ACCEPTANCE = "acceptance"
    """Semantic acceptance of a message"""
    
    REJECTION = "rejection"
    """Semantic rejection of a message with explicit reasons"""
    
    DEFERRAL = "deferral"
    """Deferred acceptance (may become acceptable later)"""
    
    # --- NEGOTIATIONS ---
    NEGOTIATION_REQUEST = "negotiation_request"
    """Negotiation request (requirement -> potential providers)"""
    
    NEGOTIATION_RESPONSE = "negotiation_response"
    """Provider response to negotiation request"""
    
    NEGOTIATION_RESULT = "negotiation_result"
    """Final negotiation result (selected providers, etc.)"""
    
    # --- SYNCHRONIZATION ---
    SYNCHRONIZATION_REQUEST = "synchronization_request"
    """Synchronization request with requirements"""
    
    SYNCHRONIZATION_STATUS = "synchronization_status"
    """Participant synchronization status"""
    
    BARRIER_STATUS = "barrier_status"
    """Coordination barrier status"""
    
    # --- TRANSITIONS ---
    TRANSITION_INTENTION = "transition_intention"
    """Declared transition intention (not executable)"""
    
    TRANSITION_STATUS = "transition_status"
    """Transition status report"""
    
    # --- CONSTRAINTS ---
    CONSTRAINT_DECLARATION = "constraint_declaration"
    """Constraint declaration"""
    
    CONSTRAINT_RELEASE = "constraint_release"
    """Constraint release"""
    
    # --- CONFLICTS ---
    CONFLICT_REPORT = "conflict_report"
    """Conflict report"""
    
    CONFLICT_STATUS = "conflict_status"
    """Conflict status update"""
    
    # --- FAILURE & RECOVERY ---
    FAILURE_REPORT = "failure_report"
    """Failure report"""
    
    RECOVERY_REQUEST = "recovery_request"
    """Recovery request"""
    
    RECOVERY_PROPOSAL = "recovery_proposal"
    """Recovery proposal from providers"""
    
    RECOVERY_RESULT = "recovery_result"
    """Final recovery result"""
    
    # --- LIFECYCLE ---
    LIFECYCLE_NOTICE = "lifecycle_notice"
    """Network lifecycle state notice"""
    
    HEARTBEAT_PROJECTION = "heartbeat_projection"
    """Semantic heartbeat (not a runtime liveness probe)"""
    
    OBSERVATION_NOTICE = "observation_notice"
    """Observation from external monitor"""
    
    FEEDBACK_NOTICE = "feedback_notice"
    """Feedback on protocol processing"""
    
    # --- VERSIONING ---
    VERSION_ADVERTISEMENT = "version_advertisement"
    """Supported protocol version advertisement"""
    
    VERSION_NEGOTIATION = "version_negotiation"
    """Protocol version negotiation result"""
    
    COMPATIBILITY_RESULT = "compatibility_result"
    """Compatibility evaluation result"""
    
    # --- META ---
    UNKNOWN = "unknown"
    """Unknown or unregistered message kind"""


# =============================================================================
# CCP PAYLOAD KINDS - Semantic payload ontologies
# =============================================================================

@unique
class CCPPayloadKind(Enum):
    """
    Canonical payload kinds for CCP messages.
    
    Payload kinds define the semantic content type of a message.
    """
    # --- NETWORK PROJECTIONS ---
    NETWORK_PROJECTION = "network_projection"
    """Network projection reference"""
    
    # --- COORDINATION STATES ---
    COORDINATION_STATE = "coordination_state"
    """Completed coordination state"""
    
    COORDINATION_STATE_VIEW = "coordination_state_view"
    """Coordination state view for consumers"""
    
    # --- CAPABILITIES & REQUIREMENTS ---
    NETWORK_CAPABILITY = "network_capability"
    """Network capability advertisement"""
    
    NETWORK_REQUIREMENT = "network_requirement"
    """Network requirement declaration"""
    
    NETWORK_SUBSCRIPTION = "network_subscription"
    """Subscription contract reference"""
    
    REQUIREMENT_SATISFACTION = "requirement_satisfaction"
    """Requirement satisfaction record"""
    
    PROVIDER_SELECTION = "provider_selection"
    """Provider selection result"""
    
    # --- SYNCHRONIZATION ---
    SYNCHRONIZATION_BARRIER = "synchronization_barrier"
    """Synchronization barrier state"""
    
    # --- TRANSITIONS ---
    TRANSITION_INTENTION = "transition_intention"
    """Transition intention record"""
    
    # --- COORDINATION ARTIFACTS ---
    COORDINATION_CONSTRAINT = "coordination_constraint"
    """Coordination constraint reference"""
    
    COORDINATION_CONFLICT = "coordination_conflict"
    """Coordination conflict report"""
    
    COORDINATION_FINDING = "coordination_finding"
    """Protocol finding record"""
    
    COORDINATION_LIMITATION = "coordination_limitation"
    """Protocol limitation record"""
    
    COORDINATION_PLAN = "coordination_plan"
    """Coordination plan reference"""
    
    # --- CYCLE & EPOCH ---
    COORDINATION_CYCLE = "coordination_cycle"
    """Coordination cycle reference"""
    
    COORDINATION_EPOCH = "coordination_epoch"
    """Coordination epoch reference"""
    
    GLOBAL_GRAPH_SNAPSHOT = "global_graph_snapshot"
    """Global Coordination Graph snapshot"""
    
    # --- PROTOCOL METADATA ---
    PROTOCOL_VERSION = "protocol_version"
    """Protocol version record"""
    
    PROTOCOL_COMPATIBILITY = "protocol_compatibility"
    """Protocol compatibility record"""
    
    # --- RECOVERY & FAILURE ---
    RECOVERY_PATH = "recovery_path"
    """Recovery path reference"""
    
    FAILURE_STATE = "failure_state"
    """Failure state record"""
    
    # --- LIFECYCLE ---
    LIFECYCLE_STATE = "lifecycle_state"
    """Lifecycle state notice"""
    
    UNKNOWN = "unknown"
    """Unknown or unregistered payload kind"""


# =============================================================================
# CCP MESSAGE VISIBILITY SCOPES
# =============================================================================

@unique
class CCPMessageVisibility(Enum):
    """
    Canonical visibility scopes for CCP messages.
    
    Visibility controls semantic eligibility without implementing access control.
    """
    PRIVATE_TO_COORDINATION = "private_to_coordination"
    """Only visible to coordination subsystem"""
    
    TARGETED_NETWORKS = "targeted_networks"
    """Visible only to specified networks"""
    
    DOMAIN_SCOPED = "domain_scoped"
    """Visible within specific coordination domain"""
    
    CORE_NETWORKS = "core_networks"
    """Visible to core coordinated networks"""
    
    OBSERVERS = "observers"
    """Visible to observers without participation"""
    
    GLOBAL_COORDINATION = "global_coordination"
    """Globally visible for coordination purposes"""
    
    ARCHIVAL = "archival"
    """Archival visibility (historical only)"""
    
    UNKNOWN = "unknown"
    """Unknown or unregistered visibility scope"""


# =============================================================================
# PUBLICATION STATUSES
# =============================================================================

@unique
class CCPPublicationStatus(Enum):
    """
    Canonical publication statuses.
    """
    CREATED = "created"
    """Message constructed, not yet validated"""
    
    SUBMITTED = "submitted"
    """Submitted for protocol processing"""
    
    VALIDATING = "validating"
    """Currently being validated"""
    
    PUBLISHED = "published"
    """Successfully published and available"""
    
    PUBLISHED_WITH_LIMITATIONS = "published_with_limitations"
    """Published but with documented limitations"""
    
    WITHHELD = "withheld"
    """Withheld from publication"""
    
    REJECTED = "rejected"
    """Rejected after validation"""
    
    DEFERRED = "deferred"
    """Deferred for later processing"""
    
    SUPERSEDED = "superseded"
    """Superseded by newer revision"""
    
    WITHDRAWN = "withdrawn"
    """Withdrawn by publisher"""
    
    INVALID = "invalid"
    """Invalid (failed validation)"""
    
    UNKNOWN = "unknown"
    """Unknown status"""


# =============================================================================
# ACKNOWLEDGEMENT KINDS
# =============================================================================

@unique
class CCPAcknowledgementKind(Enum):
    """
    Canonical acknowledgement kinds.
    """
    RECEIVED = "received"
    """Message received at coordination layer"""
    
    VALIDATED = "validated"
    """Message successfully validated"""
    
    ACCEPTED = "accepted"
    """Semantically accepted for processing"""
    
    ACCEPTED_WITH_LIMITATIONS = "accepted_with_limitations"
    """Accepted with documented limitations"""
    
    REJECTED = "rejected"
    """Rejected with explicit reasons"""
    
    DEFERRED = "deferred"
    """Deferred for later acceptance consideration"""
    
    OBSERVED = "observed"
    """Observed without participation"""
    
    SUPERSEDED = "superseded"
    """Superseded by newer message revision"""
    
    NO_LONGER_REQUIRED = "no_longer_required"
    """No longer required for coordination"""
    
    UNKNOWN = "unknown"
    """Unknown acknowledgement kind"""


# =============================================================================
# ACCEPTANCE STATUSES
# =============================================================================

@unique
class CCPMessageAcceptanceStatus(Enum):
    """
    Canonical acceptance statuses.
    """
    ACCEPTED = "accepted"
    """Semantically accepted"""
    
    ACCEPTED_WITH_LIMITATIONS = "accepted_with_limitations"
    """Accepted with documented limitations"""
    
    CONDITIONALLY_ACCEPTED = "conditionally_accepted"
    """Conditionally accepted pending further conditions"""
    
    DEFERRED = "deferred"
    """Deferred (may become acceptable later)"""
    
    REJECTED = "rejected"
    """Rejected with explicit reasons"""
    
    INCOMPATIBLE = "incompatible"
    """Incompatible (e.g., version mismatch)"""
    
    STALE = "stale"
    """Stale message (expired or superseded)"""
    
    UNKNOWN = "unknown"
    """Unknown acceptance status"""


# =============================================================================
# REJECTION KINDS
# =============================================================================

@unique
class CCPRejectionKind(Enum):
    """
    Canonical rejection kinds with explicit reasons.
    """
    INVALID_SCHEMA = "invalid_schema"
    """Message schema validation failed"""
    
    UNSUPPORTED_VERSION = "unsupported_version"
    """Protocol version not supported"""
    
    UNAUTHORIZED_PUBLISHER = "unauthorized_publisher"
    """Publisher lacks authority"""
    
    OUT_OF_SCOPE = "out_of_scope"
    """Outside coordination scope"""
    
    STALE_PAYLOAD = "stale_payload"
    """Payload is stale (expired or superseded)"""
    
    REVISION_MISMATCH = "revision_mismatch"
    """Revision lineage mismatch"""
    
    DEPENDENCY_MISMATCH = "dependency_mismatch"
    """Required dependencies not satisfied"""
    
    CONSTRAINT_CONFLICT = "constraint_conflict"
    """Constraint conflict with message"""
    
    CONSUMER_POLICY_REJECTION = "consumer_policy_rejection"
    """Rejected by consumer policy"""
    
    UNKNOWN = "unknown"
    """Unknown rejection kind"""


# =============================================================================
# DEFERRAL REASONS
# =============================================================================

@unique
class CCPDeferralReason(Enum):
    """
    Canonical deferral reasons.
    """
    MISSING_REQUIREMENTS = "missing_requirements"
    """Required capabilities not yet available"""
    
    BLOCKING_DEPENDENCIES = "blocking_dependencies"
    """Blocking dependencies active"""
    
    PENDING_CONSUMER_CYCLE = "pending_consumer_cycle"
    """Consumer cycle not ready"""
    
    VERSION_NEGOTIATION_PENDING = "version_negotiation_pending"
    """Protocol version negotiation in progress"""
    
    UNKNOWN = "unknown"
    """Unknown deferral reason"""


# =============================================================================
# NEGOTIATION STATUSES
# =============================================================================

@unique
class CCPNegotiationResponseStatus(Enum):
    """
    Canonical negotiation response statuses.
    """
    OFFERED = "offered"
    """Provider willing to offer capability"""
    
    OFFERED_WITH_LIMITATIONS = "offered_with_limitations"
    """Offered with documented limitations"""
    
    DECLINED = "declined"
    """Provider declines to offer"""
    
    UNAVAILABLE = "unavailable"
    """Provider currently unavailable"""
    
    INCOMPATIBLE = "incompatible"
    """Incompatible (e.g., version)"""
    
    DEFERRED = "deferred"
    """Deferred for later consideration"""
    
    UNKNOWN = "unknown"
    """Unknown response status"""


# =============================================================================
# SYNCHRONIZATION STATUSES
# =============================================================================

@unique
class CCPSynchronizationStatus(Enum):
    """
    Canonical synchronization statuses.
    """
    READY = "ready"
    """Fully synchronized and ready"""
    
    PARTIALLY_READY = "partially_ready"
    """Partially synchronized"""
    
    WAITING = "waiting"
    """Waiting for required participants"""
    
    BLOCKED = "blocked"
    """Blocked by constraints or dependencies"""
    
    DEFERRED = "deferred"
    """Deferred for later synchronization attempt"""
    
    UNAVAILABLE = "unavailable"
    """Synchronization unavailable"""
    
    FAILED = "failed"
    """Synchronization failed"""
    
    UNKNOWN = "unknown"
    """Unknown synchronization status"""


# =============================================================================
# TRANSITION STATUSES
# =============================================================================

@unique
class CCPTransitionStatus(Enum):
    """
    Canonical transition statuses.
    """
    PROPOSED = "proposed"
    """Transition proposed"""
    
    VALIDATED = "validated"
    """Validated successfully"""
    
    READY = "ready"
    """Ready for execution"""
    
    BLOCKED = "blocked"
    """Blocked by constraints or dependencies"""
    
    DEFERRED = "deferred"
    """Deferred for later"""
    
    COMPLETED = "completed"
    """Transition completed successfully"""
    
    FAILED = "failed"
    """Transition failed"""
    
    SUPERSEDED = "superseded"
    """Superseded by newer transition"""
    
    UNKNOWN = "unknown"
    """Unknown transition status"""


# =============================================================================
# LIFECYCLE STATES
# =============================================================================

@unique
class CCPLifecycleState(Enum):
    """
    Canonical lifecycle states for networks.
    """
    INITIALIZING = "initializing"
    """Network initializing"""
    
    AVAILABLE = "available"
    """Fully available and operational"""
    
    DEGRADED = "degraded"
    """Operating with degraded capabilities"""
    
    QUIESCENT = "quiescent"
    """Temporarily inactive but ready to resume"""
    
    SUSPENDED = "suspended"
    """Suspended by external authority"""
    
    UNAVAILABLE = "unavailable"
    """Currently unavailable"""
    
    FAILED = "failed"
    """Failed state"""
    
    RECOVERING = "recovering"
    """Attempting recovery"""
    
    RETIRED = "retired"
    """Permanently retired"""
    
    UNKNOWN = "unknown"
    """Unknown lifecycle state"""


# =============================================================================
# REVISION KINDS
# =============================================================================

@unique
class CCPRevisionKind(Enum):
    """
    Canonical revision kinds for message evolution.
    """
    INITIAL = "initial"
    """Initial version of a message"""
    
    UPDATE = "update"
    """Non-critical update"""
    
    CORRECTION = "correction"
    """Correction of error"""
    
    CONFIRMATION = "confirmation"
    """Confirmation from consumer"""
    
    WITHDRAWAL = "withdrawal"
    """Withdrawn by publisher"""
    
    SUPERSESSION = "supersession"
    """Superseded by newer revision"""
    
    REVALIDATION = "revalidation"
    """Revalidated after changes"""
    
    RECOVERY = "recovery"
    """Recovered from failure state"""
    
    UNKNOWN = "unknown"
    """Unknown revision kind"""


# =============================================================================
# COMPATIBILITY STATUSES
# =============================================================================

@unique
class CCPCompatibilityStatus(Enum):
    """
    Canonical compatibility statuses.
    """
    FULLY_COMPATIBLE = "fully_compatible"
    """Fully compatible without adapter"""
    
    BACKWARD_COMPATIBLE = "backward_compatible"
    """Compatible with backward-compatible behavior"""
    
    FORWARD_COMPATIBLE = "forward_compatible"
    """Compatible with forward-compatible behavior"""
    
    COMPATIBLE_WITH_ADAPTER = "compatible_with_adapter"
    """Compatible using semantic adapter"""
    
    COMPATIBLE_WITH_LIMITATIONS = "compatible_with_limitations"
    """Compatible but with documented limitations"""
    
    INCOMPATIBLE = "incompatible"
    """Incompatible - cannot communicate"""
    
    UNDETERMINED = "undetermined"
    """Compatibility not yet determined"""
    
    UNKNOWN = "unknown"
    """Unknown compatibility status"""