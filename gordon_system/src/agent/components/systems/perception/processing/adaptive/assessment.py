# Perception Adaptive Processing Assessment - Phase 5.2.2
# =======================================================

"""
Adaptive Processing Assessment: Evaluates whether configuration should change.

Assessment observes environmental conditions and proposes configuration changes
when processing quality would benefit from adaptation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum, auto
import time
import uuid


# =============================================================================
# ADAPTATION MODE - How should the system adapt?
# =============================================================================


class AdaptationMode(Enum):
    """
    Mode of adaptation to apply.
    
    Modes:
        STATIC:         No adaptation, fixed configuration
        CONTEXTUAL:     Adjust based on current context conditions
        QUALITY_DRIVEN: Optimize for quality metrics
        LOAD_AWARE:     Reduce processing under resource pressure
        DEGRADATION_AWARE: Compensate for degraded sources
        PLATFORM_AWARE: Adapt to platform-specific capabilities
        POLICY_CONSTRAINED: Follow policy-mandated adaptation rules
        RECOVERY:       Use recovery-focused configuration
    """
    
    STATIC = "static"               # No adaptation
    CONTEXTUAL = "contextual"       # Context-based adjustment
    QUALITY_DRIVEN = "quality_driven"
    LOAD_AWARE = "load_aware"
    DEGRADATION_AWARE = "degradation_aware"
    PLATFORM_AWARE = "platform_aware"
    POLICY_CONSTRAINED = "policy_constrained"
    RECOVERY = "recovery"


# =============================================================================
# ADAPTIVE CONDITION - What conditions triggered adaptation?
# =============================================================================


class AdaptiveCondition(Enum):
    """
    Condition that may trigger adaptation.
    
    Conditions:
        LOW_SIGNAL_QUALITY:      Signal quality below threshold
        HIGH_NOISE:              Elevated noise levels detected
        CHANGED_ILLUMINATION:    Lighting conditions changed significantly
        CHANGED_ACOUSTIC_ENVIRONMENT: Audio environment changed
        CHANGED_ENCODING:        Text encoding differs from expected
        CHANGED_SCHEMA:          Source schema changed unexpectedly
        HIGH_EVENT_RATE:         Too many events for current capacity
        RESOURCE_PRESSURE:       System resource pressure high
        SOURCE_DEGRADATION:      Source quality degrading over time
        PLATFORM_CHANGE:         Platform capabilities changed
        SANDBOX_CHANGE:          Sandbox environment changed
    """
    
    LOW_SIGNAL_QUALITY = "low_signal_quality"
    HIGH_NOISE = "high_noise"
    CHANGED_ILLUMINATION = "changed_illumination"
    CHANGED_ACOUSTIC_ENVIRONMENT = "changed_acoustic_environment"
    CHANGED_ENCODING = "changed_encoding"
    CHANGED_SCHEMA = "changed_schema"
    HIGH_EVENT_RATE = "high_event_rate"
    RESOURCE_PRESSURE = "resource_pressure"
    SOURCE_DEGRADATION = "source_degradation"
    PLATFORM_CHANGE = "platform_change"
    SANDBOX_CHANGE = "sandbox_change"


# =============================================================================
# ADAPTIVE PROCESSING ASSESSMENT - Evaluation of adaptation needs
# =============================================================================


@dataclass(frozen=True)
class AdaptiveProcessingAssessment:
    """
    Assessment of whether and how to adapt processing configuration.
    
    Fields:
        assessment_identity:     Unique identifier for this assessment
        observed_conditions:     What environmental conditions were observed?
        current_configuration:   Current configuration revision being used
        proposed_configuration:  Configuration revision that should be used
        adaptation_mode:         Mode of adaptation to apply
        expected_effect:         Expected improvement from adaptation
        confidence:              Confidence in the assessment
        uncertainty:             Known limitations of this assessment
        limitations:             Limitations of this assessment
    """
    
    assessment_identity: str            # Unique ID
    
    observed_conditions: Tuple[AdaptiveCondition, ...]  # Observed conditions
    
    current_configuration: int          # Current config revision
    proposed_configuration: Optional[int] = None  # New config if adaptation needed
    
    adaptation_mode: AdaptationMode = AdaptationMode.STATIC
    
    expected_effect: str = ""           # What improvement is expected?
    
    confidence: float = 0.5            # Assessment confidence (0.0-1.0)
    uncertainty: float = 0.3          # Assessment uncertainty (0.0-1.0)
    
    limitations: Tuple[str, ...] = field(default_factory=tuple)  # Limitations
    
    @property
    def needs_adaptation(self) -> bool:
        """Check if adaptation is needed."""
        return self.proposed_configuration is not None and self.proposed_configuration != self.current_configuration
    
    @classmethod
    def stable(
        cls,
        current_config: int = 1,
    ) -> "AdaptiveProcessingAssessment":
        """
        Create a assessment indicating no adaptation needed.
        
        Args:
            current_config: Current configuration revision
            
        Returns:
            Assessment with STATIC mode and no proposed change
        """
        return cls(
            assessment_identity=f"adapt:{uuid.uuid4().hex[:16]}",
            observed_conditions=(),
            current_configuration=current_config,
            proposed_configuration=None,
            adaptation_mode=AdaptationMode.STATIC,
            confidence=0.95,
            uncertainty=0.05,
        )
    
    @classmethod
    def propose_change(
        cls,
        current_config: int,
        new_config: int,
        conditions: List[AdaptiveCondition],
        expected_effect: str = "Improved processing quality",
        mode: AdaptationMode = AdaptationMode.CONTEXTUAL,
    ) -> "AdaptiveProcessingAssessment":
        """
        Create an assessment proposing a configuration change.
        
        Args:
            current_config: Current configuration revision
            new_config: Proposed configuration revision
            conditions: Conditions triggering the change
            expected_effect: Expected benefit of the change
            mode: Adaptation mode to use
            
        Returns:
            Assessment with proposed configuration change
        """
        return cls(
            assessment_identity=f"adapt:{uuid.uuid4().hex[:16]}",
            observed_conditions=tuple(conditions),
            current_configuration=current_config,
            proposed_configuration=new_config,
            adaptation_mode=mode,
            expected_effect=expected_effect,
            confidence=max(0.5, 0.9 - len(conditions) * 0.05),
            uncertainty=min(0.3 + len(conditions) * 0.02, 0.7),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert assessment to dictionary."""
        return {
            "assessment_identity": self.assessment_identity,
            "observed_conditions": [c.value for c in self.observed_conditions],
            "current_configuration": self.current_configuration,
            "proposed_configuration": self.proposed_configuration,
            "adaptation_mode": self.adaptation_mode.value,
            "expected_effect": self.expected_effect,
            "confidence": self.confidence,
            "uncertainty": self.uncertainty,
            "limitations": list(self.limitations),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AdaptiveProcessingAssessment":
        """Create assessment from dictionary."""
        return cls(
            assessment_identity=data.get("assessment_identity", str(uuid.uuid4())),
            observed_conditions=tuple(
                AdaptiveCondition(c) for c in data.get("observed_conditions", [])
            ),
            current_configuration=data.get("current_configuration", 1),
            proposed_configuration=data.get("proposed_configuration"),
            adaptation_mode=AdaptationMode(data.get("adaptation_mode", "static")),
            expected_effect=data.get("expected_effect", ""),
            confidence=float(data.get("confidence", 0.5)),
            uncertainty=float(data.get("uncertainty", 0.3)),
            limitations=tuple(data.get("limitations", [])),
        )