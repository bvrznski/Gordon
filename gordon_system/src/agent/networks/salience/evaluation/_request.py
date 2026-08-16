# Salience Network Evaluation Request
# ====================================

"""
Canonical evaluation request model (Phase 4.8.5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

# Import state types for type hints
from ..state.subject import SalienceSubjectReference
from ..state.assessment import SalienceAssessmentState


# Content imports (using forward references to avoid circular deps)
from gordon_system.src.agent.networks.salience.content.base import (
    BaseSalienceContent,
    SalienceContentIdentity,
)

from gordon_system.src.agent.networks.salience.content.observations.base import (
    BaseObservation,
)

from gordon_system.src.agent.networks.salience.state.evidence import (
    SalienceEvidence,
)


@dataclass(frozen=True, slots=True)
class SalienceEvaluationRequest:
    """
    Immutable evaluation request.
    
    Represents a complete set of semantic inputs for salience evaluation.
    All fields are tuples to preserve immutability and allow for
    deterministic processing order where semantically meaningful.
    """
    
    # Identity for this request
    identity: str = field(default="")
    """Unique identifier for the request (external supply)."""
    
    # Subject being evaluated
    subject: SalienceSubjectReference = field(default_factory=lambda: SalienceSubjectReference())
    """The semantic subject of evaluation."""
    
    # Input collections - all immutable
    observations: tuple[BaseObservation, ...] = field(default_factory=tuple)
    """Semantic observations from various sources."""
    
    evidence: tuple[SalienceEvidence, ...] = field(default_factory=tuple)
    """Semantic evidence supporting or contradicting assessments."""
    
    cues: tuple[BaseSalienceContent, ...] = field(default_factory=tuple)
    """Cue content that may inform but is not yet evidence."""
    
    hypotheses: tuple[BaseSalienceContent, ...] = field(default_factory=tuple)
    """Hypotheses and potential interpretations."""
    
    contexts: tuple[BaseSalienceContent, ...] = field(default_factory=tuple)
    """Context references for interpretation."""
    
    external_projections: tuple[BaseSalienceContent, ...] = field(default_factory=tuple)
    """External system projections (Goals, expectations, etc.)."""
    
    # Policy for this evaluation
    policy: str = field(default="")
    """Evaluation policy reference (external supply)."""
    
    # Semantic time reference (NOT datetime.now!)
    semantic_time_reference: str | None = field(default=None)
    """Semantic time reference for temporal comparison."""
    
    # Provenance tracking
    provenance_source: str = field(default="")
    """Source of this evaluation request."""