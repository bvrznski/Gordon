# Fault Injection Subpackage - Testing Infrastructure
# ==========================================

"""
Fault injection subpackage for failure injection testing.

This module provides:
- FaultInjector: Injects failures into system components
- Network faults: Packet loss, latency, partition
- Resource faults: Memory, CPU, disk exhaustion
- Timing faults: Delays, timeouts, deadlock simulation
"""

from .injector import (
    FaultInjector,
    InjectionContext,
)
from .network import (
    NetworkFault,
    inject_network_fault,
)
from .resource import (
    ResourceFault,
    inject_resource_fault,
)
from .timing import (
    TimingFault,
    inject_timing_fault,
)

__all__ = [
    # Injector
    "FaultInjector",
    "InjectionContext",
    
    # Fault types
    "NetworkFault",
    "ResourceFault",
    "TimingFault",
    
    # Helpers
    "inject_network_fault",
    "inject_resource_fault",
    "inject_timing_fault",
]