# Reward Network - Serialization Module (Phase 4.10.4)
# ======================================================

"""
Serialization module for temporal reward analysis results.

Implements deterministic serialization of all Phase 4.10.4 components
without using any non-deterministic operations.
"""

from __future__ import annotations

import json as _json
from typing import Any, Dict, Tuple, Optional


# =============================================================================
# SERIALIZATION CONTRACT
# =============================================================================

class SerializationError(Exception):
    """Raised when serialization fails."""
    
    def __init__(self, message: str, context: Optional[str] = None):
        self.message = message
        self.context = context
        super().__init__(f"SerializationError: {message}" + (f" ({context})" if context else ""))


class DeserializationError(Exception):
    """Raised when deserialization fails."""
    
    def __init__(self, message: str, context: Optional[str] = None):
        self.message = message
        self.context = context
        super().__init__(f"DeserializationError: {message}" + (f" ({context})" if context else ""))


# =============================================================================
# CANONICAL SERIALIZATION - RewardTrajectory
# =============================================================================

def serialize_trajectory(trajectory) -> Dict[str, Any]:
    """Serialize a RewardTrajectory to dictionary."""
    return {
        "trajectory_id": str(getattr(trajectory, 'trajectory_id', '')),
        "estimate_ref": str(getattr(trajectory, 'estimate_ref', '')),
        "trajectory_type": str(getattr(trajectory, 'trajectory_type', '')),
        "revision": int(getattr(trajectory, 'revision', 0)),
        "trend": str(getattr(trajectory, 'trend', 'stable')),
        "stability": float(getattr(trajectory, 'stability', 1.0)),
        "volatility": float(getattr(trajectory, 'volatility', 0.0)),
        "timescale": str(getattr(trajectory, 'timescale', 'medium_term')),
        "confidence": float(getattr(trajectory, 'confidence', 1.0)),
        "uncertainty": float(getattr(trajectory, 'uncertainty', 0.0)),
        "baseline_ref": str(getattr(trajectory, 'baseline_ref', '')) if getattr(trajectory, 'baseline_ref', None) else None,
        "history_window": int(getattr(trajectory, 'history_window', 1)),
        "provenance": str(getattr(trajectory, 'provenance', '')) if getattr(trajectory, 'provenance', None) else None,
        "findings": tuple(str(f) for f in getattr(trajectory, 'findings', ())),
        "trace": tuple(str(t) for t in getattr(trajectory, 'trace', ())),
    }


def serialize_trajectory_collection(collection) -> Dict[str, Any]:
    """Serialize a trajectory collection."""
    if not collection:
        return None
    return {
        "collection_id": str(getattr(collection, 'collection_id', '')),
        "revision": int(getattr(collection, 'revision', 0)),
        "trajectories": [serialize_trajectory(t) for t in getattr(collection, 'trajectories', ())],
        "dominant_pattern": str(getattr(collection, 'dominant_pattern', 'unknown')),
        "summary_trend": str(getattr(collection, 'summary_trend', 'stable')),
        "aggregate_stability": float(getattr(collection, 'aggregate_stability', 1.0)),
        "timescales_analyzed": tuple(str(t) for t in getattr(collection, 'timescales_analyzed', ())),
        "provenance": str(getattr(collection, 'provenance', '')) if getattr(collection, 'provenance', None) else None,
        "findings": tuple(str(f) for f in getattr(collection, 'findings', ())),
        "trace": tuple(str(t) for t in getattr(collection, 'trace', ())),
    }


# =============================================================================
# CANONICAL SERIALIZATION - AdaptiveRewardBaseline
# =============================================================================

def serialize_baseline(baseline) -> Dict[str, Any]:
    """Serialize an AdaptiveRewardBaseline to dictionary."""
    return {
        "baseline_id": str(getattr(baseline, 'baseline_id', '')),
        "domain": str(getattr(baseline, 'domain', '')),
        "current_value": float(getattr(baseline, 'current_value', 0.0)),
        "revision": int(getattr(baseline, 'revision', 0)),
        "adaptation_history": tuple(
            (str(e), float(v)) for e, v in getattr(baseline, 'adaptation_history', ())
        ),
        "initial_value": float(getattr(baseline, 'initial_value', 0.0)),
        "adaptation_rate": float(getattr(baseline, 'adaptation_rate', 0.1)),
        "last_adaptation_event": str(getattr(baseline, 'last_adaptation_event', '')) if getattr(baseline, 'last_adaptation_event', None) else None,
        "confidence": float(getattr(baseline, 'confidence', 1.0)),
        "uncertainty": float(getattr(baseline, 'uncertainty', 0.0)),
        "context_signature": tuple(str(s) for s in getattr(baseline, 'context_signature', ())),
        "provenance": str(getattr(baseline, 'provenance', '')) if getattr(baseline, 'provenance', None) else None,
        "findings": tuple(str(f) for f in getattr(baseline, 'findings', ())),
        "trace": tuple(str(t) for t in getattr(baseline, 'trace', ())),
    }


# =============================================================================
# CANONICAL SERIALIZATION - RewardTrend
# =============================================================================

def serialize_trend(trend) -> Dict[str, Any]:
    """Serialize a RewardTrend to dictionary."""
    return {
        "trend_id": str(getattr(trend, 'trend_id', '')),
        "domain": str(getattr(trend, 'domain', '')),
        "direction": str(getattr(trend, 'direction', 'stable')),
        "revision": int(getattr(trend, 'revision', 0)),
        "velocity": float(getattr(trend, 'velocity', 0.0)),
        "acceleration": float(getattr(trend, 'acceleration', 0.0)),
        "consistency": float(getattr(trend, 'consistency', 1.0)),
        "persistence": int(getattr(trend, 'persistence', 0)),
        "max_persistence": int(getattr(trend, 'max_persistence', 0)),
        "confidence": float(getattr(trend, 'confidence', 1.0)),
        "uncertainty": float(getattr(trend, 'uncertainty', 0.0)),
        "observation_window": int(getattr(trend, 'observation_window', 1)),
        "data_points": tuple(float(v) for v in getattr(trend, 'data_points', ())),
        "provenance": str(getattr(trend, 'provenance', '')) if getattr(trend, 'provenance', None) else None,
        "findings": tuple(str(f) for f in getattr(trend, 'findings', ())),
        "trace": tuple(str(t) for t in getattr(trend, 'trace', ())),
    }


def serialize_trend_collection(collection) -> Dict[str, Any]:
    """Serialize a trend collection."""
    if not collection:
        return None
    return {
        "collection_id": str(getattr(collection, 'collection_id', '')),
        "revision": int(getattr(collection, 'revision', 0)),
        "trends": [serialize_trend(t) for t in getattr(collection, 'trends', ())],
        "dominant_direction": str(getattr(collection, 'dominant_direction', 'stable')),
        "aggregate_velocity": float(getattr(collection, 'aggregate_velocity', 0.0)),
        "aggregate_consistency": float(getattr(collection, 'aggregate_consistency', 1.0)),
        "domains_analyzed": tuple(str(d) for d in getattr(collection, 'domains_analyzed', ())),
        "provenance": str(getattr(collection, 'provenance', '')) if getattr(collection, 'provenance', None) else None,
        "findings": tuple(str(f) for f in getattr(collection, 'findings', ())),
        "trace": tuple(str(t) for t in getattr(collection, 'trace', ())),
    }


# =============================================================================
# CANONICAL SERIALIZATION - RewardStability
# =============================================================================

def serialize_stability(stability) -> Dict[str, Any]:
    """Serialize a RewardStability to dictionary."""
    return {
        "stability_id": str(getattr(stability, 'stability_id', '')),
        "domain": str(getattr(stability, 'domain', '')),
        "value": float(getattr(stability, 'value', 1.0)),
        "revision": int(getattr(stability, 'revision', 0)),
        "resilience": float(getattr(stability, 'resilience', 1.0)),
        "persistence": int(getattr(stability, 'persistence', 0)),
        "max_persistence": int(getattr(stability, 'max_persistence', 0)),
        "variance": float(getattr(stability, 'variance', 0.0)),
        "standard_deviation": float(getattr(stability, 'standard_deviation', 0.0)),
        "coefficient_of_variation": float(getattr(stability, 'coefficient_of_variation', 0.0)),
        "classification": str(getattr(stability, 'classification', 'unknown')),
        "confidence": float(getattr(stability, 'confidence', 1.0)),
        "uncertainty": float(getattr(stability, 'uncertainty', 0.0)),
        "observation_window": int(getattr(stability, 'observation_window', 1)),
        "data_points": tuple(float(v) for v in getattr(stability, 'data_points', ())),
        "provenance": str(getattr(stability, 'provenance', '')) if getattr(stability, 'provenance', None) else None,
        "findings": tuple(str(f) for f in getattr(stability, 'findings', ())),
        "trace": tuple(str(t) for t in getattr(stability, 'trace', ())),
    }


def serialize_stability_collection(collection) -> Dict[str, Any]:
    """Serialize a stability collection."""
    if not collection:
        return None
    return {
        "collection_id": str(getattr(collection, 'collection_id', '')),
        "revision": int(getattr(collection, 'revision', 0)),
        "stabilities": [serialize_stability(s) for s in getattr(collection, 'stabilities', ())],
        "dominant_classification": str(getattr(collection, 'dominant_classification', 'unknown')),
        "aggregate_stability": float(getattr(collection, 'aggregate_stability', 1.0)),
        "aggregate_resilience": float(getattr(collection, 'aggregate_resilience', 1.0)),
        "domains_analyzed": tuple(str(d) for d in getattr(collection, 'domains_analyzed', ())),
        "provenance": str(getattr(collection, 'provenance', '')) if getattr(collection, 'provenance', None) else None,
        "findings": tuple(str(f) for f in getattr(collection, 'findings', ())),
        "trace": tuple(str(t) for t in getattr(collection, 'trace', ())),
    }


# =============================================================================
# CANONICAL SERIALIZATION - RewardVolatility
# =============================================================================

def serialize_volatility(volatility) -> Dict[str, Any]:
    """Serialize a RewardVolatility to dictionary."""
    return {
        "volatility_id": str(getattr(volatility, 'volatility_id', '')),
        "domain": str(getattr(volatility, 'domain', '')),
        "value": float(getattr(volatility, 'value', 0.0)),
        "revision": int(getattr(volatility, 'revision', 0)),
        "amplitude": float(getattr(volatility, 'amplitude', 0.0)),
        "frequency": float(getattr(volatility, 'frequency', 0.0)),
        "transience": int(getattr(volatility, 'transience', 0)),
        "variance": float(getattr(volatility, 'variance', 0.0)),
        "standard_deviation": float(getattr(volatility, 'standard_deviation', 0.0)),
        "max_deviation": float(getattr(volatility, 'max_deviation', 0.0)),
        "min_value": float(getattr(volatility, 'min_value', 0.0)),
        "max_value": float(getattr(volatility, 'max_value', 0.0)),
        "classification": str(getattr(volatility, 'classification', 'unknown')),
        "confidence": float(getattr(volatility, 'confidence', 1.0)),
        "uncertainty": float(getattr(volatility, 'uncertainty', 0.0)),
        "observation_window": int(getattr(volatility, 'observation_window', 1)),
        "data_points": tuple(float(v) for v in getattr(volatility, 'data_points', ())),
        "provenance": str(getattr(volatility, 'provenance', '')) if getattr(volatility, 'provenance', None) else None,
        "findings": tuple(str(f) for f in getattr(volatility, 'findings', ())),
        "trace": tuple(str(t) for t in getattr(volatility, 'trace', ())),
    }


def serialize_volatility_collection(collection) -> Dict[str, Any]:
    """Serialize a volatility collection."""
    if not collection:
        return None
    return {
        "collection_id": str(getattr(collection, 'collection_id', '')),
        "revision": int(getattr(collection, 'revision', 0)),
        "volatilities": [serialize_volatility(v) for v in getattr(collection, 'volatilities', ())],
        "dominant_classification": str(getattr(collection, 'dominant_classification', 'unknown')),
        "aggregate_volatility": float(getattr(collection, 'aggregate_volatility', 0.0)),
        "aggregate_amplitude": float(getattr(collection, 'aggregate_amplitude', 0.0)),
        "domains_analyzed": tuple(str(d) for d in getattr(collection, 'domains_analyzed', ())),
        "provenance": str(getattr(collection, 'provenance', '')) if getattr(collection, 'provenance', None) else None,
        "findings": tuple(str(f) for f in getattr(collection, 'findings', ())),
        "trace": tuple(str(t) for t in getattr(collection, 'trace', ())),
    }


# =============================================================================
# CANONICAL SERIALIZATION - RewardDrift
# =============================================================================

def serialize_drift(drift) -> Dict[str, Any]:
    """Serialize a RewardDrift to dictionary."""
    return {
        "drift_id": str(getattr(drift, 'drift_id', '')),
        "domain": str(getattr(drift, 'domain', '')),
        "direction": str(getattr(drift, 'direction', 'neutral')),
        "revision": int(getattr(drift, 'revision', 0)),
        "magnitude": float(getattr(drift, 'magnitude', 0.0)),
        "rate": float(getattr(drift, 'rate', 0.0)),
        "persistence": int(getattr(drift, 'persistence', 0)),
        "max_persistence": int(getattr(drift, 'max_persistence', 0)),
        "cumulative_change": float(getattr(drift, 'cumulative_change', 0.0)),
        "variance_of_change": float(getattr(drift, 'variance_of_change', 0.0)),
        "classification": str(getattr(drift, 'classification', 'unknown')),
        "confidence": float(getattr(drift, 'confidence', 1.0)),
        "uncertainty": float(getattr(drift, 'uncertainty', 0.0)),
        "observation_window": int(getattr(drift, 'observation_window', 1)),
        "data_points": tuple(float(v) for v in getattr(drift, 'data_points', ())),
        "provenance": str(getattr(drift, 'provenance', '')) if getattr(drift, 'provenance', None) else None,
        "findings": tuple(str(f) for f in getattr(drift, 'findings', ())),
        "trace": tuple(str(t) for t in getattr(drift, 'trace', ())),
    }


def serialize_drift_collection(collection) -> Dict[str, Any]:
    """Serialize a drift collection."""
    if not collection:
        return None
    return {
        "collection_id": str(getattr(collection, 'collection_id', '')),
        "revision": int(getattr(collection, 'revision', 0)),
        "drifts": [serialize_drift(d) for d in getattr(collection, 'drifts', ())],
        "dominant_direction": str(getattr(collection, 'dominant_direction', 'neutral')),
        "aggregate_magnitude": float(getattr(collection, 'aggregate_magnitude', 0.0)),
        "aggregate_rate": float(getattr(collection, 'aggregate_rate', 0.0)),
        "domains_analyzed": tuple(str(d) for d in getattr(collection, 'domains_analyzed', ())),
        "provenance": str(getattr(collection, 'provenance', '')) if getattr(collection, 'provenance', None) else None,
        "findings": tuple(str(f) for f in getattr(collection, 'findings', ())),
        "trace": tuple(str(t) for t in getattr(collection, 'trace', ())),
    }


# =============================================================================
# CANONICAL SERIALIZATION - RewardHomeostasis
# =============================================================================

def serialize_homeostasis(homeostasis) -> Dict[str, Any]:
    """Serialize a RewardHomeostasis to dictionary."""
    return {
        "homeostasis_id": str(getattr(homeostasis, 'homeostasis_id', '')),
        "domain": str(getattr(homeostasis, 'domain', '')),
        "revision": int(getattr(homeostasis, 'revision', 0)),
        "equilibrium_estimate": float(getattr(homeostasis, 'equilibrium_estimate', 0.0)),
        "current_state": str(getattr(homeostasis, 'current_state', 'equilibrium')),
        "deviation_from_equilibrium": float(getattr(homeostasis, 'deviation_from_equilibrium', 0.0)),
        "adaptation_pressure": float(getattr(homeostasis, 'adaptation_pressure', 0.0)),
        "recovery_trend": str(getattr(homeostasis, 'recovery_trend', 'stable')),
        "confidence": float(getattr(homeostasis, 'confidence', 1.0)),
        "uncertainty": float(getattr(homeostasis, 'uncertainty', 0.0)),
        "observation_window": int(getattr(homeostasis, 'observation_window', 1)),
        "data_points": tuple(float(v) for v in getattr(homeostasis, 'data_points', ())),
        "provenance": str(getattr(homeostasis, 'provenance', '')) if getattr(homeostasis, 'provenance', None) else None,
        "findings": tuple(str(f) for f in getattr(homeostasis, 'findings', ())),
        "trace": tuple(str(t) for t in getattr(homeostasis, 'trace', ())),
    }


def serialize_homeostasis_collection(collection) -> Dict[str, Any]:
    """Serialize a homeostasis collection."""
    if not collection:
        return None
    return {
        "collection_id": str(getattr(collection, 'collection_id', '')),
        "revision": int(getattr(collection, 'revision', 0)),
        "states": [serialize_homeostasis(s) for s in getattr(collection, 'states', ())],
        "dominant_state": str(getattr(collection, 'dominant_state', 'equilibrium')),
        "aggregate_adaptation_pressure": float(getattr(collection, 'aggregate_adaptation_pressure', 0.0)),
        "aggregate_deviation": float(getattr(collection, 'aggregate_deviation', 0.0)),
        "domains_analyzed": tuple(str(d) for d in getattr(collection, 'domains_analyzed', ())),
        "provenance": str(getattr(collection, 'provenance', '')) if getattr(collection, 'provenance', None) else None,
        "findings": tuple(str(f) for f in getattr(collection, 'findings', ())),
        "trace": tuple(str(t) for t in getattr(collection, 'trace', ())),
    }


# =============================================================================
# CANONICAL SERIALIZATION - RewardHistory
# =============================================================================

def serialize_history_entry(entry) -> Dict[str, Any]:
    """Serialize a RewardHistoryEntry to dictionary."""
    return {
        "entry_id": str(getattr(entry, 'entry_id', '')),
        "revision": int(getattr(entry, 'revision', 0)),
        "timestamp": str(getattr(entry, 'timestamp', '')),
        "sequence_number": int(getattr(entry, 'sequence_number', 0)),
        "landscape_id": str(getattr(entry, 'landscape_id', '')),
        "estimate_refs": tuple(str(r) for r in getattr(entry, 'estimate_refs', ())),
        "total_magnitude": float(getattr(entry, 'total_magnitude', 0.0)),
        "positive_count": int(getattr(entry, 'positive_count', 0)),
        "negative_count": int(getattr(entry, 'negative_count', 0)),
        "neutral_count": int(getattr(entry, 'neutral_count', 0)),
        "provenance": str(getattr(entry, 'provenance', '')) if getattr(entry, 'provenance', None) else None,
        "trace": tuple(str(t) for t in getattr(entry, 'trace', ())),
    }


def serialize_history(history) -> Dict[str, Any]:
    """Serialize a RewardHistory to dictionary."""
    return {
        "history_id": str(getattr(history, 'history_id', '')),
        "revision": int(getattr(history, 'revision', 0)),
        "entries": [serialize_history_entry(e) for e in getattr(history, 'entries', ())],
        "provenance": str(getattr(history, 'provenance', '')) if getattr(history, 'provenance', None) else None,
        "findings": tuple(str(f) for f in getattr(history, 'findings', ())),
        "trace": tuple(str(t) for t in getattr(history, 'trace', ())),
    }


# =============================================================================
# CANONICAL SERIALIZATION - TemporalRewardState
# =============================================================================

def serialize_temporal_state(state) -> Dict[str, Any]:
    """Serialize a TemporalRewardState to dictionary."""
    return {
        "state_id": str(getattr(state, 'state_id', '')),
        "revision": int(getattr(state, 'revision', 0)),
        "trajectories": [serialize_trajectory(t) for t in getattr(state, 'trajectories', ())],
        "baselines": [serialize_baseline(b) for b in getattr(state, 'baselines', ())],
        "trends": [serialize_trend(t) for t in getattr(state, 'trends', ())],
        "stability": [serialize_stability(s) for s in getattr(state, 'stability', ())],
        "volatility": [serialize_volatility(v) for v in getattr(state, 'volatility', ())],
        "drift": [serialize_drift(d) for d in getattr(state, 'drift', ())],
        "homeostasis": [serialize_homeostasis(h) for h in getattr(state, 'homeostasis', ())],
        "trajectory_collection": serialize_trajectory_collection(getattr(state, 'trajectory_collection', None)),
        "trend_collection": serialize_trend_collection(getattr(state, 'trend_collection', None)),
        "stability_collection": serialize_stability_collection(getattr(state, 'stability_collection', None)),
        "volatility_collection": serialize_volatility_collection(getattr(state, 'volatility_collection', None)),
        "drift_collection": serialize_drift_collection(getattr(state, 'drift_collection', None)),
        "homeostasis_collection": serialize_homeostasis_collection(getattr(state, 'homeostasis_collection', None)),
        "dominant_trajectory_pattern": str(getattr(state, 'dominant_trajectory_pattern', 'unknown')),
        "dominant_trend_direction": str(getattr(state, 'dominant_trend_direction', 'stable')),
        "aggregate_stability": float(getattr(state, 'aggregate_stability', 1.0)),
        "aggregate_volatility": float(getattr(state, 'aggregate_volatility', 0.0)),
        "observation_window": int(getattr(state, 'observation_window', 1)),
        "timescales_analyzed": tuple(str(t) for t in getattr(state, 'timescales_analyzed', ())),
        "domains_analyzed": tuple(str(d) for d in getattr(state, 'domains_analyzed', ())),
        "history": serialize_history(getattr(state, 'history', None)) if getattr(state, 'history', None) else None,
        "provenance": str(getattr(state, 'provenance', '')) if getattr(state, 'provenance', None) else None,
        "findings": tuple(str(f) for f in getattr(state, 'findings', ())),
        "limitations": tuple(str(l) for l in getattr(state, 'limitations', ())),
        "trace": tuple(str(t) for t in getattr(state, 'trace', ())),
    }


# =============================================================================
# JSON SERIALIZATION
# =============================================================================

def json_serialize_trajectory(trajectory) -> str:
    """Serialize trajectory to JSON string."""
    return _json.dumps(serialize_trajectory(trajectory), ensure_ascii=True)


def json_serialize_baseline(baseline) -> str:
    """Serialize baseline to JSON string."""
    return _json.dumps(serialize_baseline(baseline), ensure_ascii=True)


def json_serialize_temporal_state(state) -> str:
    """Serialize temporal state to JSON string."""
    return _json.dumps(serialize_temporal_state(state), ensure_ascii=True)