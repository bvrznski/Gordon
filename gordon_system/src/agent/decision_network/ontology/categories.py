# Gordon Cognitive Architecture - Phase 4.5.3
# ===========================================

"""
Action Categories Ontology

This module defines the canonical Action category taxonomy that provides
the highest-level semantic classification for all possible Actions in the
Gordon cognitive agent system.

ACTION CATEGORIES TAXONOMY
==========================

The ontology supports a multi-dimensional classification:

1. ACTION CATEGORY (Top-level grouping)
   - The fundamental semantic domain of an Action
   
2. ACTION KIND (Semantic operation type)
   - The nature of the operation being performed
   
3. ACTION FAMILY (Specific semantic pattern)
   - A canonical pattern within a category/kind

The hierarchy is:
    
    ActionCategory
        ↓ (has Kind)
    ActionKind
        ↓ (is Family)
    ActionFamily

Categories remain orthogonal to execution semantics.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import FrozenSet, Tuple


# =============================================================================
# ACTION CATEGORIES - Top-level semantic taxonomies
# =============================================================================

class ActionCategory(Enum):
    """
    The top-level semantic category of an Action.
    
    Every Action must belong to exactly one primary category. Categories
    represent the broadest semantic grouping of possible operations.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # =============================================================================
    # CORE SEMANTIC DOMAINS
    # =============================================================================
    
    OBSERVATIONAL = "observational"
    """Observe or inspect without modification."""
    
    INFORMATIONAL = "informational"
    """Gather information without necessarily storing it."""
    
    COMPUTATIONAL = "computational"
    """Perform computation or reasoning."""
    
    TRANSFORMATIONAL = "transformational"
    """Modify existing state while preserving identity."""
    
    COMMUNICATIVE = "communicative"
    """Exchange information with other systems."""
    
    DELEGATIVE = "delegative"
    """Delegate work to other components."""
    
    RESOURCE = "resource"
    """Manage system resources."""
    
    MEMORY = "memory"
    """Manage working or long-term memory."""
    
    WORKSPACE = "workspace"
    """Manage workspace artifacts and context."""
    
    PLANNING_SUPPORT = "planning_support"
    """Enable planning capabilities."""
    
    EXECUTIVE_SUPPORT = "executive_support"
    """Enable executive functions."""
    
    MONITORING_SUPPORT = "monitoring_support"
    """Enable monitoring capabilities."""
    
    RECOVERY_SUPPORT = "recovery_support"
    """Enable recovery from failures."""
    
    SECURITY = "security"
    """Handle security-sensitive operations."""
    
    POLICY = "policy"
    """Define policy-related behavior."""
    
    CONFIGURATION = "configuration"
    """Manage system configuration."""
    
    EXTERNAL_INTERACTION = "external_interaction"
    """Interact with external systems."""
    
    PHYSICAL = "physical"
    """Interact with physical world (if applicable)."""
    
    COMPOSITE = "composite"
    """Composed of multiple Actions."""
    
    # =============================================================================
    # SPECIAL CATEGORIES
    # =============================================================================
    
    GENERAL = "general"
    """General-purpose operation not fitting other categories."""
    
    UNKNOWN = "unknown"
    """Category is unknown or undetermined."""
    
    def get_kinds(self) -> Tuple[ActionKind, ...]:
        """
        Get the canonical ActionKinds that belong to this category.
        
        Returns:
            Tuple of ActionKind values valid for this category.
        """
        return _CATEGORY_KINDS.get(self, ())
    
    @property
    def is_informational(self) -> bool:
        """Check if this category is primarily informational (read-only)."""
        return self in (
            ActionCategory.OBSERVATIONAL,
            ActionCategory.INFORMATIONAL,
        )
    
    @property
    def is_transformative(self) -> bool:
        """Check if this category transforms state."""
        return self in (
            ActionCategory.TRANSFORMATIONAL,
            ActionCategory.COMPUTATIONAL,
        )
    
    @property
    def is_destructive(self) -> bool:
        """Check if this category can remove state."""
        return self in (ActionCategory.COMPOSITE,)


# =============================================================================
# ACTION KINDS - Semantic operation types within categories
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
    
    # =============================================================================
    # INFORMATIONAL KINDS - Gather information
    # =============================================================================
    
    GATHER = "gather"
    """Gather information from sources."""
    
    RETRIEVE = "retrieve"
    """Retrieve stored information."""
    
    QUERY = "query"
    """Query for specific information."""
    
    EXPLORE = "explore"
    """Explore structure or relationships."""
    
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
    
    # =============================================================================
    # CATEGORY RELATIONSHIPS
    # =============================================================================
    
    @property
    def category(self) -> ActionCategory:
        """
        Get the primary category for this kind.
        
        Returns:
            The ActionCategory that this kind belongs to.
        """
        return _KIND_CATEGORIES.get(self, ActionCategory.UNKNOWN)
    
    def is_in_category(self, category: ActionCategory) -> bool:
        """Check if this kind belongs to a specific category."""
        return self.category == category
    
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
# ACTION FAMILIES - Canonical semantic patterns
# =============================================================================

class ActionFamily(Enum):
    """
    A canonical family of Actions with shared semantics.
    
    Families represent specific patterns within a category and kind.
    They provide more precise semantic characterization than kinds alone.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # =============================================================================
    # OBSERVATIONAL FAMILIES
    # =============================================================================
    
    OBSERVE = "observe"
    """Basic observation of state."""
    
    INSPECT = "inspect"
    """Detailed inspection of structure."""
    
    MONITOR = "monitor"
    """Continuous or periodic observation."""
    
    WATCH = "watch"
    """Watch for changes in state."""
    
    # =============================================================================
    # INFORMATIONAL FAMILIES
    # =============================================================================
    
    READ = "read"
    """Read data or content."""
    
    SEARCH = "search"
    """Search across information space."""
    
    QUERY = "query"
    """Query with specific criteria."""
    
    EXPLORE = "explore"
    """Explore unknown territory."""
    
    VALIDATE = "validate"
    """Validate properties or conditions."""
    
    COMPARE = "compare"
    """Compare multiple states or values."""
    
    # =============================================================================
    # COMPUTATIONAL FAMILIES
    # =============================================================================
    
    CALCULATE = "calculate"
    """Perform mathematical calculation."""
    
    REASON = "reason"
    """Logical inference."""
    
    ANALYZE = "analyze"
    """Break down components."""
    
    SYNTHESIZE = "synthesize"
    """Build up from components."""
    
    PREDICT = "predict"
    """Predict future states."""
    
    OPTIMIZE = "optimize"
    """Find optimal solution."""
    
    # =============================================================================
    # TRANSFORMATIONAL FAMILIES
    # =============================================================================
    
    MODIFY = "modify"
    """Modify existing entity."""
    
    UPDATE = "update"
    """Update information."""
    
    TRANSFORM = "transform"
    """Transform structure or format."""
    
    REORDER = "reorder"
    """Reorder elements."""
    
    NORMALIZE = "normalize"
    """Normalize data or structure."""
    
    # =============================================================================
    # CREATION FAMILIES
    # =============================================================================
    
    CREATE = "create"
    """Create new entity."""
    
    CONSTRUCT = "construct"
    """Construct compound entity."""
    
    GENERATE = "generate"
    """Generate content."""
    
    ACQUIRE = "acquire"
    """Acquire external resource."""
    
    BUILD = "build"
    """Build new artifact."""
    
    # =============================================================================
    # DELETION FAMILIES
    # =============================================================================
    
    DELETE = "delete"
    """Delete entity."""
    
    REMOVE = "remove"
    """Remove from collection."""
    
    REVERT = "revert"
    """Revert to previous state."""
    
    COMPENSATE = "compensate"
    """Compensate for effects."""
    
    ROLLBACK = "rollback"
    """Rollback to checkpoint."""
    
    # =============================================================================
    # COMMUNICATIVE FAMILIES
    # =============================================================================
    
    NOTIFICATION = "notification"
    """Send notification."""
    
    REQUEST = "request"
    """Request service or information."""
    
    PROMPT = "prompt"
    """Prompt external input."""
    
    REPORT = "report"
    """Report status."""
    
    BROADCAST = "broadcast"
    """Broadcast to multiple recipients."""
    
    # =============================================================================
    # DELEGATIVE FAMILIES
    # =============================================================================
    
    ASSIGN = "assign"
    """Assign task."""
    
    REFER = "refer"
    """Refer to another authority."""
    
    ESCALATE = "escalate"
    """Escalate up chain."""
    
    DE_ESCALATE = "de_escalate"
    """De-escalate down chain."""
    
    # =============================================================================
    # RESOURCE FAMILIES
    # =============================================================================
    
    RESERVE = "reserve"
    """Reserve resource."""
    
    RELEASE = "release"
    """Release resource."""
    
    ALLOCATE = "allocate"
    """Allocate to purpose."""
    
    DEALLOCATE = "deallocate"
    """Deallocate from purpose."""
    
    ACQUIRE_RESOURCE = "acquire_resource"
    """Acquire new resource."""
    
    # =============================================================================
    # MEMORY FAMILIES
    # =============================================================================
    
    PERSIST = "persist"
    """Persist to storage."""
    
    LOAD = "load"
    """Load from storage."""
    
    STORE = "store"
    """Store in memory."""
    
    CACHE = "cache"
    """Cache for performance."""
    
    CLEAR = "clear"
    """Clear cache or state."""
    
    # =============================================================================
    # WORKSPACE FAMILIES
    # =============================================================================
    
    ADMISSION = "admission"
    """Admit to workspace."""
    
    REJECTION = "rejection"
    """Reject from workspace."""
    
    ORGANIZE = "organize"
    """Organize structure."""
    
    REFACTOR = "refactor"
    """Refactor content."""
    
    # =============================================================================
    # PLANNING SUPPORT FAMILIES
    # =============================================================================
    
    PLAN = "plan"
    """Create plan."""
    
    SCHEDULE = "schedule"
    """Schedule operations."""
    
    FORECAST = "forecast"
    """Forecast requirements."""
    
    CONFIGURE_PLAN = "configure_plan"
    """Configure planning parameters."""
    
    # =============================================================================
    # EXECUTIVE SUPPORT FAMILIES
    # =============================================================================
    
    DECIDE = "decide"
    """Make decision."""
    
    DIRECT = "direct"
    """Direct execution."""
    
    COORDINATE = "coordinate"
    """Coordinate operations."""
    
    OVERRIDE = "override"
    """Override current state."""
    
    # =============================================================================
    # MONITORING SUPPORT FAMILIES
    # =============================================================================
    
    AUDIT = "audit"
    """Create audit record."""
    
    LOG = "log"
    """Log information."""
    
    TRACE = "trace"
    """Trace execution."""
    
    MEASURE = "measure"
    """Measure state or performance."""
    
    # =============================================================================
    # RECOVERY SUPPORT FAMILIES
    # =============================================================================
    
    RECOVER = "recover"
    """Recover from failure."""
    
    ROLLBACK_F = "rollback"  # 'f' suffix avoids conflict with ActionFamily.ROLLBACK
    """Rollback to checkpoint."""
    
    RESTORE = "restore"
    """Restore from backup."""
    
    MITIGATE = "mitigate"
    """Mitigate negative effects."""
    
    # =============================================================================
    # SECURITY FAMILIES
    # =============================================================================
    
    AUTHORIZE = "authorize"
    """Grant authorization."""
    
    AUTHENTICATE = "authenticate"
    """Authenticate credentials."""
    
    ENCRYPT = "encrypt"
    """Encrypt data."""
    
    DECRYPT = "decrypt"
    """Decrypt data."""
    
    AUDIT_SECURITY = "audit_security"
    """Audit security events."""
    
    # =============================================================================
    # POLICY FAMILIES
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
    # CONFIGURATION FAMILIES
    # =============================================================================
    
    SET_CONFIG = "set_config"
    """Set configuration value."""
    
    GET_CONFIG = "get_config"
    """Get configuration value."""
    
    MODIFY_CONFIG_F = "modify_config"  # 'f' suffix to avoid conflict
    """Modify existing configuration."""
    
    RESET_CONFIG = "reset_config"
    """Reset to default."""
    
    # =============================================================================
    # EXTERNAL INTERACTION FAMILIES
    # =============================================================================
    
    API_CALL_F = "api_call"
    """Invoke external API."""
    
    NETWORK_REQUEST_F = "network_request"
    """Make network request."""
    
    DATABASE_QUERY_F = "database_query"
    """Query database."""
    
    FILE_ACCESS_F = "file_access"
    """Access file system."""
    
    # =============================================================================
    # PHYSICAL FAMILIES
    # =============================================================================
    
    MOVE_PHYSICAL_F = "move_physical"
    """Move physical entity."""
    
    TOUCH_F = "touch"
    """Physically interact."""
    
    CONTROL_DEVICE_F = "control_device"
    """Control device."""
    
    # =============================================================================
    # COMPOSITE FAMILIES
    # =============================================================================
    
    SEQUENCE_F = "sequence"
    """Execute in sequence."""
    
    PARALLEL_F = "parallel"
    """Execute in parallel."""
    
    CONDITIONAL_F = "conditional"
    """Execute conditionally."""
    
    LOOP_F = "loop"
    """Execute repeatedly."""
    
    # =============================================================================
    # GENERAL FAMILIES
    # =============================================================================
    
    WAIT = "wait"
    """Wait for condition."""
    
    SYNCHRONIZE = "synchronize"
    """Synchronize operations."""
    
    GENERAL = "general"
    """General operation."""
    
    UNKNOWN = "unknown"
    """Family is unknown or undetermined."""
    
    @property
    def category(self) -> ActionCategory:
        """
        Get the primary category for this family.
        
        Returns:
            The ActionCategory that this family belongs to.
        """
        return _FAMILY_CATEGORIES.get(self, ActionCategory.UNKNOWN)
    
    @property
    def kind(self) -> ActionKind:
        """
        Get the primary kind for this family.
        
        Returns:
            The ActionKind that this family represents.
        """
        return _FAMILY_KINDS.get(self, ActionKind.UNKNOWN)


# =============================================================================
# UTILITY TYPES - Ontology collections and relations
# =============================================================================

class ActionCategories(FrozenSet[ActionCategory]):
    """A collection of ActionCategory values."""
    
    def __new__(cls, categories: Tuple[ActionCategory, ...] = ()):
        return super().__new__(cls, categories)
    
    @classmethod
    def all(cls) -> "ActionCategories":
        """Get all canonical ActionCategories."""
        return cls(tuple(ActionCategory))
    
    @classmethod
    def informational(cls) -> "ActionCategories":
        """Get all informational categories."""
        return cls((ActionCategory.OBSERVATIONAL, ActionCategory.INFORMATIONAL))
    
    @classmethod
    def transformational(cls) -> "ActionCategories":
        """Get all transformational categories."""
        return cls((ActionCategory.TRANSFORMATIONAL,))


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


class ActionFamilies(FrozenSet[ActionFamily]):
    """A collection of ActionFamily values."""
    
    def __new__(cls, families: Tuple[ActionFamily, ...] = ()):
        return super().__new__(cls, families)
    
    @classmethod
    def all(cls) -> "ActionFamilies":
        """Get all canonical ActionFamilies."""
        return cls(tuple(ActionFamily))


# =============================================================================
# MAPPINGS - Category/Kind/Family relationships
# =============================================================================

_CATEGORY_KINDS: dict[ActionCategory, Tuple[ActionKind, ...]] = {
    ActionCategory.OBSERVATIONAL: (
        ActionKind.OBSERVE,
        ActionKind.INSPECT,
        ActionKind.MONITOR,
        ActionKind.WATCH,
    ),
    ActionCategory.INFORMATIONAL: (
        ActionKind.READ,
        ActionKind.SEARCH,
        ActionKind.QUERY,
        ActionKind.EXPLORE,
        ActionKind.VALIDATE,
        ActionKind.COMPARE,
    ),
    ActionCategory.COMPUTATIONAL: (
        ActionKind.CALCULATE,
        ActionKind.REASON,
        ActionKind.ANALYZE,
        ActionKind.SYNTHESIZE,
        ActionKind.PREDICT,
        ActionKind.OPTIMIZE,
    ),
    ActionCategory.TRANSFORMATIONAL: (
        ActionKind.MODIFY,
        ActionKind.UPDATE,
        ActionKind.TRANSFORM,
        ActionKind.REORDER,
    ),
    ActionCategory.COMMUNICATIVE: (
        ActionKind.NOTIFICATION,
        ActionKind.REQUEST,
        ActionKind.PROMPT,
        ActionKind.REPORT,
    ),
    ActionCategory.DELEGATIVE: (
        ActionKind.ASSIGN,
        ActionKind.REFER,
        ActionKind.ESCALATE,
        ActionKind.DE_ESCALATE,
    ),
    ActionCategory.RESOURCE: (
        ActionKind.RESERVE,
        ActionKind.RELEASE,
        ActionKind.ALLOCATE,
        ActionKind.DEALLOCATE,
    ),
    ActionCategory.MEMORY: (
        ActionKind.PERSIST,
        ActionKind.LOAD,
        ActionKind.STORE,
        ActionKind.CACHE,
        ActionKind.CLEAR,
    ),
    ActionCategory.WORKSPACE: (
        ActionKind.ADMISSION,
        ActionKind.REJECTION,
        ActionKind.ORGANIZE,
        ActionKind.REFACTOR,
    ),
    ActionCategory.PLANNING_SUPPORT: (
        ActionKind.PLAN,
        ActionKind.SCHEDULE,
        ActionKind.FORECAST,
        ActionKind.CONFIGURE_PLAN,
    ),
    ActionCategory.EXECUTIVE_SUPPORT: (
        ActionKind.DECIDE,
        ActionKind.DIRECT,
        ActionKind.COORDINATE,
        ActionKind.OVERRIDE,
    ),
    ActionCategory.MONITORING_SUPPORT: (
        ActionKind.AUDIT,
        ActionKind.LOG,
        ActionKind.TRACE,
        ActionKind.MEASURE,
    ),
    ActionCategory.RECOVERY_SUPPORT: (
        ActionKind.RECOVER,
        ActionKind.ROLLBACK,
        ActionKind.RESTORE,
        ActionKind.MITIGATE,
    ),
    ActionCategory.SECURITY: (
        ActionKind.AUTHORIZE,
        ActionKind.AUTHENTICATE,
        ActionKind.ENCRYPT,
        ActionKind.DECRYPT,
        ActionKind.AUDIT_SECURITY,
    ),
    ActionCategory.POLICY: (
        ActionKind.ENFORCE,
        ActionKind.VERIFY_POLICY,
        ActionKind.UPDATE_POLICY,
        ActionKind.CHECK_POLICY,
    ),
    ActionCategory.CONFIGURATION: (
        ActionKind.SET,
        ActionKind.GET,
        ActionKind.MODIFY_CONFIG,
        ActionKind.RESET,
    ),
    ActionCategory.EXTERNAL_INTERACTION: (
        ActionKind.API_CALL,
        ActionKind.NETWORK_REQUEST,
        ActionKind.DATABASE_QUERY,
        ActionKind.FILE_ACCESS,
    ),
    ActionCategory.PHYSICAL: (
        ActionKind.MOVE_PHYSICAL,
        ActionKind.TOUCH,
        ActionKind.CONTROL_DEVICE,
    ),
    ActionCategory.COMPOSITE: (
        ActionKind.SEQUENCE,
        ActionKind.PARALLEL,
        ActionKind.CONDITIONAL,
        ActionKind.LOOP,
    ),
}

_KIND_CATEGORIES: dict[ActionKind, ActionCategory] = {
    kind: category
    for category, kinds in _CATEGORY_KINDS.items()
    for kind in kinds
}

_FAMILY_CATEGORIES: dict[ActionFamily, ActionCategory] = {
    # Observational
    ActionFamily.OBSERVE: ActionCategory.OBSERVATIONAL,
    ActionFamily.INSPECT: ActionCategory.OBSERVATIONAL,
    ActionFamily.MONITOR: ActionCategory.OBSERVATIONAL,
    ActionFamily.WATCH: ActionCategory.OBSERVATIONAL,
    
    # Informational
    ActionFamily.READ: ActionCategory.INFORMATIONAL,
    ActionFamily.SEARCH: ActionCategory.INFORMATIONAL,
    ActionFamily.QUERY: ActionCategory.INFORMATIONAL,
    ActionFamily.EXPLORE: ActionCategory.INFORMATIONAL,
    ActionFamily.VALIDATE: ActionCategory.INFORMATIONAL,
    ActionFamily.COMPARE: ActionCategory.INFORMATIONAL,
    
    # Computational
    ActionFamily.CALCULATE: ActionCategory.COMPUTATIONAL,
    ActionFamily.REASON: ActionCategory.COMPUTATIONAL,
    ActionFamily.ANALYZE: ActionCategory.COMPUTATIONAL,
    ActionFamily.SYNTHESIZE: ActionCategory.COMPUTATIONAL,
    ActionFamily.PREDICT: ActionCategory.COMPUTATIONAL,
    ActionFamily.OPTIMIZE: ActionCategory.COMPUTATIONAL,
    
    # Transformational
    ActionFamily.MODIFY: ActionCategory.TRANSFORMATIONAL,
    ActionFamily.UPDATE: ActionCategory.TRANSFORMATIONAL,
    ActionFamily.TRANSFORM: ActionCategory.TRANSFORMATIONAL,
    ActionFamily.REORDER: ActionCategory.TRANSFORMATIONAL,
    ActionFamily.NORMALIZE: ActionCategory.TRANSFORMATIONAL,
    
    # Creation
    ActionFamily.CREATE: ActionCategory.TRANSFORMATIONAL,
    ActionFamily.CONSTRUCT: ActionCategory.TRANSFORMATIONAL,
    ActionFamily.GENERATE: ActionCategory.TRANSFORMATIONAL,
    ActionFamily.ACQUIRE: ActionCategory.TRANSFORMATIONAL,
    ActionFamily.BUILD: ActionCategory.TRANSFORMATIONAL,
    
    # Deletion
    ActionFamily.DELETE: ActionCategory.TRANSFORMATIONAL,
    ActionFamily.REMOVE: ActionCategory.TRANSFORMATIONAL,
    ActionFamily.REVERT: ActionCategory.TRANSFORMATIONAL,
    ActionFamily.COMPENSATE: ActionCategory.RECOVERY_SUPPORT,
    ActionFamily.ROLLBACK_F: ActionCategory.RECOVERY_SUPPORT,
    
    # Communicative
    ActionFamily.NOTIFICATION: ActionCategory.COMMUNICATIVE,
    ActionFamily.REQUEST: ActionCategory.COMMUNICATIVE,
    ActionFamily.PROMPT: ActionCategory.COMMUNICATIVE,
    ActionFamily.REPORT: ActionCategory.COMMUNICATIVE,
    ActionFamily.BROADCAST: ActionCategory.COMMUNICATIVE,
    
    # Delegative
    ActionFamily.ASSIGN: ActionCategory.DELEGATIVE,
    ActionFamily.REFER: ActionCategory.DELEGATIVE,
    ActionFamily.ESCALATE: ActionCategory.DELEGATIVE,
    ActionFamily.DE_ESCALATE: ActionCategory.DELEGATIVE,
    
    # Resource
    ActionFamily.RESERVE: ActionCategory.RESOURCE,
    ActionFamily.RELEASE: ActionCategory.RESOURCE,
    ActionFamily.ALLOCATE: ActionCategory.RESOURCE,
    ActionFamily.DEALLOCATE: ActionCategory.RESOURCE,
    ActionFamily.ACQUIRE_RESOURCE: ActionCategory.RESOURCE,
    
    # Memory
    ActionFamily.PERSIST: ActionCategory.MEMORY,
    ActionFamily.LOAD: ActionCategory.MEMORY,
    ActionFamily.STORE: ActionCategory.MEMORY,
    ActionFamily.CACHE: ActionCategory.MEMORY,
    ActionFamily.CLEAR: ActionCategory.MEMORY,
    
    # Workspace
    ActionFamily.ADMISSION: ActionCategory.WORKSPACE,
    ActionFamily.REJECTION: ActionCategory.WORKSPACE,
    ActionFamily.ORGANIZE: ActionCategory.WORKSPACE,
    ActionFamily.REFACTOR: ActionCategory.WORKSPACE,
    
    # Planning Support
    ActionFamily.PLAN: ActionCategory.PLANNING_SUPPORT,
    ActionFamily.SCHEDULE: ActionCategory.PLANNING_SUPPORT,
    ActionFamily.FORECAST: ActionCategory.PLANNING_SUPPORT,
    ActionFamily.CONFIGURE_PLAN: ActionCategory.PLANNING_SUPPORT,
    
    # Executive Support
    ActionFamily.DECIDE: ActionCategory.EXECUTIVE_SUPPORT,
    ActionFamily.DIRECT: ActionCategory.EXECUTIVE_SUPPORT,
    ActionFamily.COORDINATE: ActionCategory.EXECUTIVE_SUPPORT,
    ActionFamily.OVERRIDE: ActionCategory.EXECUTIVE_SUPPORT,
    
    # Monitoring Support
    ActionFamily.AUDIT: ActionCategory.MONITORING_SUPPORT,
    ActionFamily.LOG: ActionCategory.MONITORING_SUPPORT,
    ActionFamily.TRACE: ActionCategory.MONITORING_SUPPORT,
    ActionFamily.MEASURE: ActionCategory.MONITORING_SUPPORT,
    
    # Recovery Support
    ActionFamily.RECOVER: ActionCategory.RECOVERY_SUPPORT,
    ActionFamily.ROLLBACK_F: ActionCategory.RECOVERY_SUPPORT,
    ActionFamily.RESTORE: ActionCategory.RECOVERY_SUPPORT,
    ActionFamily.MITIGATE: ActionCategory.RECOVERY_SUPPORT,
    
    # Security
    ActionFamily.AUTHORIZE: ActionCategory.SECURITY,
    ActionFamily.AUTHENTICATE: ActionCategory.SECURITY,
    ActionFamily.ENCRYPT: ActionCategory.SECURITY,
    ActionFamily.DECRYPT: ActionCategory.SECURITY,
    ActionFamily.AUDIT_SECURITY: ActionCategory.SECURITY,
    
    # Policy
    ActionFamily.ENFORCE_POLICY: ActionCategory.POLICY,
    ActionFamily.VERIFY_POLICY: ActionCategory.POLICY,
    ActionFamily.UPDATE_POLICY: ActionCategory.POLICY,
    ActionFamily.CHECK_POLICY: ActionCategory.POLICY,
    
    # Configuration
    ActionFamily.SET_CONFIG: ActionCategory.CONFIGURATION,
    ActionFamily.GET_CONFIG: ActionCategory.CONFIGURATION,
    ActionFamily.MODIFY_CONFIG_F: ActionCategory.CONFIGURATION,
    ActionFamily.RESET_CONFIG: ActionCategory.CONFIGURATION,
    
    # External Interaction
    ActionFamily.API_CALL_F: ActionCategory.EXTERNAL_INTERACTION,
    ActionFamily.NETWORK_REQUEST_F: ActionCategory.EXTERNAL_INTERACTION,
    ActionFamily.DATABASE_QUERY_F: ActionCategory.EXTERNAL_INTERACTION,
    ActionFamily.FILE_ACCESS_F: ActionCategory.EXTERNAL_INTERACTION,
    
    # Physical (if applicable)
    ActionFamily.MOVE_PHYSICAL_F: ActionCategory.PHYSICAL,
    ActionFamily.TOUCH_F: ActionCategory.PHYSICAL,
    ActionFamily.CONTROL_DEVICE_F: ActionCategory.PHYSICAL,
    
    # Composite
    ActionFamily.SEQUENCE_F: ActionCategory.COMPOSITE,
    ActionFamily.PARALLEL_F: ActionCategory.COMPOSITE,
    ActionFamily.CONDITIONAL_F: ActionCategory.COMPOSITE,
    ActionFamily.LOOP_F: ActionCategory.COMPOSITE,
    
    # General
    ActionFamily.WAIT: ActionCategory.GENERAL,
    ActionFamily.SYNCHRONIZE: ActionCategory.GENERAL,
    ActionFamily.GENERAL: ActionCategory.GENERAL,
}

_FAMILY_KINDS: dict[ActionFamily, ActionKind] = {
    # Observational
    ActionFamily.OBSERVE: ActionKind.OBSERVE,
    ActionFamily.INSPECT: ActionKind.INSPECT,
    ActionFamily.MONITOR: ActionKind.MONITOR,
    ActionFamily.WATCH: ActionKind.MONITOR,
    
    # Informational
    ActionFamily.READ: ActionKind.READ,
    ActionFamily.SEARCH: ActionKind.SEARCH,
    ActionFamily.QUERY: ActionKind.QUERY,
    ActionFamily.EXPLORE: ActionKind.EXPLORE,
    ActionFamily.VALIDATE: ActionKind.VALIDATE,
    ActionFamily.COMPARE: ActionKind.COMPARE,
    
    # Computational
    ActionFamily.CALCULATE: ActionKind.CALCULATE,
    ActionFamily.REASON: ActionKind.REASON,
    ActionFamily.ANALYZE: ActionKind.ANALYZE,
    ActionFamily.SYNTHESIZE: ActionKind.SYNTHESIZE,
    ActionFamily.PREDICT: ActionKind.PREDICT,
    ActionFamily.OPTIMIZE: ActionKind.OPTIMIZE,
    
    # Transformational
    ActionFamily.MODIFY: ActionKind.MODIFY,
    ActionFamily.UPDATE: ActionKind.UPDATE,
    ActionFamily.TRANSFORM: ActionKind.TRANSFORM,
    ActionFamily.REORDER: ActionKind.REORDER,
    ActionFamily.NORMALIZE: ActionKind.UPDATE,
    
    # Creation
    ActionFamily.CREATE: ActionKind.CREATE,
    ActionFamily.CONSTRUCT: ActionKind.CONSTRUCT,
    ActionFamily.GENERATE: ActionKind.GENERATE,
    ActionFamily.ACQUIRE: ActionKind.ACQUIRE,
    ActionFamily.BUILD: ActionKind.CREATE,
    
    # Deletion
    ActionFamily.DELETE: ActionKind.DELETE,
    ActionFamily.REMOVE: ActionKind.REMOVE,
    ActionFamily.REVERT: ActionKind.REVERT,
    ActionFamily.COMPENSATE: ActionKind.COMPENSATE,
    ActionFamily.ROLLBACK_F: ActionKind.ROLLBACK,
    
    # Communicative
    ActionFamily.NOTIFICATION: ActionKind.NOTIFICATION,
    ActionFamily.REQUEST: ActionKind.REQUEST,
    ActionFamily.PROMPT: ActionKind.PROMPT,
    ActionFamily.REPORT: ActionKind.REPORT,
    ActionFamily.BROADCAST: ActionKind.NOTIFICATION,
    
    # Delegative
    ActionFamily.ASSIGN: ActionKind.ASSIGN,
    ActionFamily.REFER: ActionKind.REFER,
    ActionFamily.ESCALATE: ActionKind.ESCALATE,
    ActionFamily.DE_ESCALATE: ActionKind.DE_ESCALATE,
    
    # Resource
    ActionFamily.RESERVE: ActionKind.RESERVE,
    ActionFamily.RELEASE: ActionKind.RELEASE,
    ActionFamily.ALLOCATE: ActionKind.ALLOCATE,
    ActionFamily.DEALLOCATE: ActionKind.DEALLOCATE,
    ActionFamily.ACQUIRE_RESOURCE: ActionKind.ALLOCATE,
    
    # Memory
    ActionFamily.PERSIST: ActionKind.PERSIST,
    ActionFamily.LOAD: ActionKind.LOAD,
    ActionFamily.STORE: ActionKind.STORE,
    ActionFamily.CACHE: ActionKind.CACHE,
    ActionFamily.CLEAR: ActionKind.CLEAR,
    
    # Workspace
    ActionFamily.ADMISSION: ActionKind.ADMISSION,
    ActionFamily.REJECTION: ActionKind.REJECTION,
    ActionFamily.ORGANIZE: ActionKind.ORGANIZE,
    ActionFamily.REFACTOR: ActionKind.MODIFY_CONFIG_F,
    
    # Planning Support
    ActionFamily.PLAN: ActionKind.PLAN,
    ActionFamily.SCHEDULE: ActionKind.SCHEDULE,
    ActionFamily.FORECAST: ActionKind.FORECAST,
    ActionFamily.CONFIGURE_PLAN: ActionKind.CONFIGURE_PLAN,
    
    # Executive Support
    ActionFamily.DECIDE: ActionKind.DECIDE,
    ActionFamily.DIRECT: ActionKind.DIRECT,
    ActionFamily.COORDINATE: ActionKind.COORDINATE,
    ActionFamily.OVERRIDE: ActionKind.OVERRIDE,
    
    # Monitoring Support
    ActionFamily.AUDIT: ActionKind.AUDIT,
    ActionFamily.LOG: ActionKind.LOG,
    ActionFamily.TRACE: ActionKind.TRACE,
    ActionFamily.MEASURE: ActionKind.MEASURE,
    
    # Recovery Support
    ActionFamily.RECOVER: ActionKind.RECOVER,
    ActionFamily.ROLLBACK_F: ActionKind.ROLLBACK,
    ActionFamily.RESTORE: ActionKind.RESTORE,
    ActionFamily.MITIGATE: ActionKind.MITIGATE,
    
    # Security
    ActionFamily.AUTHORIZE: ActionKind.AUTHORIZE,
    ActionFamily.AUTHENTICATE: ActionKind.AUTHENTICATE,
    ActionFamily.ENCRYPT: ActionKind.ENCRYPT,
    ActionFamily.DECRYPT: ActionKind.DECRYPT,
    ActionFamily.AUDIT_SECURITY: ActionKind.AUDIT_SECURITY,
    
    # Policy
    ActionFamily.ENFORCE_POLICY: ActionKind.ENFORCE,
    ActionFamily.VERIFY_POLICY: ActionKind.VERIFY_POLICY,
    ActionFamily.UPDATE_POLICY: ActionKind.UPDATE_POLICY,
    ActionFamily.CHECK_POLICY: ActionKind.CHECK_POLICY,
    
    # Configuration
    ActionFamily.SET_CONFIG: ActionKind.SET,
    ActionFamily.GET_CONFIG: ActionKind.GET,
    ActionFamily.MODIFY_CONFIG_F: ActionKind.MODIFY_CONFIG,
    ActionFamily.RESET_CONFIG: ActionKind.RESET,
    
    # External Interaction
    ActionFamily.API_CALL_F: ActionKind.API_CALL,
    ActionFamily.NETWORK_REQUEST_F: ActionKind.NETWORK_REQUEST,
    ActionFamily.DATABASE_QUERY_F: ActionKind.DATABASE_QUERY,
    ActionFamily.FILE_ACCESS_F: ActionKind.FILE_ACCESS,
    
    # Physical (if applicable)
    ActionFamily.MOVE_PHYSICAL_F: ActionKind.MOVE_PHYSICAL,
    ActionFamily.TOUCH_F: ActionKind.TOUCH,
    ActionFamily.CONTROL_DEVICE_F: ActionKind.CONTROL_DEVICE,
    
    # Composite
    ActionFamily.SEQUENCE_F: ActionKind.SEQUENCE,
    ActionFamily.PARALLEL_F: ActionKind.PARALLEL,
    ActionFamily.CONDITIONAL_F: ActionKind.CONDITIONAL,
    ActionFamily.LOOP_F: ActionKind.LOOP,
    
    # General
    ActionFamily.WAIT: ActionKind.WAIT,
    ActionFamily.SYNCHRONIZE: ActionKind.SYNCHRONIZE,
    ActionFamily.GENERAL: ActionKind.GENERAL,
}


__all__ = [
    "ActionCategory",
    "ActionCategories",
    "ActionKind",
    "ActionKinds",
    "ActionFamily",
    "ActionFamilies",
]