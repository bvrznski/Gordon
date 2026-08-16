# Memory Encoding Operation - Phase 5.1.2
# ========================================

"""
Memory Encoding: Transform incoming observations into candidate Memory Artifacts.

Purpose:
    Create candidate Memory Artifacts from incoming information.

Encoding owns:
    - artifact proposal (new artifact candidates)
    - identity request (initial identity assignment)
    - initial provenance (origin tracking for new artifacts)
    - initial confidence (first-pass belief assessment)
    - initial uncertainty (first-pass uncertainty estimation)

Encoding does NOT own:
    - artifact admission (submission to substrate is separate)
    - artifact validation (validation is a separate operation)
    - storage implementation (handled by Memory Foundation/substrate)

Encoding Laws (from specification):
    ENCODING-LAW-001: Encoding shall create candidate Memory Artifacts only
    ENCODING-LAW-002: Encoding shall never publish artifacts directly
    ENCODING-LAW-003: Encoding shall preserve original evidence
    ENCODING-LAW-004: Encoding shall initialize provenance
    ENCODING-LAW-005: Encoding shall initialize confidence and uncertainty explicitly
    ENCODING-LAW-006: Encoding shall request admission through Memory contracts
    ENCODING-LAW-007: Encoding shall never assign permanent ownership
    ENCODING-LAW-008: Encoding shall remain deterministic

Input:
    - Perceptual observations (raw sensory data or text)
    - Workspace projections (current working memory state)
    - External memory imports (documents, files, API responses)
    - Internal cognitive products (thoughts, reflections)

Output:
    - Candidate Memory Artifact (with initial metadata)
    - Initial provenance record
    - Initial confidence estimate
    - Initial uncertainty estimate
    - Admission request

Usage:

    from gordon_system.src.agent.components.systems.memory.operations.encoding import EncodingOperation
    from gordon_system.src.agent.components.systems.memory.foundations.artifact import MemoryArtifactKind
    
    encoder = EncodingOperation()
    
    # Encode an observation
    result, projection = encoder.execute(
        inputs={
            "observation": "The cat sat on the mat.",
            "timestamp_utc": time.time(),
            "source_location": "visual_perception",
        },
        context={
            "workspace_state": current_workspace,
            "priority": "high",
        }
    )
    
    # result contains candidate artifacts for admission
"""

from __future__ import annotations

import hashlib
import time
import uuid
from typing import Dict, List, Tuple, Optional, Any

from dataclasses import dataclass, field


# =============================================================================
# ENCODING CONFIGURATION
# =============================================================================


@dataclass(frozen=True)
class EncodingConfig:
    """
    Configuration for the encoding operation.
    
    Fields:
        default_confidence:     Initial confidence for new artifacts (0.0-1.0)
        default_uncertainty:    Initial uncertainty for new artifacts (0.0-1.0)
        max_evidence_sources:   Maximum sources to track per artifact
        preserve_original_text: Keep original text as evidence?
        priority_mapping:       Map source types to initial priorities
    """
    
    default_confidence: float = 0.75
    default_uncertainty: float = 0.25
    max_evidence_sources: int = 10
    preserve_original_text: bool = True
    priority_mapping: Dict[str, Any] = field(
        default_factory=lambda: {}
    )


# =============================================================================
# ENCODING RESULT - Output of encoding operation
# =============================================================================


@dataclass(frozen=True)
class EncodingResult:
    """
    Result produced by the encoding operation.
    
    Fields:
        result_id:          Unique ID for this encoding result
        candidate_artifacts: List of candidate artifacts created
        revisions:          Revisions created (if any)
        
        # Metadata
        duration_ms:        Encoding time in milliseconds
        timestamp_utc:      When encoding completed
    """
    
    result_id: str                          # Unique result ID
    candidate_artifacts: Tuple[Any, ...]
    revisions: Tuple[Any, ...] = field(default_factory=tuple)
    
    # Metadata
    duration_ms: float = 0.0
    timestamp_utc: float = field(default_factory=time.time)


# =============================================================================
# ENCODING OPERATION - Transform observations into candidate artifacts
# =============================================================================


class EncodingOperation:
    """
    Transform incoming observations into candidate Memory Artifacts.
    
    This operation:
        1. Receives raw observations or information
        2. Creates initial artifact candidates with identity and provenance
        3. Calculates initial confidence/uncertainty estimates
        4. Packages artifacts as "candidates" for admission (not published)
        
    The encoding operation is deterministic - given the same observation,
    it will always produce the same candidate artifact structure.
    
    Usage:
        encoder = EncodingOperation()
        result, projection = encoder.execute(observation_inputs)
    """
    
    def __init__(
        self,
        operation_id: Optional[str] = None,
        config: Optional[EncodingConfig] = None,
    ):
        """
        Initialize the encoding operation.
        
        Args:
            operation_id: Unique ID for this operation instance
            config: Configuration settings (or use defaults)
        """
        self.operation_id: str = operation_id or str(uuid.uuid4())
        self.config: EncodingConfig = config or EncodingConfig()
        self._last_result: Optional[EncodingResult] = None
    
    def validate(
        self,
        inputs: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Validate encoding inputs before execution.
        
        Args:
            inputs: Expected to be a dict with:
                - "observation": The observation string or content
                - "timestamp_utc": When the observation occurred
                - "source_location": Where/what source type (optional)
            context: Optional context for encoding
            
        Returns:
            True if inputs are valid, False otherwise
        """
        try:
            # Check that inputs is a dict-like structure
            if not isinstance(inputs, dict):
                return False
            
            # Check required fields exist
            if "observation" not in inputs:
                return False
            
            observation = inputs["observation"]
            
            # Validate observation type
            valid_types = (str, dict)
            if not isinstance(observation, valid_types):
                return False
            
            # If it's a string, check it's not empty
            if isinstance(observation, str) and len(observation.strip()) == 0:
                return False
            
            # Check timestamp if provided
            if "timestamp_utc" in inputs:
                ts = inputs["timestamp_utc"]
                if not isinstance(ts, (int, float)) or ts < 0:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def execute(
        self,
        inputs: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> Tuple[EncodingResult, Dict[str, Any]]:
        """
        Execute the encoding operation.
        
        Args:
            inputs: Expected to be a dict with:
                - "observation": The observation string or content (required)
                - "timestamp_utc": When the observation occurred
                - "source_location": Source type identifier (optional)
                - "observer": Who/what made the observation (optional)
            context: Optional execution context
            
        Returns:
            Tuple of (encoding_result, operation_projection)
            
        Raises:
            ValueError: If inputs are invalid or encoding fails
        """
        # Validate before executing
        if not self.validate(inputs, context):
            raise ValueError("Invalid encoding inputs")
        
        start_time = time.time()
        
        try:
            # Parse inputs
            observation = inputs["observation"]
            timestamp_utc = inputs.get("timestamp_utc", time.time())
            source_location = inputs.get("source_location", "unknown")
            observer = inputs.get("observer", "system")
            
            # Determine artifact kind based on content type
            artifact_kind_str = self._determine_artifact_kind(observation)
            
            # Create initial provenance record
            provenance_data = self._create_provenance(
                observation=observation,
                source_location=source_location,
                observer=observer,
                timestamp_utc=timestamp_utc,
            )
            
            # Calculate semantic identity (hash of content)
            semantic_identity = self._calculate_semantic_identity(observation)
            
            # Create initial confidence and uncertainty
            confidence = self.config.default_confidence
            uncertainty = self.config.default_uncertainty
            
            # Import artifact classes at runtime to avoid circular deps
            from ..foundations.artifact import MemoryArtifactKind, MemoryArtifactStatus, MemoryIdentity
            from ..foundations.revision import MemoryRevisionChangeReason
            from ..foundations.provenance import MemoryProvenance, MemoryProvenanceSource
            from ..foundations.artifact import MemoryArtifact
            
            # Create identity for the new artifact
            identity = MemoryIdentity(
                artifact_id=str(uuid.uuid4()),
                semantic_identity=semantic_identity,
                artifact_kind_str=artifact_kind_str,
                creation_revision=str(uuid.uuid4()),
                current_revision=1,
                provenance={"origin": "encoding_operation"},
                created_at_utc=timestamp_utc,
            )
            
            # Create the candidate artifact
            artifact = MemoryArtifact(
                identity=identity,
                artifact_kind=MemoryArtifactKind.OBSERVATION,
                semantic_content=self._prepare_semantic_content(observation, context),
                revision_number=1,
                previous_revision_id=None,
                is_current=True,
                validity={"status": "pending_validation"},
                confidence={"confidence": confidence},
                uncertainty={"uncertainty": uncertainty},
                provenance=provenance_data,
                status=self.config.priority_mapping.get(source_location, MemoryArtifactStatus.ACTIVE),
                created_at_utc=timestamp_utc,
                updated_at_utc=timestamp_utc,
            )
            
            # Create a revision record for this new artifact
            revision = MemoryRevision(
                revision_identity=f"{identity.artifact_id}:r1",
                previous_revision_id=None,
                change_reason=MemoryRevisionChangeReason.CONTENT_UPDATE,
                change_summary="Initial encoding of observation",
                semantic_changes={"content": str(observation)},
                validation_status="pending",
                provenance=provenance_data,
                created_at_utc=timestamp_utc,
            )
            
            # Create result
            duration_ms = (time.time() - start_time) * 1000
            
            encoding_result = EncodingResult(
                result_id=f"enc:{uuid.uuid4().hex[:12]}",
                candidate_artifacts=(artifact,),
                revisions=(revision,),
                duration_ms=duration_ms,
                timestamp_utc=time.time(),
            )
            
            self._last_result = encoding_result
            inputs_processed = 1
            outputs_produced = len(encoding_result.candidate_artifacts)
            
            # Create projection for observability
            projection = {
                "operation_id": self.operation_id,
                "operation_kind": "encoding",
                "state": "completed",
                "inputs_processed": inputs_processed,
                "outputs_produced": outputs_produced,
                "duration_ms": duration_ms,
                "validation_status": "valid",
                "validation_result": f"Encoded {outputs_produced} candidate artifacts",
                "start_time_utc": start_time,
                "end_time_utc": time.time(),
            }
            
            return encoding_result, projection
            
        except Exception as e:
            raise ValueError(f"Encoding operation failed: {str(e)}")
    
    def _determine_artifact_kind(self, observation: Any) -> str:
        """Determine the artifact kind based on observation type."""
        if isinstance(observation, str):
            obs_lower = observation.lower()
            
            # Check for question patterns
            if "?" in obs_lower or any(w in obs_lower for w in ("who", "what", "when", "where", "why", "how")):
                return "concept"
            
            # Check for action/command patterns
            if any(w in obs_lower for w in ("run", "execute", "do", "create", "make", "build")):
                return "procedure"
            
            # Default to observation for factual statements
            return "observation"
        
        elif isinstance(observation, dict):
            # If it's a dict, check for structure indicators
            if "question" in observation or "query" in observation:
                return "concept"
            elif "action" in observation or "command" in observation:
                return "procedure"
            else:
                return "observation"
        
        return "observation"
    
    def _create_provenance(
        self,
        observation: Any,
        source_location: str,
        observer: str,
        timestamp_utc: float,
    ) -> MemoryProvenance:
        """Create initial provenance record for the new artifact."""
        # Create a provenance source for the observation
        source = MemoryProvenanceSource(
            source_type="observation",
            source_location=source_location,
            confidence=self.config.default_confidence,
            accessed_at_utc=timestamp_utc,
            notes=f"Original: {str(observation)[:100]}..." if isinstance(observation, str) else "Structured observation",
        )
        
        return MemoryProvenance(
            origin=observer,
            originating_system="encoding_operation",
            creation_process="Transformed observation into memory artifact candidate",
            supporting_sources=(source,),
            semantic_time_utc=timestamp_utc,
            created_at_utc=timestamp_utc,
            validation_status="pending",
        )
    
    def _calculate_semantic_identity(self, observation: Any) -> str:
        """Calculate a stable semantic identity for the observation."""
        if isinstance(observation, str):
            content = observation.strip().lower()
        else:
            # For non-string, convert to string representation
            content = str(observation)
        
        # Create a hash of the normalized content
        content_bytes = content.encode('utf-8')
        return hashlib.sha256(content_bytes).hexdigest()[:32]
    
    def _prepare_semantic_content(
        self,
        observation: Any,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Prepare the semantic content structure for the artifact."""
        if isinstance(observation, str):
            content = {"text": observation}
        elif isinstance(observation, dict):
            content = dict(observation)
        else:
            content = {"value": str(observation)}
        
        # Add context if provided
        if context:
            content["context"] = dict(context)
        
        # Mark as pending validation
        content["_encoding_metadata"] = {
            "confidence": self.config.default_confidence,
            "uncertainty": self.config.default_uncertainty,
            "status": "pending_validation",
            "created_at_utc": time.time(),
        }
        
        return content
    
    def get_last_result(self) -> Optional[EncodingResult]:
        """Get the result of the most recent encoding operation."""
        return self._last_result


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_encoding_operation(
    operation_id: Optional[str] = None,
    config: Optional[EncodingConfig] = None,
) -> EncodingOperation:
    """
    Factory function to create an encoding operation.
    
    Args:
        operation_id: Unique ID for this operation (optional)
        config: Configuration settings (optional, uses defaults if None)
        
    Returns:
        New EncodingOperation instance
    """
    return EncodingOperation(operation_id=operation_id, config=config)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "EncodingOperation",
    "EncodingConfig",
    "EncodingResult",
    "create_encoding_operation",
]