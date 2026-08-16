# Gordon Cognitive Architecture - Phase 4.11.9
# ===========================================

"""
Cognitive Coordination Governance (CCG) - Permissions and Prohibitions
======================================================================

Explicit permissions and prohibitions that govern what operations are allowed.

Following:
* PERMISSION-LAW-001 through PERMISSION-LAW-008
* PROHIBITION-LAW-001 through PROHIBITION-LAW-008
"""

from __future__ import annotations

from dataclasses import dataclass, field


# =============================================================================
# PERMISSION
# =============================================================================

@dataclass(frozen=True, slots=True)
class Permission:
    """
    Immutable permission definition.
    
    PERMISSION-LAW-001: Permissions shall remain explicit
    PERMISSION-LAW-002: Permissions shall reference governing authority
    PERMISSION-LAW-003: Permissions shall preserve applicability
    PERMISSION-LAW-004: Permissions shall remain subordinate to prohibitions
    PERMISSION-LAW-005: Permission provenance shall remain complete
    PERMISSION-LAW-006: Permission revisions shall preserve lineage
    PERMISSION-LAW-007: Historical permissions shall remain inspectable
    PERMISSION-LAW-008: Permission evaluation shall remain deterministic
    
    CCG-PERM-INV-001: Permission is immutable (deeply frozen)
    CCG-PERM-INV-002: Permission has no runtime references
    """
    permission_identity: str
    """Unique identifier for this permission."""
    
    permitted_operation: str
    """Operation that is permitted."""
    
    authority_ref: str
    """Reference to the governing authority."""
    
    scope: str = "global"
    """Scope where this permission applies."""
    
    conditions: tuple[str, ...] = field(default_factory=tuple)
    """Conditions that must be met for this permission."""
    
    revision: int = 1
    """Revision number of this permission."""
    
    provenance_ref: str | None = None
    """Reference to permission provenance record."""
    
    @classmethod
    def create(
        cls,
        permission_id: str,
        operation: str,
        authority_ref: str,
        scope: str = "global",
        conditions: tuple[str, ...] | None = None,
    ) -> Permission:
        """
        Create a new permission.
        
        Args:
            permission_id: Unique identifier
            operation: Permitted operation
            authority_ref: Governing authority reference
            scope: Scope where it applies
            conditions: Required conditions
            
        Returns:
            A new Permission instance
        """
        return cls(
            permission_identity=permission_id,
            permitted_operation=operation,
            authority_ref=authority_ref,
            scope=scope,
            conditions=conditions or (),
            revision=1,
            provenance_ref=None,
        )


# =============================================================================
# PROHIBITION
# =============================================================================

@dataclass(frozen=True, slots=True)
class Prohibition:
    """
    Immutable prohibition definition.
    
    PROHIBITION-LAW-001: Prohibitions shall override permissions
    PROHIBITION-LAW-002: Every prohibition shall preserve justification
    PROHIBITION-LAW-003: Affected architectural scope shall remain explicit
    PROHIBITION-LAW-004: Severity shall remain explicit
    PROHIBITION-LAW-005: Prohibition provenance shall remain complete
    PROHIBITION-LAW-006: Historical prohibitions shall remain inspectable
    PROHIBITION-LAW-007: Prohibition revisions shall preserve lineage
    PROHIBITION-LAW-008: Prohibition evaluation shall remain deterministic
    
    CCG-PROH-INV-001: Prohibition is immutable (deeply frozen)
    CCG-PROH-INV-002: Prohibition has no runtime references
    """
    prohibition_identity: str
    """Unique identifier for this prohibition."""
    
    prohibited_operation: str
    """Operation that is prohibited."""
    
    reason: str
    """Reason for the prohibition."""
    
    severity: str = "warning"
    """Severity level of the violation."""
    
    affected_scope: str = "global"
    """Scope where this prohibition applies."""
    
    revision: int = 1
    """Revision number of this prohibition."""
    
    provenance_ref: str | None = None
    """Reference to prohibition provenance record."""
    
    @classmethod
    def create(
        cls,
        prohibition_id: str,
        operation: str,
        reason: str,
        severity: str = "warning",
        scope: str = "global",
    ) -> Prohibition:
        """
        Create a new prohibition.
        
        Args:
            prohibition_id: Unique identifier
            operation: Prohibited operation
            reason: Reason for the prohibition
            severity: Severity level
            scope: Scope where it applies
            
        Returns:
            A new Prohibition instance
        """
        return cls(
            prohibition_identity=prohibition_id,
            prohibited_operation=operation,
            reason=reason,
            severity=severity,
            affected_scope=scope,
            revision=1,
            provenance_ref=None,
        )


# =============================================================================
# CANONICAL PERMISSIONS
# =============================================================================

class CanonicalPermissions:
    """Canonical permissions for Gordon governance."""
    
    PUBLISH_CCP = Permission.create(
        permission_id="permission:publish_ccp",
        operation="publish_coordination_protocol_message",
        authority_ref="authority:coordination",
        scope="coordination:protocol",
    )
    
    READ_MEMORY = Permission.create(
        permission_id="permission:read_memory",
        operation="read_from_memory",
        authority_ref="authority:memory",
        scope="memory:storage",
    )
    
    MODIFY_PLANNING = Permission.create(
        permission_id="permission:modify_planning",
        operation="modify_plan_state",
        authority_ref="authority:planning",
        scope="planning:strategy",
    )
    
    OBSERVE_EVENTS = Permission.create(
        permission_id="permission:observe_events",
        operation="observe_cognitive_event",
        authority_ref="authority:coordination",
        scope="events:stream",
    )
    
    ALLOCATE_RESOURCES = Permission.create(
        permission_id="permission:allocate_resources",
        operation="allocate_system_resources",
        authority_ref="authority:coordination",
        scope="resources:system",
    )
    
    @classmethod
    def all_permissions(cls) -> tuple[Permission, ...]:
        """Return all canonical permissions."""
        return (
            cls.PUBLISH_CCP,
            cls.READ_MEMORY,
            cls.MODIFY_PLANNING,
            cls.OBSERVE_EVENTS,
            cls.ALLOCATE_RESOURCES,
        )


# =============================================================================
# CANONICAL PROHIBITIONS
# =============================================================================

class CanonicalProhibitions:
    """Canonical prohibitions for Gordon governance."""
    
    MODIFY_CONSTITUTION = Prohibition.create(
        prohibition_id="prohibition:modify_constitution",
        operation="modify_active_constitution",
        reason="Constitutional changes must follow evolution protocol",
        severity="critical",
    )
    
    MUTATE_HISTORY = Prohibition.create(
        prohibition_id="prohibition:mutate_history",
        operation="mutate_historical_records",
        reason="Historical records are immutable for provenance",
        severity="critical",
    )
    
    BYPASS_CCP = Prohibition.create(
        prohibition_id="prohibition:bypass_ccp",
        operation="bypass_coordination_protocol",
        reason="Coordination protocol must be followed for all communications",
        severity="major",
    )
    
    SKIP_VALIDATION = Prohibition.create(
        prohibition_id="prohibition:skip_validation",
        operation="skip_governance_validation",
        reason="All governance decisions require validation",
        severity="critical",
    )
    
    IGNORE_PROVENANCE = Prohibition.create(
        prohibition_id="prohibition:ignore_provenance",
        operation="ignore_provenance_records",
        reason="Provenance must be preserved for traceability",
        severity="major",
    )
    
    @classmethod
    def all_prohibitions(cls) -> tuple[Prohibition, ...]:
        """Return all canonical prohibitions."""
        return (
            cls.MODIFY_CONSTITUTION,
            cls.MUTATE_HISTORY,
            cls.BYPASS_CCP,
            cls.SKIP_VALIDATION,
            cls.IGNORE_PROVENANCE,
        )


# =============================================================================
# PERMISSION PROTOCOL
# =============================================================================

@dataclass(frozen=True, slots=True)
class PermissionProtocol:
    """
    Immutable permission evaluation protocol.
    
    CCG-PERM-PROTO-INV-001: Protocol is immutable
    CPG-PERM-PROTO-INV-002: Protocol has no runtime references
    
    PERMISSION-LAW-004: Prohibitions override permissions
    """
    authority_ref: str
    """Authority for this permission check."""
    
    operation: str
    """Operation being checked."""
    
    scope: str = "global"
    """Scope of the operation."""
    
    conditions_satisfied: bool = True
    """Whether all conditions are satisfied."""
    
    has_prohibition: bool = False
    """Whether there's a conflicting prohibition."""
    
    def is_permitted(self) -> bool:
        """
        Check if the operation is permitted.
        
        Prohibitions override permissions.
        Conditions must be satisfied.
        """
        return self.conditions_satisfied and not self.has_prohibition
    
    @classmethod
    def of_permit(cls, authority: str, operation: str, scope: str = "global") -> PermissionProtocol:
        """Create a permitted protocol result."""
        return cls(
            authority_ref=authority,
            operation=operation,
            scope=scope,
            conditions_satisfied=True,
            has_prohibition=False,
        )
    
    @classmethod
    def of_deny(cls, authority: str, operation: str, reason: str) -> PermissionProtocol:
        """Create a denied protocol result."""
        return cls(
            authority_ref=authority,
            operation=operation,
            conditions_satisfied=True,
            has_prohibition=True,
        )