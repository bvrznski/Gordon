# Modality Sandbox Profile - Phase 5.2 Observation Constraints
# ============================================================

"""
ModalitySandboxProfile: A declaration of what portion of the environment a
modality may observe.

Sandboxing modifies visibility but does not change the semantics of observations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time


# =============================================================================
# SANDBOX PROFILE - Levels of sandbox restriction
# =============================================================================


class SandboxProfile(Enum):
    """
    Levels of sandbox restriction applied to a modality.
    
    Higher sandbox profiles restrict what the modality can observe but provide
    stronger isolation guarantees. Sandboxing never implies broader observation.
    """
    
    # No sandboxing
    NONE = "none"               # Full access (development only)
    
    # Process-level isolation
    PROCESS = "process"         # Current process and children
    
    # User-level isolation
    USER = "user"               # Resources owned by current user
    
    # Container-level isolation
    CONTAINER = "container"     # Container scope (Docker, Podman, etc.)
    
    # Namespace-level isolation
    NAMESPACE = "namespace"     # Linux namespaces
    
    # VM-level isolation
    VIRTUAL_MACHINE = "vm"      # Virtual machine isolation
    
    # Remote observation only
    REMOTE = "remote"           # Only remote/external observation
    
    # Maximum restriction
    STRICT = "strict"           # Strictest possible restrictions


# =============================================================================
# VISIBILITY SCOPE - What can be observed within a sandbox
# =============================================================================


class VisibilityScope(Enum):
    """
    Scope of visibility within a sandboxed environment.
    
    The effective visibility scope is the intersection of:
        1. Sandbox profile maximum visibility
        2. Permission grants
        3. Resource availability
    """
    
    # Self only
    SELF = "self"               # Own processes, files, etc.
    
    # User-scoped
    USER_PROCESS_TREE = "user_process_tree"
    USER_FILES = "user_files"
    USER_ENVIRONMENT = "user_environment"
    
    # Container-scoped
    CONTAINER_PROCESS_TREE = "container_process_tree"
    CONTAINER_FILES = "container_files"
    
    # Host-scoped (restricted)
    HOST_SUMMARY = "host_summary"       # Aggregated, non-identifying data
    HOST_DETAILED = "host_detailed"     # Detailed but not privileged


# =============================================================================
# SANDBOX CONSTRAINT - Specific restrictions applied to a sandbox
# =============================================================================


@dataclass(frozen=True)
class SandboxConstraint:
    """
    A specific constraint within a sandbox profile.
    
    Fields:
        constraint_type:   Type of constraint (READ_ONLY, NO_WRITE, etc.)
        scope:             What the constraint applies to
        value:             Constraint-specific value
    """
    
    constraint_type: str              # READ_ONLY, NO_CREATE, LIMIT_SIZE, etc.
    scope: str                        # Files, Processes, Network, etc.
    value: Optional[str] = None       # Optional parameter


# =============================================================================
# SANDBOX PROFILE - Complete sandbox configuration
# =============================================================================


@dataclass(frozen=True)
class ModalitySandboxProfile:
    """
    A complete sandbox profile for a modality.
    
    Sandbox scope constrains visibility. It does not change the semantics of
    observations produced by the modality.
    
    Fields:
        sandbox_profile:     Active sandbox level (NONE to STRICT)
        
        visibility_scope:    What can be observed within this sandbox
        
        constraints:         Additional constraints beyond profile
        
        namespace_context:   Namespace information where applicable
        
        container_id:        Container identifier if running in a container
        host_root:           Host root path when mounted
        
        provenance:          Sandbox configuration tracking
        revision:            Version number
    """
    
    # Core identity (required)
    sandbox_profile: str                # NONE, PROCESS, USER, etc.
    
    visibility_scope: str = "self"      # What's visible
    
    # Constraints
    constraints: Tuple[SandboxConstraint, ...] = field(default_factory=tuple)
    
    # Context information
    namespace_context: Dict[str, Any] = field(default_factory=dict)  # PID, UID, etc.
    container_id: Optional[str] = None
    host_root: Optional[str] = None
    
    provenance: Dict[str, Any] = field(default_factory=dict)
    
    revision: int = 1
    
    @property
    def is_sandboxed(self) -> bool:
        """Check if any sandboxing is applied."""
        return self.sandbox_profile != "none"
    
    @property
    def is_strict(self) -> bool:
        """Check if strict sandbox profile is active."""
        return self.sandbox_profile == "strict"
    
    @property
    def allows_process_observation(self) -> bool:
        """Check if process observation is allowed."""
        return "process" in self.visibility_scope.lower() or not self.is_sandboxed
    
    @property
    def allows_file_observation(self) -> bool:
        """Check if file observation is allowed."""
        return "file" in self.visibility_scope.lower() or not self.is_sandboxed
    
    @classmethod
    def create(
        cls,
        profile: str = "process",
        visibility_scope: str = "self",
        constraints: Tuple[SandboxConstraint, ...] = (),
        namespace_context: Optional[Dict[str, Any]] = None,
        container_id: Optional[str] = None,
    ) -> "ModalitySandboxProfile":
        """
        Create a new sandbox profile instance.
        
        Args:
            profile: Sandbox level (NONE, PROCESS, USER, CONTAINER, etc.)
            visibility_scope: What can be observed
            constraints: Additional constraints
            namespace_context: Namespace information
            container_id: Container identifier if applicable
            
        Returns:
            New ModalitySandboxProfile instance
        """
        return cls(
            sandbox_profile=profile,
            visibility_scope=visibility_scope,
            constraints=constraints,
            namespace_context=namespace_context or {},
            container_id=container_id,
            revision=1,
        )
    
    def get_effective_visibility(self, resource_type: str) -> VisibilityScope:
        """
        Get the effective visibility scope for a specific resource type.
        
        Args:
            resource_type: Type of resource (process, file, network, etc.)
            
        Returns:
            Effective visibility scope
        """
        # If not sandboxed, full visibility
        if not self.is_sandboxed:
            return VisibilityScope.SELF
        
        # Check constraints for this resource type
        for constraint in self.constraints:
            if constraint.scope.lower() == resource_type.lower():
                if "read_only" in constraint.constraint_type.lower():
                    return VisibilityScope.USER_FILES  # Read-only still allows observation
                elif "limit" in constraint.constraint_type.lower():
                    return VisibilityScope.HOST_SUMMARY
        
        # Default to visibility scope
        try:
            return VisibilityScope(self.visibility_scope)
        except ValueError:
            return VisibilityScope.SELF
    
    def is_compatible_with_resource(
        self,
        resource_scope: str,
        resource_type: str = "process",
    ) -> bool:
        """
        Check if a resource falls within the sandbox's effective visibility.
        
        Args:
            resource_scope: Scope of the resource (self, user, host, etc.)
            resource_type: Type of resource
            
        Returns:
            True if observation is allowed
        """
        # Not sandboxed = can observe anything
        if not self.is_sandboxed:
            return True
        
        # Sandbox hierarchy
        scope_levels = {
            "self": 0,
            "user": 1,
            "container": 2,
            "host": 3,
        }
        
        sandbox_level = scope_levels.get(self.visibility_scope, 0)
        resource_level = scope_levels.get(resource_scope.lower(), 3)
        
        # Can observe if resource is at or below sandbox level
        return resource_level <= sandbox_level


# =============================================================================
# SANDBOX VALIDATOR - Interface for sandbox validation
# =============================================================================


class SandboxValidator:
    """
    Interface for validating sandbox profiles and constraints.
    
    Implementations verify that a modality's requested observations are within
    the effective sandbox scope.
    """
    
    def validate_modality_request(
        self,
        modality_identity: str,
        requested_scope: str,
        sandbox_profile: ModalitySandboxProfile,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a modality's observation request against sandbox profile.
        
        Args:
            modality_identity: The modality making the request
            requested_scope: The scope being requested
            sandbox_profile: Active sandbox configuration
            
        Returns:
            Tuple of (is_valid, error_message if not valid)
        """
        raise NotImplementedError
    
    def get_effective_constraints(
        self,
        sandbox_profile: ModalitySandboxProfile,
    ) -> Tuple[SandboxConstraint, ...]:
        """
        Get all constraints active for a sandbox profile.
        
        Args:
            sandbox_profile: Sandbox configuration
            
        Returns:
            Tuple of active constraints
        """
        raise NotImplementedError


# =============================================================================
# EXPORTS
# =============================================================================

__all__: list[str] = [
    # Enums
    "SandboxProfile",
    "VisibilityScope",
    
    # Dataclasses
    "SandboxConstraint",
    "ModalitySandboxProfile",
    
    # Classes
    "SandboxValidator",
]