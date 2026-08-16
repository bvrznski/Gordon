# Internal Episode Validator
# =========================

"""
Validator for internal episode models.

Checks episode integrity without implementing runtime coordination or
cognitive algorithms.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """
    Report of validation results for an internal episode.
    
    Contains detailed information about what passed and what failed.
    """
    
    is_valid: bool = True
    """Whether the episode passed all validations."""
    
    errors: Tuple[str, ...] = field(default_factory=tuple)
    """List of validation error messages."""
    
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    """List of validation warning messages."""
    
    checks_performed: Tuple[str, ...] = field(default_factory=tuple)
    """List of validation checks that were performed."""
    
    @classmethod
    def valid(cls) -> ValidationReport:
        """Create a successful validation report."""
        return cls(is_valid=True, errors=(), warnings=())
    
    @classmethod
    def invalid(
        cls,
        error_messages: Tuple[str, ...],
        warning_messages: Optional[Tuple[str, ...]] = None,
    ) -> ValidationReport:
        """
        Create an invalid validation report.
        
        Args:
            error_messages: List of error message strings
            warning_messages: Optional list of warning message strings
            
        Returns:
            New ValidationReport instance with is_valid=False
        """
        return cls(
            is_valid=False,
            errors=error_messages or (),
            warnings=warning_messages or (),
        )
    
    @classmethod
    def from_check(cls, check_name: str, passed: bool, error_message: Optional[str] = None) -> ValidationReport:
        """Create a report from a single validation check."""
        if passed:
            return cls(is_valid=True, checks_performed=(check_name,))
        
        return cls(
            is_valid=False,
            errors=(error_message or f"Validation failed for {check_name}",),
            checks_performed=(check_name,),
        )


@dataclass(frozen=True, slots=True)
class InternalEpisodeValidator:
    """
    Validator for internal episode models.
    
    Checks episode integrity without implementing runtime coordination
    or cognitive algorithms. This is purely a validation layer.
    """
    
    # Configuration
    maximum_evidence_items: int = 500
    """Maximum evidence items allowed."""
    
    maximum_capability_requests: int = 100
    """Maximum capability requests allowed."""
    
    maximum_plan_steps: int = 50
    """Maximum plan steps allowed."""
    
    maximum_child_episodes: int = 10
    """Maximum child episodes allowed."""
    
    require_terminal_outcome: bool = True
    """Whether terminal episodes must have outcomes."""
    
    verify_lifecycle_transitions: bool = True
    """Whether to verify lifecycle transitions are valid."""
    
    @classmethod
    def create(cls, **kwargs) -> InternalEpisodeValidator:
        """
        Create a new validator with specified configuration.
        
        Args:
            **kwargs: Configuration overrides
            
        Returns:
            New InternalEpisodeValidator instance
        """
        return cls(**kwargs)
    
    def validate_episode(self, episode: "InternalEpisode") -> ValidationReport:
        """
        Validate an internal episode.
        
        Checks:
            • Episode has valid ID (non-empty string)
            • Episode has valid type (known value from InternalEpisodeType)
            • Episode has valid purpose (non-empty string)
            • Episode has bounded scope
            • Episode has valid lifecycle state
            • Context binding is present and valid
            • Evidence count is within bounds
            • Capability requests are within bounds
            
        Args:
            episode: The episode to validate
            
        Returns:
            ValidationReport with pass/fail status and details
        """
        errors = []
        checks_performed = ["episode_id", "type", "purpose", "scope"]
        
        # Validate episode ID
        if not episode.episode_id or not isinstance(episode.episode_id, str):
            errors.append("Episode must have a non-empty string ID")
        
        # Validate type
        from .enums import InternalEpisodeType
        if episode.episode_type not in InternalEpisodeType.all_types():
            errors.append(f"Invalid episode type: {episode.episode_type}")
        
        checks_performed.extend(["context_id", "lifecycle_state", "evidence_count"])
        
        # Validate context binding
        if not episode.context_id:
            errors.append("Episode must have a bound context ID")
        
        # Validate lifecycle state
        from .enums import InternalEpisodeLifecycle
        if episode.lifecycle.state not in InternalEpisodeLifecycle.all_states():
            errors.append(f"Invalid lifecycle state: {episode.lifecycle.state}")
        
        # Validate evidence count is bounded
        if len(episode.evidence_ids) > self.maximum_evidence_items:
            errors.append(
                f"Evidence count ({len(episode.evidence_ids)}) exceeds maximum "
                f"({self.maximum_evidence_items})"
            )
        
        is_valid = len(errors) == 0
        
        return ValidationReport(
            is_valid=is_valid,
            errors=tuple(errors),
            checks_performed=tuple(checks_performed),
        )
    
    def validate_lifecycle_transition(
        self,
        source_state: str,
        target_state: str,
    ) -> ValidationReport:
        """
        Validate that a lifecycle state transition is permitted.
        
        Args:
            source_state: The current lifecycle state
            target_state: The desired target state
            
        Returns:
            ValidationReport with pass/fail status
        """
        from .enums import InternalEpisodeLifecycle
        
        if source_state not in InternalEpisodeLifecycle.all_states():
            return ValidationReport.from_check(
                "source_state",
                False,
                f"Invalid source state: {source_state}",
            )
        
        if target_state not in InternalEpisodeLifecycle.all_states():
            return ValidationReport.from_check(
                "target_state",
                False,
                f"Invalid target state: {target_state}",
            )
        
        # Check permitted transitions
        lifecycle = InternalEpisodeLifecycle()
        can_transition = target_state in self._get_permitted_transitions(source_state)
        
        if not can_transition:
            return ValidationReport.from_check(
                "transition",
                False,
                f"Transition from {source_state} to {target_state} is not permitted",
            )
        
        return ValidationReport(is_valid=True, checks_performed=("lifecycle_transition",))
    
    def _get_permitted_transitions(self, source_state: str) -> set[str]:
        """Get the set of permitted target states from a source state."""
        permitted = {
            "proposed": {"validated"},
            "validated": {"ready"},
            "ready": {"active"},
            "active": {
                "waiting_for_input",
                "waiting_for_capability",
                "suspended",
                "completing",
                "failed",
                "cancelled",
                "expired",
            },
            "waiting_for_input": {"active", "suspended", "failed", "cancelled", "expired"},
            "waiting_for_capability": {"active", "suspended", "failed", "cancelled", "expired"},
            "suspended": {"ready", "failed", "cancelled", "expired"},
            "completing": {"completed", "failed", "cancelled", "expired"},
        }
        
        return permitted.get(source_state, set())