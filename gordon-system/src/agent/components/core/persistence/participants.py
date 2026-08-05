# Persistence Participant Protocol
# ================================

"""
Persistence participant contract and descriptors.

This module defines the protocol that components must implement to participate
in the persistence lifecycle (capture, restore, verification).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Protocol, Any, Dict, Optional, List
from enum import Enum
import uuid


# =============================================================================
# Participant State Types
# =============================================================================

@dataclass(frozen=True)
class PersistenceDescriptor:
    """
    Metadata about a participant's state for persistence coordination.
    
    This is what the persistence authority needs to know about a participant:
        - What state it owns
        - How to capture it
        - How to restore it
        - Dependencies on other participants
        - Serialization schema
    """
    
    participant_id: str
    
    # State domains owned by this participant
    state_domains: List[str] = field(default_factory=list)
    
    # Capture requirements
    requires_quiescence: bool = False  # Does capture require quiescent state?
    quiesce_timeout_seconds: float = 5.0
    
    # Restore requirements  
    restore_order: int = 0  # Lower numbers restored first
    external_dependencies: List[str] = field(default_factory=list)
    
    # Serialization
    schema_version: int = 1
    serialization_format: str = "canonical_json"
    
    # Checkpoint participation
    supports_checkpoint: bool = True
    checkpoint_dependencies: List[str] = field(default_factory=list)
    
    # Journal participation
    journal_enabled: bool = False
    
    @property
    def is_durable(self) -> bool:
        """Check if any state requires durable persistence."""
        return self.supports_checkpoint or self.journal_enabled


@dataclass(frozen=True)
class StateVersion:
    """Immutable state version for a participant."""
    
    value: int
    domain_id: str
    
    @classmethod
    def initial(cls, domain_id: str) -> "StateVersion":
        """Create initial state version (0)."""
        return cls(value=0, domain_id=domain_id)
    
    def next(self) -> "StateVersion":
        """Return the next version."""
        return StateVersion(value=self.value + 1, domain_id=self.domain_id)


# =============================================================================
# Capture Context
# =============================================================================

class CaptureMode(Enum):
    """Mode of state capture."""
    
    QUIESCENT = "quiescent"           # Block mutations during capture
    VERSIONED = "versioned"          # Use versioning to detect changes
    COPY_ON_WRITE = "copy_on_write"  # Copy-on-write snapshot
    INCREMENTAL = "incremental"      # Only changed since last snapshot
    BEST_EFFORT_DIAGNOSTIC = "best_effort_diagnostic"  # No validation


@dataclass(frozen=True)
class CaptureContext:
    """Context for a state capture operation."""
    
    context_id: str
    
    runtime_id: str
    boot_session_id: str
    
    mode: CaptureMode = CaptureMode.VERSIONED
    
    # Version boundary
    target_version: Optional[int] = None
    
    # Timeout
    timeout_seconds: float = 30.0
    
    @classmethod
    def create(cls, runtime_id: str, mode: CaptureMode = CaptureMode.VERSIONED) -> "CaptureContext":
        """Create a new capture context."""
        return cls(
            context_id=str(uuid.uuid4()),
            runtime_id=runtime_id,
            boot_session_id=str(uuid.uuid4()),
            mode=mode,
        )


# =============================================================================
# Captured State
# =============================================================================

@dataclass(frozen=True)
class CapturedState:
    """
    A captured snapshot of a participant's state.
    
    This is the artifact that will be serialized and persisted:
        - State data in canonical format
        - Version information
        - Signature for integrity verification
        - Metadata for restore coordination
    """
    
    captured_state_id: str
    
    runtime_id: str
    boot_session_id: str
    
    # Participant info
    participant_id: str
    state_domain_id: str
    
    # State data (must be serializable, no live handles)
    state_data: Dict[str, Any]
    
    # Versioning
    state_version: int
    schema_version: int
    
    # Timestamps
    captured_at: float  # monotonic timestamp
    
    # Integrity
    content_digest: str  # SHA256 of serialized state
    signature: Optional[str] = None  # If signed
    
    @classmethod
    def create(
        cls,
        runtime_id: str,
        participant_id: str,
        domain_id: str,
        state_data: Dict[str, Any],
        state_version: int,
        schema_version: int,
    ) -> "CapturedState":
        """Create captured state (digest calculated by persistence manager)."""
        return cls(
            captured_state_id=str(uuid.uuid4()),
            runtime_id=runtime_id,
            boot_session_id="",  # Will be set by persistence manager
            participant_id=participant_id,
            state_domain_id=domain_id,
            state_data=state_data,
            state_version=state_version,
            schema_version=schema_version,
            captured_at=0.0,  # Will be set by persistence manager
            content_digest="",
        )


# =============================================================================
# Persistence Participant Protocol
# =============================================================================

class PersistenceParticipantProtocol(ABC):
    """
    Protocol that components implement to participate in persistence.
    
    The persistence authority coordinates participants through this protocol:
        
        CAPTURE PHASE:
            1. Get current state version
            2. Request capture (with quiescence if needed)
            3. Validate captured state
        
        RESTORE PHASE:
            1. Receive serialized state
            2. Validate schema compatibility
            3. Restore internal state
            4. Verify restored state is valid
        
    A participant does NOT own persistence - it only declares its state.
    """
    
    @property
    @abstractmethod
    def persistence_descriptor(self) -> PersistenceDescriptor:
        """Return metadata about this participant's state."""
        pass
    
    @abstractmethod
    async def capture_state(self, context: CaptureContext) -> CapturedState:
        """
        Capture the current state for persistence.
        
        Args:
            context: Context with capture parameters
            
        Returns:
            CapturedState artifact
            
        Notes:
            - Must preserve state version
            - Must not mutate state during capture
            - Must return serializable data (no live handles)
            - Should be idempotent where possible
        """
        pass
    
    @abstractmethod
    async def validate_captured_state(
        self,
        captured: CapturedState,
        context: CaptureContext
    ) -> bool:
        """
        Validate that captured state is complete and consistent.
        
        Args:
            captured: The captured state to validate
            context: Original capture context
            
        Returns:
            True if capture is valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def restore_state(
        self,
        captured: CapturedState,
        context: CaptureContext
    ) -> bool:
        """
        Restore state from a captured snapshot.
        
        Args:
            captured: The captured state to restore from
            context: Restore context with runtime info
            
        Returns:
            True if restoration succeeded, False otherwise
            
        Notes:
            - Must not deserialize live handles
            - Should reacquire external resources
            - Must validate restored state integrity
        """
        pass
    
    @abstractmethod
    async def verify_restored_state(
        self,
        captured: CapturedState,
        context: CaptureContext
    ) -> bool:
        """
        Verify that restored state is correct and valid.
        
        Args:
            captured: Original captured state (for comparison)
            context: Restore context
            
        Returns:
            True if restored state matches expectations
            
        Notes:
            - Compare internal state to captured data
            - Verify external resources reacquired
            - Do not compare memory addresses
        """
        pass
    
    @abstractmethod
    def current_state_version(self) -> StateVersion:
        """Return the current version of this participant's state."""
        pass


# =============================================================================
# Participant Registration
# =============================================================================

@dataclass(frozen=True)
class ParticipantRegistration:
    """Result of registering a persistence participant."""
    
    registration_id: str
    
    participant_id: str
    participant_protocol: PersistenceParticipantProtocol
    
    # Registered domains
    registered_domains: List[str]
    
    # Validation result
    validation_passed: bool
    validation_message: Optional[str] = None
    
    @classmethod
    def success(
        cls,
        participant_id: str,
        protocol: PersistenceParticipantProtocol,
        domains: List[str],
    ) -> "ParticipantRegistration":
        """Create a successful registration."""
        return cls(
            registration_id=str(uuid.uuid4()),
            participant_id=participant_id,
            participant_protocol=protocol,
            registered_domains=domains,
            validation_passed=True,
            validation_message=f"Registered {len(domains)} state domains",
        )
    
    @classmethod
    def failure(cls, participant_id: str, message: str) -> "ParticipantRegistration":
        """Create a failed registration."""
        return cls(
            registration_id=str(uuid.uuid4()),
            participant_id=participant_id,
            participant_protocol=None,  # type: ignore
            registered_domains=[],
            validation_passed=False,
            validation_message=message,
        )


__all__ = [
    # Descriptors
    "PersistenceDescriptor",
    
    # Versions
    "StateVersion",
    
    # Capture
    "CaptureMode",
    "CaptureContext",
    "CapturedState",
    
    # Protocol
    "PersistenceParticipantProtocol",
    "ParticipantRegistration",
]