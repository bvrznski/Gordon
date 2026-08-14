# Gordon Core: Evolution Foundations (Phase 3.33)
"""
Evolution Philosophy and Terminology

This module establishes the foundational concepts for all evolution activities
in the Gordon Core.
"""

from enum import Enum, auto
from typing import Final, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime


# ============================================================================
# EVOLUTION TYPE ENUMERATION
# ============================================================================

class EvolutionType(Enum):
    """
    Canonical classification of evolution types.
    
    Each evolution type represents a distinct architectural change category:
    
    - EVOLUTION: Architectural change while preserving identity
    - MODERNIZATION: Upgrade to newer patterns/technologies without functional change
    - UPGRADE: Replacement with newer version maintaining compatibility
    - MIGRATION: Movement between contexts (runtime, package, module)
    - REPLACEMENT: Complete replacement with different implementation
    - COMPATIBILITY: Change that preserves continuity across versions
    - DEPRECATION: Controlled retirement of artifacts
    - SCHEMA: Evolution of data structures and formats
    - INTERFACE: Evolution of public interfaces and contracts
    - CAPABILITY: Evolution of capability implementations
    """
    
    EVOLUTION = auto()          # Architectural change preserving identity
    MODERNIZATION = auto()      # New patterns without functional change
    UPGRADE = auto()            # Version replacement maintaining compatibility
    MIGRATION = auto()          # Context movement (runtime/package/module)
    REPLACEMENT = auto()        # Complete implementation replacement
    COMPATIBILITY = auto()      # Continuity-preserving changes
    DEPRECATION = auto()        # Controlled artifact retirement
    SCHEMA = auto()             # Data structure evolution
    INTERFACE = auto()          # Interface and contract evolution
    CAPABILITY = auto()         # Capability implementation evolution


# ============================================================================
# EVOLUTION PHASE ENUMERATION
# ============================================================================

class EvolutionPhase(Enum):
    """
    Canonical evolution lifecycle phases.
    
    Every architectural evolution must follow this sequence:
    1. Proposal - Initial request for change
    2. Analysis - Architectural impact assessment
    3. Impact - Detailed impact analysis
    4. Dependencies - Dependency graph analysis
    5. Validation - Compatibility verification
    6. Risk - Formal risk assessment
    7. Planning - Implementation plan creation
    8. Approval - Governance approval
    9. Preparation - Migration preparation
    10. Execution - Upgrade/migration execution
    11. Verification - Post-execution validation
    12. Remediation - Automatic correction if needed
    13. Validation - Repository-wide validation
    14. Certification - Formal certification
    15. Archival - Record preservation
    """
    
    PROPOSAL = auto()           # Initial request for change
    ANALYSIS = auto()           # Architectural impact assessment
    IMPACT = auto()             # Detailed impact analysis
    DEPENDENCIES = auto()       # Dependency graph analysis
    VALIDATION = auto()         # Compatibility verification
    RISK = auto()               # Formal risk assessment
    PLANNING = auto()           # Implementation plan creation
    APPROVAL = auto()           # Governance approval
    PREPARATION = auto()        # Migration preparation
    EXECUTION = auto()          # Upgrade/migration execution
    VERIFICATION = auto()       # Post-execution validation
    REMEDIATION = auto()        # Automatic correction if needed
    REVALIDATION = auto()       # Repository-wide validation
    CERTIFICATION = auto()      # Formal certification
    ARCHIVAL = auto()           # Record preservation


# ============================================================================
# EVOLUTION STATUS ENUMERATION
# ============================================================================

class EvolutionStatus(Enum):
    """
    Canonical evolution status values.
    
    Status transitions follow this flow:
    PENDING → IN_PROGRESS → BLOCKED/COMPLETING → COMPLETED/FAILED/REVERSED
    
    A status can only move forward through this state machine unless explicitly
    reversed via a controlled rollback operation.
    """
    
    # Initial states
    PROPOSED = auto()           # Request submitted, awaiting analysis
    PENDING = auto()            # Ready for processing
    INITIAL = auto()            # Initial state
    
    # Active states
    IN_PROGRESS = auto()        # Actively being processed
    BLOCKED = auto()            # Waiting on external dependencies
    
    # Completion states
    COMPLETING = auto()         # Final validation phase
    COMPLETED = auto()          # Successfully completed
    FAILED = auto()             # Execution failed
    REVERSED = auto()           # Rolled back to previous state


# ============================================================================
# EVOLUTION GOVERNANCE MODEL
# ============================================================================

class EvolutionGovernance(Enum):
    """
    Governance controls for evolution activities.
    
    Controls determine how evolution activities are managed:
    - AUTO: Fully automated, no human intervention required
    - SEMIAUTO: Automated with optional human oversight
    - MANUAL: Requires explicit human approval
    
    Every evolution activity must specify its governance model before execution.
    """
    
    AUTO = auto()               # Fully automatic (safe changes only)
    SEMIAUTO = auto()           # Automatic with human review option
    MANUAL = auto()             # Explicit human approval required


# ============================================================================
# EVOLUTION PRINCIPLES
# ============================================================================

EVOLUTION_PRINCIPLES: Final[List[str]] = [
    "One canonical evolution architecture throughout repository",
    "All evolution must be explicit, governed, and auditable",
    "No silent or accidental evolution is permitted",
    "Evidence must be preserved for all evolutionary events",
    "Evolution shall preserve architectural integrity",
    "Compatibility shall be continuously validated",
    "Deprecation shall follow governed lifecycle policies",
    "Architectural drift shall never remain undetected",
]


# ============================================================================
# EVOLUTION LIFECYCLE
# ============================================================================

@dataclass(frozen=True)
class EvolutionLifecycle:
    """
    Immutable evolution lifecycle model.
    
    Represents the complete lifecycle of an evolutionary event from proposal
    through certification and archival.
    """
    
    # Lifecycle phases in order
    PHASES: Final[tuple] = (
        EvolutionPhase.PROPOSAL,
        EvolutionPhase.ANALYSIS,
        EvolutionPhase.IMPACT,
        EvolutionPhase.DEPENDENCIES,
        EvolutionPhase.VALIDATION,
        EvolutionPhase.RISK,
        EvolutionPhase.PLANNING,
        EvolutionPhase.APPROVAL,
        EvolutionPhase.PREPARATION,
        EvolutionPhase.EXECUTION,
        EvolutionPhase.VERIFICATION,
        EvolutionPhase.REMEDIATION,
        EvolutionPhase.REVALIDATION,
        EvolutionPhase.CERTIFICATION,
        EvolutionPhase.ARCHIVAL,
    )
    
    # Initial status for lifecycle
    INITIAL_STATUS: Final = EvolutionStatus.PENDING
    
    # Terminal statuses (cannot transition out of)
    TERMINAL_STATUSES: Final = (
        EvolutionStatus.COMPLETED,
        EvolutionStatus.FAILED,
        EvolutionStatus.REVERSED,
    )


# ============================================================================
# EVOLUTION IDENTIFIER MODEL
# ============================================================================

@dataclass(frozen=True)
class EvolutionIdentifier:
    """
    Immutable identifier for evolution artifacts.
    
    Every evolution artifact must have a unique, immutable identifier that
    persists throughout its lifecycle including migration and upgrade events.
    """
    
    # Identifier components
    type: str                     # Evolution type name (e.g., "module", "interface")
    name: str                     # Artifact name
    version_from: str            # Source version (can be None for new artifacts)
    version_to: str              # Target version (can be None for deletions)
    
    @property
    def id(self) -> str:
        """Generate unique identifier string."""
        return f"{self.type}:{self.name}@{self.version_from or '0.0.0'}→{self.version_to or '0.0.0'}"
    
    @classmethod
    def from_string(cls, identifier: str) -> "EvolutionIdentifier":
        """Parse identifier from string format."""
        type_name, version_part = identifier.split(":", 1)
        name_version = version_part.split("@", 1)
        name = name_version[0]
        
        if len(name_version) > 1:
            versions = name_version[1].split("→")
            return cls(
                type=type_name,
                name=name,
                version_from=versions[0] if len(versions) > 0 else None,
                version_to=versions[1] if len(versions) > 1 else None
            )
        
        return cls(type=type_name, name=name, version_from=None, version_to=None)


# ============================================================================
# EVOLUTION ARTIFACT MODEL
# ============================================================================

@dataclass(frozen=True)
class EvolutionArtifact:
    """
    Immutable representation of an evolution artifact.
    
    Artifacts are the entities that can undergo evolution (modules, interfaces,
    schemas, configurations, etc.).
    """
    
    # Artifact identity
    identifier: EvolutionIdentifier
    
    # Artifact properties
    origin: str                  # Original source/repository
    current_state: Dict[str, Any]  # Current state snapshot
    target_state: Dict[str, Any]   # Target state after evolution
    
    # Evolution context
    phase: EvolutionPhase
    status: EvolutionStatus
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def is_new(self) -> bool:
        """Check if artifact is newly created."""
        return self.identifier.version_from is None
    
    @property
    def is_deletion(self) -> bool:
        """Check if artifact is being removed."""
        return self.identifier.version_to is None
    
    @property
    def is_migration(self) -> bool:
        """Check if artifact is being migrated (version unchanged, context changed)."""
        return (
            self.identifier.version_from == self.identifier.version_to and
            self.origin != self.target_state.get("origin", "")
        )
    
    @property
    def is_upgrade(self) -> bool:
        """Check if artifact is being upgraded (version changed)."""
        return (
            self.identifier.version_from != self.identifier.version_to and
            self.identifier.version_from is not None and
            self.identifier.version_to is not None
        )


# ============================================================================
# EVOLUTION RELATIONSHIP MODEL
# ============================================================================

@dataclass(frozen=True)
class EvolutionRelationship:
    """
    Immutable relationship between evolution artifacts.
    
    Relationships define dependencies, replacements, and compatibility bridges
    between evolutionary artifacts.
    """
    
    # Relationship types
    class Type(Enum):
        DEPENDENCY = auto()      # Artifact A depends on B
        REPLACEMENT = auto()     # Artifact A is replaced by B
        COMPATIBILITY = auto()   # A and B are compatible
        EXTENSION = auto()       # B extends A's functionality
        DEPRECATION = auto()     # A is deprecated in favor of B
    
    source: str                   # Source artifact identifier
    target: str                   # Target artifact identifier
    relationship_type: Type      # Type of relationship
    strength: float              # Strength of relationship (0.0 to 1.0)
    metadata: Dict[str, Any] = field(default_factory=dict)


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
    
    # Path components
    start_state: Dict[str, Any]
    end_state: Dict[str, Any]
    steps: List[EvolutionArtifact] = field(default_factory=list)
    
    @property
    def is_complete(self) -> bool:
        """Check if path has reached terminal state."""
        return (
            len(self.steps) > 0 and 
            self.steps[-1].status in EvolutionLifecycle.TERMINAL_STATUSES
        )
    
    @property
    def current_phase(self) -> EvolutionPhase:
        """Get the current phase of evolution."""
        return self.steps[-1].phase if self.steps else EvolutionPhase.PROPOSAL


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_evolution_type(evolution_type: str) -> EvolutionType:
    """Validate and convert string to EvolutionType enum."""
    try:
        return EvolutionType[evolution_type.upper().replace("-", "_")]
    except KeyError:
        raise ValueError(f"Invalid evolution type: {evolution_type}")


def validate_evolution_phase(phase: EvolutionPhase) -> bool:
    """
    Validate that a phase is in correct lifecycle order.
    
    Returns True if the phase follows the canonical lifecycle.
    """
    valid_phases = EvolutionLifecycle.PHASES
    return phase in valid_phases


def determine_evolution_status(phase: EvolutionPhase, success: bool) -> EvolutionStatus:
    """Determine status based on phase and execution result."""
    if phase == EvolutionPhase.EXECUTION:
        return EvolutionStatus.COMPLETED if success else EvolutionStatus.FAILED
    
    if phase in (EvolutionPhase.PROPOSAL, EvolutionPhase.PENDING):
        return EvolutionStatus.IN_PROGRESS
    
    return EvolutionStatus.COMPLETING


def get_evolution_governance(evolution_type: EvolutionType) -> EvolutionGovernance:
    """Determine required governance level for evolution type."""
    # High-risk evolutions require manual approval
    high_risk_types = {
        EvolutionType.REPLACEMENT,
        EvolutionType.MIGRATION,
    }
    
    if evolution_type in high_risk_types:
        return EvolutionGovernance.MANUAL
    
    return EvolutionGovernance.SEMIAUTO


def create_evolution_identifier(
    type_name: str,
    name: str,
    version_from: str = None,
    version_to: str = None
) -> EvolutionIdentifier:
    """Create a new evolution identifier."""
    return EvolutionIdentifier(
        type=type_name,
        name=name,
        version_from=version_from,
        version_to=version_to
    )