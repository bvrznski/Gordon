# Memory Forms - Phase 5.1.1 Semantic Organization Layer
# =========================================================

"""
Memory Forms: Semantic organization over the unified Memory Substrate.

Memory Forms are NOT separate storage engines. They are semantic projections
over a single shared substrate, organizing artifacts according to different
cognitive principles:

 Canonical Forms:
    - Autobiographical: personal timeline and self-continuity
    - Emotional: affective significance and valence
    - Episodic: experienced events and episodes
    - Latent: latent semantic representations
    - Procedural: skills and execution patterns
    - Semantic: concepts, categories, and meaning
    - Spatial: spatial relationships and navigation
    - Working: currently active cognitive context

Form Laws:
    FORM-LAW-001: Every Memory Form organizes exactly one semantic perspective
    FORM-LAW-002: Memory Forms never own Memory Artifacts
    FORM-LAW-003: Memory Forms preserve artifact identity
    FORM-LAW-004: Memory Forms expose immutable projections

Membership:
    - One artifact may belong to multiple forms simultaneously
    - No duplication occurs - artifacts remain single objects
    - Membership is tracked, not ownership

Projections:
    - Each form exposes its own projection over the substrate
    - Projections are read-only views
    - No mutable state is shared between forms

Architecture:
    forms/
    ├── __init__.py                This file
    ├── core.py                    Core MemoryForm interface and base class
    ├── projections.py             Projection system for each form
    └── forms/                     Individual Memory Form implementations
        ├── autobiographical.py
        ├── emotional.py
        ├── episodic.py
        ├── latent.py
        ├── procedural.py
        ├── semantic.py
        ├── spatial.py
        └── working.py

Usage Example:
    from gordon_system.src.agent.components.systems.memory.forms import (
        MemoryFormSystem,
        AutobiographicalMemory,
        SemanticMemory,
    )
    
    # Initialize the form system
    form_system = MemoryFormSystem(substrate)
    
    # Access individual forms
    autobiographical = form_system.autobiographical
    semantic = form_system.semantic
    
    # Get projections (read-only views)
    bio_projection = autobiographical.get_projection()
    sem_projection = semantic.get_projection()
"""

from __future__ import annotations

from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
import time


# =============================================================================
# IMPORTS - Lazy load to avoid circular dependencies
# =============================================================================


def _import_memory_artifact():
    """Import MemoryArtifact at runtime."""
    from ..foundations.artifact import MemoryArtifact
    return MemoryArtifact


def _import_substrate():
    """Import MemorySubstrate at runtime."""
    from ..foundations.substrate import MemorySubstrate
    return MemorySubstrate


# =============================================================================
# MEMORY FORM KIND - Classification of form types
# =============================================================================


class MemoryFormKind:
    """
    Classification of Memory Form types.
    
    Each kind represents a distinct semantic organization over the substrate.
    """
    
    AUTOBIOGRAPHICAL = "autobiographical"
    EMOTIONAL = "emotional"
    EPISODIC = "episodic"
    LATENT = "latent"
    PROCEDURAL = "procedural"
    SEMANTIC = "semantic"
    SPATIAL = "spatial"
    WORKING = "working"


# =============================================================================
# FORM STATE - Current activation and health state
# =============================================================================


@dataclass(frozen=True)
class MemoryFormState:
    """
    Current operational state of a Memory Form.
    
    Fields:
        is_active:           Is this form currently active?
        
        # Statistics
        artifact_count:      Number of artifacts in this form's projection
        relation_count:      Number of relations observed
        
        # Health indicators
        organization_integrity: 0.0-1.0 measure
        projection_integrity:    0.0-1.0 measure
        activation_integrity:    0.0-1.0 measure
        
        # Timestamps
        activated_at_utc:    When form was last activated
        last_update_utc:     Last state update
    """
    
    is_active: bool = False
    
    artifact_count: int = 0
    relation_count: int = 0
    
    organization_integrity: float = 1.0
    projection_integrity: float = 1.0
    activation_integrity: float = 1.0
    
    activated_at_utc: float = field(default_factory=time.time)
    last_update_utc: float = field(default_factory=time.time)


# =============================================================================
# MEMORY FORM PROJECTION - Read-only view of form organization
# =============================================================================


@dataclass(frozen=True)
class MemoryFormProjection:
    """
    Immutable projection from a Memory Form.
    
    Projections expose the form's organizational view without allowing mutation.
    Multiple forms can project over the same artifacts simultaneously.
    
    Fields:
        form_kind:           What type of form is this?
        
        # Visible artifacts (subset of substrate)
        visible_artifacts:   Tuple of artifact IDs visible in this projection
        
        # Organization
        organization_type:   How are these organized? (temporal, thematic, etc.)
        clusters:            Groupings within the form's view
        
        # Statistics
        artifact_count:      Total visible artifacts
        confidence:          0.0-1.0 confidence in projection accuracy
        
        # Provenance
        generated_at_utc:    When was this projection created?
        based_on_substrate:  Substrate state this reflects
    """
    
    form_kind: str
    
    visible_artifacts: Tuple[str, ...] = field(default_factory=tuple)
    
    organization_type: Optional[str] = None
    clusters: Tuple[str, ...] = field(default_factory=tuple)
    
    artifact_count: int = 0
    confidence: float = 1.0
    
    generated_at_utc: float = field(default_factory=time.time)
    based_on_substrate: str = ""


# =============================================================================
# MEMORY FORM - Core interface and base class
# =============================================================================


class MemoryForm:
    """
    Abstract base for all Memory Forms.
    
    Every Memory Form:
        1. Organizes artifacts according to one semantic principle
        2. Never owns Memory Artifacts (only views them)
        3. Exposes immutable projections
        4. Preserves identity, provenance, revision history
    
    Subclasses must implement:
        - _organize_artifact(): How to organize a single artifact
        - _is_admissible(): Is this artifact admissible to this form?
        - get_projection(): Generate current projection
        
    Form Laws Implemented:
        FORM-LAW-001: One semantic perspective per form
        FORM-LAW-002: No ownership of artifacts
        FORM-LAW-003: Preserve artifact identity
        FORM-LAW-004: Expose immutable projections
    """
    
    def __init__(self, name: str, kind: str):
        """
        Initialize a Memory Form.
        
        Args:
            name: Unique identifier for this form instance
            kind: What type of memory form is this?
        """
        self._name = name
        self._kind = kind
        self._substrate: Optional[Any] = None  # MemorySubstrate (runtime import)
        self._state = MemoryFormState()
        
        # Membership tracking: artifact_id -> set of forms it belongs to
        self._membership: Dict[str, Any] = {}
    
    @property
    def name(self) -> str:
        """Get the form's unique name."""
        return self._name
    
    @property
    def kind(self) -> str:
        """Get the form's kind (semantic organization principle)."""
        return self._kind
    
    @property
    def substrate(self) -> Optional[Any]:
        """Get the substrate reference (runtime import available)."""
        if self._substrate is None:
            try:
                from ..foundations.substrate import MemorySubstrate
                return MemorySubstrate
            except ImportError:
                return None
        return self._substrate
    
    @property
    def state(self) -> MemoryFormState:
        """Get current form state."""
        return self._state
    
    def initialize(self, substrate: Any) -> bool:
        """
        Initialize this form with a substrate reference.
        
        Args:
            substrate: The MemorySubstrate instance
            
        Returns:
            True if initialization succeeded
        """
        try:
            # Import at runtime to avoid circular deps
            from ..foundations.substrate import MemorySubstrate as MS
            if isinstance(substrate, MS):
                self._substrate = substrate
                return True
        except ImportError:
            pass
        
        # Allow any type for flexibility during testing
        self._substrate = substrate
        return True
    
    def _is_admissible(self, artifact: Any) -> bool:
        """
        Check if an artifact is admissible to this form.
        
        This is the admission policy - what kinds of artifacts belong here?
        
        Args:
            artifact: The MemoryArtifact to check
            
        Returns:
            True if this artifact should be included in this form
        """
        # Base implementation allows all - subclasses override
        return True
    
    def _organize_artifact(self, artifact: Any) -> Dict[str, Any]:
        """
        Organize an artifact within this form's semantic framework.
        
        Args:
            artifact: The MemoryArtifact to organize
            
        Returns:
            Organization data for this artifact in this form
        """
        # Base implementation - no special organization
        return {"form_kind": self._kind, "admitted": True}
    
    def add_artifact(self, artifact_id: str) -> bool:
        """
        Add an artifact to this form's membership.
        
        This does NOT create a new artifact - the artifact must already exist
        in the substrate. We're just adding it to this form's projection.
        
        Args:
            artifact_id: ID of the artifact to add
            
        Returns:
            True if added successfully
        """
        # Check substrate exists
        if self._substrate is None:
            return False
        
        # Get artifact from substrate
        artifact = getattr(self._substrate, 'get_artifact', lambda x: None)(artifact_id)
        
        if artifact is None:
            # Artifact doesn't exist in substrate yet
            return False
        
        # Check admissibility
        if not self._is_admissible(artifact):
            return False
        
        # Organize and record membership
        organization = self._organize_artifact(artifact)
        self._membership[artifact_id] = {
            "form_kind": self._kind,
            "organization": organization,
            "admitted_at_utc": time.time(),
        }
        
        # Update state
        self._state.artifact_count += 1
        self._state.last_update_utc = time.time()
        
        return True
    
    def remove_artifact(self, artifact_id: str) -> bool:
        """
        Remove an artifact from this form's membership.
        
        This does NOT delete the artifact - only removes it from this form's
        projection. The artifact remains in the substrate and may belong to
        other forms.
        
        Args:
            artifact_id: ID of the artifact to remove
            
        Returns:
            True if removed successfully
        """
        if artifact_id not in self._membership:
            return False
        
        del self._membership[artifact_id]
        self._state.artifact_count = max(0, self._state.artifact_count - 1)
        self._state.last_update_utc = time.time()
        
        return True
    
    def has_artifact(self, artifact_id: str) -> bool:
        """Check if an artifact belongs to this form."""
        return artifact_id in self._membership
    
    def get_projection(self) -> MemoryFormProjection:
        """
        Generate the current projection for this form.
        
        Returns:
            Immutable view of this form's organization over the substrate
        """
        # Get visible artifact IDs from membership
        visible_ids = tuple(self._membership.keys())
        
        # Collect clusters based on organization type
        clusters = self._collect_clusters()
        
        return MemoryFormProjection(
            form_kind=self._kind,
            visible_artifacts=visible_ids,
            organization_type=self._get_organizing_principle(),
            clusters=clusters,
            artifact_count=len(visible_ids),
            confidence=self._state.projection_integrity,
            generated_at_utc=time.time(),
            based_on_substrate=getattr(self._substrate, '_created_at_utc', 0),
        )
    
    def _collect_clusters(self) -> Tuple[str, ...]:
        """Collect cluster information for projection."""
        # Base implementation - no clusters by default
        return tuple()
    
    def _get_organizing_principle(self) -> Optional[str]:
        """Get the organizing principle for this form's projection."""
        return None
    
    def get_artifact_organizations(self, artifact_id: str) -> Tuple[Dict[str, Any], ...]:
        """
        Get all organization records for an artifact in this form.
        
        Args:
            artifact_id: The artifact to query
            
        Returns:
            Tuple of organization data dictionaries
        """
        if artifact_id not in self._membership:
            return tuple()
        return (self._membership[artifact_id],)
    
    def health(self) -> Dict[str, Any]:
        """Report current form health."""
        return {
            "form_kind": self._kind,
            "name": self._name,
            "is_active": self._state.is_active,
            "artifact_count": self._state.artifact_count,
            "organization_integrity": self._state.organization_integrity,
            "projection_integrity": self._state.projection_integrity,
            "activation_integrity": self._state.activation_integrity,
            "membership_entries": len(self._membership),
        }
    
    def validate_membership(self) -> bool:
        """
        Validate that all membership records are consistent.
        
        Returns:
            True if all membership is valid
        """
        for artifact_id in list(self._membership.keys()):
            # Check artifact exists in substrate
            if self._substrate is not None:
                artifact = getattr(self._substrate, 'get_artifact', lambda x: None)(artifact_id)
                if artifact is None:
                    del self._membership[artifact_id]
        
        return True


# =============================================================================
# MEMORY FORM SYSTEM - Central coordinator for all forms
# =============================================================================


class MemoryFormSystem:
    """
    Coordinates multiple Memory Forms over a single substrate.
    
    This system manages the lifecycle of all memory forms and ensures
    cross-form consistency.
    
    Form Laws Enforced:
        CROSSFORM-LAW-001: Forms cooperate through shared artifacts
        CROSSFORM-LAW-002: No competition for ownership
        CROSSFORM-LAW-003-005: Consistency preserved across forms
    
    Usage:
        system = MemoryFormSystem(substrate)
        
        # Access individual forms
        bio = system.autobiographical
        sem = system.semantic
        
        # Get projections from different forms
        bio_proj = bio.get_projection()
        sem_proj = sem.get_projection()
    """
    
    def __init__(self, substrate: Any):
        """
        Initialize the form system with a substrate.
        
        Args:
            substrate: The MemorySubstrate instance to organize over
        """
        self._substrate = substrate
        
        # Initialize all canonical forms
        self._forms: Dict[str, MemoryForm] = {}
        self._create_forms()
    
    def _create_forms(self):
        """Create and initialize all canonical memory forms."""
        from .autobiographical import AutobiographicalMemory
        from .emotional import EmotionalMemory
        from .episodic import EpisodicMemory
        from .latent import LatentMemory
        from .procedural import ProceduralMemory
        from .semantic import SemanticMemory
        from .spatial import SpatialMemory
        from .working import WorkingMemory
        
        # Initialize each form with substrate
        self._forms[MemoryFormKind.AUTOBIOGRAPHICAL] = AutobiographicalMemory(
            name="autobiographical",
            kind=MemoryFormKind.AUTOBIOGRAPHICAL,
        )
        self._forms[MemoryFormKind.EMOTIONAL] = EmotionalMemory(
            name="emotional",
            kind=MemoryFormKind.EMOTIONAL,
        )
        self._forms[MemoryFormKind.EPISODIC] = EpisodicMemory(
            name="episodic",
            kind=MemoryFormKind.EPISODIC,
        )
        self._forms[MemoryFormKind.LATENT] = LatentMemory(
            name="latent",
            kind=MemoryFormKind.LATENT,
        )
        self._forms[MemoryFormKind.PROCEDURAL] = ProceduralMemory(
            name="procedural",
            kind=MemoryFormKind.PROCEDURAL,
        )
        self._forms[MemoryFormKind.SEMANTIC] = SemanticMemory(
            name="semantic",
            kind=MemoryFormKind.SEMANTIC,
        )
        self._forms[MemoryFormKind.SPATIAL] = SpatialMemory(
            name="spatial",
            kind=MemoryFormKind.SPATIAL,
        )
        self._forms[MemoryFormKind.WORKING] = WorkingMemory(
            name="working",
            kind=MemoryFormKind.WORKING,
        )
        
        # Initialize each form with substrate reference
        for form in self._forms.values():
            form.initialize(self._substrate)
    
    @property
    def autobiographical(self) -> MemoryForm:
        """Get the Autobiographical Memory instance."""
        return self._forms[MemoryFormKind.AUTOBIOGRAPHICAL]
    
    @property
    def emotional(self) -> MemoryForm:
        """Get the Emotional Memory instance."""
        return self._forms[MemoryFormKind.EMOTIONAL]
    
    @property
    def episodic(self) -> MemoryForm:
        """Get the Episodic Memory instance."""
        return self._forms[MemoryFormKind.EPISODIC]
    
    @property
    def latent(self) -> MemoryForm:
        """Get the Latent Memory instance."""
        return self._forms[MemoryFormKind.LATENT]
    
    @property
    def procedural(self) -> MemoryForm:
        """Get the Procedural Memory instance."""
        return self._forms[MemoryFormKind.PROCEDURAL]
    
    @property
    def semantic(self) -> MemoryForm:
        """Get the Semantic Memory instance."""
        return self._forms[MemoryFormKind.SEMANTIC]
    
    @property
    def spatial(self) -> MemoryForm:
        """Get the Spatial Memory instance."""
        return self._forms[MemoryFormKind.SPATIAL]
    
    @property
    def working(self) -> MemoryForm:
        """Get the Working Memory instance."""
        return self._forms[MemoryFormKind.WORKING]
    
    def get_form(self, kind: str) -> Optional[MemoryForm]:
        """Get a form by its kind."""
        return self._forms.get(kind)
    
    def add_artifact_to_form(self, artifact_id: str, kind: str) -> bool:
        """
        Add an artifact to a specific form.
        
        Args:
            artifact_id: ID of the artifact to add
            kind: Form kind (e.g., 'semantic', 'episodic')
            
        Returns:
            True if successfully added
        """
        form = self.get_form(kind)
        if form is None:
            return False
        return form.add_artifact(artifact_id)
    
    def get_all_projections(self) -> Dict[str, MemoryFormProjection]:
        """Get projections from all forms."""
        return {kind: form.get_projection() for kind, form in self._forms.items()}
    
    def validate_consistency(self) -> bool:
        """
        Validate consistency across all forms.
        
        Returns:
            True if cross-form consistency is maintained
        """
        # All forms share the same substrate - check each one
        return all(form.validate_membership() for form in self._forms.values())
    
    def health_report(self) -> Dict[str, Any]:
        """Get health report from all forms."""
        return {
            "system_state": {
                "form_count": len(self._forms),
                "substrate_connected": self._substrate is not None,
            },
            "forms": {kind: form.health() for kind, form in self._forms.items()},
        }


# =============================================================================
# EXPORTS
# =============================================================================


__all__ = [
    # Constants
    "MemoryFormKind",
    
    # Data classes
    "MemoryFormState",
    "MemoryFormProjection",
    
    # Core classes
    "MemoryForm",
    "MemoryFormSystem",
]