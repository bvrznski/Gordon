"""Gordon Agent Process Entrypoint.

Phase 3.7.29-I + 3.7.32-I: Agent Process Entrypoint with Preflight

Preflight Integration:
- Phase 3.7.32: Preflight execution before initialization
- Immutable preflight request construction  
- Preflight result validation before initialization proceeds
- Exit status mapping for preflight outcomes

Architecture Boundaries
-----------------------
This module owns:
- Process-level entry point normalization
- CLI argument parsing (Agent-specific surface only)
- Launch request construction (immutable)
- Preflight request construction and invocation
- Preflight result consumption
- Initialization invocation only after preflight passes
- Signal routing to shutdown intent
- Exit-status mapping

This module does NOT own:
- Configuration-file parsing internals
- Component discovery or loading
- Agent Core construction
- Runtime assembly or activation
- Cognition, planning, or operation
- Shutdown sequencing implementation
- Preflight check implementations (entrypoint/check.py)
========================================

The canonical Agent process entry point. This module provides exactly one
canonical entrypoint function that:

1. Receives explicit command-line arguments
2. Normalizes invocation surface and CLI parsing
3. Constructs an immutable Agent launch request
4. Invokes the canonical initialization facade
5. Delegates operation to the canonical operational runner
6. Handles shutdown handoff through canonical authority
7. Returns a deterministic shell-compatible exit code

Architecture Boundaries
-----------------------
This module owns:
- Process-level entry point normalization
- CLI argument parsing (Agent-specific surface only)
- Launch request construction (immutable)
- Signal routing to shutdown intent
- Exit-status mapping

This module does NOT own:
- Configuration-file parsing internals
- Component discovery or loading
- Agent Core construction
- Runtime assembly or activation
- Cognition, planning, or operation
- Shutdown sequencing implementation

Public API
----------
- main(argv: Sequence[str] | None = None) -> int: Canonical process entrypoint

Import-time behavior:
- No CLI parsing occurs at import time
- No logging configuration occurs at import time
- No signal handlers are installed at import time
- No event loop is created at import time
- No Agent runtime is constructed at import time
"""
from __future__ import annotations

import sys
from typing import Dict, Any
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    Dict,
    Final,
    List,
    Optional,
    Sequence,
    Tuple,
)


def _normalize_invocation_surface() -> str:
    """Determine the invocation surface from the execution context.

    This function examines how Python was invoked to determine which
    entrypoint path was used. It does not parse arguments.
    
    Returns:
        Invocation surface string identifier.
    """
    # Check for gordon --mode agent pattern (top-level launcher)
    if len(sys.argv) >= 3 and sys.argv[1] == "--mode" and sys.argv[2] == "agent":
        return "TOP_LEVEL_LAUNCHER"
    
    # Check for gordon-agent console script
    if len(sys.argv) > 0:
        argv0 = sys.argv[0]
        if argv0 and "gordon" in argv0.lower() and "agent" in argv0.lower():
            return "CONSOLE_SCRIPT"
    
    # Default to module execution (python -m agent)
    return "MODULE_EXECUTION"


def _normalize_raw_arguments(argv: Sequence[str]) -> Tuple[str, ...]:
    """Normalize raw command-line arguments.

    Args:
        argv: Raw command-line arguments as passed to main()

    Returns:
        Normalized tuple of argument strings
    """
    if not argv:
        return tuple(sys.argv[1:])  # Skip program name
    return tuple(argv)


# =============================================================================
# CLI PARSING (deterministic, side-effect-free)
# =============================================================================


def _parse_cli_arguments(
    raw_arguments: Tuple[str, ...]
) -> Tuple[Dict[str, Any], Optional[str]]:
    """Parse Agent-specific CLI arguments.

    This function is:
    - Deterministic: same inputs produce same outputs
    - Side-effect-free: no mutable state changes
    - Testable: accepts explicit argument sequences

    Args:
        raw_arguments: Raw command-line arguments

    Returns:
        Tuple of (parsed_options_dict, error_message or None)
    """
    options: Dict[str, Any] = {
        "invocation_surface": _normalize_invocation_surface(),
        "raw_arguments": raw_arguments,
    }

    # Parse arguments (simple stateless parsing)
    args_iter = iter(raw_arguments)
    errors: List[str] = []

    for arg in args_iter:
        if arg.startswith("-"):
            if arg in ("--help", "-h"):
                options["show_help"] = True
                return options, None

            elif arg == "--version":
                options["show_version"] = True
                return options, None

            elif arg == "--validation-only":
                options["validation_only"] = True

            elif arg == "--safe-mode":
                options["safe_mode_enabled"] = True

            elif arg == "--offline":
                options["offline_mode_enabled"] = True

            elif arg == "--mode" or arg.startswith("--mode="):
                # Handle --mode agent or --mode=agent
                mode_value = None
                if "=" in arg:
                    _, mode_value = arg.split("=", 1)
                else:
                    try:
                        mode_value = next(args_iter, None)
                    except StopIteration:
                        errors.append(f"Missing value for {arg}")

                if mode_value and mode_value == "agent":
                    options["run_mode"] = "DEFAULT"

            elif arg.startswith("--log-level="):
                _, level = arg.split("=", 1)
                valid_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
                if level in valid_levels:
                    options["log_level"] = level
                else:
                    errors.append(f"Invalid log level: {level}")

            elif arg.startswith("--config="):
                _, config_path = arg.split("=", 1)
                options["config_path"] = config_path

            elif arg.startswith("--profile="):
                _, profile = arg.split("=", 1)
                options["profile"] = profile

            elif arg.startswith("--environment="):
                _, env = arg.split("=", 1)
                options["environment"] = env

            elif arg == "--debug":
                options["development_mode"] = True

            elif arg in ("--structured", "--json"):
                options["structured_output"] = True

            elif arg == "--help-all":
                options["show_help_all"] = True
                return options, None

            else:
                errors.append(f"Unknown option: {arg}")

        else:
            # Positional argument
            if "positional_args" not in options:
                options["positional_args"] = []
            options["positional_args"].append(arg)

    if errors:
        error_msg = "; ".join(errors)
        return {}, f"CLI parsing failed: {error_msg}"

    return options, None


# =============================================================================
# PROCESS HOST (thin wrapper, no state)
# =============================================================================


@dataclass(frozen=True)
class AgentProcessHost:
    """Thin process host facade.

    This is a stateless data structure for process metadata. It does NOT
    own lifecycle management or runtime creation.
    """

    process_id: int
    parent_process_id: Optional[int]
    invocation_surface: str

    @classmethod
    def create(cls, invocation_surface: str) -> "AgentProcessHost":
        """Create a new process host with auto-computed metadata."""
        import os

        return cls(
            process_id=os.getpid(),
            parent_process_id=os.getppid() if hasattr(os, "getppid") else None,
            invocation_surface=invocation_surface,
        )

    @property
    def short_id(self) -> str:
        """Return a short printable ID."""
        return f"proc-{self.process_id}"


# =============================================================================
# SIGNAL ROUTING (minimal, no direct cleanup)
# =============================================================================


class SignalHandler:
    """Minimal signal routing to shutdown intent.

    This class does NOT perform any resource cleanup directly. It only
    records the signal as a shutdown intent and defers to canonical
    shutdown authority.
    
    NOTE: This uses request-scoped intent via thread-local storage to avoid
    mutable global state. Each invocation gets its own clean state.
    """

    # Use a callable that returns fresh Event per call for thread safety
    # without module-level mutable state
    
    _intent_lock: Final[Any] = None  # Placeholder for potential locking
    _shutdown_intent: Optional[Any] = None

    @classmethod
    def get_shutdown_intent(cls) -> Any:
        """Get a fresh shutdown intent (request-scoped, not global)."""
        import threading
        return threading.Event()

    @staticmethod
    def set_shutdown_intent(intent: Any) -> None:
        """Set shutdown intent on the provided intent object."""
        intent.set()

    @staticmethod
    def is_shutdown_requested(intent: Any) -> bool:
        """Check if shutdown has been requested on this intent."""
        return intent.is_set()


def _setup_signal_handlers() -> Tuple[Any, Callable[[], None]]:
    """Install signal handlers for SIGINT and SIGTERM.

    These handlers do NOT perform cleanup directly. They only set
    the shutdown intent flag.
    
    Returns:
        Tuple of (shutdown_intent_event, reset_function)
    """
    import threading
    import signal
    
    # Create a fresh intent for this invocation
    shutdown_intent = SignalHandler.get_shutdown_intent()

    def _handle_sigint(signum: int, frame: Any) -> None:
        SignalHandler.set_shutdown_intent(shutdown_intent)

    def _handle_sigterm(signum: int, frame: Any) -> None:
        SignalHandler.set_shutdown_intent(shutdown_intent)

    try:
        # Install handlers (only in main thread)
        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, _handle_sigint)
            signal.signal(signal.SIGTERM, _handle_sigterm)
    except (ImportError, ValueError, OSError):
        # Signal handling not available (e.g., non-POSIX platforms)
        pass

    def reset_intent() -> None:
        shutdown_intent.clear()

    return shutdown_intent, reset_intent


# =============================================================================
# BOOTSTRAP DIAGNOSTICS (minimal, bounded, secret-safe)
# =============================================================================


class BootstrapDiagnostics:
    """Minimal diagnostics for early failures.

    This is a stateless container for diagnostic information. It does NOT
    perform logging - that's the responsibility of the canonical Agent
    observability system.
    """

    @staticmethod
    def format_entrypoint_context(
        invocation_surface: str,
        process_id: int,
    ) -> Dict[str, Any]:
        """Format entrypoint context for diagnostics.

        This returns a bounded dictionary - no secrets, no raw prompts.
        """
        return {
            "invocation_surface": invocation_surface,
            "process_id": process_id,
        }

    @staticmethod
    def format_launch_request_preview(
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Format a preview of the launch request.

        Excludes any secrets or sensitive data.
        """
        return {
            "launch_id": request.get("launch_identity", {}).get("launch_id"),
            "mode": request.get("mode", {}).get("run_mode"),
            "log_level": request.get("log_level"),
            "is_validation_only": request.get("is_validation_only", False),
            "is_safe_mode": request.get("is_safe_mode", False),
            "is_offline": request.get("is_offline", False),
        }


# =============================================================================
# INITIALIZATION INVOCATION
# =============================================================================


def _invoke_startup(
    request: Dict[str, Any],
) -> Tuple[bool, str]:
    """Invoke the canonical Agent startup coordinator.

    Phase 3.7.33-I: Startup coordination replaces direct check/init calls.

    Args:
        request: The launch request (as a dictionary for compatibility)

    Returns:
        Tuple of (success: bool, result_or_error_message: str)
    """
    # Import and invoke startup coordinator
    try:
        from . import startup as startup_module
    except (ImportError, ModuleNotFoundError):
        return False, "Startup module not available"

    # Call the start_agent function
    if hasattr(startup_module, "start_agent"):
        try:
            result = startup_module.start_agent(request)
            
            # Check outcome
            outcome = getattr(result, "outcome", None)
            if isinstance(outcome, str):
                is_success = outcome in ("started", "started_degraded")
            elif hasattr(outcome, "value"):
                is_success = outcome.value in ("started", "started_degraded")
            else:
                is_success = False
            
            if is_success:
                return True, f"Startup completed: {outcome}"
            else:
                return False, f"Startup failed with outcome: {outcome}"
                
        except Exception as e:
            return False, f"Startup failed: {e}"

    else:
        return False, "No start_agent function found"


# =============================================================================
# OPERATIONAL RUNNER
# =============================================================================


def _invoke_operational_runner(
    request: Dict[str, Any],
) -> Tuple[bool, str]:
    """Invoke the canonical operational runner.

    This delegates to Phase 3.7.30+ components that implement actual
    Agent operation. It does NOT invoke cognition directly.
    
    NOTE: The actual implementation is delegated to Phase 3.7.30+.
    This stub returns a success status for testing purposes.
    """
    # Return success - actual implementation provided by Phase 3.7.30+
    return True, "Operational runner completed (stub)"


# =============================================================================
# SHUTDOWN HANDOFF
# =============================================================================


def _request_shutdown(shutdown_intent: Any) -> None:
    """Request canonical shutdown through the shutdown authority.

    This function does NOT perform cleanup sequencing. It only signals
    that shutdown has been requested.
    
    Args:
        shutdown_intent: The intent object to set (not global state)
    """
    SignalHandler.set_shutdown_intent(shutdown_intent)


# =============================================================================
# TERMINAL VERIFICATION
# =============================================================================


def _verify_terminal_state(
    init_success: bool,
    op_success: bool,
    shutdown_requested: bool,
) -> Tuple[bool, str]:
    """Verify the terminal state of the process.

    Successful exit requires:
    - Operation completed or intentional termination was requested
    - Canonical shutdown completed (intent recorded)
    - Terminal runtime state is valid
    
    Args:
        init_success: Whether initialization succeeded
        op_success: Whether operational runner completed
        shutdown_requested: Whether shutdown intent was recorded

    Returns:
        Tuple of (verified: bool, message: str)
    """
    # If initialization failed, we cannot verify terminal state properly
    if not init_success:
        return False, "Initialization never completed"

    # Operational phase - if not validation-only and operation failed
    if op_success is False:
        return False, "Operational runner did not complete successfully"

    # Terminal verification passes when shutdown intent is set
    if shutdown_requested:
        return True, "Terminal state verified: shutdown intent recorded"

    # For normal completion (operation succeeded)
    if op_success:
        return True, "Terminal state verified: operation completed normally"

    return False, "Terminal state verification failed"


# =============================================================================
# EXIT STATUS MAPPING
# =============================================================================


def _map_exit_status(
    result: Tuple[bool, str],
    init_failed: bool = False,
) -> int:
    """Map a result tuple to an exit status code.

    Args:
        result: Tuple of (success: bool, message: str)
        init_failed: Whether initialization failed

    Returns:
        Shell-compatible integer exit code
    """
    success, message = result

    if success:
        return 0  # SUCCESS

    # Map common failure patterns to exit statuses
    message_lower = message.lower()

    if "invalid" in message_lower or "usage" in message_lower:
        return 1  # INVALID_USAGE

    elif init_failed and ("initialization" in message_lower or "not available" in message_lower):
        return 3  # INITIALIZATION_FAILURE

    elif "configuration" in message_lower:
        return 2  # CONFIGURATION_FAILURE

    elif "bridge" in message_lower:
        return 106  # BRIDGE_FAILURE (approximate)

    else:
        return 200  # INTERNAL_ERROR


# =============================================================================
# ASYNC PROCESS RUNNER
# =============================================================================


def _invoke_preflight(launch_request: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke the preflight checker.
    
    Phase 3.7.32-I: Preflight execution before initialization.
    
    Args:
        launch_request: The launch request from main
        
    Returns:
        Preflight result dictionary with outcome info
    """
    try:
        from . import check as preflight_module
    except (ImportError, ModuleNotFoundError):
        return {
            "outcome": {"value": "failed", "is_success": False},
            "error": "Preflight module not available"
        }
    
    # Build preflight request from launch request
    try:
        preflight_request = _build_preflight_request(launch_request)
        
        if hasattr(preflight_module, "check_agent"):
            result = preflight_module.check_agent(preflight_request)
            
            # Convert to dict for compatibility
            return {
                "outcome": {
                    "value": result.outcome.value if hasattr(result, "outcome") else "unknown",
                    "is_success": getattr(result, "outcome", None) and 
                               (getattr(result.outcome, "is_success", lambda: False)() 
                                if callable(getattr(result.outcome, "is_success", None)) else False)
                },
                "execution_id": getattr(result, "execution_id", ""),
                "error_count": getattr(result, "failed_checks_count", 0),
            }
        elif hasattr(preflight_module, "AgentPreflightChecker"):
            checker = preflight_module.AgentPreflightChecker()
            result = checker.check(preflight_request)
            
            return {
                "outcome": {
                    "value": result.outcome.value if hasattr(result, "outcome") else "unknown",
                    "is_success": getattr(result.outcome, "is_success", False) 
                                if hasattr(result, "outcome") else False
                },
                "execution_id": getattr(result, "execution_id", ""),
                "error_count": getattr(result, "failed_checks_count", 0),
            }
        else:
            return {
                "outcome": {"value": "failed", "is_success": False},
                "error": "No preflight checker found"
            }
            
    except Exception as e:
        return {
            "outcome": {"value": "failed", "is_success": False},
            "error": str(e)
        }


def _build_preflight_request(launch_request: Dict[str, Any]) -> Any:
    """Build a preflight request from the launch request."""
    # Import types for construction
    try:
        from .check import AgentPreflightRequest, AgentLaunchIdentity, AgentProcessIdentity
        
        process_identity = launch_request.get("process_identity", {})
        
        return AgentPreflightRequest(
            request_id=str(launch_request.get("launch_identity", {}).get("timestamp_ns", 0)),
            launch_identity=AgentLaunchIdentity(
                launch_id=str(launch_request.get("launch_identity", {}).get("launch_id", "")),
                timestamp_ns=int(launch_request.get("launch_identity", {}).get("timestamp_ns", 0)),
                invocation_surface=str(process_identity.get("invocation_surface", "UNKNOWN")),
            ),
            process_identity=AgentProcessIdentity(
                process_id=int(process_identity.get("process_id", 0)),
                parent_process_id=process_identity.get("parent_process_id"),
            ),
            approved_source_roots=("src",),
            compilation_policy=None,  # Will use default from policy
        )
    except Exception:
        # Fallback - return a basic dict-based request
        return launch_request


def _map_preflight_failure(preflight_result: Dict[str, Any]) -> int:
    """Map preflight failure to exit code."""
    outcome = preflight_result.get("outcome", {})
    
    if isinstance(outcome, dict):
        value = outcome.get("value", "unknown")
    else:
        value = str(outcome)
    
    if value in ("blocked", "BLOCKED"):
        return 5  # BLOCKED_BY_PREFLIGHT
    elif value in ("failed", "FAILED"):
        return 6  # PREFLIGHT_FAILURE
    elif value in ("cancelled", "CANCELLED"):
        return 130  # INTERRUPTED
    elif value in ("timed_out", "TIMED_OUT"):
        return 7  # TIMEOUT
    else:
        return 200  # INTERNAL_ERROR


def _run_agent_process(request: Dict[str, Any]) -> Tuple[bool, str]:
    """Run the Agent process through all phases.

    Phase 3.7.33-I: This invokes the canonical startup coordinator instead of
    directly calling check and init.

    This is the canonical async runner that:
    1. Sets up signal handlers (if available)
    2. Invokes startup coordination (includes preflight + initialization)
    3. Invokes operational runner if startup succeeds
    4. Requests shutdown and verifies terminal state

    Args:
        request: The launch request as a dictionary

    Returns:
        Tuple of (success: bool, message: str)
    """
    # Step 1: Setup signal handlers with fresh intent (only in main thread)
    shutdown_intent = None
    reset_intent_fn = lambda: None
    
    try:
        import threading
        if threading.current_thread() is threading.main_thread():
            shutdown_intent, reset_intent_fn = _setup_signal_handlers()
    except Exception:
        pass

    # Step 2: Invoke startup coordinator (includes preflight + initialization)
    startup_success, startup_result = _invoke_startup(request)

    if not startup_success:
        return False, f"Startup failed: {startup_result}"

    # Step 3: Run operational phase (if not validation-only)
    op_success = True
    op_result = ""
    
    is_validation_only = request.get("mode", {}).get("is_validation_only", False)
    if not is_validation_only:
        op_success, op_result = _invoke_operational_runner(request)

        if not op_success:
            return False, f"Operational runner failed: {op_result}"

    # Step 4: Request shutdown (canonical handoff)
    if shutdown_intent is not None:
        _request_shutdown(shutdown_intent)

    # Reset the intent for future use
    reset_intent_fn()

    # Step 5: Verify terminal state
    shutdown_requested = shutdown_intent is not None and SignalHandler.is_shutdown_requested(shutdown_intent)
    
    verified, verify_msg = _verify_terminal_state(True, op_success, shutdown_requested)  # init always passes after startup
    
    if not verified:
        return False, f"Terminal verification failed: {verify_msg}"

    # Step 6: Return success
    return True, "Process completed successfully"


# =============================================================================
# MAIN ENTRYPOINT (THE ONLY PUBLIC FUNCTION)
# =============================================================================


def main(argv: Sequence[str] | None = None) -> int:
    """Canonical Agent process entrypoint.

    This is the ONE canonical function that all Agent invocation surfaces
    must converge on. It:

    1. Accepts explicit arguments for deterministic testing
    2. Does NOT mutate sys.argv directly
    3. Returns an integer exit code compatible with shells
    4. Never calls sys.exit() during ordinary operation
    5. Never calls os._exit() during ordinary operation

    Args:
        argv: Explicit command-line arguments for testing.
              If None, uses sys.argv[1:].

    Returns:
        Integer exit status code:
        - 0: Success
        - Non-zero: Failure (specific code depends on failure type)
    """
    try:
        # Step 1: Normalize invocation surface and arguments
        invocation_surface = _normalize_invocation_surface()
        raw_arguments = _normalize_raw_arguments(argv or ())
        
    except Exception as e:
        # Critical failure before we can even build a launch request
        return 200  # INTERNAL_ERROR

    try:
        # Step 2: Parse CLI arguments (deterministic, side-effect-free)
        parsed_options, parse_error = _parse_cli_arguments(raw_arguments)

        if parse_error:
            # CLI parsing failed - return error without initializing Agent
            print(f"Error: {parse_error}", file=sys.stderr)
            if parsed_options.get("show_help") or parsed_options.get("show_version"):
                # Show help or version info would go here
                pass
            return 1  # INVALID_USAGE

    except Exception as e:
        return 200  # INTERNAL_ERROR

    # Step 3: Build launch request (immutable - represented as dict for Phase 3.7.29)
    try:
        process_host = AgentProcessHost.create(invocation_surface)
        
        import time
        import uuid
        
        launch_identity = {
            "launch_id": str(uuid.uuid4()),
            "timestamp_ns": time.time_ns(),
            "invocation_surface": invocation_surface,
        }

        mode_dict = {
            "run_mode": parsed_options.get("run_mode", "DEFAULT"),
            "bridge_policy": "OPTIONAL",
            "safe_mode_enabled": parsed_options.get("safe_mode_enabled", False),
            "offline_mode_enabled": parsed_options.get("offline_mode_enabled", False),
            "is_validation_only": parsed_options.get("validation_only", False),
        }
        
        launch_request = {
            "process_identity": {
                "process_id": process_host.process_id,
                "launch_id": launch_identity["launch_id"],
                "parent_process_id": process_host.parent_process_id,
                "invocation_surface": invocation_surface,
            },
            "launch_identity": launch_identity,
            "system_identity": {"system_id": None, "parent_system_id": None},
            "runtime_identity": {"runtime_id": "uninitialized", "boot_session_id": "uninitialized"},
            "mode": mode_dict,
            "config_request": {
                "config_path": parsed_options.get("config_path"),
                "profile": parsed_options.get("profile", "default"),
                "environment": parsed_options.get("environment", "production"),
                "deployment_mode": "standalone",
            },
            "startup_deadline_seconds": 30.0,
            "shutdown_deadline_seconds": 15.0,
            "log_level": parsed_options.get("log_level", "INFO"),
            "structured_output": parsed_options.get("structured_output", False),
            "development_mode": parsed_options.get("development_mode", False),
            "raw_arguments": raw_arguments,
        }

    except Exception as e:
        return 4  # PROCESS_HOST_FAILURE

    # Step 4: Run Agent process through canonical startup coordinator
    # The startup coordinator handles preflight and initialization internally
    try:
        success, result = _run_agent_process(launch_request)

    except KeyboardInterrupt:
        return 130  # INTERRUPTED (SIGINT)

    except SystemExit as e:
        # Handle SystemExit with code
        if isinstance(e.code, int) and 0 <= e.code <= 255:
            return int(e.code)
        return 0

    except Exception as e:
        return 200  # INTERNAL_ERROR (UNEXPECTED_EXCEPTION)

    # Step 7: Map result to exit status
    init_failed = False
    exit_code = _map_exit_status((success, result), init_failed=init_failed)
    
    # Step 8: Return exit code (do NOT call sys.exit())
    return exit_code


# =============================================================================
# MODULE-EXECUTION ADAPTER (in a separate module: __main__.py)
# =============================================================================

# This module provides main(). The module execution adapter should be
# in /src/agent/__main__.py and should simply:
#   from agent.entrypoint.main import main
#   sys.exit(main())