# Default Network Validation
# =========================

"""
Deterministic validation for the DefaultNetwork.

Validation ensures inputs, outputs, and assessments are semantically correct
and maintain proper ownership boundaries without runtime machinery.

PHASE 4.3.1: Semantic Validation Only
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


# =============================================================================
# VALIDATION RESULT (single check result)
# =============================================================================

@dataclass(frozen=True, slots=True)
class ValidationResult:
    """
    Result of a single validation check.
    
    Used to report validation outcomes without runtime dependencies.
    """
    
    # Check identifier
    check_id: str
    
    # Whether validation passed
    is_valid: bool
    
    # Optional error message (only present if not valid)
    error_message: Optional[str] = None
    
    # Optional suggestion for fixing the issue
    suggestion: Optional[str] = None


# =============================================================================
# VALIDATION SUMMARY
# =============================================================================

@dataclass(frozen=True, slots=True)
class ValidationSummary:
    """
    Summary of all validation checks performed.
    
    Collects individual results into a complete assessment.
    """
    
    # Overall validity
    is_valid: bool
    
    # Total checks performed
    total_checks: int
    
    # Checks that passed
    passed_checks: int
    
    # Checks that failed
    failed_checks: int
    
    # Individual results (frozen tuple)
    results: Tuple[ValidationResult, ...] = field(default_factory=tuple)


# =============================================================================
# INPUT VALIDATION
# =============================================================================

def validate_input(input_id: str) -> ValidationResult:
    """
    Validate an input has a valid identity.
    
    Args:
        input_id: The input ID to validate
        
    Returns:
        ValidationResult indicating pass/fail
    """
    if not input_id or len(input_id) > 256:
        return ValidationResult(
            check_id="input_id_valid",
            is_valid=False,
            error_message="Input ID must be non-empty and under 256 characters",
            suggestion="Use a valid string identifier for the input",
        )
    return ValidationResult(check_id="input_id_valid", is_valid=True)


def validate_input_context(context: dict) -> Tuple[ValidationResult, ...]:
    """
    Validate an input context.
    
    Args:
        context: The context dictionary to validate
        
    Returns:
        Tuple of validation results
    """
    results = []
    
    # Validate focus strength if present (must be 0.0-1.0)
    focus_strength = context.get("active_focus_strength")
    if focus_strength is not None:
        if not isinstance(focus_strength, (int, float)) or not (0.0 <= focus_strength <= 1.0):
            results.append(ValidationResult(
                check_id="focus_strength_valid",
                is_valid=False,
                error_message="Focus strength must be a number in [0.0, 1.0]",
                suggestion="Use a normalized float value between 0.0 and 1.0",
            ))
    
    # Validate task criticality if present
    task_criticality = context.get("current_task_criticality")
    if task_criticality is not None:
        if not isinstance(task_criticality, (int, float)) or not (0.0 <= task_criticality <= 1.0):
            results.append(ValidationResult(
                check_id="task_criticality_valid",
                is_valid=False,
                error_message="Task criticality must be a number in [0.0, 1.0]",
                suggestion="Use a normalized float value between 0.0 and 1.0",
            ))
    
    # Validate semantic weight if present
    semantic_weight = context.get("semantic_weight")
    if semantic_weight is not None:
        if not isinstance(semantic_weight, (int, float)) or not (0.0 <= semantic_weight <= 1.0):
            results.append(ValidationResult(
                check_id="semantic_weight_valid",
                is_valid=False,
                error_message="Semantic weight must be a number in [0.0, 1.0]",
                suggestion="Use a normalized float value between 0.0 and 1.0",
            ))
    
    if not results:
        results.append(ValidationResult(
            check_id="input_context_valid",
            is_valid=True,
        ))
    
    return tuple(results)


def validate_input_batch(inputs: Tuple[dict, ...]) -> ValidationSummary:
    """
    Validate a batch of inputs.
    
    Args:
        inputs: Tuple of input dictionaries to validate
        
    Returns:
        ValidationSummary for the entire batch
    """
    results = []
    total_checks = 0
    
    # Check count bounds (bounded)
    if len(inputs) > 1000:
        results.append(ValidationResult(
            check_id="batch_size_valid",
            is_valid=False,
            error_message="Batch size exceeds maximum of 1000 inputs",
            suggestion="Split the batch into smaller groups",
        ))
    
    for input_data in inputs:
        total_checks += 1
        input_id = input_data.get("input_id", "")
        result = validate_input(input_id)
        results.append(result)
        
        # Validate context if present
        if "context_hint" in input_data:
            context_results = validate_input_context(input_data["context_hint"])
            results.extend(context_results)
    
    passed_count = sum(1 for r in results if r.is_valid)
    is_valid = all(r.is_valid for r in results)
    
    return ValidationSummary(
        is_valid=is_valid,
        total_checks=total_checks + len(results),
        passed_checks=passed_count,
        failed_checks=len(results) - passed_count,
        results=tuple(results),
    )


# =============================================================================
# OUTPUT VALIDATION
# =============================================================================

def validate_output_type(output_type: str) -> ValidationResult:
    """
    Validate that an output type is recognized.
    
    Args:
        output_type: The output type to validate
        
    Returns:
        ValidationResult indicating pass/fail
    """
    valid_types = {
        "proposal",
        "assessment",
    }
    
    if output_type not in valid_types:
        return ValidationResult(
            check_id="output_type_valid",
            is_valid=False,
            error_message=f"Unknown output type: {output_type}",
            suggestion="Use 'proposal' or 'assessment'",
        )
    return ValidationResult(check_id="output_type_valid", is_valid=True)


def validate_confidence(confidence: float) -> ValidationResult:
    """
    Validate that a confidence value is in valid range.
    
    Args:
        confidence: The confidence value to validate
        
    Returns:
        ValidationResult indicating pass/fail
    """
    if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
        return ValidationResult(
            check_id="confidence_valid",
            is_valid=False,
            error_message="Confidence must be a number in [0.0, 1.0]",
            suggestion="Use a normalized float value between 0.0 and 1.0",
        )
    return ValidationResult(check_id="confidence_valid", is_valid=True)


def validate_output_count(count: int) -> ValidationResult:
    """
    Validate that output count is within bounds.
    
    Args:
        count: The output count to validate
        
    Returns:
        ValidationResult indicating pass/fail
    """
    if not isinstance(count, int):
        return ValidationResult(
            check_id="output_count_valid",
            is_valid=False,
            error_message="Output count must be an integer",
            suggestion="Use a positive integer value",
        )
    
    max_count = 10
    if count < 0 or count > max_count:
        return ValidationResult(
            check_id="output_count_valid",
            is_valid=False,
            error_message=f"Output count must be in [0, {max_count}]",
            suggestion=f"Use a value between 0 and {max_count}",
        )
    return ValidationResult(check_id="output_count_valid", is_valid=True)


# =============================================================================
# ASSESSMENT VALIDATION
# =============================================================================

def validate_assessment_level(level: float) -> ValidationResult:
    """
    Validate that an assessment level is in valid range.
    
    Args:
        level: The assessment level to validate (should be 0.0-1.0)
        
    Returns:
        ValidationResult indicating pass/fail
    """
    if not isinstance(level, (int, float)) or not (0.0 <= level <= 1.0):
        return ValidationResult(
            check_id="assessment_level_valid",
            is_valid=False,
            error_message="Assessment level must be a number in [0.0, 1.0]",
            suggestion="Use a normalized float value between 0.0 and 1.0",
        )
    return ValidationResult(check_id="assessment_level_valid", is_valid=True)


def validate_internal_orientation_score(score: float) -> ValidationResult:
    """
    Validate that an internal orientation score is in valid range.
    
    Args:
        score: The internal orientation score to validate
        
    Returns:
        ValidationResult indicating pass/fail
    """
    if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
        return ValidationResult(
            check_id="orientation_score_valid",
            is_valid=False,
            error_message="Internal orientation score must be a number in [0.0, 1.0]",
            suggestion="Use a normalized float value between 0.0 and 1.0",
        )
    return ValidationResult(check_id="orientation_score_valid", is_valid=True)


# =============================================================================
# OUTPUT VALIDATION (additional helpers)
# =============================================================================

def validate_output(output_id: str, output_type: str) -> ValidationResult:
    """
    Validate an output has valid identity and type.
    
    Args:
        output_id: The output ID to validate
        output_type: The output type to validate
        
    Returns:
        ValidationResult indicating pass/fail
    """
    id_result = validate_input(output_id)
    
    if not id_result.is_valid:
        return id_result
    
    valid_types = {"proposal", "assessment"}
    if output_type not in valid_types:
        return ValidationResult(
            check_id="output_type_valid",
            is_valid=False,
            error_message=f"Invalid output type: {output_type}",
            suggestion="Use 'proposal' or 'assessment'",
        )
    
    return ValidationResult(check_id="output_valid", is_valid=True)


def validate_assessment(activation_level: float, confidence: float) -> ValidationResult:
    """
    Validate an assessment has valid values.
    
    Args:
        activation_level: The activation level (0.0-1.0)
        confidence: The confidence value (0.0-1.0)
        
    Returns:
        ValidationResult indicating pass/fail
    """
    if not isinstance(activation_level, (int, float)) or not (0.0 <= activation_level <= 1.0):
        return ValidationResult(
            check_id="assessment_activation_valid",
            is_valid=False,
            error_message="Activation level must be a number in [0.0, 1.0]",
            suggestion="Use a normalized float value between 0.0 and 1.0",
        )
    
    if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
        return ValidationResult(
            check_id="assessment_confidence_valid",
            is_valid=False,
            error_message="Confidence must be a number in [0.0, 1.0]",
            suggestion="Use a normalized float value between 0.0 and 1.0",
        )
    
    return ValidationResult(check_id="assessment_valid", is_valid=True)


# =============================================================================
# STATE CONSISTENCY VALIDATION
# =============================================================================

def validate_state_consistency(state: dict) -> ValidationSummary:
    """
    Validate that state values are consistent.
    
    Args:
        state: The state dictionary to validate
        
    Returns:
        ValidationSummary for the state
    """
    results = []
    
    # Check activation level if present
    activation_level = state.get("activation_level")
    if activation_level is not None:
        result = validate_assessment_level(activation_level)
        results.append(result)
    
    # Check internal orientation score if present
    orientation_score = state.get("internal_orientation_score")
    if orientation_score is not None:
        result = validate_internal_orientation_score(orientation_score)
        results.append(result)
    
    # Check proposal count if present (bounded)
    proposal_count = state.get("proposal_count")
    if proposal_count is not None:
        result = validate_output_count(proposal_count)
        results.append(result)
    
    # Check confidence if present
    confidence = state.get("confidence")
    if confidence is not None:
        result = validate_confidence(confidence)
        results.append(result)
    
    if not results:
        results.append(ValidationResult(
            check_id="state_consistency_valid",
            is_valid=True,
        ))
    
    passed_count = sum(1 for r in results if r.is_valid)
    
    return ValidationSummary(
        is_valid=passed_count == len(results),
        total_checks=len(results),
        passed_checks=passed_count,
        failed_checks=len(results) - passed_count,
        results=tuple(results),
    )