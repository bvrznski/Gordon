# Alerting Feature Extraction Modules
# ====================================

"""
Feature extraction modules for transforming AlertingSignals into AlertingEvidence.

Architecture:
    - Each analyzer performs exactly one type of analysis
    - All analyzers are independently replaceable
    - No behavioral decisions or attention demand estimation
    - Pure deterministic feature extraction

Feature Families:
    - Change Detection: absolute change, relative change, rate of change, acceleration
    - Onset Detection: appearance, activation, emergence
    - Offset Detection: termination, disappearance, cessation
    - Contrast Detection: local contrast, background contrast, context contrast
    - Temporal Stability: variance, oscillation, consistency, drift
    - Frequency Analysis: event frequency, periodicity, burstiness
    - Prediction Error: expected signal vs observed signal deviation
    - Novelty: deviation from baseline, history, recent context
    - Urgency Indicators: rapid escalation, critical thresholds, time-sensitive transitions
    - Context Projection: task criticality, focus strength, resource pressure

Public API:
    AlertingFeatureVector: Aggregated features with provenance and confidence
    
Usage:
    Each analyzer takes a Signal and produces one or more Features.
    The FeatureAggregator combines all features into an Evidence object.
"""

from .analyzers import (
    ChangeDetector,
    OnsetDetector,
    OffsetDetector,
    ContrastAnalyzer,
    TemporalStabilityAnalyzer,
    FrequencyAnalyzer,
    PredictionErrorAnalyzer,
    NoveltyAnalyzer,
    UrgencyIndicatorAnalyzer,
    ContextProjectionAnalyzer,
    FeatureAggregator,
)

from .vector import AlertingFeatureVector, validate_feature_vector

__all__ = (
    # Analyzers
    "ChangeDetector",
    "OnsetDetector", 
    "OffsetDetector",
    "ContrastAnalyzer",
    "TemporalStabilityAnalyzer",
    "FrequencyAnalyzer",
    "PredictionErrorAnalyzer",
    "NoveltyAnalyzer",
    "UrgencyIndicatorAnalyzer",
    "ContextProjectionAnalyzer",
    # Aggregator
    "FeatureAggregator",
    # Output model
    "AlertingFeatureVector",
    "validate_feature_vector",
)