# Gordon Cognitive Architecture - Phase 4.5.3
# ===========================================

"""
Action Targets Ontology

This module defines the canonical Action target taxonomy that describes
what Actions may operate on.

ACTION TARGETS TAXONOMY
=======================

Targets represent the semantic entities or objects that an Action may
affect or interact with.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import FrozenSet, Tuple


# =============================================================================
# ACTION TARGET KINDS - Semantic target types
# =============================================================================

class ActionTargetKind(Enum):
    """
    The kind of target an Action operates on.
    
    Targets represent the semantic entities or objects that Actions may
    affect. Each target kind represents a coherent category of target.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # =============================================================================
    # FILESYSTEM TARGETS
    # =============================================================================
    
    FILE = "file"
    """File system file."""
    
    DIRECTORY = "directory"
    """Directory or folder."""
    
    PATH = "path"
    """Path reference (file or directory)."""
    
    # =============================================================================
    # REPOSITORY TARGETS
    # =============================================================================
    
    REPOSITORY = "repository"
    """Repository of content or artifacts."""
    
    COMMIT = "commit"
    """Version control commit."""
    
    BRANCH = "branch"
    """Version control branch."""
    
    TAG = "tag"
    """Version control tag."""
    
    # =============================================================================
    # WORKSPACE TARGETS
    # =============================================================================
    
    WORKSPACE = "workspace"
    """Workspace or project context."""
    
    ARTIFACT = "artifact"
    """Artifact within workspace."""
    
    CONTEXT = "context"
    """Execution context."""
    
    SCOPE = "scope"
    """Semantic scope boundary."""
    
    # =============================================================================
    # MEMORY TARGETS
    # =============================================================================
    
    MEMORY_OBJECT = "memory_object"
    """Memory object or fact."""
    
    CONVERSATION = "conversation"
    """Conversation history."""
    
    MESSAGE = "message"
    """Message in conversation."""
    
    SESSION = "session"
    """Session state."""
    
    CACHE_ENTRY = "cache_entry"
    """Cache entry."""
    
    # =============================================================================
    # USER TARGETS
    # =============================================================================
    
    USER = "user"
    """Human user or actor."""
    
    AGENT = "agent"
    """Autonomous agent."""
    
    GROUP = "group"
    """Group of users or agents."""
    
    ROLE = "role"
    """Role definition."""
    
    PERMISSION = "permission"
    """Permission or authorization."""
    
    # =============================================================================
    # CAPABILITY TARGETS
    # =============================================================================
    
    CAPABILITY = "capability"
    """Capability or skill."""
    
    MODEL = "model"
    """AI model or algorithm."""
    
    SERVICE = "service"
    """Service endpoint."""
    
    API = "api"
    """API endpoint."""
    
    # =============================================================================
    # CONFIGURATION TARGETS
    # =============================================================================
    
    CONFIGURATION = "configuration"
    """Configuration object or settings."""
    
    SETTINGS = "settings"
    """Application settings."""
    
    PARAMETER = "parameter"
    """Function parameter or configuration value."""
    
    VARIABLE = "variable"
    """Variable reference."""
    
    # =============================================================================
    # DEVICE TARGETS
    # =============================================================================
    
    DEVICE = "device"
    """Physical device."""
    
    SENSOR = "sensor"
    """Sensor device."""
    
    ACTUATOR = "actuator"
    """Actuator device."""
    
    INTERFACE = "interface"
    """Interface or connection point."""
    
    # =============================================================================
    # NETWORK TARGETS
    # =============================================================================
    
    NETWORK_RESOURCE = "network_resource"
    """Network-accessible resource."""
    
    ENDPOINT = "endpoint"
    """Network endpoint."""
    
    SOCKET = "socket"
    """Socket connection."""
    
    CHANNEL = "channel"
    """Communication channel."""
    
    # =============================================================================
    # KNOWLEDGE TARGETS
    # =============================================================================
    
    KNOWLEDGE_OBJECT = "knowledge_object"
    """Knowledge artifact or fact."""
    
    DOCUMENT = "document"
    """Document or article."""
    
    DATA_SET = "data_set"
    """Dataset or collection."""
    
    FACT = "fact"
    """Atomic fact or assertion."""
    
    # =============================================================================
    # ABSTRACT TARGETS
    # =============================================================================
    
    ABSTRACT_CONCEPT = "abstract_concept"
    """Abstract concept or idea."""
    
    PLAN = "plan"
    """Plan or strategy."""
    
    GOAL = "goal"
    """Goal or objective."""
    
    OBJECTIVE = "objective"
    """Target objective."""
    
    # =============================================================================
    # SYSTEM TARGETS
    # =============================================================================
    
    PROCESS = "process"
    """Running process."""
    
    THREAD = "thread"
    """Execution thread."""
    
    TASK = "task"
    """Task unit of work."""
    
    RESOURCE = "resource"
    """System resource."""
    
    # =============================================================================
    # SPECIAL TARGETS
    # =============================================================================
    
    ANY = "any"
    """Any target type (polymorphic)."""
    
    UNKNOWN = "unknown"
    """Target kind is unknown or undetermined."""


# =============================================================================
# UTILITY TYPES - Target collections
# =============================================================================

class ActionTargetKinds(FrozenSet[ActionTargetKind]):
    """A collection of ActionTargetKind values."""
    
    def __new__(cls, targets: Tuple[ActionTargetKind, ...] = ()):
        return super().__new__(cls, targets)
    
    @classmethod
    def all(cls) -> "ActionTargetKinds":
        """Get all canonical ActionTargetKinds."""
        return cls(tuple(ActionTargetKind))
    
    @classmethod
    def filesystem(cls) -> "ActionTargetKinds":
        """Get all filesystem-related target kinds."""
        return cls((
            ActionTargetKind.FILE,
            ActionTargetKind.DIRECTORY,
            ActionTargetKind.PATH,
        ))
    
    @classmethod
    def user_related(cls) -> "ActionTargetKinds":
        """Get all user-related target kinds."""
        return cls((
            ActionTargetKind.USER,
            ActionTargetKind.AGENT,
            ActionTargetKind.GROUP,
            ActionTargetKind.ROLE,
            ActionTargetKind.PERMISSION,
        ))


__all__ = [
    "ActionTargetKind",
    "ActionTargetKinds",
]