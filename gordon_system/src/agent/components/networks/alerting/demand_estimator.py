# Alerting Demand Estimator - Phase 4.1.4
# ==========================================

"""
Demand estimation and modulation for the AlertingNetwork.

This module implements AlertingDemandEstimator, which converts extracted
features into advisory attention-demand assessments.

Architecture:
    - Demand estimation from features
    - Confidence estimation
    - Contextual modulation (focus commitment, task criticality, resource pressure)
    - Habituation modulation (repeated exposure decreases demand)
    - Refractory suppression (suppresses repeated immediate alerts)
    - Deterministic classification into levels
    - Advisory recommendation generation
    - Complete explanation with evidence and provenance

Output:
    AlertingAssessment containing:
        - demand_score: Continuous attention demand (0.0 to 1.0)
        - confidence: Confidence in the assessment
        - level: NEGLIGIBLE, LOW, MODERATE, HIGH, CRITICAL
        - recommendation: IGNORE, OBSERVE, REQUEST_ATTENTION, etc.
        - features: Computed feature values for explainability
        - modulation: Modulation evidence
        - reasons: List of AlertingReason instances explaining the assessment
        - provenance: Input/output tracking metadata

Invariants:
    - Never interrupts execution
    - Never modifies Thread state
    - Never invokes Core scheduling
    - Never executes actions
    - Never alters Working Memory
    - Never changes behavioral policy

This estimator is advisory only. Downstream layers (Arbitration, Executive,
Execution, Core) decide what to do with the assessment.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any
from datetime import datetime

# Import from alerting module
from gordon_system.src.agent.components.networks.alerting.models import (
    AlertingInput,
    AlertingContext,
    AlertingFeatures,
    AlertingModulation,
    AlertingReason,
    AlertingProvenance,
    AlertingAssessment,
)

from gordon_system.src.agent.components.networks.alerting.features.vector import AlertingFeatureVector
from gordon_system.src.agent.components.networks.alerting.enums import (
    AlertingLevel,
    AlertingRecommendation,
    AlertingReasonCategory,
    AlertingStateTransition,
)
from gordon_system.src.agent.components.networks.alerting.states import (
    HabituationState,
    RefractoryState,
    TemporalState,
)
from gordon_system.src.agent.components.networks.alerting.configuration import (
    AlertingNetworkConfig,
)


# =============================================================================
# Demand Estimator Configuration
# =============================================================================

@dataclass(frozen=True)
class DemandEstimatorConfig:
    """
    Configuration specific to demand estimation.
    
    These parameters control how features combine into demand scores.
    """
    
    # Base feature weights (normalized during computation)
    intensity_weight: float = 0.25
    novelty_weight: float = 0.15
    urgency_weight: float = 0.20
    change_weight: float = 0.15
    contrast_weight: float = 0.10
    temporal_weight: float = 0.05
    
    # State-based attenuation weights
    habituation_weight: float = 0.08
    refractory_weight: float = 0.07
    
    # Modulation bounds
    max_positive_modulation: float = 0.3  # Context can increase demand by up to this
    max_negative_modulation: float = 0.5  # Habituation/refractory can decrease by this
    
    # Minimum evidence threshold for any assessment
    min_evidence_score: float = 0.1


# =============================================================================
# Evidence Summary
# =============================================================================

@dataclass(frozen=True)
class EvidenceSummary:
    """
    Summary of which features contributed to the demand estimate.
    
    Records:
        - Which features had non-zero values
        - How each feature contributed (weighted contribution)
        - Confidence in each feature's measurement
    """
    
    # Contributing features with their contributions
    contributing_features: Tuple[str, ...]  # Feature names
    contributions: Tuple[float, ...]        # Weighted contributions (sum to ~1.0)
    
    # Summary statistics
    active_feature_count: int
    total_evidence_score: float
    
    # Confidence metrics
    average_confidence: float
    min_confidence: float


@dataclass(frozen=True)
class ModulationSummary:
    """
    Record of how modulation affected the final demand estimate.
    
    Breaks down the contribution from each modulating factor:
        - Contextual (focus, task criticality, resource pressure)
        - Habituation (attenuation from repeated exposure)
        - Refractory (suppression from recent alerts)
    """
    
    # Base demand (before modulation)
    base_demand: float
    
    # Modulation components
    positive_modulation: float   # Increases demand
    negative_modulation: float   # Decreases demand
    final_demand: float          # After all modulation
    
    # Breakdown by source
    context_modulation: float
    habituation_modulation: float
    refractory_modulation: float
    
    # Evidence that each modulation was applied
    context_evidence: Tuple[str, ...]
    habituation_evidence: Tuple[str, ...]
    refractory_evidence: Tuple[str, ...]


# =============================================================================
# Demand Estimator
# =============================================================================

class AlertingDemandEstimator:
    """
    Computes attention demand from extracted features.
    
    This is the core estimator that Phase 4.1.3's feature vectors feed into.
    It produces advisory assessments that downstream layers interpret.
    
    Input:
        - AlertingFeatureVector: Normalized features from analyzers
        - AlertingContext: External context (focus, task criticality, etc.)
        - HabituationState: State for habituation modulation
        - RefractoryState: State for refractory suppression
        
    Output:
        - AlertingAssessment: Complete advisory assessment
        
    No side effects. Pure computation.
    """
    
    def __init__(
        self,
        config: Optional[AlertingNetworkConfig] = None,
        demand_config: Optional[DemandEstimatorConfig] = None,
    ):
        """
        Initialize the demand estimator.
        
        Args:
            config: General AlertingNetwork configuration
            demand_config: Specific demand estimation configuration
        """
        self.config = config or AlertingNetworkConfig()
        self.demand_config = demand_config or DemandEstimatorConfig()
    
    def compute_demand(
        self,
        features: AlertingFeatureVector,
        context: Optional[AlertingContext] = None,
        habituation_state: Optional[HabituationState] = None,
        refractory_state: Optional[RefractoryState] = None,
    ) -> Tuple[float, float, EvidenceSummary, ModulationSummary]:
        """
        Compute demand score and confidence from features.
        
        Args:
            features: Feature vector with normalized values
            context: Optional external context for modulation
            habituation_state: State for repeated exposure attenuation
            refractory_state: State for immediate re-alert suppression
            
        Returns:
            Tuple of (demand_score, confidence, evidence_summary, modulation_summary)
        """
        # Step 1: Compute base demand from features
        base_demand = self._compute_base_demand(features)
        
        # Step 2: Compute feature confidence (average or weighted)
        confidence = self._compute_confidence(features)
        
        # Step 3: Apply contextual modulation
        context_mod, context_evidence = self._apply_context_modulation(
            base_demand, features, context
        )
        
        # Step 4: Apply habituation modulation
        habituation_mod, habituation_evidence, updated_habituation = self._apply_habituation_modulation(
            context_mod, features, habituation_state
        )
        
        # Step 5: Apply refractory suppression
        refractory_mod, refractory_evidence, updated_refractory = self._apply_refractory_suppression(
            habituation_mod, features, refractory_state
        )
        
        final_demand = max(0.0, min(1.0, refractory_mod))
        
        # Step 6: Build summaries
        evidence_summary = self._build_evidence_summary(features, base_demand)
        modulation_summary = ModulationSummary(
            base_demand=base_demand,
            positive_modulation=context_mod - base_demand if context_mod > base_demand else 0.0,
            negative_modulation=math.hypot(habituation_mod, refractory_mod),
            final_demand=final_demand,
            context_modulation=context_mod,
            habituation_modulation=habituation_mod,
            refractory_modulation=refractory_mod,
            context_evidence=context_evidence,
            habituation_evidence=habituation_evidence,
            refractory_evidence=refractory_evidence,
        )
        
        return final_demand, confidence, evidence_summary, modulation_summary
    
    def _compute_base_demand(self, features: AlertingFeatureVector) -> float:
        """
        Compute base demand score from feature values.
        
        This is the raw demand without any context or state modulation.
        Uses weighted combination of relevant features.
        """
        weights = self.demand_config
        
        # Normalize weights
        total_weight = (
            weights.intensity_weight + weights.novelty_weight +
            weights.urgency_weight + weights.change_weight +
            weights.contrast_weight + weights.temporal_weight
        )
        
        # Intensity components (from contrast and local features)
        intensity_contribution = (
            (features.local_contrast * weights.intensity_weight +
             features.background_contrast * (weights.intensity_weight * 0.5)) / total_weight
        ) if hasattr(features, 'local_contrast') else 0.0
        
        # Novelty components
        novelty_contribution = (
            (features.baseline_deviation * weights.novelty_weight +
             features.history_deviation * (weights.novelty_weight * 0.7)) / total_weight
        ) if hasattr(features, 'baseline_deviation') else 0.0
        
        # Urgency components
        urgency_contribution = (
            (features.rapid_escalation * weights.urgency_weight +
             features.time_sensitive_transition * (weights.urgency_weight * 0.6)) / total_weight
        ) if hasattr(features, 'rapid_escalation') else 0.0
        
        # Change components (from change detection)
        change_contribution = (
            (features.absolute_change * weights.change_weight +
             features.rate_of_change * (weights.change_weight * 0.8)) / total_weight
        ) if hasattr(features, 'absolute_change') else 0.0
        
        # Contrast (already partially covered in intensity, add additional signal)
        contrast_contribution = (
            features.context_contrast * weights.contrast_weight / total_weight
        ) if hasattr(features, 'context_contrast') else 0.0
        
        # Temporal stability (lower variance/oscillation = more predictable = lower demand)
        temporal_contribution = (
            (1.0 - features.variance) * weights.temporal_weight / total_weight
        ) if hasattr(features, 'variance') else 0.0
        
        # Compute weighted sum and normalize to [0, 1]
        raw_score = (
            intensity_contribution +
            novelty_contribution +
            urgency_contribution +
            change_contribution +
            contrast_contribution +
            temporal_contribution
        )
        
        # Apply sigmoid-like normalization to keep in [0, 1] range
        normalized = min(1.0, max(0.0, raw_score * 2))
        
        return normalized
    
    def _compute_confidence(self, features: AlertingFeatureVector) -> float:
        """
        Estimate confidence in the demand assessment.
        
        Based on:
            - Feature completeness (how many valid features)
            - Feature confidence scores
            - Consistency of signals
        """
        # Count valid features
        total_features = len(features.feature_names)
        valid_feature_count = sum(
            1 for name in features.feature_names
            if features.is_valid(name) and getattr(features, name, None) is not None
        )
        
        # Base confidence from completeness
        completeness_ratio = valid_feature_count / max(1, total_features)
        base_confidence = completeness_ratio * 0.8
        
        # Add confidence from feature-level confidence scores
        if features.features_confidence:
            avg_feature_confidence = sum(features.features_confidence.values()) / len(
                features.features_confidence
            )
            confidence_bonus = avg_feature_confidence * 0.2
        else:
            confidence_bonus = 0.1  # Default low confidence without explicit scores
        
        return min(1.0, max(0.0, base_confidence + confidence_bonus))
    
    def _apply_context_modulation(
        self,
        base_demand: float,
        features: AlertingFeatureVector,
        context: Optional[AlertingContext],
    ) -> Tuple[float, Tuple[str, ...]]:
        """
        Apply contextual modulation to demand.
        
        Context never overrides evidence - it modulates evidence.
        """
        if not context:
            return base_demand, ()
        
        evidence = []
        
        # Focus strength modulation
        focus_modulation = 0.0
        if context.focus_strength_projection is not None:
            # Low focus = higher demand (signal needs attention)
            # High focus = lower demand (focus already allocated)
            focus_contribution = (
                (1.0 - context.focus_strength_projection) * 
                self.config.relevance.focus_strength_weight *
                base_demand
            )
            focus_modulation = focus_contribution
            evidence.append(f"focus_modulation={focus_modulation:.3f}")
        
        # Task criticality modulation  
        task_crit_modulation = 0.0
        if context.task_criticality_projection is not None:
            # High task criticality increases demand for relevant signals
            task_crit_contribution = (
                context.task_criticality_projection *
                self.config.relevance.task_criticality_weight *
                base_demand
            )
            task_crit_modulation = task_crit_contribution
            evidence.append(f"task_criticality_modulation={task_crit_modulation:.3f}")
        
        # Resource pressure modulation (high pressure reduces demand capacity)
        resource_pressure_modulation = 0.0
        if context.resource_pressure_projection is not None:
            # High pressure may increase urgency perception
            resource_contribution = (
                context.resource_pressure_projection *
                self.config.relevance.max_context_modulation *
                base_demand * 0.5
            )
            resource_pressure_modulation = resource_contribution
            evidence.append(f"resource_pressure_modulation={resource_pressure_modulation:.3f}")
        
        total_modulation = focus_modulation + task_crit_modulation + resource_pressure_modulation
        
        # Clamp to bounds
        new_demand = base_demand + total_modulation
        new_demand = max(0.0, min(1.0, new_demand))
        
        return new_demand, tuple(evidence)
    
    def _apply_habituation_modulation(
        self,
        demand: float,
        features: AlertingFeatureVector,
        habituation_state: Optional[HabituationState],
    ) -> Tuple[float, Tuple[str, ...], HabituationState]:
        """
        Apply habituation modulation (repeated exposure decreases demand).
        
        Returns:
            Tuple of (modulated_demand, evidence_tuple, updated_habituation_state)
        """
        if not habituation_state:
            # Default: no habituation
            return demand, (), HabituationState()
        
        evidence = []
        
        # Get current habituation coefficient (0.0 to 1.0, where 1.0 = no attenuation)
        coef = habituation_state.habituation_coefficient
        
        # Apply attenuation: higher habituation = lower demand
        attenuated_demand = demand * coef
        
        attenuation_amount = demand - attenuated_demand
        if attenuation_amount > 0:
            evidence.append(f"habituation_attenuation={attenuation_amount:.3f}")
        
        # Record new exposure and update state
        updated_state = habituation_state.record_exposure(
            getattr(features, 'extraction_timestamp', datetime.utcnow())
        )
        
        return attenuated_demand, tuple(evidence), updated_state
    
    def _apply_refractory_suppression(
        self,
        demand: float,
        features: AlertingFeatureVector,
        refractory_state: Optional[RefractoryState],
    ) -> Tuple[float, Tuple[str, ...], RefractoryState]:
        """
        Apply refractory suppression (immediate re-alerts are suppressed).
        
        Returns:
            Tuple of (suppressed_demand, evidence_tuple, updated_refractory_state)
        """
        if not refractory_state:
            # Default: no suppression
            return demand, (), RefractoryState()
        
        evidence = []
        
        # Check if in refractory period
        current_time = getattr(features, 'extraction_timestamp', datetime.utcnow())
        
        if refractory_state.is_suppressed(current_time):
            multiplier = refractory_state.suppression_multiplier(current_time)
            suppressed_demand = demand * multiplier
            
            suppression_amount = demand - suppressed_demand
            if suppression_amount > 0:
                evidence.append(f"refractory_suppression={suppression_amount:.3f}")
            
            # Update state (record new alert event)
            updated_state = refractory_state.record_alert(current_time)
        else:
            suppressed_demand = demand
            updated_state = refractory_state
        
        return suppressed_demand, tuple(evidence), updated_state
    
    def _build_evidence_summary(
        self,
        features: AlertingFeatureVector,
        base_demand: float,
    ) -> EvidenceSummary:
        """
        Build evidence summary for the assessment.
        
        Records which features contributed and how strongly.
        """
        # Find contributing features (non-zero values with validity)
        contributing = []
        contributions = []
        
        feature_names = [
            "absolute_change", "relative_change", "rate_of_change",
            "onset_appearance", "onset_activation", "onset_emergence",
            "offset_termination", "offset_disappearance", "offset_cessation",
            "local_contrast", "background_contrast", "context_contrast",
            "variance", "oscillation", "event_frequency",
            "prediction_error_estimate",
            "baseline_deviation", "history_deviation",
            "rapid_escalation", "critical_threshold",
        ]
        
        for name in feature_names:
            value = getattr(features, name, 0.0)
            if value and features.is_valid(name):
                contributing.append(name)
                # Contribution proportional to value
                contributions.append(value)
        
        total_contribution = sum(contributions) if contributions else 1.0
        normalized_contributions = tuple(c / total_contribution for c in contributions)
        
        return EvidenceSummary(
            contributing_features=tuple(contributing),
            contributions=normalized_contributions,
            active_feature_count=len(contributing),
            total_evidence_score=total_contribution,
            average_confidence=features.average_confidence if features.features_confidence else 0.5,
            min_confidence=min(features.features_confidence.values()) if features.features_confidence else 1.0,
        )
    
    def classify_level(self, demand_score: float) -> AlertingLevel:
        """
        Classify demand score into a level.
        
        Deterministic classification based on thresholds from config.
        """
        thresholds = self.config.classification
        
        if demand_score < thresholds.low_threshold:
            return AlertingLevel.NEGLIGIBLE
        elif demand_score < thresholds.moderate_threshold:
            return AlertingLevel.LOW
        elif demand_score < thresholds.high_threshold:
            return AlertingLevel.MODERATE
        elif demand_score < thresholds.critical_threshold:
            return AlertingLevel.HIGH
        else:
            return AlertingLevel.CRITICAL
    
    def generate_recommendation(
        self,
        level: AlertingLevel,
        confidence: float,
    ) -> AlertingRecommendation:
        """
        Generate advisory recommendation based on level and confidence.
        
        Never commands execution - only advises what action might be appropriate.
        """
        # High confidence + significant demand = request attention
        if level in (AlertingLevel.HIGH, AlertingLevel.CRITICAL):
            return AlertingRecommendation.REQUEST_URGENT_ATTENTION
        
        # Moderate demand with decent confidence
        if level == AlertingLevel.MODERATE:
            return AlertingRecommendation.REQUEST_ATTENTION
        
        # Low demand - just observe
        if level == AlertingLevel.LOW:
            return AlertingRecommendation.OBSERVE
        
        # Negligible - ignore
        return AlertingRecommendation.IGNORE
    
    def generate_reasons(
        self,
        features: AlertingFeatureVector,
        evidence_summary: EvidenceSummary,
        modulation_summary: ModulationSummary,
        level: AlertingLevel,
    ) -> Tuple[AlertingReason, ...]:
        """
        Generate structured reasons for the assessment.
        
        Every assessment must explain:
            - Why the demand was assigned
            - Which features contributed
            - How strongly each contributed
            - What modulation occurred
        
        Returns a tuple of AlertingReason instances (immutable).
        """
        reasons = []
        
        # Feature-based reasons (top contributors)
        for i, feature_name in enumerate(evidence_summary.contributing_features):
            if i >= 5:  # Limit to top 5 reasons
                break
            
            contribution = evidence_summary.contributions[i]
            
            # Determine category based on feature type
            if "onset" in feature_name.lower():
                category = AlertingReasonCategory.UNEXPECTED_ONSET
                description = f"Onset detected: {feature_name}"
            elif "offset" in feature_name.lower():
                category = AlertingReasonCategory.UNEXPECTED_OFFSET
                description = f"Offset detected: {feature_name}"
            elif "change" in feature_name.lower():
                category = AlertingReasonCategory.SUDDEN_INTENSITY_CHANGE
                description = f"Intensity change: {feature_name}"
            elif "contrast" in feature_name.lower():
                category = AlertingReasonCategory.HIGH_CONTRAST
                description = f"High contrast: {feature_name}"
            elif "novelty" in feature_name.lower() or "deviation" in feature_name.lower():
                category = AlertingReasonCategory.NOVELTY
                description = f"Novelty detected: {feature_name}"
            elif "urgency" in feature_name.lower() or "escalation" in feature_name.lower():
                category = AlertingReasonCategory.URGENCY
                description = f"Urgency indicator: {feature_name}"
            else:
                category = AlertingReasonCategory.PREDICTION_ERROR
                description = f"Feature signal: {feature_name}"
            
            reasons.append(AlertingReason(
                code=f"FEATURE_{feature_name.upper().replace('_', '')}",
                category=category,
                description=description,
                contribution=contribution,
                confidence=evidence_summary.average_confidence,
                evidence_reference=f"{feature_name}={getattr(features, feature_name, None)}",
            ))
        
        # Context modulation reasons (if any)
        for ctx_evidence in modulation_summary.context_evidence:
            if "task_criticality" in ctx_evidence.lower():
                reasons.append(AlertingReason(
                    code="CONTEXT_TASK_CRITICALITY",
                    category=AlertingReasonCategory.TASK_CRITICALITY_RESPONSE,
                    description="Task criticality increased demand",
                    contribution=self.config.relevance.task_criticality_weight * 0.5,
                    confidence=modulation_summary.base_demand * 0.8,
                    evidence_reference=ctx_evidence,
                ))
        
        # Habituation reasons (if attenuated)
        if modulation_summary.habituation_modulation > 0:
            reasons.append(AlertingReason(
                code="HABITUATION_ATTENUATION",
                category=AlertingReasonCategory.LOW_HABITUATION,
                description="Habituation reduced demand due to repeated exposure",
                contribution=-modulation_summary.habituation_modulation,
                confidence=0.9,
                evidence_reference=f"habituation_coefficient={1 - modulation_summary.habituation_modulation:.3f}",
            ))
        
        # Refractory reasons (if suppressed)
        if modulation_summary.refractory_modulation > 0:
            reasons.append(AlertingReason(
                code="REFRACTORY_SUPPRESSION",
                category=AlertingReasonCategory.REFRACTORY_SUPPRESSION,
                description="Refractory period suppressed immediate re-alert",
                contribution=-modulation_summary.refractory_suppression,
                confidence=0.95,
                evidence_reference=f"suppression_multiplier={1 - modulation_summary.refractory_modulation:.3f}",
            ))
        
        # If no specific reasons found, add a default
        if not reasons:
            reasons.append(AlertingReason(
                code="BASELINE_ASSESSMENT",
                category=AlertingReasonCategory.PREDICTION_ERROR,
                description="Assessment based on baseline signal characteristics",
                contribution=1.0,
                confidence=modulation_summary.base_demand * 0.5,
                evidence_reference=f"base_demand={modulation_summary.base_demand:.3f}",
            ))
        
        return tuple(reasons)
    
    def assess(
        self,
        alerting_input: AlertingInput,
        habituation_state: Optional[HabituationState] = None,
        refractory_state: Optional[RefractoryState] = None,
        timestamp: Optional[datetime] = None,
    ) -> AlertingAssessment:
        """
        Perform complete assessment of an input signal.
        
        This is the main entry point for producing an AlertingAssessment.
        
        Args:
            alerting_input: The signal to assess
            habituation_state: Current habituation state (for attenuation)
            refractory_state: Current refractory state (for suppression)
            timestamp: Override timestamp (defaults to input's timestamp)
            
        Returns:
            Immutable AlertingAssessment with all required fields
        """
        # Extract features from input (simplified - in production, would use FeatureAggregator)
        # For now, create a feature vector based on available values
        extraction_time = timestamp or alerting_input.timestamp
        
        features = AlertingFeatureVector(
            vector_id=alerting_input.signal_id,
            absolute_change=abs(alerting_input.intensity - (alerting_input.previous_intensity or 0.0))
            if alerting_input.intensity and alerting_input.previous_intensity else 0.0,
            relative_change=(alerting_input.intensity / max(0.01, alerting_input.background_intensity or 1.0)
                            if alerting_input.intensity and alerting_input.background_intensity else 0.0),
            rate_of_change=0.0,
            acceleration=0.0,
            onset_appearance=1.0 if alerting_input.onset else 0.0,
            onset_activation=1.0 if alerting_input.onset else 0.0,
            onset_emergence=0.5,
            offset_termination=1.0 if alerting_input.offset else 0.0,
            offset_disappearance=0.0,
            offset_cessation=0.0,
            local_contrast=alerting_input.intensity or 0.0,
            background_contrast=(alerting_input.intensity / max(0.01, alerting_input.background_intensity)
                                if alerting_input.background_intensity else 0.5),
            context_contrast=0.5,
            variance=0.2,
            oscillation=0.3,
            consistency=0.7,
            drift=0.1,
            event_frequency=alerting_input.attributes.get("event_frequency", 0.1) if alerting_input.attributes else 0.1,
            periodicity=0.5,
            burstiness=0.2,
            prediction_error_estimate=alerting_input.prediction_error or 0.0
            if alerting_input.prediction_error is not None else 0.3,
            baseline_deviation=0.4,
            history_deviation=0.3,
            recent_context_deviation=0.2,
            rapid_escalation=1.0 if (alerting_input.intensity and alerting_input.intensity > 0.8) else 0.0,
            critical_threshold=1.0 if (alerting_input.intensity and alerting_input.intensity > 0.9) else 0.0,
            time_sensitive_transition=0.5,
            task_criticality_projection=alerting_input.context.task_criticality
            if alerting_input.context and hasattr(alerting_input.context, 'task_criticality') else None,
            focus_strength_projection=alerting_input.context.focus_strength
            if alerting_input.context and hasattr(alerting_input.context, 'focus_strength') else None,
            resource_pressure_projection=alerting_input.context.resource_pressure
            if alerting_input.context and hasattr(alerting_input.context, 'resource_pressure') else None,
            features_confidence={
                "intensity": 0.95,
                "onset": 0.9 if alerting_input.onset else 0.1,
                "offset": 0.9 if alerting_input.offset else 0.1,
            },
            validity_flags={
                name: True for name in features.feature_names
            },
            extraction_timestamp=extraction_time,
            signal_id_reference=alerting_input.signal_id,
        )
        
        # Compute demand
        demand_score, confidence, evidence_summary, modulation_summary = self.compute_demand(
            features,
            alerting_input.context,
            habituation_state,
            refractory_state,
        )
        
        # Classify level
        level = self.classify_level(demand_score)
        
        # Generate recommendation
        recommendation = self.generate_recommendation(level, confidence)
        
        # Generate reasons
        reasons = self.generate_reasons(features, evidence_summary, modulation_summary, level)
        
        # Build assessment features
        assessment_features = AlertingFeatures(
            intensity=alerting_input.intensity or 0.0,
            delta_intensity=features.absolute_change,
            normalized_change=features.relative_change,
            onset_strength=features.onset_appearance,
            offset_strength=features.offset_termination,
            novelty=features.baseline_deviation,
            prediction_error=features.prediction_error_estimate,
            urgency=demand_score * 0.8,  # Urgency correlates with demand
            contrast=features.local_contrast,
            biological_relevance=0.3,  # Placeholder for now
            pattern_violation=features.oscillation,
            unexpected_onset=float(alerting_input.onset or False),
            unexpected_offset=float(alerting_input.offset or False),
            habituation=max(0.0, 1.0 - modulation_summary.habituation_modulation),
            refractory_attenuation=max(0.0, 1.0 - modulation_summary.refractory_modulation),
        )
        
        # Build modulation record
        assessment_modulation = AlertingModulation(
            positive_modulation=modulation_summary.positive_modulation,
            negative_modulation=modulation_summary.negative_modulation,
            focus_modulation=modulation_summary.context_modulation * 0.5,
            task_criticality_modulation=modulation_summary.context_modulation * 0.3,
            cognitive_load_modulation=0.0,  # Placeholder
            habituation_modulation=modulation_summary.habituation_modulation,
            refractory_modulation=modulation_summary.refractory_modulation,
        )
        
        # Build provenance
        assessment_provenance = AlertingProvenance(
            input_source=alerting_input.source,
            processed_at=extraction_time,
            config_version="4.1.4",
            seed_hash=None,  # For deterministic testing, this could be set
            caller_id=None,
        )
        
        return AlertingAssessment(
            assessment_id=f"assessment_{alerting_input.signal_id}",
            signal_id=alerting_input.signal_id,
            source=alerting_input.source,
            modality=alerting_input.modality,
            timestamp=alerting_input.timestamp,
            demand_score=demand_score,
            confidence=confidence,
            level=level,
            recommendation=recommendation,
            features=assessment_features,
            modulation=assessment_modulation,
            reasons=reasons,
            state_transition=None,  # Can be populated with state change info if needed
            provenance=assessment_provenance,
        )