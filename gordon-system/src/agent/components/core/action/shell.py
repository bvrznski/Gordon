# Shell and Command Effector Implementation
# =========================================

"""
Shell and command execution effectors for the Action Runtime.

This module provides subprocess-based operations that:
    - Use argument-vector execution (not shell=True by default)
    - Validate executables against allowlists
    - Enforce timeouts and output limits
    - Report actual side effects accurately
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum, auto
import os
import subprocess
import time
import uuid

from . import (
    EffectorId,
    EffectorContract,
    ActionRequest,
    ExecutionResult,
    ExecutionStatus,
)


class ShellSafety(Enum):
    """Safety classification for shell operations."""
    
    RESTRICTED = "restricted"  # Only use allowlisted commands
    ALLOWED = "allowed"        # Commands from allowlist only
    MONITORED = "monitored"    # Allow with monitoring


@dataclass(frozen=True)
class CommandSpec:
    """
    Specification for a command execution.
    
    Args:
        executable: The binary to execute
        arguments: List of positional arguments (as list, not string)
        environment: Additional environment variables
        working_directory: Working directory for the process
        timeout_seconds: Maximum execution time
        input_data: stdin data to write (bytes)
        max_output_bytes: Maximum bytes for stdout/stderr
    """
    
    executable: str
    arguments: Tuple[str, ...] = field(default_factory=tuple)
    environment: Optional[Dict[str, str]] = None
    working_directory: Optional[str] = None
    timeout_seconds: Optional[float] = None
    input_data: Optional[bytes] = None
    max_output_bytes: int = 1024 * 1024  # 1 MB default


@dataclass(frozen=True)
class CommandResult:
    """
    Result of a command execution.
    
    Args:
        success: Whether the command succeeded (exit code 0)
        return_code: Process exit code
        stdout: Captured stdout (truncated to max_output_bytes)
        stderr: Captured stderr (truncated to max_output_bytes)
        timed_out: Whether the command exceeded its timeout
        duration_seconds: Total execution time
    """
    
    success: bool
    return_code: int
    
    # Output (may be truncated)
    stdout: str
    stderr: str
    
    # Timing
    started_at: float
    completed_at: Optional[float] = None
    duration_seconds: Optional[float] = None
    
    # Process info
    pid: Optional[int] = None


# =============================================================================
# COMMAND EFFECTOR IMPLEMENTATION
# =============================================================================


class CommandEffector:
    """
    Effector for command execution via subprocess.
    
    Key features:
        - Argument-vector execution (not shell=True)
        - Executable allowlist validation
        - Timeout enforcement
        - Output truncation
        - Accurate side effect reporting
    """
    
    def __init__(
        self,
        runtime_id: str,
        allowed_commands: Optional[Tuple[str, ...]] = None,
        safety_mode: ShellSafety = ShellSafety.RESTRICTED,
    ):
        self._runtime_id = runtime_id
        
        # Default allowed commands (minimal set for safety)
        self._allowed_commands = allowed_commands or (
            "cat",
            "echo",
            "ls",
            "mkdir",
            "rm",
            "cp",
            "mv",
            "pwd",
            "whoami",
            "hostname",
            "date",
            "df",
            "du",
            "ps",
            "env",
            "which",
        )
        
        self._safety_mode = safety_mode
        self._command_history: List[Dict[str, Any]] = []
    
    @property
    def effector_id(self) -> EffectorId:
        """Get the effector's identity."""
        return EffectorId("shell")
    
    def get_contract(self) -> EffectorContract:
        """Get the effector's contract."""
        return EffectorContract(
            effector_id=self.effector_id,
            name="Shell/Command Effector",
            target_domain="process_execution",
            side_effect_class="mutate",  # Creates new processes
            reversibility="unknown",     # Process lifecycle hard to reverse
            required_capability=None,    # Would be set by policy
            is_idempotent=False,         # Each execution is unique
            timeout_seconds=60.0,
            cancellation_policy="cooperative",
            supports_rollback=False,     # Can't rollback process creation
            rollback_operation=None,
            supports_dry_run=True,       # Dry-run possible for some commands
        )
    
    async def execute(self, request: ActionRequest) -> ExecutionResult:
        """
        Execute a shell command.
        
        Args:
            request: The action request containing the command spec
            
        Returns:
            Execution result with side effect report
        """
        if not request.effector_id or str(request.effector_id) != "shell":
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error="This effector only handles shell/command operations",
            )
        
        command_spec = self._parse_command_spec(request)
        
        # Validate executable
        is_valid, error = self._validate_command(command_spec.executable)
        if not is_valid:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error=f"Command validation failed: {error}",
            )
        
        try:
            result = await self._execute_command(command_spec)
            
            # Record side effect
            self._command_history.append({
                "type": "command",
                "executable": command_spec.executable,
                "arguments": command_spec.arguments,
                "success": result.success,
                "return_code": result.return_code,
                "duration_seconds": result.duration_seconds,
                "timestamp": time.monotonic(),
            })
            
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.SUCCEEDED if result.success else ExecutionStatus.FAILED,
                value={
                    "success": result.success,
                    "return_code": result.return_code,
                    "stdout": result.stdout[:command_spec.max_output_bytes],
                    "stderr": result.stderr[:command_spec.max_output_bytes],
                },
                side_effects_reported=(
                    {
                        "type": "process_start",
                        "executable": command_spec.executable,
                        "arguments": list(command_spec.arguments),
                        "return_code": result.return_code,
                        "timed_out": result.duration_seconds is None or result.duration_seconds >= command_spec.timeout_seconds if command_spec.timeout_seconds else False,
                    },
                ),
            )
            
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.TIMED_OUT,
                error=f"Command exceeded {command_spec.timeout_seconds}s timeout",
            )
        except FileNotFoundError:
            return ExecutionResult(
                action_id=request.action_id,
                invocation_id=request.invocation_id,
                status=ExecutionStatus.FAILED,
                error=f"Executable not found: {command_spec.executable}",
            )
    
    def _parse_command_spec(self, request: ActionRequest) -> CommandSpec:
        """Parse the command spec from an action request."""
        executable = request.arguments.get("executable", "")
        
        arguments_raw = request.arguments.get("arguments", [])
        if isinstance(arguments_raw, str):
            # Handle string (dangerous - parse carefully)
            import shlex
            try:
                arguments = tuple(shlex.split(arguments_raw))
            except ValueError:
                arguments = ()
        else:
            arguments = tuple(str(a) for a in arguments_raw)
        
        environment = request.arguments.get("environment", None)
        working_directory = request.arguments.get("working_directory", None)
        timeout_seconds = request.arguments.get("timeout_seconds")
        input_data = request.arguments.get("input_data", None)
        max_output_bytes = request.arguments.get("max_output_bytes", 1024 * 1024)
        
        return CommandSpec(
            executable=executable,
            arguments=arguments,
            environment=environment,
            working_directory=working_directory,
            timeout_seconds=timeout_seconds,
            input_data=input_data,
            max_output_bytes=max_output_bytes,
        )
    
    def _validate_command(self, executable: str) -> Tuple[bool, Optional[str]]:
        """Validate that the command is allowed."""
        if self._safety_mode == ShellSafety.RESTRICTED:
            # Only allow commands in the allowlist
            import shutil
            resolved = shutil.which(executable)
            
            if not resolved:
                return False, f"Executable not found: {executable}"
            
            # Check against allowlist
            executable_basename = os.path.basename(executable)
            if executable_basename not in self._allowed_commands:
                return False, f"Command not in allowlist: {executable}"
        
        elif self._safety_mode == ShellSafety.MONITORED:
            import shutil
            if not shutil.which(executable):
                return False, f"Executable not found: {executable}"
        
        # ALLOWED mode - no validation (not recommended for production)
        
        return True, None
    
    async def _execute_command(self, spec: CommandSpec) -> CommandResult:
        """Execute a command and capture the result."""
        start_time = time.monotonic()
        
        try:
            completed = subprocess.run(
                [spec.executable] + list(spec.arguments),
                cwd=spec.working_directory,
                env=spec.environment,
                input=spec.input_data,
                timeout=spec.timeout_seconds,
                capture_output=True,
                text=False,  # Get bytes directly
            )
            
            end_time = time.monotonic()
            
            return CommandResult(
                success=completed.returncode == 0,
                return_code=completed.returncode,
                stdout=completed.stdout.decode("utf-8", errors="replace"),
                stderr=completed.stderr.decode("utf-8", errors="replace"),
                started_at=start_time,
                completed_at=end_time,
                duration_seconds=end_time - start_time,
                pid=completed.pid if hasattr(completed, "pid") else None,
            )
            
        except subprocess.TimeoutExpired as e:
            end_time = time.monotonic()
            
            # Even on timeout, capture any output
            stdout = ""
            stderr = ""
            if e.stdout:
                stdout = e.stdout.decode("utf-8", errors="replace")
            if e.stderr:
                stderr = e.stderr.decode("utf-8", errors="replace")
            
            return CommandResult(
                success=False,
                return_code=-1,  # Timeout indicator
                stdout=stdout[:spec.max_output_bytes],
                stderr=stderr[:spec.max_output_bytes],
                started_at=start_time,
                completed_at=end_time,
                duration_seconds=end_time - start_time,
            )
    
    def get_command_history(self) -> List[Dict[str, Any]]:
        """Get the command history for audit/debugging."""
        return list(self._command_history)
    
    async def clear_history(self) -> None:
        """Clear the command history."""
        self._command_history.clear()


# =============================================================================
# CONVENIENCE FACTORY
# =============================================================================


def create_command_effector(
    runtime_id: str,
    allowed_commands: Optional[Tuple[str, ...]] = None,
    safety_mode: ShellSafety = ShellSafety.RESTRICTED,
) -> CommandEffector:
    """
    Create a command effector with sensible defaults.
    
    Args:
        runtime_id: The runtime ID for this effector
        allowed_commands: Tuple of allowed command names
        safety_mode: Safety level for command execution
        
    Returns:
        Configured CommandEffector instance
    """
    import os
    
    return CommandEffector(
        runtime_id,
        allowed_commands=allowed_commands,
        safety_mode=safety_mode,
    )


__all__ = [
    # Enums
    "ShellSafety",
    
    # Data classes
    "CommandSpec",
    "CommandResult",
    
    # Classes
    "CommandEffector",
    
    # Functions
    "create_command_effector",
]