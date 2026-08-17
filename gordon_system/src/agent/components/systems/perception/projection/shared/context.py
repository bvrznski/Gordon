# Perception Projection Context - Phase 5.2.4
# ===========================================

"""
Projection Context: Constrains publication.

Context constrains publication. It does not redefine source perceptual artifacts.
"""

from __future__ import annotations

import time as _time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
import uuid


# =============================================================================
# CONSUMER KINDS
# =============================================================================


class ConsumerKind:
    """Kinds of consumers that may request projections."""
    
    WORKSPACE = "workspace"
    ATTENTION = "attention"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    COORDINATION = "coordination"
    WORLD_MODEL = "world_model"
    LEARNING = "learning"
    IDENTITY = "identity"
    REASONING = "reasoning"
    GOVERNANCE = "governance"
    OBSERVABILITY = "observability"
    EXTERNAL_INTERFACE = "external_interface"
    HUMAN_INTERFACE = "human_interface"


# =============================================================================
# PROJECTION CONSUMER CONTRACT
# =============================================================================


@dataclass(frozen=True)
class PerceptionProjectionConsumerContract:
    """
    Contract declaring what a consumer can safely interpret.
    
    The consumer contract declares what the consumer can safely interpret.
    Projection shall not publish an incompatible view silently.
    """
    
    contract_identity: str
    
    # Consumer identification
    consumer_identity: str
    consumer_kind: str  # From ConsumerKind enum
    
    # Supported projection kinds
    supported_projection_kinds: Tuple[str, ...] = field(default_factory=tuple)
    
    # Supported artifact kinds
    supported_artifact_kinds: Tuple[str, ...] = field(default_factory=tuple)
    
    # Revision compatibility
    supported_revisions: Tuple[int, ...] = field(default_factory=lambda: (1,))
    
    # Required and optional fields
    required_fields: Tuple[str, ...] = field(default_factory=tuple)
    optional_fields: Tuple[str, ...] = field(default_factory=tuple)
    
    # Unsupported fields (explicitly not supported)
    unsupported_fields: Tuple[str, ...] = field(default_factory=tuple)
    
    # Update mode support
    accepted_update_modes: Tuple[str, ...] = field(
        default_factory=lambda: ("on_demand", "snapshot")
    )
    
    # Staleness acceptance
    accepted_staleness: str = "current_or_recent"  # current, recent, stale, any
    
    # Visibility requirements
    requires_conflict_visibility: bool = True
    requires_ambiguity_visibility: bool = True
    requires_missing_evidence_visibility: bool = False
    
    # Revision tracking
    contract_revision: int = 1
    
    @classmethod
    def workspace_contract(
        cls,
        consumer_id: str,
        supported_kinds: Optional[List[str]] = None,
    ) -> "PerceptionProjectionConsumerContract":
        """Create a Workspace-consumer contract."""
        return cls(
            contract_identity=f"contract:{uuid.uuid4().hex[:16]}",
            consumer_identity=consumer_id,
            consumer_kind=ConsumerKind.WORKSPACE,
            supported_projection_kinds=tuple(supported_kinds or ["workspace", "percept"]),
            accepted_update_modes=("stream", "snapshot", "on_demand"),
            accepted_staleness="current_or_recent",
            requires_conflict_visibility=True,
            requires_ambiguity_visibility=False,  # Workspace may suppress some ambiguity
            requires_missing_evidence_visibility=True,
        )
    
    @classmethod
    def attention_contract(
        cls,
        consumer_id: str,
    ) -> "PerceptionProjectionConsumerContract":
        """Create an Attention-consumer contract."""
        return cls(
            contract_identity=f"contract:{uuid.uuid4().hex[:16]}",
            consumer_identity=consumer_id,
            consumer_kind=ConsumerKind.ATTENTION,
            supported_projection_kinds=("percept", "scene", "event"),
            accepted_update_modes=("stream", "snapshot"),
            accepted_staleness="current",
            requires_conflict_visibility=True,
            requires_ambiguity_visibility=True,
            requires_missing_evidence_visibility=False,
        )
    
    @classmethod
    def memory_contract(
        cls,
        consumer_id: str,
    ) -> "PerceptionProjectionConsumerContract":
        """Create a Memory-consumer contract."""
        return cls(
            contract_identity=f"contract:{uuid.uuid4().hex[:16]}",
            consumer_identity=consumer_id,
            consumer_kind=ConsumerKind.MEMORY,
            supported_projection_kinds=("percept",),
            accepted_update_modes=("on_demand", "snapshot"),
            accepted_staleness="any",  # Memory can store stale content
            requires_conflict_visibility=False,  # May not need conflict info for storage
            requires_ambiguity_visibility=True,
            requires_missing_evidence_visibility=False,
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if the contract has valid data."""
        if not self.contract_identity or len(self.contract_identity) == 0:
            return False
        if not self.consumer_identity or len(self.consumer_identity) == 0:
            return False
        if not self.consumer_kind or len(self.consumer_kind) == 0:
            return False
        
        # Check supported revisions are valid
        for rev in self.supported_revisions:
            if rev < 1:
                return False
        
        return True


# =============================================================================
# PROJECTION CONTEXT
# =============================================================================


@dataclass(frozen=True)
class PerceptionProjectionContext:
    """
    Context that constrains projection publication.
    
    Context constrains publication. It does not redefine source perceptual artifacts.
    
    Context fields:
        context_identity: Unique identifier for this context
        consumer_kind: What kind of consumer is requesting
        consumer_contract: Their contract (for compatibility checking)
        current_task_reference: What task is being performed
        temporal_reference: Time reference point
        spatial_reference: Space reference frame
        requested_semantic_granularity: Detail level expected
        latency_requirement: How fast updates are needed
        completeness_requirement: How much data must be included
        freshness_requirement: How current must it be
        update_requirement: Update frequency expected
        authorization_context: For access control
        sandbox_context: For permission checking
    """
    
    context_identity: str
    
    # Consumer identification
    consumer_kind: str  # From ConsumerKind enum
    consumer_contract_reference: str = ""
    
    # Task and reference frames
    current_task_reference: str = ""
    temporal_reference: Optional[str] = None  # e.g., "current_command_execution"
    spatial_reference: Optional[str] = None   # e.g., "screen_1920x1080"
    
    # Semantic requirements
    requested_semantic_granularity: str = "percept"  # feature, percept, integrated_percept, scene, event, summary
    
    # Quality requirements
    latency_requirement: float = 1.0      # seconds max for update delivery
    completeness_requirement: float = 1.0  # 0.0-1.0, minimum completeness fraction
    freshness_requirement: str = "current"  # current, recent, stale_allowed
    
    # Update requirements
    update_requirement: str = "on_demand"  # on_demand, stream, periodic
    
    # Authorization and sandbox context
    authorization_context: Dict[str, Any] = field(default_factory=dict)
    sandbox_context: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def workspace_context(
        cls,
        consumer_id: str,
        task_reference: str = "",
        temporal_ref: Optional[str] = None,
        spatial_ref: Optional[str] = None,
    ) -> "PerceptionProjectionContext":
        """Create a Workspace projection context."""
        return cls(
            context_identity=f"context:{uuid.uuid4().hex[:16]}",
            consumer_kind=ConsumerKind.WORKSPACE,
            consumer_contract_reference="contract:workspace_default",
            current_task_reference=task_reference,
            temporal_reference=temporal_ref,
            spatial_reference=spatial_ref,
            requested_semantic_granularity="percept",
            latency_requirement=0.5,  # Fast updates for workspace
            completeness_requirement=1.0,
            freshness_requirement="current",
            update_requirement="stream",
        )
    
    @classmethod
    def attention_context(
        cls,
        consumer_id: str,
    ) -> "PerceptionProjectionContext":
        """Create an Attention projection context."""
        return cls(
            context_identity=f"context:{uuid.uuid4().hex[:16]}",
            consumer_kind=ConsumerKind.ATTENTION,
            consumer_contract_reference="contract:attention_default",
            requested_semantic_granularity="percept",
            latency_requirement=0.1,  # Very fast for attention
            completeness_requirement=0.8,
            freshness_requirement="current",
            update_requirement="stream",
        )
    
    @classmethod
    def memory_context(
        cls,
        consumer_id: str,
    ) -> "PerceptionProjectionContext":
        """Create a Memory projection context."""
        return cls(
            context_identity=f"context:{uuid.uuid4().hex[:16]}",
            consumer_kind=ConsumerKind.MEMORY,
            consumer_contract_reference="contract:memory_default",
            requested_semantic_granularity="percept",
            latency_requirement=5.0,  # Can be slow for memory
            completeness_requirement=1.0,
            freshness_requirement="any",
            update_requirement="on_demand",
        )
    
    @property
    def is_valid(self) -> bool:
        """Check if the context has valid data."""
        if not self.context_identity or len(self.context_identity) == 0:
            return False
        if not self.consumer_kind or len(self.consumer_kind) == 0:
            return False
        
        # Check latency is positive
        if self.latency_requirement < 0.0:
            return False
        
        # Check completeness is in range
        if not (0.0 <= self.completeness_requirement <= 1.0):
            return False
        
        return True


__all__ = [
    "ConsumerKind",
    "PerceptionProjectionConsumerContract",
    "PerceptionProjectionContext",
]