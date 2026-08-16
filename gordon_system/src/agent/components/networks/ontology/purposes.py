# Gordon Cognitive Architecture - Phase 4.5.3
# ===========================================

"""
Action Purposes Ontology

This module defines the canonical Action purpose taxonomy that describes
why Actions exist and what they are intended to accomplish.

ACTION PURPOSES TAXONOMY
========================

Purpose describes the intent or objective behind an Action. It answers
the question: "Why does this Action exist?"

Purposes remain purely semantic - they describe intent without describing
how that intent is achieved.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import FrozenSet, Tuple


# =============================================================================
# ACTION PURPOSES - Semantic intentions of Actions
# =============================================================================

class ActionPurpose(Enum):
    """
    The purpose or intent of an Action.
    
    Purpose describes why the operation is needed in semantic terms,
    not how it accomplishes that goal. Each purpose represents a coherent
    semantic category of intent.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # =============================================================================
    # OBSERVATIONAL PURPOSES - Understanding current state
    # =============================================================================
    
    OBSERVE = "observe"
    """Observe or monitor state."""
    
    INSPECT = "inspect"
    """Inspect structure or composition."""
    
    MONITOR = "monitor"
    """Monitor changes over time."""
    
    WATCH = "watch"
    """Watch for specific conditions or events."""
    
    # =============================================================================
    # INFORMATIONAL PURPOSES - Gather information
    # =============================================================================
    
    READ = "read"
    """Read data or content."""
    
    SEARCH = "search"
    """Search across information space."""
    
    QUERY = "query"
    """Query with specific criteria."""
    
    EXPLORE = "explore"
    """Explore unknown territory or relationships."""
    
    VALIDATE = "validate"
    """Validate properties or conditions."""
    
    COMPARE = "compare"
    """Compare multiple states or values."""
    
    # =============================================================================
    # COMPUTATIONAL PURPOSES - Process information
    # =============================================================================
    
    CALCULATE = "calculate"
    """Perform mathematical calculation."""
    
    REASON = "reason"
    """Perform logical inference."""
    
    ANALYZE = "analyze"
    """Break down into components for understanding."""
    
    SYNTHESIZE = "synthesize"
    """Combine information into new understanding."""
    
    PREDICT = "predict"
    """Predict future states or outcomes."""
    
    OPTIMIZE = "optimize"
    """Find optimal solution or configuration."""
    
    # =============================================================================
    # TRANSFORMATIONAL PURPOSES - Modify existing state
    # =============================================================================
    
    TRANSFORM = "transform"
    """Transform data or structure."""
    
    MODIFY = "modify"
    """Modify properties of existing entity."""
    
    UPDATE = "update"
    """Update information or configuration."""
    
    REORDER = "reorder"
    """Reorder elements or components."""
    
    NORMALIZE = "normalize"
    """Normalize data or structure."""
    
    # =============================================================================
    # CREATION PURPOSES - Create new state
    # =============================================================================
    
    CREATE = "create"
    """Create new entity or state."""
    
    CONSTRUCT = "construct"
    """Construct new compound entity."""
    
    GENERATE = "generate"
    """Generate new content or artifacts."""
    
    ACQUIRE = "acquire"
    """Acquire new resources or capabilities."""
    
    BUILD = "build"
    """Build new artifact or structure."""
    
    # =============================================================================
    # DELETION PURPOSES - Remove state
    # =============================================================================
    
    DELETE = "delete"
    """Delete information or artifact."""
    
    REMOVE = "remove"
    """Remove from collection or location."""
    
    REVERT = "revert"
    """Revert to previous state."""
    
    COMPENSATE = "compensate"
    """Compensate for effects of another action."""
    
    ROLLBACK = "rollback"
    """Rollback to checkpoint."""
    
    # =============================================================================
    # COMMUNICATIVE PURPOSES - Exchange information
    # =============================================================================
    
    NOTIFICATION = "notification"
    """Send notification or alert."""
    
    REQUEST = "request"
    """Request service or information."""
    
    PROMPT = "prompt"
    """Prompt external input or confirmation."""
    
    REPORT = "report"
    """Report status or results."""
    
    BROADCAST = "broadcast"
    """Broadcast to multiple recipients."""
    
    # =============================================================================
    # DELEGATIVE PURPOSES - Delegate work
    # =============================================================================
    
    ASSIGN = "assign"
    """Assign task or responsibility."""
    
    REFER = "refer"
    """Refer to another authority or component."""
    
    ESCALATE = "escalate"
    """Escalate to higher authority."""
    
    DE_ESCALATE = "de_escalate"
    """De-escalate from higher authority."""
    
    # =============================================================================
    # RESOURCE PURPOSES - Manage resources
    # =============================================================================
    
    RESERVE = "reserve"
    """Reserve resource for use."""
    
    RELEASE = "release"
    """Release reserved resource."""
    
    ALLOCATE = "allocate"
    """Allocate resource to purpose."""
    
    DEALLOCATE = "deallocate"
    """Deallocate resource from purpose."""
    
    ACQUIRE_RESOURCE = "acquire_resource"
    """Acquire new resource."""
    
    # =============================================================================
    # MEMORY PURPOSES - Manage memory
    # =============================================================================
    
    PERSIST = "persist"
    """Persist state to storage."""
    
    LOAD = "load"
    """Load from persistent storage."""
    
    STORE = "store"
    """Store information in memory."""
    
    CACHE = "cache"
    """Cache for faster access."""
    
    CLEAR = "clear"
    """Clear memory or cache."""
    
    # =============================================================================
    # WORKSPACE PURPOSES - Manage workspace
    # =============================================================================
    
    ADMISSION = "admission"
    """Admit new artifacts to workspace."""
    
    REJECTION = "rejection"
    """Reject artifacts from workspace."""
    
    ORGANIZE = "organize"
    """Organize workspace structure."""
    
    REFACTOR = "refactor"
    """Refactor workspace content."""
    
    # =============================================================================
    # PLANNING SUPPORT PURPOSES
    # =============================================================================
    
    PLAN = "plan"
    """Create or modify a plan."""
    
    SCHEDULE = "schedule"
    """Schedule operations within a plan."""
    
    FORECAST = "forecast"
    """Forecast future requirements or states."""
    
    CONFIGURE_PLAN = "configure_plan"
    """Configure planning parameters."""
    
    # =============================================================================
    # EXECUTIVE SUPPORT PURPOSES
    # =============================================================================
    
    DECIDE = "decide"
    """Make an executive decision."""
    
    DIRECT = "direct"
    """Direct execution flow."""
    
    COORDINATE = "coordinate"
    """Coordinate multiple operations."""
    
    OVERRIDE = "override"
    """Override current state or decision."""
    
    # =============================================================================
    # MONITORING SUPPORT PURPOSES
    # =============================================================================
    
    AUDIT = "audit"
    """Create audit record."""
    
    LOG = "log"
    """Log information for observation."""
    
    TRACE = "trace"
    """Trace execution flow."""
    
    MEASURE = "measure"
    """Measure system state or performance."""
    
    # =============================================================================
    # RECOVERY SUPPORT PURPOSES
    # =============================================================================
    
    RECOVER = "recover"
    """Recover from failure or error."""
    
    RESTORE = "restore"
    """Restore from backup or snapshot."""
    
    MITIGATE = "mitigate"
    """Mitigate negative effects."""
    
    # =============================================================================
    # SECURITY PURPOSES
    # =============================================================================
    
    AUTHORIZE = "authorize"
    """Grant or modify authorization."""
    
    AUTHENTICATE = "authenticate"
    """Authenticate credentials."""
    
    ENCRYPT = "encrypt"
    """Encrypt data."""
    
    DECRYPT = "decrypt"
    """Decrypt data."""
    
    AUDIT_SECURITY = "audit_security"
    """Audit security-relevant events."""
    
    # =============================================================================
    # POLICY PURPOSES
    # =============================================================================
    
    ENFORCE_POLICY = "enforce_policy"
    """Enforce policy rules."""
    
    VERIFY_POLICY = "verify_policy"
    """Verify policy compatibility."""
    
    UPDATE_POLICY = "update_policy"
    """Update policy configuration."""
    
    CHECK_POLICY = "check_policy"
    """Check action against policy."""
    
    # =============================================================================
    # CONFIGURATION PURPOSES
    # =============================================================================
    
    SET_CONFIG = "set_config"
    """Set configuration value."""
    
    GET_CONFIG = "get_config"
    """Get configuration value."""
    
    MODIFY_CONFIG = "modify_config"
    """Modify existing configuration."""
    
    RESET_CONFIG = "reset_config"
    """Reset to default configuration."""
    
    # =============================================================================
    # EXTERNAL INTERACTION PURPOSES
    # =============================================================================
    
    API_CALL = "api_call"
    """Invoke external API."""
    
    NETWORK_REQUEST = "network_request"
    """Make network request."""
    
    DATABASE_QUERY = "database_query"
    """Query database."""
    
    FILE_ACCESS = "file_access"
    """Access file system."""
    
    # =============================================================================
    # PHYSICAL PURPOSES (if applicable)
    # =============================================================================
    
    MOVE_PHYSICAL = "move_physical"
    """Move physical entity."""
    
    TOUCH = "touch"
    """Physically interact with device or sensor."""
    
    CONTROL_DEVICE = "control_device"
    """Control physical device."""
    
    # =============================================================================
    # COMPOSITE PURPOSES
    # =============================================================================
    
    SEQUENCE = "sequence"
    """Execute actions in sequence."""
    
    PARALLEL = "parallel"
    """Execute actions in parallel."""
    
    CONDITIONAL = "conditional"
    """Execute action conditionally."""
    
    LOOP = "loop"
    """Execute action repeatedly."""
    
    # =============================================================================
    # GENERAL PURPOSES
    # =============================================================================
    
    WAIT = "wait"
    """Wait for condition or timeout."""
    
    SYNCHRONIZE = "synchronize"
    """Synchronize with other operations."""
    
    GENERAL = "general"
    """General-purpose operation."""
    
    UNKNOWN = "unknown"
    """Purpose is unknown or undetermined."""
    
    @property
    def category(self) -> str:
        """
        Get the semantic category for this purpose.
        
        Returns:
            String representation of the primary category.
        """
        # Informational purposes
        if self in (
            ActionPurpose.OBSERVE,
            ActionPurpose.INSPECT,
            ActionPurpose.READ,
            ActionPurpose.SEARCH,
            ActionPurpose.QUERY,
            ActionPurpose.EXPLORE,
            ActionPurpose.VALIDATE,
            ActionPurpose.COMPARE,
        ):
            return "informational"
        
        # Transformational purposes
        if self in (
            ActionPurpose.TRANSFORM,
            ActionPurpose.MODIFY,
            ActionPurpose.UPDATE,
            ActionPurpose.REORDER,
            ActionPurpose.NORMALIZE,
            ActionPurpose.CREATE,
            ActionPurpose.CONSTRUCT,
            ActionPurpose.GENERATE,
            ActionPurpose.ACQUIRE,
            ActionPurpose.BUILD,
        ):
            return "transformational"
        
        # Deletion purposes
        if self in (
            ActionPurpose.DELETE,
            ActionPurpose.REMOVE,
            ActionPurpose.REVERT,
            ActionPurpose.COMPENSATE,
            ActionPurpose.ROLLBACK,
        ):
            return "deletion"
        
        # Communicative purposes
        if self in (
            ActionPurpose.NOTIFICATION,
            ActionPurpose.REQUEST,
            ActionPurpose.PROMPT,
            ActionPurpose.REPORT,
            ActionPurpose.BROADCAST,
        ):
            return "communicative"
        
        # Resource purposes
        if self in (
            ActionPurpose.RESERVE,
            ActionPurpose.RELEASE,
            ActionPurpose.ALLOCATE,
            ActionPurpose.DEALLOCATE,
            ActionPurpose.ACQUIRE_RESOURCE,
        ):
            return "resource"
        
        # Memory purposes
        if self in (
            ActionPurpose.PERSIST,
            ActionPurpose.LOAD,
            ActionPurpose.STORE,
            ActionPurpose.CACHE,
            ActionPurpose.CLEAR,
        ):
            return "memory"
        
        # Workspace purposes
        if self in (
            ActionPurpose.ADMISSION,
            ActionPurpose.REJECTION,
            ActionPurpose.ORGANIZE,
            ActionPurpose.REFACTOR,
        ):
            return "workspace"
        
        # Security purposes
        if self in (
            ActionPurpose.AUTHORIZE,
            ActionPurpose.AUTHENTICATE,
            ActionPurpose.ENCRYPT,
            ActionPurpose.DECRYPT,
            ActionPurpose.AUDIT_SECURITY,
        ):
            return "security"
        
        # Policy purposes
        if self in (
            ActionPurpose.ENFORCE_POLICY,
            ActionPurpose.VERIFY_POLICY,
            ActionPurpose.UPDATE_POLICY,
            ActionPurpose.CHECK_POLICY,
        ):
            return "policy"
        
        # Configuration purposes
        if self in (
            ActionPurpose.SET_CONFIG,
            ActionPurpose.GET_CONFIG,
            ActionPurpose.MODIFY_CONFIG,
            ActionPurpose.RESET_CONFIG,
        ):
            return "configuration"
        
        # External interaction purposes
        if self in (
            ActionPurpose.API_CALL,
            ActionPurpose.NETWORK_REQUEST,
            ActionPurpose.DATABASE_QUERY,
            ActionPurpose.FILE_ACCESS,
        ):
            return "external_interaction"
        
        # Physical purposes
        if self in (
            ActionPurpose.MOVE_PHYSICAL,
            ActionPurpose.TOUCH,
            ActionPurpose.CONTROL_DEVICE,
        ):
            return "physical"
        
        # Composite purposes
        if self in (
            ActionPurpose.SEQUENCE,
            ActionPurpose.PARALLEL,
            ActionPurpose.CONDITIONAL,
            ActionPurpose.LOOP,
        ):
            return "composite"
        
        # General purposes
        return "general"
    
    @property
    def is_informational(self) -> bool:
        """Check if purpose is information-focused."""
        return self in (
            ActionPurpose.OBSERVE,
            ActionPurpose.INSPECT,
            ActionPurpose.READ,
            ActionPurpose.SEARCH,
            ActionPurpose.QUERY,
            ActionPurpose.EXPLORE,
            ActionPurpose.VALIDATE,
            ActionPurpose.COMPARE,
        )
    
    @property
    def is_mutating(self) -> bool:
        """Check if purpose involves state mutation."""
        return self in (
            ActionPurpose.TRANSFORM,
            ActionPurpose.MODIFY,
            ActionPurpose.UPDATE,
            ActionPurpose.REORDER,
            ActionPurpose.NORMALIZE,
            ActionPurpose.CREATE,
            ActionPurpose.CONSTRUCT,
            ActionPurpose.GENERATE,
            ActionPurpose.ACQUIRE,
            ActionPurpose.BUILD,
            ActionPurpose.DELETE,
            ActionPurpose.REMOVE,
            ActionPurpose.REVERT,
        )


# =============================================================================
# UTILITY TYPES - Purpose collections
# =============================================================================

class ActionPurposes(FrozenSet[ActionPurpose]):
    """A collection of ActionPurpose values."""
    
    def __new__(cls, purposes: Tuple[ActionPurpose, ...] = ()):
        return super().__new__(cls, purposes)
    
    @classmethod
    def all(cls) -> "ActionPurposes":
        """Get all canonical ActionPurposes."""
        return cls(tuple(ActionPurpose))
    
    @classmethod
    def informational(cls) -> "ActionPurposes":
        """Get all informational purposes."""
        return cls(p for p in ActionPurpose if p.is_informational)
    
    @classmethod
    def mutating(cls) -> "ActionPurposes":
        """Get all mutating purposes."""
        return cls(p for p in ActionPurpose if p.is_mutating)


__all__ = [
    "ActionPurpose",
    "ActionPurposes",
]