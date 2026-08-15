# Gordon Cognitive Architecture - Phase 4.5.3
# ===========================================

"""
Action Kinds Ontology

This module defines the canonical Action kind taxonomy that describes
the semantic type of operation an Action performs.

ACTION KINDS TAXONOMY
=====================

Kinds describe the fundamental nature of the operation being performed.
Each kind represents a coherent semantic category of operations within
a broader category.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import FrozenSet, Tuple


# =============================================================================
# ACTION KINDS - Semantic operation types
# =============================================================================

class ActionKind(Enum):
    """
    The semantic kind or type of an Action.
    
    Kinds describe the fundamental nature of the operation within a
    category. Multiple kinds may belong to the same category.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # =============================================================================
    # OBSERVATIONAL KINDS - Read-only observation and inspection
    # =============================================================================
    
    OBSERVE = "observe"
    """Observe or monitor state."""
    
    INSPECT = "inspect"
    """Inspect structure or composition."""
    
    READ = "read"
    """Read data or content."""
    
    SEARCH = "search"
    """Search for information or entities."""
    
    MONITOR = "monitor"
    """Monitor system state over time."""
    
    WATCH = "watch"
    """Watch or observe continuously."""
    
    COMPARE = "compare"
    """Compare two entities or values."""
    
    EXPLORE = "explore"
    """Explore structure or relationships."""
    
    # =============================================================================
    # INFORMATIONAL KINDS - Gather information
    # =============================================================================
    
    GATHER = "gather"
    """Gather information from sources."""
    
    RETRIEVE = "retrieve"
    """Retrieve stored information."""
    
    QUERY = "query"
    """Query for specific information."""
    
    VALIDATE = "validate"
    """Verify properties or conditions."""
    
    # =============================================================================
    # COMPUTATIONAL KINDS - Perform computation or reasoning
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
    # TRANSFORMATIONAL KINDS - Modify existing state
    # =============================================================================
    
    MODIFY = "modify"
    """Modify properties of existing entity."""
    
    UPDATE = "update"
    """Update information or configuration."""
    
    TRANSFORM = "transform"
    """Transform data or structure."""
    
    REORDER = "reorder"
    """Reorder elements or components."""
    
    # =============================================================================
    # CREATION KINDS - Create new state
    # =============================================================================
    
    CREATE = "create"
    """Create new entity or state."""
    
    CONSTRUCT = "construct"
    """Construct new compound entity."""
    
    GENERATE = "generate"
    """Generate new content or artifacts."""
    
    ACQUIRE = "acquire"
    """Acquire new resources or capabilities."""
    
    # =============================================================================
    # DELETION KINDS - Remove state
    # =============================================================================
    
    DELETE = "delete"
    """Delete information or artifact."""
    
    REMOVE = "remove"
    """Remove from collection or location."""
    
    REVERT = "revert"
    """Revert to previous state."""
    
    COMPENSATE = "compensate"
    """Compensate for effects of another action."""
    
    # =============================================================================
    # COMMUNICATIVE KINDS - Exchange information
    # =============================================================================
    
    NOTIFICATION = "notification"
    """Send notification or alert."""
    
    REQUEST = "request"
    """Request service or information."""
    
    PROMPT = "prompt"
    """Prompt external input or confirmation."""
    
    REPORT = "report"
    """Report status or results."""
    
    # =============================================================================
    # DELEGATIVE KINDS - Delegate work
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
    # RESOURCE KINDS - Manage resources
    # =============================================================================
    
    RESERVE = "reserve"
    """Reserve resources for use."""
    
    RELEASE = "release"
    """Release reserved resources."""
    
    ALLOCATE = "allocate"
    """Allocate resources to purposes."""
    
    DEALLOCATE = "deallocate"
    """Deallocate resources from purposes."""
    
    # =============================================================================
    # MEMORY KINDS - Manage memory
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
    # WORKSPACE KINDS - Manage workspace
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
    # PLANNING SUPPORT KINDS
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
    # EXECUTIVE SUPPORT KINDS
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
    # MONITORING SUPPORT KINDS
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
    # RECOVERY SUPPORT KINDS
    # =============================================================================
    
    RECOVER = "recover"
    """Recover from failure or error."""
    
    ROLLBACK = "rollback"
    """Rollback to previous state."""
    
    RESTORE = "restore"
    """Restore from backup or snapshot."""
    
    MITIGATE = "mitigate"
    """Mitigate negative effects."""
    
    # =============================================================================
    # SECURITY KINDS
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
    # POLICY KINDS
    # =============================================================================
    
    ENFORCE = "enforce"
    """Enforce policy rules."""
    
    VERIFY_POLICY = "verify_policy"
    """Verify policy compatibility."""
    
    UPDATE_POLICY = "update_policy"
    """Update policy configuration."""
    
    CHECK_POLICY = "check_policy"
    """Check action against policy."""
    
    # =============================================================================
    # CONFIGURATION KINDS
    # =============================================================================
    
    SET = "set"
    """Set configuration value."""
    
    GET = "get"
    """Get configuration value."""
    
    MODIFY_CONFIG = "modify_config"
    """Modify existing configuration."""
    
    RESET = "reset"
    """Reset to default configuration."""
    
    # =============================================================================
    # EXTERNAL INTERACTION KINDS
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
    # PHYSICAL KINDS (if applicable)
    # =============================================================================
    
    MOVE_PHYSICAL = "move_physical"
    """Move physical entity."""
    
    TOUCH = "touch"
    """Physically interact with device or sensor."""
    
    CONTROL_DEVICE = "control_device"
    """Control physical device."""
    
    # =============================================================================
    # COMPOSITE KINDS
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
    # GENERAL KINDS
    # =============================================================================
    
    WAIT = "wait"
    """Wait for condition or timeout."""
    
    SYNCHRONIZE = "synchronize"
    """Synchronize with other operations."""
    
    GENERAL = "general"
    """General-purpose operation."""
    
    UNKNOWN = "unknown"
    """Kind is unknown or undetermined."""
    
    @property
    def is_informational(self) -> bool:
        """Check if this kind is informational (read-only)."""
        return self in (
            ActionKind.OBSERVE,
            ActionKind.INSPECT,
            ActionKind.READ,
            ActionKind.SEARCH,
            ActionKind.MONITOR,
            ActionKind.GATHER,
            ActionKind.RETRIEVE,
            ActionKind.QUERY,
            ActionKind.EXPLORE,
            ActionKind.VALIDATE,
        )
    
    @property
    def is_transformative(self) -> bool:
        """Check if this kind transforms state."""
        return self in (
            ActionKind.MODIFY,
            ActionKind.UPDATE,
            ActionKind.TRANSFORM,
            ActionKind.REORDER,
            ActionKind.CREATE,
            ActionKind.CONSTRUCT,
            ActionKind.GENERATE,
            ActionKind.ACQUIRE,
            ActionKind.DELETE,
            ActionKind.REMOVE,
            ActionKind.REVERT,
            ActionKind.COMPENSATE,
        )
    
    @property
    def is_destructive(self) -> bool:
        """Check if this kind removes or destroys state."""
        return self in (
            ActionKind.DELETE,
            ActionKind.REMOVE,
            ActionKind.REVERT,
        )


# =============================================================================
# UTILITY TYPES - Kind collections
# =============================================================================

class ActionKinds(FrozenSet[ActionKind]):
    """A collection of ActionKind values."""
    
    def __new__(cls, kinds: Tuple[ActionKind, ...] = ()):
        return super().__new__(cls, kinds)
    
    @classmethod
    def all(cls) -> "ActionKinds":
        """Get all canonical ActionKinds."""
        return cls(tuple(ActionKind))
    
    @classmethod
    def informational(cls) -> "ActionKinds":
        """Get all informational kinds."""
        return cls(k for k in ActionKind if k.is_informational)
    
    @classmethod
    def transformative(cls) -> "ActionKinds":
        """Get all transformative kinds."""
        return cls(k for k in ActionKind if k.is_transformative)


__all__ = [
    "ActionKind",
    "ActionKinds",
]