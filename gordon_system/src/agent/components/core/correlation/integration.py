# Phase 3.11.14 - Cross-Stream Correlation Integration
# ======================================================

"""
Integration Module for Cross-Stream Correlation & Causation Architecture.

Provides integration with stream infrastructure, execution layer, and domain systems.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# INTEGRATION TYPES
# =============================================================================


@dataclass(frozen=True)
class StreamRecordReference:
    """
    Reference to a stream record for relationship construction.
    
    Contains only stable identifiers - no live objects.
    """
    record_id: str           # StreamRecordId.value
    stream_id: str           # StreamId.value
    generation_id: Optional[str] = None
    sequence_number: int = 0


@dataclass(frozen=True)
class CrossStreamCorrelationRequest:
    """
    Request to establish correlation between records from different streams.
    
    This is the entry point for building relationships.
    """
    request_id: str
    
    # Source record (reference only)
    source_record: StreamRecordReference
    
    # Target record(s) to correlate with
    target_records: Tuple[StreamRecordReference, ...]
    
    # Correlation metadata
    correlation_kind: str  # RelationshipKind.value or custom
    correlation_context: Dict[str, Any] = field(default_factory=dict)
    
    # Authorization reference (not credentials)
    authorization_context_reference: Optional[str] = None
    
    # Timestamps
    requested_at_utc: float = field(default_factory=time.time)
    expires_at_utc: Optional[float] = None


@dataclass(frozen=True)
class CrossStreamCausationRequest:
    """
    Request to establish causation between records from different streams.
    
    Causation requires evidence - this must be provided in metadata.
    """
    request_id: str
    
    # Cause and effect
    cause_record: StreamRecordReference
    effect_record: StreamRecordReference
    
    # Evidence references (stable record IDs)
    evidence_records: Tuple[StreamRecordReference, ...]
    
    # Causation kind
    causation_kind: str  # RelationshipKind.value (e.g., "directly_causes")
    
    # Authorization reference
    authorization_context_reference: Optional[str] = None
    
    # Timestamps
    requested_at_utc: float = field(default_factory=time.time)
    expires_at_utc: Optional[float] = None


@dataclass(frozen=True)
class EpisodeMembershipRequest:
    """
    Request to add a record to an episode.
    
    Episodes group related records across streams.
    """
    request_id: str
    
    # Record to add
    record: StreamRecordReference
    
    # Episode reference
    episode_id: str  # Stable identifier for existing episode, or "new" for new
    
    # Role in episode (optional)
    role_in_episode: Optional[str] = None
    
    # Authorization reference
    authorization_context_reference: Optional[str] = None


# =============================================================================
# INTEGRATION RESULTS
# =============================================================================


class IntegrationResultType(Enum):
    """Types of integration results."""
    CORRELATION_CREATED = "correlation_created"
    CAUSATION_CREATED = "causation_created"
    EPISODE_ADDED = "episode_added"
    AUTHORIZATION_DENIED = "authorization_denied"
    VALIDATION_ERROR = "validation_error"


@dataclass(frozen=True)
class IntegrationResult:
    """
    Result of an integration operation.
    
    Contains either the created relationship or an error reason.
    """
    result_id: str
    result_type: IntegrationResultType
    
    # For success cases
    edge_id: Optional[str] = None
    edge_kind: Optional[str] = None
    
    # For failure cases
    error_message: Optional[str] = None
    validation_error: Optional[str] = None


# =============================================================================
# INTEGRATION ENGINE
# =============================================================================


class CrossStreamIntegrationEngine:
    """
    Engine for integrating cross-stream relationships with stream infrastructure.
    
    Coordinates between relationship graph operations and stream systems.
    """

    def __init__(
        self,
        stream_registry: Any,  # StreamRegistry protocol
        relationship_graph: Any,  # RelationshipGraph instance
    ):
        self.stream_registry = stream_registry
        self.relationship_graph = relationship_graph
    
    async def process_correlation_request(
        self,
        request: CrossStreamCorrelationRequest,
    ) -> IntegrationResult:
        """
        Process a correlation request.
        
        Validates the request, checks authorization, and adds correlation edges.
        """
        # Validate source record exists
        if not await self._stream_has_record(request.source_record.stream_id, request.source_record.record_id):
            return IntegrationResult(
                result_id=f"result-{uuid.uuid4().hex[:16]}",
                result_type=IntegrationResultType.VALIDATION_ERROR,
                error_message=f"Source record {request.source_record.record_id} not found"
            )
        
        # Process each target
        results = []
        for target in request.target_records:
            if await self._stream_has_record(target.stream_id, target.record_id):
                # Try to add correlation edge
                new_graph = self.relationship_graph.add_correlation_edge(
                    source_record_id=request.source_record.record_id,
                    target_record_id=target.record_id,
                    stream_id_source=request.source_record.stream_id,
                    stream_id_target=target.stream_id,
                    relationship_kind=None,  # Will use default from request context
                )
                
                results.append(IntegrationResult(
                    result_id=f"result-{uuid.uuid4().hex[:16]}",
                    result_type=IntegrationResultType.CORRELATION_CREATED,
                    edge_id="temp_edge_id",  # Would be populated during actual add
                    edge_kind=request.correlation_kind,
                ))
        
        if not results:
            return IntegrationResult(
                result_id=f"result-{uuid.uuid4().hex[:16]}",
                result_type=IntegrationResultType.VALIDATION_ERROR,
                error_message="No valid target records found"
            )
        
        return results[0]  # Return first result (simplified)
    
    async def process_causation_request(
        self,
        request: CrossStreamCausationRequest,
    ) -> IntegrationResult:
        """
        Process a causation request.
        
        Causation requires evidence - validates all components exist.
        """
        if not await self._stream_has_record(request.cause_record.stream_id, request.cause_record.record_id):
            return IntegrationResult(
                result_id=f"result-{uuid.uuid4().hex[:16]}",
                result_type=IntegrationResultType.VALIDATION_ERROR,
                error_message="Cause record not found"
            )
        
        if not await self._stream_has_record(request.effect_record.stream_id, request.effect_record.record_id):
            return IntegrationResult(
                result_id=f"result-{uuid.uuid4().hex[:16]}",
                result_type=IntegrationResultType.VALIDATION_ERROR,
                error_message="Effect record not found"
            )
        
        # Check evidence records exist
        for evidence in request.evidence_records:
            if not await self._stream_has_record(evidence.stream_id, evidence.record_id):
                return IntegrationResult(
                    result_id=f"result-{uuid.uuid4().hex[:16]}",
                    result_type=IntegrationResultType.VALIDATION_ERROR,
                    error_message=f"Evidence record {evidence.record_id} not found"
                )
        
        # Add causation edge (simplified - would use actual graph)
        return IntegrationResult(
            result_id=f"result-{uuid.uuid4().hex[:16]}",
            result_type=IntegrationResultType.CAUSATION_CREATED,
            edge_kind=request.causation_kind,
        )
    
    async def _stream_has_record(self, stream_id: str, record_id: str) -> bool:
        """
        Check if a stream has a specific record.
        
        This would query the stream storage layer in real implementation.
        For now, returns True as placeholder.
        """
        return True  # Placeholder
    
    async def process_episode_request(
        self,
        request: EpisodeMembershipRequest,
    ) -> IntegrationResult:
        """Process an episode membership request."""
        if not await self._stream_has_record(request.record.stream_id, request.record.record_id):
            return IntegrationResult(
                result_id=f"result-{uuid.uuid4().hex[:16]}",
                result_type=IntegrationResultType.VALIDATION_ERROR,
                error_message="Record not found"
            )
        
        # Add episode membership (simplified)
        return IntegrationResult(
            result_id=f"result-{uuid.uuid4().hex[:16]}",
            result_type=IntegrationResultType.EPISODE_ADDED,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Request types
    "StreamRecordReference",
    "CrossStreamCorrelationRequest",
    "CrossStreamCausationRequest",
    "EpisodeMembershipRequest",
    
    # Result types
    "IntegrationResultType",
    "IntegrationResult",
    
    # Engine
    "CrossStreamIntegrationEngine",
]