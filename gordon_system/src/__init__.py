# Gordon System Package Root
"""
Gordon autonomous cognitive agent system.

This package contains the core runtime infrastructure for the Gordon agent:
- Kernel construction and dependency injection (Phase 3.7)
- Runtime assembly and lifecycle management
- Registry, context, and configuration services
"""

# Make gordon a namespace package by using pkg_resources-like pattern
__path__ = __import__('pkgutil').extend_path(__path__, 'gordon')