# Action Runtime Registry
# =======================

"""
Tool and effector registry for the Action Runtime.

This module provides:
    - Canonical tool registration authority
    - Tool discovery and lookup
    - Schema validation integration
    - Duplicate detection
    - Registry sealing
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum, auto
import uuid


# =============================================================================
# IDENTITY TYPES (defined here to avoid circular imports)
# =============================================================================

@dataclass(frozen=True)
class ToolId:
    """Identifier for a tool."""
    
    value: str
    
    @classmethod
    def from_name(cls, name: str) -> "ToolId":
        return cls(value=name.lower().replace(" ", "_"))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class EffectorId:
    """Identifier for an effector."""
    
    value: str
    
    @classmethod
    def from_name(cls, name: str) -> "EffectorId":
        return cls(value=name.lower().replace(" ", "_"))
    
    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ToolContract:
    """Contract defining a tool's capabilities and behavior."""
    
    tool_id: ToolId
    name: str
    supported_operations: Tuple[str, ...]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    side_effect_class: str = "none"
    is_idempotent: bool = False
    timeout_seconds: float = 60.0
    concurrency_class: str = "concurrent"
    cpu_required: Optional[float] = None
    memory_required: Optional[int] = None
    failure_classification: str = "retryable"


@dataclass(frozen=True)
class EffectorContract:
    """Contract defining an effector's side-effecting capabilities."""
    
    effector_id: EffectorId
    name: str
    target_domain: str
    side_effect_class: str
    reversibility: str = "unknown"
    required_capability: Optional[str] = None
    is_idempotent: bool = False
    timeout_seconds: float = 60.0
    cancellation_policy: str = "cooperative"
    supports_rollback: bool = False
    rollback_operation: Optional[str] = None
    supports_dry_run: bool = False


class RegistryError(Exception):
    """Base exception for registry errors."""
    pass


class RegistrationState(Enum):
    """Registry registration states."""
    
    OPEN = "open"      # New registrations allowed
    LOCKED = "locked"  # No new registrations (immutable)
    CLOSED = "closed"  # Read-only, no modifications


@dataclass(frozen=True)
class RegistryEntry:
    """
    A registry entry for a tool or effector.
    
    Args:
        identifier: The ToolId or EffectorId
        name: Human-readable name
        contract: The full contract definition
        registered_at: When registration occurred
        registerer_id: Who registered this (for audit)
    """
    
    identifier: str  # String representation of ToolId/EffectorId
    name: str
    contract: Dict[str, Any]
    registered_at: float
    registerer_id: Optional[str] = None


# =============================================================================
# ACTION REGISTRY
# =============================================================================


class ActionRegistry:
    """
    Canonical registry for tools and effectors in the action runtime.
    
    This is the single source of truth for what operations are available.
    All tool and effector registrations go through this authority.
    
    Invariants:
        1. Exactly one canonical registry per runtime
        2. No duplicate identifiers allowed
        3. Registration is deterministic (same inputs = same result)
        4. Registry can be sealed to prevent modification
    """
    
    def __init__(self, runtime_id: str):
        self._runtime_id = runtime_id
        
        # Tool registry
        self._tools: Dict[ToolId, ToolContract] = {}
        
        # Effector registry  
        self._effectors: Dict[EffectorId, EffectorContract] = {}
        
        # State
        self._state = RegistrationState.OPEN
        
        # Audit trail
        self._registration_history: List[Dict[str, Any]] = []
    
    @property
    def runtime_id(self) -> str:
        """Get the runtime ID."""
        return self._runtime_id
    
    @property
    def state(self) -> RegistrationState:
        """Get current registration state."""
        return self._state
    
    # -------------------------------------------------------------------------
    # Tool registration
    # -------------------------------------------------------------------------
    
    async def register_tool(
        self,
        contract: ToolContract,
        registerer_id: Optional[str] = None,
    ) -> bool:
        """
        Register a tool.
        
        Args:
            contract: The tool contract (contains all metadata)
            registerer_id: Optional identifier for who is registering
            
        Returns:
            True if registration succeeded
        """
        if self._state != RegistrationState.OPEN:
            raise RuntimeError(f"Registry is {self._state.value}, cannot register")
        
        # Check for duplicates
        if contract.tool_id in self._tools:
            return False
        
        # Register the tool
        with self._get_lock():
            self._tools[contract.tool_id] = contract
            
            # Record in history
            self._registration_history.append({
                "type": "tool",
                "identifier": str(contract.tool_id),
                "name": contract.name,
                "registered_at": 0.0,
                "registerer_id": registerer_id,
            })
        
        return True
    
    async def unregister_tool(self, tool_id: ToolId) -> bool:
        """
        Unregister a tool.
        
        Returns:
            True if the tool was registered and unregistered
        """
        if self._state != RegistrationState.OPEN:
            raise RuntimeError(f"Registry is {self._state.value}, cannot unregister")
        
        with self._get_lock():
            if tool_id in self._tools:
                del self._tools[tool_id]
                
                self._registration_history.append({
                    "type": "unregister_tool",
                    "identifier": str(tool_id),
                    "timestamp": 0.0,
                })
                
                return True
        
        return False
    
    async def get_tool(self, tool_id: ToolId) -> Optional[ToolContract]:
        """Get a registered tool contract."""
        with self._get_lock():
            return self._tools.get(tool_id)
    
    # -------------------------------------------------------------------------
    # Effector registration
    # -------------------------------------------------------------------------
    
    async def register_effector(
        self,
        contract: EffectorContract,
        registerer_id: Optional[str] = None,
    ) -> bool:
        """
        Register an effector.
        
        Args:
            contract: The effector contract
            registerer_id: Optional identifier for who is registering
            
        Returns:
            True if registration succeeded
        """
        if self._state != RegistrationState.OPEN:
            raise RuntimeError(f"Registry is {self._state.value}, cannot register")
        
        # Check for duplicates
        if contract.effector_id in self._effectors:
            return False
        
        with self._get_lock():
            self._effectors[contract.effector_id] = contract
            
            self._registration_history.append({
                "type": "effector",
                "identifier": str(contract.effector_id),
                "name": contract.name,
                "timestamp": 0.0,
                "registerer_id": registerer_id,
            })
        
        return True
    
    async def unregister_effector(self, effector_id: EffectorId) -> bool:
        """
        Unregister an effector.
        
        Returns:
            True if the effector was registered and unregistered
        """
        if self._state != RegistrationState.OPEN:
            raise RuntimeError(f"Registry is {self._state.value}, cannot unregister")
        
        with self._get_lock():
            if effector_id in self._effectors:
                del self._effectors[effector_id]
                
                self._registration_history.append({
                    "type": "unregister_effector",
                    "identifier": str(effector_id),
                    "timestamp": 0.0,
                })
                
                return True
        
        return False
    
    async def get_effector(self, effector_id: EffectorId) -> Optional[EffectorContract]:
        """Get a registered effector contract."""
        with self._get_lock():
            return self._effectors.get(effector_id)
    
    # -------------------------------------------------------------------------
    # Discovery and listing
    # -------------------------------------------------------------------------
    
    async def list_tools(self) -> Tuple[ToolId, ...]:
        """List all registered tool IDs."""
        with self._get_lock():
            return tuple(self._tools.keys())
    
    async def list_effectors(self) -> Tuple[EffectorId, ...]:
        """List all registered effector IDs."""
        with self._get_lock():
            return tuple(self._effectors.keys())
    
    # -------------------------------------------------------------------------
    # Registry control
    # -------------------------------------------------------------------------
    
    async def seal(self) -> None:
        """
        Seal the registry - no further modifications allowed.
        
        After sealing, only read operations are permitted.
        """
        if self._state == RegistrationState.CLOSED:
            return
        
        self._state = RegistrationState.LOCKED
    
    async def close(self) -> None:
        """
        Close the registry completely - even read-only access may fail.
        
        Used during shutdown.
        """
        self._state = RegistrationState.CLOSED
    
    # -------------------------------------------------------------------------
    # Utility methods
    # -------------------------------------------------------------------------
    
    def get_state_snapshot(self) -> Dict[str, Any]:
        """Get current registry state (for diagnostics)."""
        with self._get_lock():
            return {
                "runtime_id": self._runtime_id,
                "state": self._state.value,
                "tool_count": len(self._tools),
                "effector_count": len(self._effectors),
                "registered_tools": [str(k) for k in self._tools.keys()],
                "registered_effectors": [str(k) for k in self._effectors.keys()],
                "history_length": len(self._registration_history),
            }
    
    def get_registration_history(self) -> List[Dict[str, Any]]:
        """Get the full registration history (for audit)."""
        return list(self._registration_history)
    
    # -------------------------------------------------------------------------
    # Internal
    # -------------------------------------------------------------------------
    
    def _get_lock(self):
        """Get a lock for thread-safe operations."""
        import threading
        if not hasattr(self, "_lock"):
            self._lock = threading.RLock()
        return self._lock


# =============================================================================
# PUBLIC API EXPORTS
# =============================================================================

__all__ = [
    # Identity types
    "ToolId",
    "EffectorId",
    
    # Contract types
    "ToolContract",
    "EffectorContract",
    
    # Enums
    "RegistrationState",
    
    # Data classes
    "RegistryEntry",
    
    # Classes
    "ActionRegistry",
    
    # Exceptions
    "RegistryError",
]