# Restart Contracts
# =================

"""
Restart contracts for Phase 3.7.10.

Every managed entity must declare one of these restart capability types:
    - RESTARTABLE: Can be fully restarted (stop + start)
    - REINITIALIZABLE: Can reinitialize internal state without full stop
    - RELOADABLE: Configuration/state can be reloaded
    - RECONNECTABLE: Connection-based entities that can reconnect
    - PROCESS_RESTART_ONLY: Process restart only (external management)
    - RUNTIME_RESTART_REQUIRED: Entire runtime must restart
    - NON_RESTARTABLE: Cannot be restarted (requires human intervention)
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Any


@dataclass(frozen=True)
class RestartContract:
    """
    A contract declaring a component's restart capabilities.
    
    Args:
        entity_id: Which entity this contract is for
        
        capability_type: What kind of restart is supported
        quiescence_required: Whether quiescence must be achieved first
        state_preservation: Can state be preserved during restart?
        
        resource_cleanup_actions: List of actions to clean up resources
        reconstruction_actions: List of actions to rebuild component
        
        readiness_probes: Probes that must pass before considered ready
        verification_probes: Optional additional verification probes
    """
    
    entity_id: str
    
    capability_type: "RestartKind"
    
    quiescence_required: bool = True
    state_preservation: bool = False
    
    resource_cleanup_actions: List[str] = field(default_factory=lambda: [
        "release_ports",
        "close_connections", 
        "free_memory",
        "stop_processes"
    ])
    
    reconstruction_actions: List[str] = field(default_factory=lambda: [
        "acquire_resources",
        "initialize_state",
        "register_services",
        "enable_admission"
    ])
    
    readiness_probes: List[str] = field(default_factory=lambda: [
        "health_check",
        "readiness_probe"
    ])


class RestartKind(Enum):
    """Restart capability types."""
    
    RESTARTABLE = "restartable"              # Full stop + start cycle
    REINITIALIZABLE = "reinitializable"      # Reinitialize internal state only
    RELOADABLE = "reloadable"                # Configuration/state reload
    RECONNECTABLE = "reconnectable"          # Connection-based reconnection
    PROCESS_RESTART_ONLY = "process_restart_only"  # Process restart only
    RUNTIME_RESTART_REQUIRED = "runtime_restart_required"  # Full runtime restart
    NON_RESTARTABLE = "non_restartable"      # Cannot be restarted


@dataclass(frozen=True)
class GenerationId:
    """
    Unique generation identifier for an entity.
    
    Each restart increments the generation number. Stale generations
    are rejected by the system.
    
    Args:
        entity_id: Which entity this generation is for
        
        generation_number: Monotonically increasing generation counter
        epoch: Epoch (restart cycle) number
        timestamp: When this generation was created
    """
    
    entity_id: str
    
    generation_number: int = 1
    epoch: int = 0
    timestamp: float = field(default_factory=lambda: __import__("time").time())
    
    @property
    def is_stale(self) -> bool:
        """Check if this generation should be considered stale."""
        # Would check against current runtime state
        return False


@dataclass(frozen=True)
class GenerationFence:
    """
    A fence preventing use of stale generations.
    
    Args:
        entity_id: Which entity is fenced
        
        allowed_generations: List of valid generation numbers
        fence_timestamp: When the fence was created
        
        allow_newer: Whether newer generations are automatically accepted
    """
    
    entity_id: str
    
    allowed_generations: List[int] = field(default_factory=lambda: [1])
    fence_timestamp: float = field(default_factory=lambda: __import__("time").time())
    
    allow_newer: bool = True


class RestartCoordinator:
    """
    Coordinator for restart operations.
    
    Usage:
        coordinator = RestartCoordinator()
        
        contract = await coordinator.get_restart_contract("entity_123")
        
        if contract.capability_type == RestartKind.RESTARTABLE:
            await coordinator.request_restart("entity_123", contract)
    """
    
    def __init__(self) -> None:
        """Initialize the restart coordinator."""
        self._contracts: Dict[str, RestartContract] = {}
        self._generations: Dict[str, GenerationId] = {}
        self._fences: Dict[str, GenerationFence] = {}
    
    async def get_restart_contract(self, entity_id: str) -> Optional[RestartContract]:
        """Get the restart contract for an entity."""
        return self._contracts.get(entity_id)
    
    def register_contract(
        self,
        entity_id: str,
        contract: RestartContract
    ) -> None:
        """Register a restart contract for an entity."""
        self._contracts[entity_id] = contract
        
        # Initialize generation if not exists
        if entity_id not in self._generations:
            self._generations[entity_id] = GenerationId(
                entity_id=entity_id,
                generation_number=1,
                epoch=0
            )
    
    async def request_restart(self, entity_id: str) -> Optional[GenerationId]:
        """
        Request a restart for an entity.
        
        Returns new generation if restart is allowed, None otherwise.
        """
        contract = self._contracts.get(entity_id)
        if contract is None:
            return None
        
        # Check fence
        fence = self._fences.get(entity_id)
        current_gen = self._generations.get(entity_id)
        
        if current_gen is not None and fence is not None:
            if current_gen.generation_number in fence.allowed_generations:
                pass  # Generation allowed
        
        # Increment generation
        gen = self._generations[entity_id]
        new_gen = GenerationId(
            entity_id=gen.entity_id,
            generation_number=gen.generation_number + 1,
            epoch=gen.epoch + 1,
            timestamp=__import__("time").time()
        )
        
        self._generations[entity_id] = new_gen
        
        # Update fence
        if fence is not None:
            fence = GenerationFence(
                entity_id=fence.entity_id,
                allowed_generations=[new_gen.generation_number],
                allow_newer=True
            )
            self._fences[entity_id] = fence
        
        return new_gen
    
    def verify_generation(self, entity_id: str, generation: int) -> bool:
        """Verify that a generation is valid for an entity."""
        gen = self._generations.get(entity_id)
        if gen is None:
            return False
        
        return generation >= gen.generation_number
    
    def snapshot(self) -> Dict[str, Any]:
        """Get an immutable snapshot of restart state."""
        return {
            "registered_contracts": len(self._contracts),
            "tracked_generations": len(self._generations),
            "active_fences": len(self._fences),
        }
    
    def fence_entity(self, entity_id: str) -> GenerationFence:
        """Create a fence for an entity (used during restart)."""
        current = self._generations.get(entity_id)
        
        if current is None:
            fence = GenerationFence(
                entity_id=entity_id,
                allowed_generations=[1]
            )
        else:
            fence = GenerationFence(
                entity_id=entity_id,
                allowed_generations=[current.generation_number],
                allow_newer=False
            )
        
        self._fences[entity_id] = fence
        return fence


class DefaultRestartCoordinator(RestartCoordinator):
    """
    Default implementation of RestartCoordinator.
    
    Provides sensible defaults for contract registration and generation fencing.
    """
    
    def __init__(self) -> None:
        super().__init__()
        # Would register default contracts here