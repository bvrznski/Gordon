# Precision Validation - Phase 4.9.4
# ====================================

"""
Validation module for Precision Estimation Engine.

Provides validation functions for precision estimates and landscapes.
"""

from __future__ import annotations

from typing import Any


def validate_precision_estimate(estimate: dict[str, Any]) -> tuple[bool, str]:
    """
    Validate a single precision estimate.
    
    Args:
        estimate: PrecisionEstimate as dictionary
        
    Returns:
        (is_valid, error_message) tuple
    """
    # Required fields check
    required = {"identity", "target_prediction_error", "precision"}
    for field in required:
        if field not in estimate:
            return False, f"Missing required field: {field}"
    
    # Type validation
    if not isinstance(estimate.get("identity"), str):
        return False, "precision identity must be a string"
    if not isinstance(estimate.get("target_prediction_error"), str):
        return False, "precision target_prediction_error must be a string"
    
    # Range validation
    precision = estimate.get("precision")
    if not isinstance(precision, (int, float)) or not (0.0 <= precision <= 1.0):
        return False, "precision must be in [0.0, 1.0]"
    
    confidence = estimate.get("confidence", 0.5)
    if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
        return False, "precision confidence must be in [0.0, 1.0]"
    
    # Source validation
    sources = estimate.get("sources", [])
    for source in sources:
        if isinstance(source, dict):
            value = source.get("value", 0.5)
            if not isinstance(value, (int, float)) or not (0.0 <= value <= 1.0):
                return False, "source value must be in [0.0, 1.0]"
    
    return True, ""


def validate_precision_landscape(landscape: dict[str, Any]) -> tuple[bool, str]:
    """
    Validate a precision landscape.
    
    Args:
        landscape: PrecisionLandscape as dictionary
        
    Returns:
        (is_valid, error_message) tuple
    """
    # Required fields check
    if "estimates" not in landscape:
        return False, "Missing required field: estimates"
    
    # Estimates must be tuple or list
    estimates = landscape.get("estimates", ())
    if not isinstance(estimates, (tuple, list)):
        return False, "precision estimates must be a tuple or list"
    
    # Validate each estimate
    for i, estimate in enumerate(estimates):
        is_valid, error_msg = validate_precision_estimate(estimate)
        if not is_valid:
            return False, f"Estimate {i}: {error_msg}"
    
    # Hierarchy validation (if present)
    hierarchy = landscape.get("hierarchy")
    if hierarchy and not isinstance(hierarchy, dict):
        return False, "precision hierarchy must be a dictionary"
    
    return True, ""