# Digital Modalities Package - Phase 5.2
# =====================================

"""
Digital Modalities: Observe computational structures, states and events.

These modalities share common characteristics:
    - Permission evaluation required before activation
    - Sandbox inspection important for visibility scope
    - Namespace awareness for context isolation
    - Platform compatibility checking
    - Event-source validation
    
Current digital modalities:
    console     - Terminal output, logs, command streams
    shell       - Shell-level execution state (commands, pipelines)
    kernel      - OS-level evidence (processes, signals, scheduling)
    filesystem  - Filesystem events (create, modify, delete)
    network     - Network communication evidence
    processes   - Process structure and lifecycle
    windows     - Graphical application window state
    clipboard   - Clipboard content changes
    editor      - Development environment state
    browser     - Browser-level state
    api         - Structured machine interface observation

Future digital modalities (Phase 5.2.x):
    shell       - Shell history access
    kernel      - Kernel tracepoints
    filesystem  - File content fingerprinting
    network     - Payload inspection
"""

from .console import ConsoleModality

__all__: list[str] = [
    "ConsoleModality",
]