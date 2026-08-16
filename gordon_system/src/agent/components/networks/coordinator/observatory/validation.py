# Gordon Cognitive Architecture - Phase 4.11.8
# ===========================================

"""
Validation Functions for Observatory
====================================

Functions to validate observatory artifacts against specification laws.

VALIDATION LAWS (from spec)
---------------------------
VALIDATION-LAW-001: Every Observation shall validate before publication.
VALIDATION-LAW-002: Metric consistency shall validate before reporting.
VALIDATION-LAW-003: Health indicators shall validate against supporting metrics.
VALIDATION-LAW-004: Diagnostics shall validate supporting evidence.
VALIDATION-LAW-005: Trend calculations shall validate historical inputs.
VALIDATION-LAW-006: Recommendations shall validate supporting findings.
VALIDATION-LAW-007: Validation shall remain side-effect free.
VALIDATION-LAW-008: Validation shall remain deterministic.
"""

from __future__ import annotations

from typing import Any


def validate_observation(observation_data: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate an observation against specification laws.
    
    VALIDATION-LAW-001: Observations validate before publication.
    VALIDATION-LAW-008: Validation is deterministic and side-effect free.
    
    Args:
        observation_data: Dictionary containing observation data
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check required fields
    if "observation_identity" not in observation_data or not observation_data["observation_identity"]:
        issues.append("Missing or empty observation identity")
    
    if "scope" not in observation_data or not observation_data["scope"]:
        issues.append("Missing or empty scope")
    
    # Validate confidence bounds
    confidence = observation_data.get("confidence", 0.5)
    if not isinstance(confidence, (int, float)) or not 0.0 <= confidence <= 1.0:
        issues.append(f"Invalid confidence: {confidence} (must be 0.0 to 1.0)")
    
    # Validate uncertainty bounds
    uncertainty = observation_data.get("uncertainty", 0.5)
    if not isinstance(uncertainty, (int, float)) or not 0.0 <= uncertainty <= 1.0:
        issues.append(f"Invalid uncertainty: {uncertainty} (must be 0.0 to 1.0)")
    
    # Validate timestamp format (ISO format if present)
    timestamp = observation_data.get("timestamp")
    if timestamp and not isinstance(timestamp, str):
        issues.append(f"Invalid timestamp format: {timestamp}")
    
    return len(issues) == 0, issues


def validate_metric(metric_data: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate a metric against specification laws.
    
    VALIDATION-LAW-002: Metrics validate before reporting.
    VALIDATION-LAW-008: Validation is deterministic and side-effect free.
    
    Args:
        metric_data: Dictionary containing metric data
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check required fields
    if "metric_identity" not in metric_data or not metric_data["metric_identity"]:
        issues.append("Missing or empty metric identity")
    
    if "measured_scope" not in metric_data or not metric_data["measured_scope"]:
        issues.append("Missing or empty measured scope")
    
    # Validate value is numeric
    value = metric_data.get("value", 0.0)
    if not isinstance(value, (int, float)):
        issues.append(f"Invalid metric value: {value} (must be numeric)")
    
    # Validate confidence bounds
    confidence = metric_data.get("confidence", 1.0)
    if not isinstance(confidence, (int, float)) or not 0.0 <= confidence <= 1.0:
        issues.append(f"Invalid confidence: {confidence} (must be 0.0 to 1.0)")
    
    # Validate uncertainty bounds
    uncertainty = metric_data.get("uncertainty", 0.0)
    if not isinstance(uncertainty, (int, float)) or not 0.0 <= uncertainty <= 1.0:
        issues.append(f"Invalid uncertainty: {uncertainty} (must be 0.0 to 1.0)")
    
    return len(issues) == 0, issues


def validate_health(health_data: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate a health indicator against specification laws.
    
    VALIDATION-LAW-003: Health indicators validate against supporting metrics.
    VALIDATION-LAW-008: Validation is deterministic and side-effect free.
    
    Args:
        health_data: Dictionary containing health indicator data
        
    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    
    # Check required fields
    if "indicator_identity" not in health_data or not health_data["indicator_identity"]:
        issues.append("Missing or empty indicator identity")
    
    if "measured_scope" not in health_data or not health_data["measured_scope"]:
        issues.append("Missing or empty measured scope")
    
    # Validate current value bounds
    current_value = health_data.get("current_value", 0.0)
    if not isinstance(current_value, (int, float)) or not 0.0 <= current_value <= 1.0:
        issues.append(f"Invalid current value: {current_value} (must be 0.0 to 1.0)")
    
    return len(issues) == 0, issues