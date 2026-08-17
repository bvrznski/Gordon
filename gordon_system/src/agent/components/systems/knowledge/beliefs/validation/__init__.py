# Knowledge Belief System - Validation Module - Phase 6.6
# =========================================================

"""
Validation module for belief validation.

This module validates beliefs against semantic integrity rules and
provides tools for quality assurance of the belief system.
"""

from __future__ import annotations

import uuid
import time


class BeliefValidator:
    """
    Validates individual beliefs for semantic integrity.
    
    Checks that beliefs have minimal required data and meet
    validation criteria before being accepted into the belief system.
    """
    
    def __init__(
        self,
        minimum_confidence: float = 0.3,
        maximum_uncertainty: float = 0.95,
    ):
        """Initialize the validator."""
        self._min_confidence = minimum_confidence
        self._max_uncertainty = maximum_uncertainty
    
    @property
    def minimum_confidence(self) -> float:
        """Get minimum acceptable confidence threshold."""
        return self._min_confidence
    
    @property
    def maximum_uncertainty(self) -> float:
        """Get maximum acceptable uncertainty threshold."""
        return self._max_uncertainty
    
    def validate_identity(
        self,
        belief_id: str,
    ) -> tuple[bool, str | None]:
        """
        Validate belief identity.
        
        Args:
            belief_id: The belief ID to validate
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        if not belief_id or len(belief_id) == 0:
            return False, "Missing belief identity"
        
        # Check format
        if not isinstance(belief_id, str):
            return False, f"Identity must be string, got {type(belief_id)}"
        
        return True, None
    
    def validate_semantic_reference(
        self,
        semantic_identity: str,
    ) -> tuple[bool, str | None]:
        """
        Validate semantic identity reference.
        
        Args:
            semantic_identity: The semantic reference to validate
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        if not semantic_identity or len(semantic_identity) == 0:
            return False, "Missing semantic identity reference"
        
        return True, None
    
    def validate_confidence(
        self,
        confidence: float,
    ) -> tuple[bool, str | None]:
        """
        Validate confidence measure.
        
        Args:
            confidence: The confidence value to validate
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        if not isinstance(confidence, (int, float)):
            return False, f"Confidence must be numeric, got {type(confidence)}"
        
        if confidence < 0.0 or confidence > 1.0:
            return False, f"Confidence out of range: {confidence} (must be 0.0-1.0)"
        
        return True, None
    
    def validate_uncertainty(
        self,
        uncertainty: float,
    ) -> tuple[bool, str | None]:
        """
        Validate uncertainty measure.
        
        Args:
            uncertainty: The uncertainty value to validate
            
        Returns:
            Tuple of (is_valid, error_message if invalid)
        """
        if not isinstance(uncertainty, (int, float)):
            return False, f"Uncertainty must be numeric, got {type(uncertainty)}"
        
        if uncertainty < 0.0 or uncertainty > 1.0:
            return False, f"Uncertainty out of range: {uncertainty} (must be 0.0-1.0)"
        
        return True, None
    
    def validate_base_belief(
        self,
        belief_id: str,
        semantic_identity: str,
        confidence: float = 0.5,
        uncertainty: float = 0.5,
    ) -> tuple[bool, list[str]]:
        """
        Validate a base belief's minimal requirements.
        
        Args:
            belief_id: The belief's identity
            semantic_identity: The assertion's identity being believed
            confidence: Confidence measure (default: 0.5)
            uncertainty: Uncertainty measure (default: 0.5)
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        valid, msg = self.validate_identity(belief_id)
        if not valid:
            issues.append(msg)
        
        valid, msg = self.validate_semantic_reference(semantic_identity)
        if not valid:
            issues.append(msg)
        
        valid, msg = self.validate_confidence(confidence)
        if not valid:
            issues.append(msg)
        
        valid, msg = self.validate_uncertainty(uncertainty)
        if not valid:
            issues.append(msg)
        
        return len(issues) == 0, issues
    
    def validate_full_belief(
        self,
        belief_data: dict,
    ) -> tuple[bool, list[str]]:
        """
        Validate a complete belief data dictionary.
        
        Args:
            belief_data: Full belief data dictionary
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check required fields
        if "belief_identity" not in belief_data:
            issues.append("Missing 'belief_identity' field")
        
        if "semantic_identity" not in belief_data:
            issues.append("Missing 'semantic_identity' field")
        
        confidence = belief_data.get("confidence", 0.5)
        uncertainty = belief_data.get("uncertainty", 0.5)
        
        valid, msg = self.validate_confidence(confidence)
        if not valid:
            issues.append(f"Confidence: {msg}")
        
        valid, msg = self.validate_uncertainty(uncertainty)
        if not valid:
            issues.append(f"Uncertainty: {msg}")
        
        # Check confidence + uncertainty sum
        total = confidence + uncertainty
        if not (0.8 <= total <= 1.2):
            issues.append(
                f"Confidence-uncertainty imbalance: {total:.2f} "
                f"(should be approximately 1.0)"
            )
        
        return len(issues) == 0, issues


class ValidationEngine:
    """
    Engine for comprehensive belief validation.
    
    Orchestrates multiple validators and tracks validation results
    over time.
    """
    
    def __init__(self):
        """Initialize the engine."""
        self._validators: list = []
        self._results: list = []
    
    @property
    def validator_count(self) -> int:
        """Get count of registered validators."""
        return len(self._validators)
    
    def register_validator(
        self,
        name: str,
        validate_func: callable,
    ):
        """
        Register a validation function.
        
        Args:
            name: Name of the validator
            validate_func: Function that takes belief data and returns (is_valid, issues)
        """
        self._validators.append({
            "name": name,
            "validate": validate_func,
        })
    
    def validate(
        self,
        belief_data: dict,
    ) -> tuple[bool, list[str]]:
        """
        Run all validators on a belief.
        
        Args:
            belief_data: Full belief data dictionary
            
        Returns:
            Tuple of (is_valid, combined_issues)
        """
        all_issues = []
        
        for v in self._validators:
            valid, issues = v["validate"](belief_data)
            if not valid and issues:
                all_issues.extend(issues)
        
        result = {
            "validation_id": f"val:{uuid.uuid4().hex[:16]}",
            "timestamp_utc": time.time(),
            "is_valid": len(all_issues) == 0,
            "issues": all_issues,
        }
        
        self._results.append(result)
        
        return len(all_issues) == 0, all_issues
    
    def get_results(self) -> list:
        """Get all validation results."""
        return list(self._results)
    
    def clear_results(self):
        """Clear validation results (for reset)."""
        self._results.clear()


class ValidationHistory:
    """
    Maintains complete validation history for a belief.
    
    Tracks when beliefs were validated and whether they passed,
    enabling audit trails and quality analysis.
    """
    
    def __init__(self, belief_id: str):
        """Initialize the history tracker."""
        self._belief_id = belief_id
        self._entries: list = []
    
    @property
    def entry_count(self) -> int:
        """Get count of recorded entries."""
        return len(self._entries)
    
    def add_entry(
        self,
        validation_id: str,
        is_valid: bool,
        issues: list[str] = None,
        timestamp_utc: float = None,
    ):
        """
        Add a validation entry.
        
        Args:
            validation_id: ID of the validation
            is_valid: Whether the belief passed validation
            issues: List of issue descriptions (optional)
            timestamp_utc: Entry timestamp (default: now)
        """
        self._entries.append({
            "validation_id": validation_id,
            "is_valid": bool(is_valid),
            "issues": list(issues or []),
            "timestamp_utc": timestamp_utc or time.time(),
        })
    
    def get_all_entries(self) -> list:
        """Get all history entries in order."""
        return list(self._entries)
    
    def get_latest_entry(self) -> dict | None:
        """Get the most recent entry."""
        if not self._entries:
            return None
        return self._entries[-1]
    
    def to_dict(self) -> dict:
        """Convert history to dictionary."""
        return {
            "belief_id": self._belief_id,
            "entry_count": len(self._entries),
            "latest_valid": (
                self._entries[-1]["is_valid"] if self._entries else None
            ),
            "entries": self._entries,
        }


__all__ = [
    "BeliefValidator",
    "ValidationEngine",
    "ValidationHistory",
]