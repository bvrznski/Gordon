# Gordon Core: Architectural Evolution Model (Phase 3.33)
"""
Architectural Evolution Model - The canonical model for tracking and managing
all evolution activities in the Gordon Core.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

from gordon_system.src.agent.architecture.evolution.foundations import (
    EvolutionType,
    EvolutionPhase,
    EvolutionStatus,
    EvolutionIdentifier,
    EvolutionGovernance,
    EvolutionLifecycle,
)


# ============================================================================
# EVOLUTION MODEL
# ============================================================================

@dataclass(frozen=True)
class EvolutionModel:
    """
    Immutable evolution model representing a complete architectural change.
    
    The model defines the structure and lifecycle of all evolution activities
    in the Gordon Core, ensuring consistency across all types of evolutionary
    changes (modules, interfaces, schemas, configurations, etc.).
    """
    
    # Model identity
    id: str                          # Unique identifier for this evolution model
    
    # Evolution metadata
    type: EvolutionType              # Type of evolution being performed
    phase: EvolutionPhase            # Current lifecycle phase
    status: EvolutionStatus          # Current execution status
    
    # Artifact information
    source_artifact: str             # Source artifact identifier (e.g., "module:core@1.0.0")
    target_artifact: str             # Target artifact identifier (e.g., "module:core@2.0.0")
    
    # Model properties
    description: str                 # Human-readable description of the evolution
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Execution context
    owner: Optional[str] = None      # Owner responsible for execution
    governance: EvolutionGovernance = EvolutionGovernance.SEMIAUTO
    
    # Relationships
    dependencies: List[str] = field(default_factory=list)  # Required dependencies
    dependents: List[str] = field(default_factory=list)    # Dependent artifacts
    
    @property
    def is_new_evolution(self) -> bool:
        """Check if this is a new evolution (no previous state)."""
        return "@0.0.0" in self.source_artifact or "None" in self.source_artifact
    
    @property
    def is_deletion(self) -> bool:
        """Check if this evolution results in deletion."""
        return not self.target_artifact or "delete" in self.target_artifact.lower()
    
    @property
    def is_migration(self) -> bool:
        """Check if this is a migration (context change, version unchanged)."""
        source_version = self._extract_version(self.source_artifact)
        target_version = self._extract_version(self.target_artifact)
        return source_version == target_version and source_version is not None
    
    @property
    def is_upgrade(self) -> bool:
        """Check if this is a version upgrade."""
        source_version = self._extract_version(self.source_artifact)
        target_version = self._extract_version(self.target_artifact)
        
        if source_version is None or target_version is None:
            return False
        
        # Simple semantic version comparison
        return self._compare_versions(target_version, source_version) > 0
    
    def _extract_version(self, artifact: str) -> Optional[str]:
        """Extract version from artifact identifier."""
        if not artifact or "@" not in artifact:
            return "0.0.0"
        
        parts = artifact.split("@")
        if len(parts) < 2:
            return "0.0.0"
        
        version_str = parts[1]
        # Remove any path information
        if "/" in version_str:
            version_str = version_str.rsplit("/", 1)[0]
        
        return version_str
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare two semantic versions. Returns >0 if v1>v2, <0 if v1<v2, 0 if equal."""
        try:
            v1_parts = [int(x) for x in v1.split(".")]
            v2_parts = [int(x) for x in v2.split(".")]
            
            # Pad to same length
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts.extend([0] * (max_len - len(v1_parts)))
            v2_parts.extend([0] * (max_len - len(v2_parts)))
            
            for p1, p2 in zip(v1_parts, v2_parts):
                if p1 != p2:
                    return p1 - p2
            
            return 0
        except (ValueError, IndexError):
            # Fallback to string comparison
            return 1 if v1 > v2 else (-1 if v1 < v2 else 0)
    
    def next_phase(self) -> EvolutionPhase:
        """Get the next phase in the evolution lifecycle."""
        current_index = EvolutionLifecycle.PHASES.index(self.phase)
        
        if current_index >= len(EvolutionLifecycle.PHASES) - 1:
            return self.phase  # Already at terminal phase
        
        return EvolutionLifecycle.PHASES[current_index + 1]
    
    def can_transition_to(self, target_phase: EvolutionPhase) -> bool:
        """Check if transition to target phase is valid."""
        try:
            current_index = EvolutionLifecycle.PHASES.index(self.phase)
            target_index = EvolutionLifecycle.PHASES.index(target_phase)
            
            # Only allow forward transitions
            return target_index == current_index + 1 or (
                self.status in (EvolutionStatus.COMPLETED, EvolutionStatus.REVERSED) and
                target_phase == EvolutionPhase.PROPOSAL
            )
        except ValueError:
            return False
    
    def transition_to(self, new_phase: EvolutionPhase, new_status: EvolutionStatus = None):
        """Transition to a new phase (returns new model instance)."""
        if not self.can_transition_to(new_phase):
            raise ValueError(f"Cannot transition from {self.phase} to {new_phase}")
        
        return EvolutionModel(
            id=self.id,
            type=self.type,
            phase=new_phase,
            status=new_status or self.status,
            source_artifact=self.source_artifact,
            target_artifact=self.target_artifact,
            description=self.description,
            owner=self.owner,
            governance=self.governance,
            dependencies=self.dependencies,
            dependents=self.dependents,
        )


# ============================================================================
# EVOLUTION ARTIFACT MODEL
# ============================================================================

@dataclass(frozen=True)
class EvolutionArtifact:
    """
    Immutable representation of an artifact undergoing evolution.
    
    Artifacts are the entities that can evolve - modules, interfaces, schemas,
    configurations, and other architectural components.
    """
    
    # Artifact identity
    identifier: str                  # Unique identifier for this artifact
    
    # State information
    current_state: Dict[str, Any]   # Current state of the artifact
    target_state: Dict[str, Any]    # Target state after evolution
    
    # Evolution context
    evolution_type: EvolutionType    # Type of evolution being performed
    phase: EvolutionPhase           # Current lifecycle phase
    status: EvolutionStatus         # Current execution status
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_new(self) -> bool:
        """Check if artifact is newly created."""
        return "version" not in self.current_state or self.current_state.get("version") == "0.0.0"
    
    @property
    def is_deleted(self) -> bool:
        """Check if artifact has been deleted."""
        return self.status == EvolutionStatus.REVERSED
    
    @property
    def version_change(self) -> str:
        """Get the version change string (e.g., '1.0.0 → 2.0.0')."""
        current_version = self.current_state.get("version", "0.0.0")
        target_version = self.target_state.get("version", "0.0.0")
        
        if current_version == target_version:
            return f"{current_version}"
        
        return f"{current_version} → {target_version}"


# ============================================================================
# EVOLUTION RELATIONSHIP MODEL
# ============================================================================

@dataclass(frozen=True)
class EvolutionRelationship:
    """
    Immutable relationship between evolution artifacts.
    
    Relationships define how evolutionary artifacts depend on, replace, or
    interact with each other during evolution.
    """
    
    class Type(Enum):
        DEPENDENCY = "dependency"       # A depends on B
        REPLACEMENT = "replacement"     # A is replaced by B
        COMPATIBILITY = "compatibility" # A and B are compatible
        EXTENSION = "extension"         # B extends A's functionality
        DEPRECATION = "deprecation"     # A is deprecated in favor of B
    
    source_artifact: str              # Source artifact identifier
    target_artifact: str              # Target artifact identifier
    relationship_type: Type          # Type of relationship
    strength: float                  # Strength of relationship (0.0 to 1.0)
    
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional data
    
    @property
    def is_strong(self) -> bool:
        """Check if relationship is strong (>= 0.8)."""
        return self.strength >= 0.8
    
    @property
    def is_weak(self) -> bool:
        """Check if relationship is weak (< 0.5)."""
        return self.strength < 0.5


# ============================================================================
# EVOLUTION PATH MODEL
# ============================================================================

@dataclass(frozen=True)
class EvolutionPath:
    """
    Immutable path representing a sequence of evolution steps.
    
    Paths define the complete journey from initial state to final state,
    including all intermediate transitions and validations.
    """
    
    # Path identity
    id: str                          # Unique identifier for this path
    
    # Path components
    start_state: Dict[str, Any]      # Initial state before any evolution
    end_state: Dict[str, Any]        # Final state after all evolution
    steps: List[EvolutionArtifact] = field(default_factory=list)  # Evolution steps
    
    # Path metadata
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def is_complete(self) -> bool:
        """Check if path has reached terminal state."""
        return (
            len(self.steps) > 0 and 
            self.steps[-1].status in (EvolutionStatus.COMPLETED, EvolutionStatus.FAILED, EvolutionStatus.REVERSED)
        )
    
    @property
    def current_phase(self) -> EvolutionPhase:
        """Get the current phase of evolution."""
        return self.steps[-1].phase if self.steps else EvolutionPhase.PROPOSAL
    
    @property
    def progress(self) -> float:
        """Calculate progress as percentage (0.0 to 1.0)."""
        total_phases = len(EvolutionLifecycle.PHASES)
        current_index = EvolutionLifecycle.PHASES.index(self.current_phase)
        
        return (current_index + 1) / total_phases
    
    def add_step(self, step: EvolutionArtifact) -> "EvolutionPath":
        """Add a new evolution step to the path."""
        new_steps = self.steps.copy() if isinstance(self.steps, list) else list(self.steps)
        new_steps.append(step)
        
        return EvolutionPath(
            id=self.id,
            start_state=self.start_state,
            end_state=step.target_state,
            steps=new_steps,
        )
    
    def get_artifact(self, identifier: str) -> Optional[EvolutionArtifact]:
        """Get a specific artifact by its identifier."""
        for step in self.steps:
            if step.identifier == identifier:
                return step
        return None
    
    def get_artifacts_by_type(self, evolution_type: EvolutionType) -> List[EvolutionArtifact]:
        """Get all artifacts of a specific evolution type."""
        return [step for step in self.steps if step.evolution_type == evolution_type]


# ============================================================================
# EVOLUTION PATH BUILDER
# ============================================================================

class EvolutionPathBuilder:
    """
    Builder for constructing evolution paths.
    
    Provides a fluent API for building complex evolution paths with multiple
    steps, relationships, and validations.
    """
    
    def __init__(self):
        self._id: str = ""
        self._start_state: Dict[str, Any] = {}
        self._end_state: Dict[str, Any] = {}
        self._steps: List[EvolutionArtifact] = []
    
    def with_id(self, path_id: str) -> "EvolutionPathBuilder":
        """Set the evolution path ID."""
        self._id = path_id
        return self
    
    def from_state(self, state: Dict[str, Any]) -> "EvolutionPathBuilder":
        """Set the initial state."""
        self._start_state = dict(state)
        return self
    
    def to_state(self, state: Dict[str, Any]) -> "EvolutionPathBuilder":
        """Set the target state."""
        self._end_state = dict(state)
        return self
    
    def add_step(
        self,
        identifier: str,
        current_state: Dict[str, Any],
        target_state: Dict[str, Any],
        evolution_type: EvolutionType,
        phase: EvolutionPhase = EvolutionPhase.PROPOSAL,
        status: EvolutionStatus = EvolutionStatus.PENDING
    ) -> "EvolutionPathBuilder":
        """Add an evolution step."""
        artifact = EvolutionArtifact(
            identifier=identifier,
            current_state=dict(current_state),
            target_state=dict(target_state),
            evolution_type=evolution_type,
            phase=phase,
            status=status,
        )
        self._steps.append(artifact)
        return self
    
    def build(self) -> EvolutionPath:
        """Build the evolution path."""
        if not self._steps:
            raise ValueError("Evolution path must have at least one step")
        
        return EvolutionPath(
            id=self._id or f"evolution-path-{len(self._steps)}-steps",
            start_state=dict(self._start_state),
            end_state=dict(self._end_state),
            steps=list(self._steps),
        )


# ============================================================================
# EVOLUTION MODEL MANAGER
# ============================================================================

class EvolutionModelManager:
    """
    Manager for evolution models and their lifecycle.
    
    Provides operations for creating, updating, and tracking evolution models
    throughout their lifecycle.
    """
    
    def __init__(self):
        self._models: Dict[str, EvolutionModel] = {}
    
    def create_model(
        self,
        model_id: str,
        source_artifact: str,
        target_artifact: str,
        description: str = "",
        evolution_type: EvolutionType = EvolutionType.EVOLUTION,
        phase: EvolutionPhase = EvolutionPhase.PROPOSAL,
        status: EvolutionStatus = EvolutionStatus.PENDING,
        owner: Optional[str] = None,
        governance: EvolutionGovernance = EvolutionGovernance.SEMIAUTO
    ) -> EvolutionModel:
        """Create a new evolution model."""
        model = EvolutionModel(
            id=model_id,
            type=evolution_type,
            phase=phase,
            status=status,
            source_artifact=source_artifact,
            target_artifact=target_artifact,
            description=description,
            owner=owner,
            governance=governance,
        )
        
        self._models[model_id] = model
        return model
    
    def get_model(self, model_id: str) -> Optional[EvolutionModel]:
        """Get an evolution model by ID."""
        return self._models.get(model_id)
    
    def update_status(
        self,
        model_id: str,
        new_phase: EvolutionPhase = None,
        new_status: EvolutionStatus = None
    ) -> bool:
        """Update the phase and/or status of a model."""
        model = self._models.get(model_id)
        
        if not model:
            return False
        
        # Calculate new state
        target_phase = new_phase or model.next_phase()
        
        try:
            updated_model = model.transition_to(target_phase, new_status)
            self._models[model_id] = updated_model
            return True
        except ValueError:
            return False
    
    def list_models(self) -> List[EvolutionModel]:
        """List all evolution models."""
        return list(self._models.values())
    
    def get_pending_models(self) -> List[EvolutionModel]:
        """Get all models with pending status."""
        return [
            m for m in self._models.values()
            if m.status == EvolutionStatus.PENDING
        ]