# Perception Interfaces - Phase 5.2.5
# ===================================

"""
Perception Interfaces: The communication boundary for the Perception System.

This module provides formal interfaces through which every other subsystem
interacts with Perception. Interfaces define stable architectural contracts
without exposing internal implementation details.

Canonical interfaces:
    - Sensors Interface: Acquisition of sensor evidence
    - Workspace Interface: Bounded perceptual candidates  
    - Memory Interface: Candidate submission for memory admission
    - Knowledge Interface: Semantic grounding and normalization
    - Attention Interface: Priority exposure and inspection
    - Learning Interface: Performance evidence and proposals
    - Identity Interface: Self-related perceptual grounding
    - Reasoning Interface: Evidence for reasoning tasks
    - World Model Interface: Observational updates to world state
    - Coordination Interface: Operational status and synchronization
    - Governance Interface: Architecture integrity evaluation
    - External Interface: Approved public capabilities

Interface Laws:
    INTERFACE-LAW-001: Every interaction crossing the Perception boundary shall use an explicit, versioned Interface Contract.
    INTERFACE-LAW-002: Perception Interfaces shall never expose private Perception implementation objects.
    INTERFACE-LAW-003: Interfaces shall preserve the semantic identity, provenance, revision, confidence, uncertainty and limitations of transported perceptual artifacts.
    INTERFACE-LAW-004: Interfaces shall remain communication boundaries rather than cognitive or execution subsystems.
    INTERFACE-LAW-005: Interfaces shall preserve authorization, compatibility and synchronization context.
    INTERFACE-LAW-006: Published Interface messages shall remain immutable.
    INTERFACE-LAW-007: Every Interface shall remain independently testable and replaceable.
    INTERFACE-LAW-008: Interface behavior shall remain deterministic for equivalent contracts, requests, authorization, source revisions and runtime context.
"""

from .shared import (
    # Contracts
    InterfaceKind,
    InterfaceStatus,
    CompatibilityRevision,
    AuthorizationContext,
    PerceptionInterfaceContract,
    InterfaceDiscoveryResult,
    InterfaceHealth,
    PerceptionCapabilityDescriptor,
    CompatibilityEvaluator,
    VersionNegotiationResult,
    VersionNegotiator,
    
    # Requests
    RequestKind,
    RequestPriority,
    RequestScope,
    PerceptionInterfaceRequest,
    PerceptionInterfaceRequestBuilder,
    RequestResult,
    
    # Responses
    ResponseStatus,
    PerceptionInterfaceResponse,
    SensorAcquisitionResponse,
    PerceptionWorkspacePublication,
    WorkspacePerceptionFeedback,
    PerceptionMemoryAdmissionResponse,
    PerceptionGroundingResponse,
    
    # Events
    EventKind,
    EventContext,
    PerceptionInterfaceEvent,
)

# Interface implementations (lazy loaded via import)
_sensors_interface = None
_workspace_interface = None
_memory_interface = None
_knowledge_interface = None
_attention_interface = None
_learning_interface = None
_identity_interface = None
_reasoning_interface = None
_world_model_interface = None
_coordination_interface = None
_governance_interface = None
_external_interface = None


def get_sensors_interface(provider_id: str) -> "SensorsInterface":
    """Get or create the Sensors Interface instance."""
    global _sensors_interface
    if _sensors_interface is None:
        from .sensors.interface import SensorsInterface
        _sensors_interface = SensorsInterface(provider_id)
    return _sensors_interface


def get_workspace_interface(provider_id: str) -> "WorkspaceInterface":
    """Get or create the Workspace Interface instance."""
    global _workspace_interface
    if _workspace_interface is None:
        from .workspace.interface import WorkspaceInterface
        _workspace_interface = WorkspaceInterface(provider_id)
    return _workspace_interface


def get_memory_interface(provider_id: str) -> "MemoryInterface":
    """Get or create the Memory Interface instance."""
    global _memory_interface
    if _memory_interface is None:
        from .memory.interface import MemoryInterface
        _memory_interface = MemoryInterface(provider_id)
    return _memory_interface


def get_knowledge_interface(provider_id: str) -> "KnowledgeInterface":
    """Get or create the Knowledge Interface instance."""
    global _knowledge_interface
    if _knowledge_interface is None:
        from .knowledge.interface import KnowledgeInterface
        _knowledge_interface = KnowledgeInterface(provider_id)
    return _knowledge_interface


def get_attention_interface(provider_id: str) -> "AttentionInterface":
    """Get or create the Attention Interface instance."""
    global _attention_interface
    if _attention_interface is None:
        from .attention.interface import AttentionInterface
        _attention_interface = AttentionInterface(provider_id)
    return _attention_interface


def get_learning_interface(provider_id: str) -> "LearningInterface":
    """Get or create the Learning Interface instance."""
    global _learning_interface
    if _learning_interface is None:
        from .learning.interface import LearningInterface
        _learning_interface = LearningInterface(provider_id)
    return _learning_interface


def get_identity_interface(provider_id: str) -> "IdentityInterface":
    """Get or create the Identity Interface instance."""
    global _identity_interface
    if _identity_interface is None:
        from .identity.interface import IdentityInterface
        _identity_interface = IdentityInterface(provider_id)
    return _identity_interface


def get_reasoning_interface(provider_id: str) -> "ReasoningInterface":
    """Get or create the Reasoning Interface instance."""
    global _reasoning_interface
    if _reasoning_interface is None:
        from .reasoning.interface import ReasoningInterface
        _reasoning_interface = ReasoningInterface(provider_id)
    return _reasoning_interface


def get_world_model_interface(provider_id: str) -> "WorldModelInterface":
    """Get or create the World Model Interface instance."""
    global _world_model_interface
    if _world_model_interface is None:
        from .world_model.interface import WorldModelInterface
        _world_model_interface = WorldModelInterface(provider_id)
    return _world_model_interface


def get_coordination_interface(provider_id: str) -> "CoordinationInterface":
    """Get or create the Coordination Interface instance."""
    global _coordination_interface
    if _coordination_interface is None:
        from .coordination.interface import CoordinationInterface
        _coordination_interface = CoordinationInterface(provider_id)
    return _coordination_interface


def get_governance_interface(provider_id: str) -> "GovernanceInterface":
    """Get or create the Governance Interface instance."""
    global _governance_interface
    if _governance_interface is None:
        from .governance.interface import GovernanceInterface
        _governance_interface = GovernanceInterface(provider_id)
    return _governance_interface


def get_external_interface(provider_id: str) -> "ExternalInterface":
    """Get or create the External Interface instance."""
    global _external_interface
    if _external_interface is None:
        from .external.interface import ExternalInterface
        _external_interface = ExternalInterface(provider_id)
    return _external_interface


__all__ = [
    # Shared components (exported from shared module)
    "InterfaceKind",
    "InterfaceStatus",
    "CompatibilityRevision",
    "AuthorizationContext",
    "PerceptionInterfaceContract",
    "InterfaceDiscoveryResult",
    "InterfaceHealth",
    "PerceptionCapabilityDescriptor",
    "CompatibilityEvaluator",
    "VersionNegotiationResult",
    "VersionNegotiator",
    
    "RequestKind",
    "RequestPriority",
    "RequestScope",
    "PerceptionInterfaceRequest",
    "PerceptionInterfaceRequestBuilder",
    "RequestResult",
    
    "ResponseStatus",
    "PerceptionInterfaceResponse",
    "SensorAcquisitionResponse",
    "PerceptionWorkspacePublication",
    "WorkspacePerceptionFeedback",
    "PerceptionMemoryAdmissionResponse",
    "PerceptionGroundingResponse",
    
    "EventKind",
    "EventContext",
    "PerceptionInterfaceEvent",
    
    # Interface factories
    "get_sensors_interface",
    "get_workspace_interface", 
    "get_memory_interface",
    "get_knowledge_interface",
    "get_attention_interface",
    "get_learning_interface",
    "get_identity_interface",
    "get_reasoning_interface",
    "get_world_model_interface",
    "get_coordination_interface",
    "get_governance_interface",
    "get_external_interface",
]