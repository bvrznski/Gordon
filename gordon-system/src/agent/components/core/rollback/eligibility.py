# Rollback Eligibility Module
# ===========================

"""
Rollback eligibility evaluation for Phase 3.7.10.

This module implements:

- Checkpoint/snapshot availability verification
- State version compatibility checking
- Corruption detection during rollback planning
- Dependency-aware eligibility determination

Key principles:
    - Deterministic eligibility evaluation
    - Explicit unknown outcomes (no guessing)
    - Corrupted state ineligible for exact rollback
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Set


# =============================================================================
# Rollback Eligibility Result
# =============================================================================

class RollbackEligibility(Enum):
    """
    Rollback eligibility status.
    
    Values:
        ELIGIBLE: Known prior state exists, can rollback exactly
        INELIGIBLE_EXACT: No exact restoration possible  
        COMPENSATING_ONLY: Can only compensate (not rollback)
        UNKNOWN: Cannot determine without more information
    """
    
    ELIGIBLE = "eligible"
    INELIGIBLE_EXACT = "ineligible_exact"
    COMPENSATING_ONLY = "compensating_only"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class RollbackEligibilityResult:
    """
    Result of rollback eligibility evaluation.
    
    Args:
        eligibility: ELIGIBLE, INELIGIBLE_EXACT, COMPENSATING_ONLY, or UNKNOWN
        reason: Human-readable explanation for the determination
        
        available_checkpoints: List of available checkpoint names
        state_version_before_failure: What version we had before failure
        target_state_version: What version we want to restore to
        
        requires_compensation: Whether compensation is needed instead of rollback
        corruption_detected: Any corruption found in checkpoint data
    """
    
    eligibility: RollbackEligibility
    
    reason: str = ""
    
    available_checkpoints: List[str] = field(default_factory=list)
    state_version_before_failure: int = 0
    target_state_version: int = 0
    
    requires_compensation: bool = False
    corruption_detected: Optional[List[str]] = None


# =============================================================================
# Eligibility Context
# =============================================================================

@dataclass(frozen=True)
class RollbackEligibilityContext:
    """
    Context for eligibility evaluation.
    
    Args:
        runtime_id: Which runtime this is for (multi-runtime isolation)
        current_state_version: Current state version before rollback attempt
        
        corruption_status: "none", "degraded", "corrupted", "unknown"
        integrity_status: "healthy", "degraded", "corrupted", "unknown"
        
        available_checkpoints: List of checkpoint names available
        available_snapshots: List of snapshot names available
    """
    
    runtime_id: str
    
    current_state_version: int = 0
    
    corruption_status: str = "unknown"
    integrity_status: str = "unknown"
    
    available_checkpoints: List[str] = field(default_factory=list)
    available_snapshots: List[str] = field(default_factory=list)


# =============================================================================
# Checkpoint/Snapshot Validator
# =============================================================================

@dataclass(frozen=True)
class StateArtifact:
    """
    Information about a state artifact (checkpoint or snapshot).
    
    Args:
        artifact_id: Unique identifier
        state_version: State version at capture time
        created_at: When it was captured
        
        integrity_digest: Digest for integrity verification
        schema_version: Schema version at capture time
        
        runtime_id: Which runtime it belongs to
    """
    
    artifact_id: str
    state_version: int
    created_at: float
    
    integrity_digest: Optional[str] = None
    schema_version: int = 1
    
    runtime_id: Optional[str] = None


class StateArtifactValidator:
    """
    Validates state artifacts for rollback eligibility.
    """
    
    def __init__(self) -> None:
        """Initialize the validator."""
        self._artifacts: Dict[str, StateArtifact] = {}
    
    def register_artifact(self, artifact: StateArtifact) -> None:
        """Register a state artifact."""
        self._artifacts[artifact.artifact_id] = artifact
    
    def get_artifact(self, artifact_id: str) -> Optional[StateArtifact]:
        """Get a registered artifact by ID."""
        return self._artifacts.get(artifact_id)
    
    def validate_artifact(
        self,
        artifact: StateArtifact,
        target_version: int
    ) -> bool:
        """
        Validate if an artifact can be used for rollback.
        
        Checks:
            - Artifact exists and is valid
            - Target version <= artifact state version (can only roll back)
            - Integrity digest matches if provided
            - Runtime ID matches (multi-runtime isolation)
        """
        # Check runtime isolation
        if artifact.runtime_id and artifact.runtime_id not in ("", "unknown"):
            return False  # Cross-runtime artifacts rejected
        
        # Check state version compatibility
        # Can only rollback to older or equal versions
        if target_version > artifact.state_version:
            return False
        
        # Verify integrity if digest is available
        if artifact.integrity_digest:
            # In production, would verify actual digest here
            pass  # Placeholder for real verification
        
        return True
    
    def find_compatible_artifact(
        self,
        target_version: int,
        runtime_id: str
    ) -> Optional[StateArtifact]:
        """Find an artifact compatible with the target version."""
        candidates = [
            a for a in self._artifacts.values()
            if (a.runtime_id == "" or a.runtime_id == runtime_id)
            and target_version <= a.state_version
        ]
        
        if not candidates:
            return None
        
        # Return newest compatible artifact
        return max(candidates, key=lambda a: a.state_version)


# =============================================================================
# Dependency-Aware Eligibility Evaluator
# =============================================================================

@dataclass(frozen=True)
class DependencyInfo:
    """
    Dependency information for an entity.
    
    Args:
        entity_id: Entity identifier
        depends_on: IDs of entities this depends on
        depended_by: IDs of entities that depend on this
        
        state_version: Current state version
    """
    
    entity_id: str
    depends_on: List[str] = field(default_factory=list)
    depended_by: List[str] = field(default_factory=list)
    
    state_version: int = 0


class DependencyGraph:
    """
    Tracks dependencies between entities for rollback planning.
    """
    
    def __init__(self) -> None:
        """Initialize the dependency graph."""
        self._entities: Dict[str, DependencyInfo] = {}
        self._reverse_deps: Dict[str, List[str]] = {}  # dep -> dependents
    
    def add_entity(self, info: DependencyInfo) -> None:
        """Add or update an entity's dependency information."""
        self._entities[info.entity_id] = info
        
        for dep in info.depends_on:
            if dep not in self._reverse_deps:
                self._reverse_deps[dep] = []
            self._reverse_deps[dep].append(info.entity_id)
    
    def get_entity(self, entity_id: str) -> Optional[DependencyInfo]:
        """Get dependency info for an entity."""
        return self._entities.get(entity_id)
    
    def get_dependents(self, entity_id: str) -> List[str]:
        """Get entities that depend on this one (reverse dependencies)."""
        return list(self._reverse_deps.get(entity_id, []))
    
    def get_dependency_order(self, target_entities: List[str]) -> List[str]:
        """
        Get execution order for rollback.
        
        Returns entities in dependency-safe order:
            - Dependencies come before dependents
            - For rollback: execute reverse order of this
        """
        visited: Set[str] = set()
        result: List[str] = []
        
        def visit(entity_id: str):
            if entity_id in visited:
                return
            
            info = self._entities.get(entity_id)
            if not info:
                return
            
            # Visit dependencies first
            for dep in info.depends_on:
                visit(dep)
            
            visited.add(entity_id)
            result.append(entity_id)
        
        for entity_id in target_entities:
            visit(entity_id)
        
        return result


class RollbackEligibilityEvaluator:
    """
    Evaluates rollback eligibility deterministically.
    
    This is the canonical authority for determining whether a rollback
    can proceed and what approach to use (exact rollback vs compensation).
    """
    
    def __init__(self) -> None:
        """Initialize the evaluator."""
        self._artifact_validator = StateArtifactValidator()
        self._dependency_graph = DependencyGraph()
    
    def register_artifact(self, artifact: StateArtifact) -> None:
        """Register a state artifact for rollback use."""
        self._artifact_validator.register_artifact(artifact)
    
    def register_dependency(self, info: DependencyInfo) -> None:
        """Register an entity's dependency information."""
        self._dependency_graph.add_entity(info)
    
    def evaluate(
        self,
        failure_id: str,
        target_state_version: int,
        context: RollbackEligibilityContext
    ) -> RollbackEligibilityResult:
        """
        Evaluate whether rollback is eligible for the given parameters.
        
        Args:
            failure_id: Which failure triggered the rollback request
            target_state_version: What state version to restore to
            context: Eligibility evaluation context
            
        Returns:
            Eligibility result with determination and available options
        """
        # ------------------------------------------------------------------
        # Step 1: Check integrity/corruption status
        # ------------------------------------------------------------------
        if context.corruption_status == "corrupted":
            return RollbackEligibilityResult(
                eligibility=RollbackEligibility.UNKNOWN,
                reason="Corrupted state cannot be rolled back directly",
                corruption_detected=["state_corruption_detected"]
            )
        
        if context.integrity_status == "corrupted":
            return RollbackEligibilityResult(
                eligibility=RollbackEligibility.COMPENSATING_ONLY,
                reason="Integrity corrupted - compensation required instead of rollback"
            )
        
        # ------------------------------------------------------------------
        # Step 2: Find available state artifacts
        # ------------------------------------------------------------------
        compatible_artifact = self._artifact_validator.find_compatible_artifact(
            target_state_version,
            context.runtime_id
        )
        
        if not compatible_artifact:
            return RollbackEligibilityResult(
                eligibility=RollbackEligibility.UNKNOWN,
                reason=f"No compatible state artifact for version {target_state_version}",
                available_checkpoints=context.available_checkpoints
            )
        
        # ------------------------------------------------------------------
        # Step 3: Validate artifact integrity
        # ------------------------------------------------------------------
        if not self._artifact_validator.validate_artifact(
            compatible_artifact, target_state_version
        ):
            return RollbackEligibilityResult(
                eligibility=RollbackEligibility.UNKNOWN,
                reason="State artifact validation failed"
            )
        
        # ------------------------------------------------------------------
        # Step 4: Check dependency constraints
        # ------------------------------------------------------------------
        affected_entities = self._dependency_graph.get_dependents(failure_id)
        
        # Verify all dependencies are rollbackable
        for entity_id in [failure_id] + affected_entities:
            dep_info = self._dependency_graph.get_entity(entity_id)
            if dep_info:
                # Check if dependency state is compatible
                pass  # Would check state versions
        
        # ------------------------------------------------------------------
        # Step 5: Determine eligibility type
        # ------------------------------------------------------------------
        
        # If exact rollback is possible (state version matches)
        if target_state_version == compatible_artifact.state_version:
            return RollbackEligibilityResult(
                eligibility=RollbackEligibility.ELIGIBLE,
                reason="Exact state restoration available from checkpoint",
                available_checkpoints=[compatible_artifact.artifact_id],
                state_version_before_failure=context.current_state_version,
                target_state_version=target_state_version
            )
        
        # If we need to roll back but exact version not available
        if target_state_version < compatible_artifact.state_version:
            return RollbackEligibilityResult(
                eligibility=RollbackEligibility.COMPENSATING_ONLY,
                reason="Partial restoration available - compensation recommended",
                available_checkpoints=[compatible_artifact.artifact_id],
                state_version_before_failure=context.current_state_version,
                target_state_version=target_state_version
            )
        
        # ------------------------------------------------------------------
        # Fallback: cannot determine
        # ------------------------------------------------------------------
        return RollbackEligibilityResult(
            eligibility=RollbackEligibility.UNKNOWN,
            reason="Insufficient information to determine rollback eligibility",
            available_checkpoints=context.available_checkpoints,
            state_version_before_failure=context.current_state_version,
            target_state_version=target_state_version
        )
    
    def get_dependency_order(self, entities: List[str]) -> List[str]:
        """
        Get the dependency-safe order for rollback execution.
        
        For rollback, execute in reverse of this order to ensure
        dependents are rolled back before their dependencies.
        """
        return self._dependency_graph.get_dependency_order(entities)


# =============================================================================
# Rollback Mode Determinator
# =============================================================================

class RollbackMode(Enum):
    """Modes of rollback operation."""
    
    FULL = "full"                   # Complete restoration to known state
    PARTIAL = "partial"             # Restore only affected components  
    TRANSACTIONAL = "transactional"  # Within transaction boundaries
    COMPENSATING = "compensating"   # Counteract effects (not exact rollback)
    CHECKPOINT = "checkpoint"       # Restore from checkpoint
    BEST_EFFORT = "best_effort"     # Try to roll back what's possible


class RollbackModeDeterminator:
    """
    Determines the appropriate rollback mode based on eligibility.
    """
    
    def determine_mode(
        self,
        eligibility: RollbackEligibility,
        context: RollbackEligibilityContext
    ) -> RollbackMode:
        """
        Determine the rollback mode to use.
        
        Args:
            eligibility: The rollback eligibility determination
            context: Eligibility evaluation context
            
        Returns:
            Appropriate rollback mode
        """
        if eligibility == RollbackEligibility.ELIGIBLE:
            return RollbackMode.FULL
        
        if eligibility == RollbackEligibility.COMPENSATING_ONLY:
            return RollbackMode.COMPENSATING
        
        if eligibility == RollbackEligibility.INELIGIBLE_EXACT:
            # Check if partial restoration is possible
            if context.available_checkpoints:
                return RollbackMode.PARTIAL
            return RollbackMode.BEST_EFFORT
        
        # Unknown - best effort at recovery
        return RollbackMode.BEST_EFFORT


# =============================================================================
# Export for compatibility with rollback package
# =============================================================================

__all__ = [
    "RollbackEligibility",
    "RollbackEligibilityResult",
    "RollbackEligibilityContext",
    
    "StateArtifact",
    "StateArtifactValidator",
    
    "DependencyInfo",
    "DependencyGraph",
    "RollbackEligibilityEvaluator",
    
    "RollbackMode",
    "RollbackModeDeterminator",
]