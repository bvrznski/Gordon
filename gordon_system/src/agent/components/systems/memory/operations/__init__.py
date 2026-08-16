# Memory Operations - Phase 5.1.2 Memory Transformation Architecture
# ====================================================================

"""
Memory Operations: The transformational layer of the Gordon Memory System.

This module implements the canonical memory operations that define how
memory evolves over time:

    Encoding        : Create candidate artifacts from observations
    Retrieval       : Expose artifacts through projections (read-only)
    Reconstruction  : Reconstruct coherent structures from evidence
    Association     : Create semantic relationships
    Consolidation   : Strengthen and stabilize semantic structures
    Reconsolidation : Update existing memories while preserving history
    Abstraction     : Create higher-level semantic representations
    Forgetting      : Reduce accessibility without deletion
    Decay           : Model gradual weakening of activation
    Compression     : Reduce representational complexity

Memory Operations follow these core principles:

    OP-PRINCIPLE-001: Every operation performs exactly one semantic transformation
    OP-PRINCIPLE-002: Operations never own Memory Artifacts (Foundation owns them)
    OP-PRINCIPLE-003: Operations preserve artifact identity
    OP-PRINCIPLE-004: Operations preserve provenance
    OP-PRINCIPLE-005: Every transformation creates an explicit revision
    OP-PRINCIPLE-006: Operations are independently testable and deterministic

Architecture:

    memory/
    ├── foundation/   # What exists (artifacts, identity, provenance, etc.)
    ├── forms/        # How it is organized (semantic projections)
    └── operations/   # How it evolves (transformations) ← THIS LAYER
"""

from __future__ import annotations

import time
import uuid
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, Type, Optional, Any, Tuple

if TYPE_CHECKING:
    from .encoding import EncodingOperation
    from .retrieval import RetrievalOperation
    from .reconstruction import ReconstructionOperation
    from .association import AssociationOperation
    from .consolidation import ConsolidationOperation
    from .reconsolidation import ReconsolidationOperation
    from .abstraction import AbstractionOperation
    from .forgetting import ForgettingOperation
    from .decay import DecayOperation
    from .compression import CompressionOperation

# =============================================================================
# OPERATION TYPES - Categories of memory operations
# =============================================================================


class OperationType:
    """Categories of canonical memory operations."""
    
    ENCODING = "encoding"
    RETRIEVAL = "retrieval"
    RECONSTRUCTION = "reconstruction"
    ASSOCIATION = "association"
    CONSOLIDATION = "consolidation"
    RECONSOLIDATION = "reconsolidation"
    ABSTRACTION = "abstraction"
    FORGETTING = "forgetting"
    DECAY = "decay"
    COMPRESSION = "compression"


# =============================================================================
# OPERATION STATES - Execution lifecycle states
# =============================================================================


class OperationState:
    """States in the operation execution lifecycle."""
    
    IDLE = "idle"                   # Operation not yet started
    WAITING = "waiting"             # Waiting for input or resources
    RUNNING = "running"             # Currently executing
    VALIDATING = "validating"       # Validating results before publication
    COMPLETED = "completed"         # Successfully finished
    FAILED = "failed"               # Execution failed
    SUSPENDED = "suspended"         # Temporarily paused


# =============================================================================
# OPERATION PROJECTION - State and diagnostics exposure
# =============================================================================


@dataclass(frozen=True)
class MemoryOperationProjection:
    """
    Exposes operation state for observability and debugging.
    
    Fields:
        operation_id:       Unique ID for this operation instance
        operation_kind:     What type of operation is this?
        state:              Current execution state
        
        # Statistics (reset on each run)
        inputs_processed:   Number of input artifacts/relations processed
        outputs_produced:   Number of output revisions/projections created
        duration_ms:        Total execution time in milliseconds
        
        # Validation
        validation_status:  Was validation successful?
        validation_result:  Details of validation (if any)
        
        # Diagnostics
        start_time_utc:     When did this operation start?
        end_time_utc:       When did it complete (or fail)?
        error_message:      If failed, what went wrong?
    """
    
    operation_id: str                       # Unique instance ID
    operation_kind: OperationType           # What kind of operation?
    state: OperationState                   # Current execution state
    
    # Statistics
    inputs_processed: int = 0               # Input artifacts processed
    outputs_produced: int = 0               # Outputs created
    duration_ms: float = 0.0                # Execution time (ms)
    
    # Validation
    validation_status: str = "unvalidated"  # valid/invalid/unvalidated
    validation_result: Optional[str] = None
    
    # Diagnostics
    start_time_utc: float = field(default_factory=time.time)
    end_time_utc: float = 0.0               # Set when completed/failed
    error_message: Optional[str] = None     # If failed


# =============================================================================
# MEMORY OPERATION - Base interface for all memory operations
# =============================================================================


class MemoryOperation:
    """
    Abstract base class for all memory operations.
    
    Every operation must implement:
        - execute(): Perform the semantic transformation
        - validate(): Validate inputs before execution
        
    Operations follow these contracts:
        - Operations never own Memory Artifacts (Foundation owns them)
        - Every transformation creates an explicit revision
        - Operations are deterministic (same inputs → same outputs)
        - Operations are independently testable
    """
    
    def __init__(
        self,
        operation_id: Optional[str] = None,
        operation_type: str = OperationType.ENCODING,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.operation_id: str = operation_id or str(uuid.uuid4())
        self.operation_type: str = operation_type
        self.config: Dict[str, Any] = config or {}
    
    @abstractmethod
    def execute(
        self,
        inputs: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Any, MemoryOperationProjection]:
        """Execute the memory operation."""
        pass
    
    @abstractmethod
    def validate(
        self,
        inputs: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Validate inputs before execution."""
        pass


# =============================================================================
# CONCRETE OPERATIONS - All canonical operations imported here
# =============================================================================

from .encoding import EncodingOperation, EncodingConfig, EncodingResult, create_encoding_operation
from .retrieval import RetrievalOperation, RetrievalConfig, RetrievalResult, create_retrieval_operation
from .reconstruction import ReconstructionOperation, ReconstructionConfig, ReconstructionResult, create_reconstruction_operation
from .association import AssociationOperation, AssociationConfig, AssociationResult, create_association_operation
from .consolidation import ConsolidationOperation, ConsolidationConfig, ConsolidationResult, create_consolidation_operation
from .reconsolidation import ReconsolidationOperation, ReconsolidationConfig, ReconsolidationResult, create_reconsolidation_operation
from .abstraction import AbstractionOperation, AbstractionConfig, AbstractionResult, create_abstraction_operation
from .forgetting import ForgettingOperation, ForgettingConfig, ForgettingResult, create_forgetting_operation
from .decay import DecayOperation, DecayConfig, DecayResult, create_decay_operation
from .compression import CompressionOperation, CompressionConfig, CompressionResult, create_compression_operation


# =============================================================================
# OPERATIONS REGISTRY - Map operation types to classes
# =============================================================================

OPERATIONS_REGISTRY: Dict[str, Type] = {
    OperationType.ENCODING: EncodingOperation,
    OperationType.RETRIEVAL: RetrievalOperation,
    OperationType.RECONSTRUCTION: ReconstructionOperation,
    OperationType.ASSOCIATION: AssociationOperation,
    OperationType.CONSOLIDATION: ConsolidationOperation,
    OperationType.RECONSOLIDATION: ReconsolidationOperation,
    OperationType.ABSTRACTION: AbstractionOperation,
    OperationType.FORGETTING: ForgettingOperation,
    OperationType.DECAY: DecayOperation,
    OperationType.COMPRESSION: CompressionOperation,
}


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_operation(
    operation_type: str,
    operation_id: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
) -> MemoryOperation:
    """
    Factory function to create any memory operation.
    
    Args:
        operation_type: Type of operation (encoding, retrieval, etc.)
        operation_id: Unique ID for this operation instance
        config: Operation-specific configuration
        
    Returns:
        New operation instance
        
    Raises:
        ValueError: If operation type is not recognized
    """
    if operation_type not in OPERATIONS_REGISTRY:
        raise ValueError(f"Unknown operation type: {operation_type}")
    
    op_class = OPERATIONS_REGISTRY[operation_type]
    
    # Map config to appropriate class-specific config if needed
    if operation_type == OperationType.ENCODING:
        from .encoding import EncodingConfig
        return op_class(operation_id=operation_id, config=config)
    elif operation_type == OperationType.RETRIEVAL:
        from .retrieval import RetrievalConfig
        return op_class(operation_id=operation_id, config=config)
    elif operation_type == OperationType.ASSOCIATION:
        from .association import AssociationConfig
        return op_class(operation_id=operation_id, config=config)
    elif operation_type == OperationType.CONSOLIDATION:
        from .consolidation import ConsolidationConfig
        return op_class(operation_id=operation_id, config=config)
    elif operation_type == OperationType.RECONSOLIDATION:
        from .reconsolidation import ReconsolidationConfig
        return op_class(operation_id=operation_id, config=config)
    elif operation_type == OperationType.ABSTRACTION:
        from .abstraction import AbstractionConfig
        return op_class(operation_id=operation_id, config=config)
    elif operation_type == OperationType.FORGETTING:
        from .forgetting import ForgettingConfig
        return op_class(operation_id=operation_id, config=config)
    elif operation_type == OperationType.DECAY:
        from .decay import DecayConfig
        return op_class(operation_id=operation_id, config=config)
    elif operation_type == OperationType.COMPRESSION:
        from .compression import CompressionConfig
        return op_class(operation_id=operation_id, config=config)
    
    # For reconstruction, no specific config class yet
    if operation_type == OperationType.RECONSTRUCTION:
        return op_class(operation_id=operation_id, config=config)
    
    raise ValueError(f"Could not create operation for type: {operation_type}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Base classes
    "MemoryOperation",
    "MemoryOperationProjection",
    "OperationState",
    "OperationType",
    
    # Concrete operations
    "EncodingOperation",
    "RetrievalOperation",
    "ReconstructionOperation",
    "AssociationOperation",
    "ConsolidationOperation",
    "ReconsolidationOperation",
    "AbstractionOperation",
    "ForgettingOperation",
    "DecayOperation",
    "CompressionOperation",
    
    # Config classes
    "EncodingConfig",
    "RetrievalConfig",
    "ReconstructionConfig",
    "AssociationConfig",
    "ConsolidationConfig",
    "ReconsolidationConfig",
    "AbstractionConfig",
    "ForgettingConfig",
    "DecayConfig",
    "CompressionConfig",
    
    # Result classes
    "EncodingResult",
    "RetrievalResult",
    "ReconstructionResult",
    "AssociationResult",
    "ConsolidationResult",
    "ReconsolidationResult",
    "AbstractionResult",
    "ForgettingResult",
    "DecayResult",
    "CompressionResult",
    
    # Factory functions
    "create_operation",
    "create_encoding_operation",
    "create_retrieval_operation",
    "create_reconstruction_operation",
    "create_association_operation",
    "create_consolidation_operation",
    "create_reconsolidation_operation",
    "create_abstraction_operation",
    "create_forgetting_operation",
    "create_decay_operation",
    "create_compression_operation",
    
    # Registry
    "OPERATIONS_REGISTRY",
]