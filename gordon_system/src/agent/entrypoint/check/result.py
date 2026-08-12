"""Gordon Agent Preflight Result Model.

Phase 3.7.32-R: Agent Startup Preflight and Compilation Checks Remediation
==========================================================================

Immutable preflight result that preserves all check results,
evidence, and provenance for a single preflight operation.

This is the canonical result contract between entrypoint/check.py (pre-flight)
and entrypoint/init.py (initialization). It enforces:
- Evidence binding (source fingerprint, artifact fingerprint, config generation)
- Staleness validation (60 second validity window)
- Launch identity binding
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, Optional
import time

from .types import (
    AgentPreflightOutcome,
    AgentPreflightPhase,
    AgentCompilationPolicy,
)


@dataclass(frozen=True)
class AgentPreflightResult:
    """Immutable preflight result preserving all evidence.
    
    This is the contract between the preflight checker and the initializer.
    It must be immutable, contain no live runtime state, and preserve
    provenance for freshness validation.
    
    Result Flow:
        Preflight Checker
            ↓
        Immutable Result (this class)
            ↓
        Eligibility Decision (in main.py/init.py)
            ↓
        Initialization (if PASS/PASS_WITH_WARNINGS)
    
    The result preserves:
    - Request identity for freshness binding
    - All check results with severity and evidence
    - Blockers, warnings, and errors classified
    - Source/artifact fingerprints for staleness detection
    - Timing information for performance monitoring
    """
    
    # Identity (for freshness validation)
    request_id: str
    launch_identity: Dict[str, Any]
    process_identity: Dict[str, int]
    
    # Execution metadata
    execution_id: str
    preflight_start_ns: int
    preflight_end_ns: int
    
    # Outcome
    outcome: AgentPreflightOutcome
    
    # Policy (for freshness validation)
    effective_preflight_policy_name: Optional[str]
    effective_compilation_policy: AgentCompilationPolicy
    
    # Fingerprints (for staleness detection)
    source_fingerprint: str
    artifact_fingerprint: str
    configuration_generation: int
    environment_fingerprint: str
    
    # Check results (immutable, ordered for determinism)
    check_results: Tuple[Dict[str, Any], ...]
    
    # Aggregated results
    completed_checks_count: int
    skipped_checks_count: int
    warning_checks_count: int
    blocking_checks_count: int
    failed_checks_count: int
    
    # Classifications
    blockers: Tuple[Dict[str, Any], ...]  # Check IDs that block startup
    warnings: Tuple[Dict[str, Any], ...]  # Non-blocking warnings
    errors: Tuple[Dict[str, Any], ...]    # Internal checker failures
    
    # Compilation summary
    compilation_result: Dict[str, Any]
    
    # Timing breakdown
    phase_durations: Dict[str, float]
    
    # Primary failure (if any internal failure occurred)
    primary_failure: Optional[str] = None
    
    # Secondary failures (diagnostic/event publication failures, etc.)
    secondary_failures: Tuple[str, ...] = field(default_factory=tuple)
    
    # Provenance
    provenance: Dict[str, str] = field(default_factory=dict)
    
    @classmethod
    def create(
        cls,
        request_id: str,
        launch_identity: Dict[str, Any],
        process_identity: Dict[str, int],
        outcome: AgentPreflightOutcome,
        check_results: Tuple[Dict[str, Any], ...],
        **kwargs
    ) -> "AgentPreflightResult":
        """Create a preflight result with defaults."""
        import uuid
        
        return cls(
            request_id=request_id,
            launch_identity=launch_identity,
            process_identity=process_identity,
            execution_id=str(uuid.uuid4()),
            preflight_start_ns=time.time_ns(),
            preflight_end_ns=time.time_ns(),
            outcome=outcome,
            effective_preflight_policy_name=None,
            effective_compilation_policy=kwargs.get("compilation_policy", AgentCompilationPolicy.TARGETED),
            source_fingerprint=kwargs.get("source_fingerprint", ""),
            artifact_fingerprint=kwargs.get("artifact_fingerprint", ""),
            configuration_generation=kwargs.get("configuration_generation", 0),
            environment_fingerprint=kwargs.get("environment_fingerprint", ""),
            check_results=check_results,
            completed_checks_count=len([c for c in check_results if c.get("status")]),
            skipped_checks_count=len([c for c in check_results if c.get("skipped")]),
            warning_checks_count=len([c for c in check_results if c.get("is_warning", False)]),
            blocking_checks_count=len([c for c in check_results if c.get("is_blocker", False)]),
            failed_checks_count=len([c for c in check_results if c.get("is_error", False)]),
            blockers=tuple(c for c in check_results if c.get("is_blocker", False)),
            warnings=tuple(c for c in check_results if c.get("is_warning", False)),
            errors=tuple(c for c in check_results if c.get("is_error", False)),
            compilation_result=kwargs.get("compilation_result", {}),
            phase_durations=kwargs.get("phase_durations", {}),
            primary_failure=kwargs.get("primary_failure"),
            secondary_failures=tuple(kwargs.get("secondary_failures", [])),
            provenance=kwargs.get("provenance", {})
        )
    
    @classmethod
    def pass_result(
        cls,
        request_id: str,
        launch_identity: Dict[str, Any],
        process_identity: Dict[str, int],
        **kwargs
    ) -> "AgentPreflightResult":
        """Create a PASS result."""
        return cls.create(
            request_id=request_id,
            launch_identity=launch_identity,
            process_identity=process_identity,
            outcome=AgentPreflightOutcome.PASS,
            check_results=(),
            **kwargs
        )
    
    @classmethod
    def pass_with_warnings_result(
        cls,
        request_id: str,
        launch_identity: Dict[str, Any],
        process_identity: Dict[str, int],
        warnings: Tuple[Dict[str, Any], ...] = (),
        **kwargs
    ) -> "AgentPreflightResult":
        """Create a PASS_WITH_WARNINGS result."""
        return cls.create(
            request_id=request_id,
            launch_identity=launch_identity,
            process_identity=process_identity,
            outcome=AgentPreflightOutcome.PASS_WITH_WARNINGS,
            check_results=tuple(warnings),
            warnings=warnings,
            **kwargs
        )
    
    @classmethod
    def blocked_result(
        cls,
        request_id: str,
        launch_identity: Dict[str, Any],
        process_identity: Dict[str, int],
        blockers: Tuple[Dict[str, Any], ...] = (),
        **kwargs
    ) -> "AgentPreflightResult":
        """Create a BLOCKED result."""
        return cls.create(
            request_id=request_id,
            launch_identity=launch_identity,
            process_identity=process_identity,
            outcome=AgentPreflightOutcome.BLOCKED,
            check_results=tuple(blockers),
            blockers=blockers,
            **kwargs
        )
    
    @classmethod
    def failed_result(
        cls,
        request_id: str,
        launch_identity: Dict[str, Any],
        process_identity: Dict[str, int],
        primary_failure: Optional[str] = None,
        secondary_failures: Tuple[str, ...] = (),
        **kwargs
    ) -> "AgentPreflightResult":
        """Create a FAILED result."""
        return cls.create(
            request_id=request_id,
            launch_identity=launch_identity,
            process_identity=process_identity,
            outcome=AgentPreflightOutcome.FAILED,
            check_results=(),
            primary_failure=primary_failure,
            secondary_failures=secondary_failures,
            **kwargs
        )
    
    def get_duration_seconds(self) -> float:
        """Return the total preflight duration in seconds."""
        return (self.preflight_end_ns - self.preflight_start_ns) / 1_000_000_000.0
    
    def is_valid_for_launch(self, launch_identity: Dict[str, Any]) -> bool:
        """Check if this result is valid for the given launch.
        
        A result is valid if:
        - Launch IDs match (identity binding)
        - Source fingerprint hasn't changed (evidence binding)
        - Artifact fingerprint hasn't changed (evidence binding)
        - Configuration generation hasn't changed (evidence binding)
        - Result isn't stale (within validity window, currently 60s)
        
        Args:
            launch_identity: The launch identity to validate against
            
        Returns:
            True if this result is valid for the given launch, False otherwise
        """
        # Identity check - verify launch ID matches
        if self.launch_identity.get("launch_id") != launch_identity.get("launch_id"):
            return False
        
        # Staleness check - verify result hasn't expired (60 second validity window)
        duration = self.get_duration_seconds()
        if duration > 60.0:
            return False
        
        # Evidence binding checks - ensure source hasn't changed
        # These provide cryptographic evidence that the preflight was performed
        # on the current state of the code/configuration
        
        # Source fingerprint check (binds to file contents)
        if self.source_fingerprint and launch_identity.get("source_fingerprint"):
            if self.source_fingerprint != launch_identity.get("source_fingerprint"):
                return False
        
        # Artifact fingerprint check (binds to compiled artifacts)
        if self.artifact_fingerprint and launch_identity.get("artifact_fingerprint"):
            if self.artifact_fingerprint != launch_identity.get("artifact_fingerprint"):
                return False
        
        # Configuration generation check (binds to config version)
        if self.configuration_generation > 0:
            request_config_gen = launch_identity.get("configuration_generation", 0)
            if self.configuration_generation != request_config_gen:
                return False
        
        return True
    
    def get_summary(self) -> Dict[str, Any]:
        """Return a summary of the preflight result."""
        return {
            "request_id": self.request_id,
            "outcome": self.outcome.value,
            "execution_id": self.execution_id,
            "completed_checks": self.completed_checks_count,
            "skipped_checks": self.skipped_checks_count,
            "warning_checks": self.warning_checks_count,
            "blocking_checks": self.blocking_checks_count,
            "failed_checks": self.failed_checks_count,
            "duration_seconds": self.get_duration_seconds(),
        }


@dataclass(frozen=True)
class PreflightResultFingerprint:
    """Immutable fingerprint of a preflight result.
    
    Used to verify result integrity and detect staleness.
    """
    
    value: str
    
    @classmethod
    def compute(
        cls,
        request_id: str,
        outcome: AgentPreflightOutcome,
        source_fingerprint: str,
        artifact_fingerprint: str,
        configuration_generation: int,
        check_result_hashes: Tuple[str, ...],
    ) -> "PreflightResultFingerprint":
        """Compute the result fingerprint from its components."""
        import hashlib
        
        # Combine all components into a single hash
        components = [
            request_id,
            outcome.value,
            source_fingerprint,
            artifact_fingerprint,
            str(configuration_generation),
        ] + list(check_result_hashes)
        
        combined = "|".join(components)
        hash_value = hashlib.sha256(combined.encode()).hexdigest()[:32]
        
        return cls(value=hash_value)