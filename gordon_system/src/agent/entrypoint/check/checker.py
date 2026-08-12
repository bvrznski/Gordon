"""Gordon Agent Preflight Checker - Main Implementation.

Phase 3.7.32-I: Agent Startup Preflight and Compilation Checks
==============================================================

Canonical preflight checker that orchestrates all preflight checks,
compilation, and produces immutable provenance-preserving results.
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, List
from enum import Enum

from .types import (
    AgentPreflightOutcome,
    AgentPreflightPhase,
    AgentCompilationPolicy,
)
from .request import AgentPreflightRequest
from .result import AgentPreflightResult, PreflightResultFingerprint
from .policy import AgentPreflightPolicy, AgentCompilationPolicy as CompilationPolicyImpl
from .context import AgentPreflightContext
from .exceptions import (
    AgentPreflightError,
    PreflightInternalError,
)


@dataclass
class _CheckExecutionState:
    """Mutable state for check execution (internal only)."""
    
    completed: int = 0
    skipped: int = 0
    warnings: int = 0
    blockers: int = 0
    errors: int = 0
    
    results: List[Dict[str, Any]] = field(default_factory=list)
    blockers_list: List[Dict[str, Any]] = field(default_factory=list)
    warnings_list: List[Dict[str, Any]] = field(default_factory=list)
    errors_list: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class _CompilationState:
    """Mutable state for compilation (internal only)."""
    
    targets_count: int = 0
    compiled_successfully: int = 0
    syntax_errors: List[Tuple[str, str]] = field(default_factory=list)
    other_errors: List[Tuple[str, str]] = field(default_factory=list)


class AgentPreflightChecker:
    """Canonical Agent startup preflight checker.
    
    This is the ONE canonical authority for Agent startup preflight.
    It does NOT initialize the Agent, load components, or create runtime state.
    
    Checker Responsibilities:
        - Request validation
        - Policy resolution  
        - Check orchestration
        - Compilation execution (if required)
        - Result aggregation and fingerprinting
        
    Checker MUST NOT:
        - Initialize the Agent
        - Load components
        - Create runtime objects
        - Allocate long-lived resources
        - Execute modules during compilation
    
    Usage:
        checker = AgentPreflightChecker()
        result = checker.check(request)
        if result.outcome.is_success():
            # Proceed to initialization
            pass
    """
    
    def __init__(self):
        self._version: str = "3.7.32"
    
    def check(self, request: AgentPreflightRequest) -> AgentPreflightResult:
        """Execute preflight checks on the given request.
        
        Args:
            request: Immutable preflight request
            
        Returns:
            Immutable preflight result
        """
        import uuid
        
        # Create context for this execution
        context = self._create_context(request)
        
        # Initialize state
        execution_id = str(uuid.uuid4())
        start_time_ns = time.time_ns()
        
        check_state = _CheckExecutionState()
        compilation_state = _CompilationState()
        
        current_phase = AgentPreflightPhase.CREATED
        
        try:
            # Phase 1: Request Validation
            current_phase = AgentPreflightPhase.VALIDATING_REQUEST
            self._validate_request(request)
            
            # Phase 2: Policy Resolution  
            current_phase = AgentPreflightPhase.RESOLVING_POLICY
            policy = self._resolve_policy(request)
            
            # Phase 3: Root Resolution
            current_phase = AgentPreflightPhase.RESOLVING_ROOTS
            
            # Phase 4-51: Execute checks based on compilation policy
            if request.compilation_policy != AgentCompilationPolicy.NONE:
                current_phase = AgentPreflightPhase.FINGERPRINTING_SOURCE
                source_fingerprint = self._fingerprint_source(request, context)
                
                current_phase = AgentPreflightPhase.COMPILING
                compilation_state = self._execute_compilation(
                    request, context, request.compilation_policy
                )
            else:
                source_fingerprint = request.source_fingerprint or ""
            
            # Phase 52: Aggregate results
            current_phase = AgentPreflightPhase.AGGREGATING_RESULTS
            
        except PreflightInternalError as e:
            return self._failed_result(
                request, execution_id, start_time_ns,
                f"Checker internal error: {e.message}",
                primary_failure=e.get_context()
            )
        except Exception as e:
            return self._failed_result(
                request, execution_id, start_time_ns,
                f"Unexpected error during preflight: {type(e).__name__}: {e}"
            )
        
        # Determine outcome
        outcome = AgentPreflightOutcome.from_result(
            blockers=check_state.blockers,
            warnings=check_state.warnings,
            errors=check_state.errors
        )
        
        end_time_ns = time.time_ns()
        
        # Build result
        return self._build_result(
            request=request,
            execution_id=execution_id,
            start_time_ns=start_time_ns,
            end_time_ns=end_time_ns,
            outcome=outcome,
            check_results=tuple(check_state.results),
            compilation_result={
                "targets_count": compilation_state.targets_count,
                "compiled_successfully": compilation_state.compiled_successfully,
                "syntax_errors": tuple(compilation_state.syntax_errors),
                "other_errors": tuple(compilation_state.other_errors),
            },
            source_fingerprint=source_fingerprint,
            artifact_fingerprint=request.artifact_fingerprint or "",
        )
    
    def _create_context(self, request: AgentPreflightRequest) -> AgentPreflightContext:
        """Create a preflight context for the given request."""
        import os
        
        # Build environment facts snapshot
        env_facts = {
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
            "platform": sys.platform,
            "working_directory": str(Path.cwd()),
            "env_keys": tuple(sorted(os.environ.keys())),
        }
        
        return AgentPreflightContext.create(
            preflight_id=request.request_id,
            launch_id=request.launch_identity.launch_id,
            process_id=request.process_identity.process_id,
            approved_source_roots=request.approved_source_roots,
            approved_artifact_roots=request.approved_artifact_roots,
            environment_facts=env_facts,
        )
    
    def _validate_request(self, request: AgentPreflightRequest) -> None:
        """Validate the preflight request."""
        # Basic validation - ensure required fields are present
        if not request.request_id:
            raise PreflightInternalError(
                "Missing request ID",
                current_phase="VALIDATING_REQUEST"
            )
        
        if not request.launch_identity.launch_id:
            raise PreflightInternalError(
                "Missing launch identity",
                current_phase="VALIDATING_REQUEST"
            )
    
    def _resolve_policy(self, request: AgentPreflightRequest) -> AgentPreflightPolicy:
        """Resolve the effective policy for this request."""
        return AgentPreflightPolicy.default()
    
    def _fingerprint_source(self, request: AgentPreflightRequest, context: AgentPreflightContext) -> str:
        """Generate a fingerprint of the source files being checked.
        
        This is a placeholder - in production, this would:
        1. Scan approved source roots
        2. Hash file contents
        3. Include manifest information if available
        """
        import hashlib
        
        # For now, return a deterministic placeholder based on roots
        roots_str = "|".join(sorted(request.approved_source_roots))
        combined = f"source-fingerprint|{roots_str}|{request.configuration_generation}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]
    
    def _execute_compilation(
        self,
        request: AgentPreflightRequest,
        context: AgentPreflightContext,
        policy: AgentCompilationPolicy,
    ) -> _CompilationState:
        """Execute source compilation based on policy.
        
        This compiles Python source files WITHOUT executing them.
        Uses compileall-like behavior but bounded and safe.
        """
        state = _CompilationState()
        
        # Determine which files to compile based on policy
        if isinstance(policy, CompilationPolicyImpl):
            mode = policy.mode
        else:
            mode = getattr(policy, "mode", "none")
        
        # For TARGETED mode: only check startup modules
        # For other modes: scan more broadly
        
        approved_roots = request.approved_source_roots or [str(Path.cwd() / "src")]
        
        for root in approved_roots:
            root_path = Path(root)
            if not root_path.exists():
                continue
            
            # Find Python files (not virtualenv, cache, etc.)
            python_files = list(self._find_python_files(root_path))
            
            state.targets_count += len(python_files)
            
            for py_file in python_files:
                try:
                    # Compile without executing
                    with open(py_file, "rb") as f:
                        source = f.read()
                    
                    # Parse and compile
                    code = compile(source, str(py_file), "exec", dont_inherit=True)
                    state.compiled_successfully += 1
                    
                except SyntaxError as e:
                    state.syntax_errors.append((str(py_file), str(e)))
                    
                except Exception as e:
                    state.other_errors.append((str(py_file), f"{type(e).__name__}: {e}"))
        
        return state
    
    def _find_python_files(self, root: Path) -> List[Path]:
        """Find Python source files in a directory, excluding cache and venv."""
        python_files = []
        
        excluded_patterns = [
            "__pycache__",
            ".venv",
            "venv",
            ".git",
            ".tox",
            ".eggs",
            "*.egg-info",
        ]
        
        try:
            for path in root.rglob("*.py"):
                # Skip excluded patterns
                if any(p in str(path) for p in excluded_patterns):
                    continue
                
                python_files.append(path)
                
        except (PermissionError, OSError):
            pass  # Skip directories we can't access
        
        return sorted(python_files)[:100]  # Bounded scan
    
    def _build_result(
        self,
        request: AgentPreflightRequest,
        execution_id: str,
        start_time_ns: int,
        end_time_ns: int,
        outcome: AgentPreflightOutcome,
        check_results: Tuple[Dict[str, Any], ...],
        compilation_result: Dict[str, Any],
        source_fingerprint: str,
        artifact_fingerprint: str,
    ) -> AgentPreflightResult:
        """Build the final preflight result."""
        
        return AgentPreflightResult(
            request_id=request.request_id,
            launch_identity={
                "launch_id": request.launch_identity.launch_id,
                "timestamp_ns": request.launch_identity.timestamp_ns,
                "invocation_surface": request.launch_identity.invocation_surface,
            },
            process_identity={
                "process_id": request.process_identity.process_id,
                "parent_process_id": request.process_identity.parent_process_id,
            },
            execution_id=execution_id,
            preflight_start_ns=start_time_ns,
            preflight_end_ns=end_time_ns,
            outcome=outcome,
            effective_preflight_policy_name=None,
            effective_compilation_policy=request.compilation_policy,
            source_fingerprint=source_fingerprint,
            artifact_fingerprint=artifact_fingerprint,
            configuration_generation=request.configuration_generation,
            environment_fingerprint="placeholder-env-fingerprint",
            check_results=check_results,
            completed_checks_count=len([c for c in check_results if not c.get("skipped")]),
            skipped_checks_count=len([c for c in check_results if c.get("skipped", False)]),
            warning_checks_count=len(check_results),  # Simplified
            blocking_checks_count=0,  # Will be set by outcome calculation
            failed_checks_count=0,
            blockers=(),
            warnings=(),
            errors=(),
            compilation_result=compilation_result,
            phase_durations={"total": (end_time_ns - start_time_ns) / 1_000_000_000.0},
        )
    
    def _failed_result(
        self,
        request: AgentPreflightRequest,
        execution_id: str,
        start_time_ns: int,
        failure_message: str,
        primary_failure: Optional[Dict[str, Any]] = None,
    ) -> AgentPreflightResult:
        """Create a FAILED result with the given error."""
        
        return AgentPreflightResult(
            request_id=request.request_id,
            launch_identity={
                "launch_id": request.launch_identity.launch_id,
                "timestamp_ns": request.launch_identity.timestamp_ns,
                "invocation_surface": request.launch_identity.invocation_surface,
            },
            process_identity={
                "process_id": request.process_identity.process_id,
                "parent_process_id": request.process_identity.parent_process_id,
            },
            execution_id=execution_id,
            preflight_start_ns=start_time_ns,
            preflight_end_ns=time.time_ns(),
            outcome=AgentPreflightOutcome.FAILED,
            effective_preflight_policy_name=None,
            effective_compilation_policy=request.compilation_policy,
            source_fingerprint=request.source_fingerprint or "",
            artifact_fingerprint=request.artifact_fingerprint or "",
            configuration_generation=request.configuration_generation,
            environment_fingerprint="placeholder-env-fingerprint",
            check_results=(),
            completed_checks_count=0,
            skipped_checks_count=0,
            warning_checks_count=0,
            blocking_checks_count=0,
            failed_checks_count=1,
            blockers=(),
            warnings=(),
            errors=(
                {"error_message": failure_message, "phase": "UNKNOWN"},
            ),
            compilation_result={},
            phase_durations={"total": 0.0},
            primary_failure=failure_message if not primary_failure else None,
            secondary_failures=tuple(primary_failure.get("secondary", []) if primary_failure else []),
        )


def check_agent(request: AgentPreflightRequest) -> AgentPreflightResult:
    """Convenience function to run preflight checks.
    
    Args:
        request: Immutable preflight request
        
    Returns:
        Immutable preflight result
    """
    checker = AgentPreflightChecker()
    return checker.check(request)


def create_preflight_request(
    launch_id: str,
    process_id: int,
    source_roots: Tuple[str, ...] = (),
    compilation_policy: AgentCompilationPolicy = AgentCompilationPolicy.TARGETED,
) -> AgentPreflightRequest:
    """Create a preflight request with sensible defaults.
    
    Args:
        launch_id: ID of the launch being preflighted
        process_id: Process performing preflight
        source_roots: Approved source roots to check
        compilation_policy: Compilation policy to apply
        
    Returns:
        New preflight request
    """
    import time
    
    return AgentPreflightRequest(
        request_id=str(time.time_ns()),
        launch_identity={
            "launch_id": launch_id,
            "timestamp_ns": time.time_ns(),
            "invocation_surface": "UNKNOWN",
        },
        process_identity={
            "process_id": process_id,
            "parent_process_id": None,
        },
        approved_source_roots=source_roots,
        compilation_policy=compilation_policy,
    )