# Alerting Network Contract Validation
# ======================================

"""
Contract validation for AlertingNetwork.

This module validates AlertingInput, AlertingAssessment, and related contracts.
It does NOT perform runtime assessment - only structural contract validation.
"""

from __future__ import annotations

from datetime import datetime


def validate_alerting_input(input_obj: object) -> bool:
    """
    Validate that an object conforms to the AlertingInput contract.
    
    This is a structural validator. It checks:
        - Required fields are present and of correct types
        - Enum values are from allowed sets
        - Numeric ranges are valid (0.0-1.0 where required)
        - Timestamps are datetime objects
    
    Args:
        input_obj: The object to validate.
    
    Returns:
        True if the object conforms to the contract, False otherwise.
    """
    # Basic type check - must be an AlertingInput or compatible
    from gordon_system.src.agent.components.networks.alerting.models import (
        AlertingInput,
    )
    from gordon_system.src.agent.components.networks.alerting.enums import (
        AlertingSource,
        AlertingModality,
    )
    
    if not isinstance(input_obj, AlertingInput):
        return False
    
    # Required fields must be non-None
    if input_obj.signal_id is None:
        return False
    
    if input_obj.source is None or not isinstance(input_obj.source, AlertingSource):
        return False
    
    if input_obj.modality is None or not isinstance(input_obj.modality, AlertingModality):
        return False
    
    if input_obj.timestamp is None or not isinstance(input_obj.timestamp, datetime):
        return False
    
    # Optional numeric fields must be in valid ranges if provided
    for field_name in ["intensity", "previous_intensity", "background_intensity"]:
        value = getattr(input_obj, field_name)
        if value is not None:
            if not (0.0 <= value <= 1.0):
                return False
    
    # Hint fields must be in valid range if provided
    for hint_field in [
        "novelty_hint", "urgency_hint", "prediction_error",
        "biological_relevance_hint"
    ]:
        value = getattr(input_obj, hint_field)
        if value is not None:
            if not (0.0 <= value <= 1.0):
                return False
    
    # Context fields
    context = input_obj.context
    if context is not None:
        for field in ["signal_relevance", "safety_relevance"]:
            value = getattr(context, field, None)
            if value is not None:
                if not (0.0 <= value <= 1.0):
                    return False
        
        for field in ["current_focus_strength", "current_task_criticality"]:
            value = getattr(context, field, None)
            if value is not None:
                if not (0.0 <= value <= 1.0):
                    return False
    
    return True


def validate_alerting_assessment(assessment_obj: object) -> bool:
    """
    Validate that an object conforms to the AlertingAssessment contract.
    
    Args:
        assessment_obj: The assessment to validate.
    
    Returns:
        True if the assessment conforms, False otherwise.
    """
    from gordon_system.src.agent.components.networks.alerting.models import (
        AlertingAssessment,
    )
    
    if not isinstance(assessment_obj, AlertingAssessment):
        return False
    
    # Core values must be in valid ranges
    if not (0.0 <= assessment_obj.demand_score <= 1.0):
        return False
    
    if not (0.0 <= assessment_obj.confidence <= 1.0):
        return False
    
    # Level and recommendation must be from allowed enums
    from gordon_system.src.agent.components.networks.alerting.enums import (
        AlertingLevel,
        AlertingRecommendation,
    )
    
    if not isinstance(assessment_obj.level, AlertingLevel):
        return False
    
    if not isinstance(assessment_obj.recommendation, AlertingRecommendation):
        return False
    
    # Timestamp must be datetime
    if not isinstance(assessment_obj.timestamp, datetime):
        return False
    
    return True


def validate_reset_request(request: object) -> bool:
    """
    Validate an AlertingResetRequest.
    
    Args:
        request: The reset request to validate.
    
    Returns:
        True if valid, False otherwise.
    """
    from gordon_system.src.agent.components.networks.alerting.models import (
        AlertingResetRequest,
    )
    
    if not isinstance(request, AlertingResetRequest):
        return False
    
    # All fields must be boolean
    return isinstance(request.is_full_reset, bool)