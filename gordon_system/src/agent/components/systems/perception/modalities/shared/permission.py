# Modality Permission - Phase 5.2 Authorization Grant
# ====================================================

"""
ModalityPermission: An authorization grant for a specific capability within
a defined scope.

Permissions are evaluated before modality activation. A permission grant does
not imply the capability exists or is available.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# PERMISSION DECISION - Outcome of permission evaluation
# =============================================================================


class PermissionDecision(Enum):
    """
    Decision made after evaluating a permission request.
    
    ALLOWED: Permission granted without restrictions
    DENIED: Permission explicitly denied
    RESTRICTED: Permission granted with limitations
    SANDBOX_ONLY: Permission only in sandboxed mode
    REQUIRES_APPROVAL: Human or policy approval required
    UNAVAILABLE: Cannot determine (source unavailable)
    """
    
    ALLOWED = "allowed"
    DENIED = "denied"
    RESTRICTED = "restricted"
    SANDBOX_ONLY = "sandbox_only"
    REQUIRES_APPROVAL = "requires_approval"
    UNAVAILABLE = "unavailable"


# =============================================================================
# PERMISSION SCOPE - What can be observed with a permission
# =============================================================================


class PermissionScope(Enum):
    """
    Scope of what can be observed with a given permission.
    
    The scope defines the breadth of observation, not whether it is currently
    being observed.
    """
    
    # Sensory modalities
    SENSOR_SELF = "sensor_self"           # Only this sensor's data
    SENSOR_USER = "sensor_user"           # Sensors owned by user
    SENSOR_HOST = "sensor_host"           # All host sensors
    
    # Digital modalities
    PROCESS_SELF = "process_self"         # Own processes only
    PROCESS_TREE = "process_tree"         # Current process tree
    USER_FILES = "user_files"             # User's files
    NETWORK_INTERFACE = "network_interface"  # Network interfaces
    KERNEL_EVENTS = "kernel_events"       # Kernel event stream
    WINDOW_DESKTOP = "window_desktop"     # Desktop windows
    CLIPBOARD_SELF = "clipboard_self"     # Own clipboard changes


# =============================================================================
# PERMISSION - Authorization grant for a capability
# =============================================================================


@dataclass(frozen=True)
class ModalityPermission:
    """
    An authorization grant for a specific capability within a defined scope.
    
    Permissions are evaluated before modality activation. A permission grant
    does not imply the capability exists or is available.
    
    Fields:
        permission_identity:  Unique identifier for this permission
        
        modality_identity:    Which modality this grants access to
        
        permitted_capability: What capability is granted (CAPTURE_IMAGE, etc.)
        
        scope:                Scope of observation (PROCESS_SELF, USER_FILES, etc.)
        
        constraints:          Additional constraints on the permission
        validity:             When this permission is valid (time range)
        
        authority:            Who granted this permission
        provenance:           Permission grant tracking
        
        revision:             Version number
    """
    
    # Core identity (required)
    permission_identity: str            # Globally unique identifier
    
    modality_identity: str              # Which modality?
    
    permitted_capability: str           # Capability being permitted
    
    scope: str = "self"                 # Observation scope
    
    # Constraints and validity
    constraints: Tuple[str, ...] = field(default_factory=tuple)
    validity_start_utc: Optional[float] = None  # Start time (optional)
    validity_end_utc: Optional[float] = None    # End time (optional)
    
    # Authority
    authority: str = "unknown"          # Who granted this?
    authority_type: str = "system"      # system, user, policy, admin
    
    provenance: Dict[str, Any] = field(default_factory=dict)  # Origin tracking
    
    revision: int = 1
    
    @property
    def is_active(self) -> bool:
        """Check if permission is currently active (within validity window)."""
        current_time = time.time()
        
        if self.validity_start_utc and current_time < self.validity_start_utc:
            return False
        
        if self.validity_end_utc and current_time > self.validity_end_utc:
            return False
        
        return True
    
    @property
    def has_constraints(self) -> bool:
        """Check if this permission has constraints."""
        return len(self.constraints) > 0
    
    @classmethod
    def create(
        cls,
        modality_identity: str,
        permitted_capability: str,
        identity: Optional[str] = None,
        scope: str = "self",
        authority: str = "system",
        validity_start_utc: Optional[float] = None,
        validity_end_utc: Optional[float] = None,
    ) -> "ModalityPermission":
        """
        Create a new permission instance.
        
        Args:
            modality_identity: Which modality this grants access to
            permitted_capability: What capability is granted
            identity: Unique identifier (auto-generated if None)
            scope: Observation scope
            authority: Who granted this permission
            validity_start_utc: Start time (optional)
            validity_end_utc: End time (optional)
            
        Returns:
            New ModalityPermission instance
        """
        return cls(
            permission_identity=identity or f"perm:{modality_identity}:{permitted_capability}",
            modality_identity=modality_identity,
            permitted_capability=permitted_capability,
            scope=scope,
            constraints=(),
            validity_start_utc=validity_start_utc,
            validity_end_utc=validity_end_utc,
            authority=authority,
            revision=1,
        )


# =============================================================================
# PERMISSION SET - Collection of permissions
# =============================================================================


@dataclass(frozen=True)
class PermissionSet:
    """
    A collection of permissions granted to a modality.
    
    Fields:
        permission_set_identity: Set identifier
        permissions:             Tuple of individual permissions
        revision:                Version number
    """
    
    permission_set_identity: str        # Globally unique identifier
    permissions: Tuple[ModalityPermission, ...] = field(default_factory=tuple)
    revision: int = 1
    
    def has_permission(self, modality: str, capability: str) -> bool:
        """Check if this set contains a permission for the given capability."""
        return any(
            p.modality_identity == modality and p.permitted_capability == capability
            for p in self.permissions
        )
    
    def get_permission(self, modality: str, capability: str) -> Optional[ModalityPermission]:
        """Get a specific permission from this set."""
        for perm in self.permissions:
            if (perm.modality_identity == modality and 
                perm.permitted_capability == capability):
                return perm
        return None
    
    def get_active_permissions(self) -> Tuple[ModalityPermission, ...]:
        """Get only permissions that are currently active."""
        return tuple(p for p in self.permissions if p.is_active)
    
    def get_scopes(self) -> Tuple[str, ...]:
        """Get all unique scopes from permissions in this set."""
        scopes = set()
        for perm in self.permissions:
            scopes.add(perm.scope)
        return tuple(scopes)


# =============================================================================
# PERMISSION EVALUATOR - Interface for permission evaluation
# =============================================================================


class PermissionEvaluator:
    """
    Interface for evaluating permissions before modality activation.
    
    Implementations may check:
        - User authorization
        - Policy rules
        - Sandbox constraints
        - Time-based validity
        - Resource availability
    
    The evaluator returns a Decision indicating whether and how the permission
    should be applied.
    """
    
    def evaluate(
        self,
        modality_identity: str,
        capability: str,
        requested_scope: str,
    ) -> PermissionDecision:
        """
        Evaluate a permission request.
        
        Args:
            modality_identity: The modality requesting access
            capability: The capability being requested
            requested_scope: The scope of observation requested
            
        Returns:
            Decision indicating the outcome
        """
        raise NotImplementedError
    
    def get_effective_scopes(
        self,
        modality_identity: str,
        capability: str,
    ) -> Tuple[str, ...]:
        """
        Get all effective scopes for a capability.
        
        Args:
            modality_identity: The modality requesting access
            capability: The capability being queried
            
        Returns:
            Tuple of scope strings
        """
        raise NotImplementedError


# =============================================================================
# EXPORTS
# =============================================================================

__all__: list[str] = [
    # Enums
    "PermissionDecision",
    "PermissionScope",
    
    # Dataclasses
    "ModalityPermission",
    "PermissionSet",
    
    # Classes
    "PermissionEvaluator",
]