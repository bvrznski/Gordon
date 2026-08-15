# Gordon Cognitive Architecture - Phase 4.5.3
# ===========================================

"""
Action Capabilities Ontology

This module defines the canonical Action capability taxonomy that describes
the domains where Actions may operate.

ACTION CAPABILITIES TAXONOMY
============================

Capabilities represent the domains or areas where Actions can be performed.
Each capability represents a coherent semantic domain of operation.
"""

from __future__ import annotations

from enum import Enum, auto
from typing import FrozenSet, Tuple


# =============================================================================
# ACTION CAPABILITIES - Semantic operational domains
# =============================================================================

class ActionCapability(Enum):
    """
    The capability or domain where an Action may be performed.
    
    Capabilities represent the semantic areas of operation that an Action
    may access or affect. They remain external to the Action - the Action
    describes what it would do IF the capability is available.
    
    Runtime-neutral: Yes
    Executable: No
    """
    
    # =============================================================================
    # CORE CAPABILITIES
    # =============================================================================
    
    FILESYSTEM = "filesystem"
    """Filesystem operations (read/write/modify/delete)."""
    
    WORKSPACE = "workspace"
    """Workspace management and artifact handling."""
    
    MEMORY = "memory"
    """Memory operations (working/long-term storage, retrieval)."""
    
    COMMUNICATION = "communication"
    """Communication with other systems or components."""
    
    # =============================================================================
    # COMPUTATIONAL CAPABILITIES
    # =============================================================================
    
    NETWORK = "network"
    """Network operations and connectivity."""
    
    COMPUTATION = "computation"
    """General computation and processing."""
    
    PLANNING = "planning"
    """Planning capabilities (goal setting, strategy)."""
    
    REASONING = "reasoning"
    """Reasoning and logical inference capabilities."""
    
    # =============================================================================
    # SENSORY/PERCEPTUAL CAPABILITIES
    # =============================================================================
    
    VISION = "vision"
    """Visual perception and analysis capabilities."""
    
    LANGUAGE = "language"
    """Language understanding and generation capabilities."""
    
    # =============================================================================
    # CONTROL/CAPABILITY MANAGEMENT
    # =============================================================================
    
    SECURITY = "security"
    """Security operations (authentication, authorization)."""
    
    CONFIGURATION = "configuration"
    """Configuration management capabilities."""
    
    EXTERNAL_SERVICE = "external_service"
    """External service invocation capabilities."""
    
    USER_INTERACTION = "user_interaction"
    """User interaction and interface capabilities."""
    
    # =============================================================================
    # SPECIALIZED CAPABILITIES
    # =============================================================================
    
    DATABASE = "database"
    """Database query and manipulation capabilities."""
    
    FILE_ACCESS = "file_access"
    """File system access capabilities."""
    
    NETWORK_REQUEST = "network_request"
    """Network request capabilities."""
    
    API_CALL = "api_call"
    """API invocation capabilities."""
    
    # =============================================================================
    # GENERAL CAPABILITIES
    # =============================================================================
    
    GENERAL = "general"
    """General-purpose operation capability."""
    
    UNKNOWN = "unknown"
    """Capability is unknown or undetermined."""
    
    @property
    def is_computational(self) -> bool:
        """Check if this capability involves computation."""
        return self in (
            ActionCapability.NETWORK,
            ActionCapability.COMPUTATION,
            ActionCapability.PLANNING,
            ActionCapability.REASONING,
        )
    
    @property
    def is_sensory(self) -> bool:
        """Check if this capability involves sensory input."""
        return self in (
            ActionCapability.VISION,
            ActionCapability.LANGUAGE,
        )


# =============================================================================
# UTILITY TYPES - Capability collections
# =============================================================================

class ActionCapabilities(FrozenSet[ActionCapability]):
    """A collection of ActionCapability values."""
    
    def __new__(cls, capabilities: Tuple[ActionCapability, ...] = ()):
        return super().__new__(cls, capabilities)
    
    @classmethod
    def all(cls) -> "ActionCapabilities":
        """Get all canonical ActionCapabilities."""
        return cls(tuple(ActionCapability))
    
    @classmethod
    def computational(cls) -> "ActionCapabilities":
        """Get all computational capabilities."""
        return cls(c for c in ActionCapability if c.is_computational)
    
    @classmethod
    def sensory(cls) -> "ActionCapabilities":
        """Get all sensory capabilities."""
        return cls(c for c in ActionCapability if c.is_sensory)


__all__ = [
    "ActionCapability",
    "ActionCapabilities",
]