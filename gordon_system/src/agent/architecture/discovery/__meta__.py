# Meta: Architecture Discovery Framework
# ======================================

"""
Meta information about the Architecture Discovery Framework.

This file contains metadata and configuration information for the
architecture discovery system.
"""

from typing import Dict, Any

__version__ = "1.0.0"
__author__ = "Gordon Core Team"

# Framework metadata
metadata: Dict[str, Any] = {
    "name": "Architecture Discovery Framework",
    "version": __version__,
    "description": "Deterministic, repository-driven architecture discovery for Gordon Core",
    "author": __author__,
    
    # Components
    "components": [
        "architecture_inventory_manager",
        "package_discovery_manager", 
        "module_discovery_manager",
        "authority_discovery_manager",
        "dependency_discovery_manager",
        "import_graph_manager",
        "runtime_topology_manager",
        "architecture_report_manager",
        "metrics_manager",
    ],
    
    # Invariants (must be preserved)
    "invariants": [
        "Discovery never mutates runtime state.",
        "Discovery is deterministic.",
        "Discovery preserves provenance.",
        "Runtime topology is immutable.",
        "Package ownership is explicit.",
        "Authority ownership is explicit.",
        "Import graphs are generated independently of dependency graphs.",
        "Reports are reproducible.",
        "Diagnostics remain read-only.",
        "Importing discovery packages performs no repository scanning automatically.",
        "Architecture metadata is authoritative.",
    ],
    
    # Output formats
    "output_formats": [
        "Markdown",
        "JSON",
        "Mermaid diagrams",
    ],
}

# Exports
__all__ = ["metadata", "__version__", "__author__"]