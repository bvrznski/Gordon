# Narrative Perspective Models
# ============================

"""
Immutable models for narrative perspectives and bias representation.

ARCHITECTURAL PRINCIPLES:
    - Perspectives are explicit, not merged silently
    - Bias limitations are documented
    - Multiple perspectives may remain unresolved
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# NARRATIVE PERSPECTIVE - Narrative viewpoint representation
# =============================================================================

@dataclass(frozen=True, slots=True)
class NarrativePerspective:
    """
    Immutable description of a narrative perspective.
    
    A perspective determines:
        - What evidence is accessible from that viewpoint
        - Interpretation limits and constraints
        - Potential biases in the account
        
    A perspective is NOT objective truth.
    """
    
    # Identity
    kind: str  # NarrativePerspectiveKind.*
    """The canonical perspective category."""
    
    participant_id: Optional[str] = None
    """Participant ID if this is a participant-specific perspective."""
    
    # Evidence availability
    available_evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence IDs accessible from this perspective."""
    
    unavailable_evidence_ids: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence IDs NOT accessible from this perspective."""
    
    # Bias and limitations
    limitation_kind: Optional[str] = None
    """Kind of limitation (e.g., 'first_person_bias', 'no_internal_state')."""
    
    bias_risk_score: float = 0.0
    """Estimated risk of bias in this perspective (0.0 to 1.0)."""
    
    self_serving_bias_risk: bool = False
    """Whether self-serving bias is possible from this perspective."""
    
    hindsight_risk: bool = False
    """Whether hindsight bias is possible from this perspective."""
    
    incomplete_context: bool = False
    """Whether full context is available from this perspective."""
    
    # Interpretation constraints
    interpretation_risk: float = 0.0
    """Estimated risk of misinterpretation from this perspective."""
    
    @classmethod
    def agent_first_person(cls) -> NarrativePerspective:
        """Create an agent first-person perspective."""
        return cls(
            kind="agent_first_person",
            participant_id="agent",
            available_evidence_ids=("internal_state", "actions", "observations"),
            unavailable_evidence_ids=(),
            limitation_kind=None,
            bias_risk_score=0.2,
            self_serving_bias_risk=True,
            hindsight_risk=False,
            incomplete_context=False,
        )
    
    @classmethod
    def participant_view(
        cls,
        participant_id: str,
    ) -> NarrativePerspective:
        """Create a participant's perspective."""
        return cls(
            kind="participant",
            participant_id=participant_id,
            available_evidence_ids=("actions", "statements"),
            unavailable_evidence_ids=(
                "agent_internal_state",
                "other_participant_thoughts"
            ),
            limitation_kind="no_access_to_other_intentions",
            bias_risk_score=0.3,
            self_serving_bias_risk=True,
            hindsight_risk=False,
            incomplete_context=True,
        )
    
    @classmethod
    def external_observer(cls) -> NarrativePerspective:
        """Create an external observer perspective."""
        return cls(
            kind="external_observer",
            available_evidence_ids=("actions", "statements", "outcomes"),
            unavailable_evidence_ids=(
                "internal_state",
                "intentions",
                "thoughts"
            ),
            limitation_kind="no_access_to_internal_states",
            bias_risk_score=0.1,
            self_serving_bias_risk=False,
            hindsight_risk=False,
            incomplete_context=True,
        )
    
    @classmethod
    def multi_perspective(cls) -> NarrativePerspective:
        """Create a multi-perspective account (perspectives kept distinct)."""
        return cls(
            kind="multi_perspective",
            available_evidence_ids=(),
            unavailable_evidence_ids=(),
            limitation_kind=None,
            bias_risk_score=0.05,
            self_serving_bias_risk=False,
            hindsight_risk=False,
            incomplete_context=False,
        )


# =============================================================================
# PERSPECTIVE BIAS - Bias and limitation representation
# =============================================================================

@dataclass(frozen=True, slots=True)
class PerspectiveBias:
    """
    Immutable description of bias introduced by perspective.
    
    Every narrative has some perspective-related limitations. These should
    be documented rather than silently merged or hidden.
    """
    
    unavailable_evidence: Tuple[str, ...] = field(default_factory=tuple)
    """Evidence that is not accessible from this perspective."""
    
    participant_assumptions: Tuple[str, ...] = field(default_factory=tuple)
    """Participant-specific assumptions that may influence interpretation."""
    
    interpretation_risk: float = 0.0
    """Risk of misinterpretation (0.0 to 1.0)."""
    
    self_serving_bias_risk: bool = False
    """Whether self-serving bias is possible."""
    
    hindsight_risk: bool = False
    """Whether hindsight bias is possible."""
    
    incomplete_context: bool = False
    """Whether full context is available."""
    
    unresolved_disagreement_risk: float = 0.0
    """Risk of unresolved disagreement with other perspectives."""
    
    @classmethod
    def first_person_bias(cls) -> PerspectiveBias:
        """Create a bias profile for first-person perspective."""
        return cls(
            unavailable_evidence=("other_participant_thoughts",),
            participant_assumptions=("my_intent_will_be_understood",),
            interpretation_risk=0.2,
            self_serving_bias_risk=True,
            hindsight_risk=False,
            incomplete_context=False,
        )
    
    @classmethod
    def external_observation_bias(cls) -> PerspectiveBias:
        """Create a bias profile for external observation."""
        return cls(
            unavailable_evidence=("intentions", "internal_states"),
            participant_assumptions=(),
            interpretation_risk=0.3,
            self_serving_bias_risk=False,
            hindsight_risk=False,
            incomplete_context=True,
        )