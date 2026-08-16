# Perception Processing Stage - Phase 5.2.2
# ==========================================

"""
Processing Stage: A single semantic transformation class.

A Processing Stage performs exactly one class of perceptual transformation.
It accepts input artifacts, applies transformations, and produces output artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Callable, Type
from enum import Enum, auto
import time
import uuid

from gordon_system.src.agent.components.systems.perception.foundations.confidence import PerceptionConfidence, PerceptionUncertainty
from gordon_system.src.agent.components.systems.perception.foundations.provenance import PerceptionProvenance


# =============================================================================
# PROCESSING STAGE KIND - What class of transformation does this stage perform?
# =============================================================================


class ProcessingStageKind(Enum):
    """
    Category of transformation performed by a processing stage.
    
    Kinds:
        ADAPTIVE:       Adjust configuration based on environmental conditions
        HABITUATION:    Assess repetition and adjust processing emphasis
        TEMPORAL:       Align timing across evidence streams
        SPATIAL:        Map between coordinate systems
        IDENTITY:       Evaluate cross-source entity correspondence
        SCHEMA:         Align structural schemas between sources
        TRANSLATION:    Convert representation to canonical form
        NORMALIZATION:  Convert conventions to canonical form
        VALIDATION:     Validate artifacts before publication
    """
    
    ADAPTIVE = "adaptive"           # Config adjustment based on conditions
    HABITUATION = "habituation"     # Repetition assessment
    TEMPORAL = "temporal"          # Timing alignment
    SPATIAL = "spatial"            # Coordinate mapping
    IDENTITY = "identity"          # Entity correspondence
    SCHEMA = "schema"              # Structural alignment
    TRANSLATION = "translation"     # Representation conversion
    NORMALIZATION = "normalization"  # Convention normalization
    VALIDATION = "validation"       # Output validation


# =============================================================================
# STAGE INPUT CONTRACT - What does this stage accept?
# =============================================================================


@dataclass(frozen=True)
class ProcessingStageInput:
    """
    Input contract for a processing stage.
    
    Fields:
        artifacts:           Input perceptual artifacts
        accepted_kinds:      Which artifact kinds are accepted (Percept, Signal, Feature, etc.)
        source_revisions:    Revisions of source artifacts
        source_modalities:   Modalities that produced sources
        confidence_state:    Current confidence state for propagation
        uncertainty_state:   Current uncertainty state for propagation
        provenance:          Origin tracking metadata
    """
    
    # Artifact input
    artifacts: Tuple[Any, ...]           # Input perceptual artifacts
    
    accepted_kinds: Tuple[str, ...]      # e.g., ("Percept", "Signal", "Feature")
    
    source_revisions: Dict[str, int]     # artifact_id -> revision mapping
    
    source_modalities: Tuple[str, ...]   # modalities that produced sources
    
    # Confidence/uncertainty propagation state
    confidence_state: PerceptionConfidence
    uncertainty_state: PerceptionUncertainty
    
    provenance: PerceptionProvenance


# =============================================================================
# STAGE OUTPUT CONTRACT - What does this stage produce?
# =============================================================================


@dataclass(frozen=True)
class ProcessingStageOutput:
    """
    Output contract from a processing stage.
    
    Fields:
        artifacts:           Transformed artifacts
        output_kinds:        Kinds of artifacts produced (Percept, Signal, etc.)
        transformation_reference: Reference to transformation record
        confidence_state:    Updated confidence state
        uncertainty_state:   Updated uncertainty state
        information_loss:    Declared information loss from processing
        findings:            Processing observations and insights
        limitations:         Known limitations of this output
        provenance:          Origin tracking with transformation history
    """
    
    # Artifact output
    artifacts: Tuple[Any, ...]           # Transformed artifacts
    
    output_kinds: Tuple[str, ...]        # e.g., ("Percept", "Signal")
    
    transformation_reference: str        # Reference to transformation record
    
    # State updates
    confidence_state: PerceptionConfidence
    uncertainty_state: PerceptionUncertainty
    
    # Processing information
    information_loss: Optional["ProcessingInformationLoss"] = None  # noqa
    
    findings: Tuple[str, ...] = field(default_factory=tuple)
    limitations: Tuple[str, ...] = field(default_factory=tuple)
    
    provenance: PerceptionProvenance


# =============================================================================
# PROCESSING INFORMATION LOSS - What was lost during transformation?
# =============================================================================


class InformationLossKind(Enum):
    """
    Kind of information lost during processing.
    
    Kinds:
        NONE:            No information loss (lossless transformation)
        PRECISION:       Reduced numeric precision
        RESOLUTION:      Reduced spatial or temporal resolution
        TEMPORAL:        Lost timing information
        SPATIAL:         Lost spatial information
        STRUCTURAL:      Lost structural information (nested fields, etc.)
        CONTEXTUAL:      Lost contextual information
        FIELD_OMISSION:  Field was omitted entirely
        AGGREGATION:     Information lost through aggregation
        COMPRESSION:     Lossy compression applied
    """
    
    NONE = "none"
    PRECISION = "precision"
    RESOLUTION = "resolution"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    STRUCTURAL = "structural"
    CONTEXTUAL = "contextual"
    FIELD_OMISSION = "field_omission"
    AGGREGATION = "aggregation"
    COMPRESSION = "compression"


@dataclass(frozen=True)
class ProcessingInformationLoss:
    """
    Information loss record for a transformation.
    
    Fields:
        identity:            Unique identifier
        stage_identity:      Which stage caused this loss?
        loss_kind:           Category of information loss
        affected_fields:     Which fields were affected?
        affected_resolution: Resolution that was reduced (if applicable)
        recoverability:      Can the loss be recovered? ("yes", "no", "partial")
        expected_semantic_impact: Expected impact on downstream processing
    """
    
    identity: str                          # Unique ID
    stage_identity: str                    # Stage that caused this
    
    loss_kind: InformationLossKind        # Category of loss
    affected_fields: Tuple[str, ...]      # Field names
    affected_resolution: Optional[str] = None  # Resolution description if applicable
    
    recoverability: str = "no"            # "yes", "no", or "partial"
    
    expected_semantic_impact: str = ""    # Description of impact


# =============================================================================
# PROCESSING STAGE - Core processing unit
# =============================================================================


class ProcessingStage:
    """
    A single semantic transformation class in the perception pipeline.
    
    Each Processing Stage performs exactly one class of perceptual transformation.
    It must:
        - Accept only canonical artifacts or explicitly declared source representations
        - Preserve source artifact identity and provenance
        - Expose confidence, uncertainty, and information-loss effects
        - Publish only validated canonical outputs
    
    Properties:
        identity:            Unique stage identifier
        stage_kind:          What class of transformation?
        accepted_input_kinds: Which artifact kinds are accepted?
        produced_output_kinds: Which artifact kinds are produced?
        preconditions:       Required conditions before processing
        postconditions:      Guaranteed conditions after processing
        configuration:       Stage-specific configuration parameters
        revision:            Revision number for this stage definition
        provenance:          Origin tracking
    
    Example:
        class TemporalAlignmentStage(ProcessingStage):
            def __init__(self):
                super().__init__(
                    identity="temporal_align",
                    stage_kind=ProcessingStageKind.TEMPORAL,
                    accepted_input_kinds=("Percept", "Signal"),
                    produced_output_kinds=("AlignedPercept",),
                )
    """
    
    # Class-level registration
    _stage_registry: Dict[str, Type["ProcessingStage"]] = {}
    
    def __init__(
        self,
        identity: Optional[str] = None,
        stage_kind: ProcessingStageKind = ProcessingStageKind.VALIDATION,
        accepted_input_kinds: Tuple[str, ...] = ("Percept", "Signal", "Feature"),
        produced_output_kinds: Tuple[str, ...] = ("Percept",),
        transformation_contract: str = "",
        preconditions: Tuple[str, ...] = (),
        postconditions: Tuple[str, ...] = (),
        configuration: Optional[Dict[str, Any]] = None,
        revision: int = 1,
        provenance: Optional[PerceptionProvenance] = None,
    ):
        """
        Initialize a Processing Stage.
        
        Args:
            identity: Unique identifier (auto-generated if None)
            stage_kind: What class of transformation?
            accepted_input_kinds: Which artifact kinds are accepted?
            produced_output_kinds: Which artifact kinds are produced?
            transformation_contract: Description of the transformation
            preconditions: Required conditions before processing
            postconditions: Guaranteed conditions after processing
            configuration: Stage-specific parameters
            revision: Revision number for this stage definition
            provenance: Origin tracking metadata
        """
        self._identity = identity or f"stage:{uuid.uuid4().hex[:16]}"
        self._stage_kind = stage_kind
        self._accepted_input_kinds = accepted_input_kinds
        self._produced_output_kinds = produced_output_kinds
        self._transformation_contract = transformation_contract
        self._preconditions = preconditions
        self._postconditions = postconditions
        self._configuration = configuration or {}
        self._revision = revision
        self._provenance = provenance or PerceptionProvenance(
            origin=self._identity,
            creation_process=f"ProcessingStage created: {stage_kind.value}",
            semantic_time_utc=time.time(),
            created_at_utc=time.time(),
        )
    
    @property
    def identity(self) -> str:
        """Unique stage identifier."""
        return self._identity
    
    @property
    def stage_kind(self) -> ProcessingStageKind:
        """What class of transformation does this perform?"""
        return self._stage_kind
    
    @property
    def accepted_input_kinds(self) -> Tuple[str, ...]:
        """Which artifact kinds are accepted as input."""
        return self._accepted_input_kinds
    
    @property
    def produced_output_kinds(self) -> Tuple[str, ...]:
        """Which artifact kinds are produced as output."""
        return self._produced_output_kinds
    
    @property
    def transformation_contract(self) -> str:
        """Description of the transformation performed."""
        return self._transformation_contract
    
    @property
    def preconditions(self) -> Tuple[str, ...]:
        """Required conditions before processing."""
        return self._preconditions
    
    @property
    def postconditions(self) -> Tuple[str, ...]:
        """Guaranteed conditions after processing."""
        return self._postconditions
    
    @property
    def configuration(self) -> Dict[str, Any]:
        """Stage-specific configuration parameters."""
        return dict(self._configuration)
    
    @property
    def revision(self) -> int:
        """Revision number for this stage definition."""
        return self._revision
    
    @property
    def provenance(self) -> PerceptionProvenance:
        """Origin tracking metadata."""
        return self._provenance
    
    def can_accept(self, artifact_kind: str) -> bool:
        """
        Check if an artifact kind is accepted by this stage.
        
        Args:
            artifact_kind: The artifact category to check
            
        Returns:
            True if the kind is accepted
        """
        return artifact_kind in self._accepted_input_kinds
    
    def validate_input(self, input_data: ProcessingStageInput) -> Tuple[bool, List[str]]:
        """
        Validate that input meets stage requirements.
        
        Args:
            input_data: The proposed input to the stage
            
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check artifact kinds
        for artifact in input_data.artifacts:
            if hasattr(artifact, "__class__"):
                artifact_kind = artifact.__class__.__name__
                if artifact_kind not in self._accepted_input_kinds:
                    errors.append(
                        f"Stage {self._identity} does not accept '{artifact_kind}'. "
                        f"Accepted kinds: {', '.join(self._accepted_input_kinds)}"
                    )
        
        # Check preconditions
        for precondition in self._preconditions:
            if not self._check_precondition(precondition, input_data):
                errors.append(f"Precondition failed: {precondition}")
        
        return len(errors) == 0, errors
    
    def _check_precondition(self, precondition: str, input_data: ProcessingStageInput) -> bool:
        """
        Check if a precondition is satisfied.
        
        Args:
            precondition: Precondition string to evaluate
            input_data: Input data for evaluation
            
        Returns:
            True if the precondition is satisfied
        """
        # Default implementation - all preconditions pass
        # Override in subclasses for specific checks
        return True
    
    def process(self, input_data: ProcessingStageInput) -> ProcessingStageOutput:
        """
        Process input artifacts and produce transformed output.
        
        This is an abstract method that must be implemented by subclasses.
        It should:
            - Validate input first
            - Apply the transformation
            - Preserve source references
            - Update confidence/uncertainty appropriately
            - Record any information loss
            - Return a ProcessingStageOutput
        
        Args:
            input_data: The input to process
            
        Returns:
            Processed output artifacts
            
        Raises:
            ValueError: If input validation fails
        """
        is_valid, errors = self.validate_input(input_data)
        if not is_valid:
            raise ValueError(f"Input validation failed for stage {self._identity}: {errors}")
        
        # Default implementation - return unchanged with empty transformation record
        return ProcessingStageOutput(
            artifacts=input_data.artifacts,
            output_kinds=self._produced_output_kinds,
            transformation_reference=f"transform:{uuid.uuid4().hex[:16]}",
            confidence_state=input_data.confidence_state,
            uncertainty_state=input_data.uncertainty_state,
            information_loss=None,
            findings=(),
            limitations=(),
            provenance=input_data.provenance.extend(
                change_reason=f"Applied {self._stage_kind.value} transformation",
                changed_by=self._identity,
            ),
        )
    
    def __call__(self, input_data: ProcessingStageInput) -> ProcessingStageOutput:
        """Make stage callable."""
        return self.process(input_data)
    
    @classmethod
    def register_stage(cls, kind: str, stage_class: Type["ProcessingStage"]) -> None:
        """
        Register a stage class for a given kind.
        
        Args:
            kind: The processing stage kind identifier
            stage_class: The stage class to register
        """
        cls._stage_registry[kind] = stage_class
    
    @classmethod
    def get_stage(cls, kind: str) -> Type["ProcessingStage"]:
        """
        Get a registered stage class by kind.
        
        Args:
            kind: The processing stage kind identifier
            
        Returns:
            The registered stage class
            
        Raises:
            KeyError: If no stage is registered for this kind
        """
        return cls._stage_registry[kind]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stage configuration to dictionary."""
        return {
            "identity": self._identity,
            "stage_kind": self._stage_kind.value,
            "accepted_input_kinds": list(self._accepted_input_kinds),
            "produced_output_kinds": list(self._produced_output_kinds),
            "transformation_contract": self._transformation_contract,
            "preconditions": list(self._preconditions),
            "postconditions": list(self._postconditions),
            "configuration": dict(self._configuration),
            "revision": self._revision,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessingStage":
        """
        Create a stage instance from dictionary configuration.
        
        Args:
            data: Configuration dictionary
            
        Returns:
            New stage instance
        """
        return cls(
            identity=data.get("identity"),
            stage_kind=ProcessingStageKind(data.get("stage_kind", "validation")),
            accepted_input_kinds=tuple(data.get("accepted_input_kinds", ["Percept"])),
            produced_output_kinds=tuple(data.get("produced_output_kinds", ["Percept"])),
            transformation_contract=data.get("transformation_contract", ""),
            preconditions=tuple(data.get("preconditions", [])),
            postconditions=tuple(data.get("postconditions", [])),
            configuration=dict(data.get("configuration", {})),
            revision=data.get("revision", 1),
        )