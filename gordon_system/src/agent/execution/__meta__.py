# Execution Package Metadata (Phase 3.10.8)
# ===========================================

"""
Execution package metadata and documentation.
"""

__title__ = "Agent Execution"
__version__ = "3.10.8"
__description__ = "Behavioral organization of the autonomous agent"

__canonical_structure__ = {
    "threads": "Long-lived semantic activity ownership",
    "loops": "Continuation and repetition policy ownership",
    "cycles": "Finite semantic progression ownership",
    "streams": "Ordered semantic information flow ownership",
}

__core_dependencies__ = [
    "core.contracts",  # Core execution contracts
    "core.communication.streams",  # Generic stream infrastructure
]

__status__ = "production"