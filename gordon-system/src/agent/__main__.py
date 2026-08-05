"""Module-execution adapter for Gordon Agent.

Phase 3.7.29-I: Agent Process Entrypoint
========================================

This module adapts Python module execution (`python -m agent`) to the
canonical Agent process entrypoint. It is a minimal delegate that:

1. Imports `main` from `agent.entrypoint.main`
2. Invokes `main()`
3. Raises `SystemExit` with the returned integer exit code

This module does NOT:
- Parse CLI arguments independently
- Resolve configuration
- Construct launch requests
- Install signals independently
- Initialize the Agent
- Load components
- Construct Agent Core
- Create an event loop
- Implement failure handling independently
- Implement shutdown independently

All responsibility is delegated to `agent.entrypoint.main.main()`.

Canonical invocation chain:
    python -m agent
        ↓
    agent.__main__ (this module)
        ↓
    agent.entrypoint.main.main()
        ↓
    Agent process execution...
"""
from __future__ import annotations

import sys


def main() -> None:
    """Module-execution adapter entry point.

    This function is called when running `python -m agent`. It delegates
    entirely to the canonical Agent process entrypoint and propagates
    the exit code through SystemExit.
    """
    # Import the canonical entrypoint (deferred until runtime)
    from agent.entrypoint.main import main as entrypoint_main

    # Invoke the canonical entrypoint with explicit arguments
    # This allows tests to pass custom argv without mutating sys.argv
    exit_code = entrypoint_main()

    # Raise SystemExit with the returned integer code.
    # sys.exit() is acceptable here because we're at the module execution level
    # and this is the final exit path for the process.
    raise SystemExit(exit_code)


# If running as a script (unusual but possible), execute main()
if __name__ == "__main__":
    main()