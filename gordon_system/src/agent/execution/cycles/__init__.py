# Canonical Cycle Architecture Package
# ====================================

"""
Canonical Cycle architecture for finite semantic execution units.

A Cycle is NOT:
    - An operating-system thread, coroutine, task, worker, process, or scheduler entry
    - A runtime execution unit (that belongs to Core)
    - An event loop, retry loop, or long-lived behavioral controller

A Cycle IS:
    - The smallest finite semantic execution unit belonging to a Thread
    - Selected by exactly one Loop decision
    - One complete bounded semantic pass with terminal outcome
    - Owner of Stage progression within its execution scope

Architecture:

    src/agent/execution/cycles/
        ├── __init__.py           # Package exports (this file)
        ├── base.py               # Abstract Cycle definition contracts
        ├── definition.py         # Reusable Cycle definitions
        ├── instance.py           # Concrete Cycle executions (instances)
        ├── context.py            # Ephemeral execution context
        ├── progression.py        # Progression state machine
        ├── outcome.py            # Terminal result types
        ├── stages.py             # Stage coordination model
        └── validation.py         # Invariant validators

Ownership Model:

    Thread: semantic continuity, identity, objectives, completion intent
    Loop: repetition policy, Cycle selection decision, continuation policy
    Cycle: finite semantic pass, Stage progression, outcome production
    Core: runtime scheduling, lifecycle state transitions, resource allocation

Architecture Invariants:
    C-001: Every Cycle belongs to exactly one Thread
    C-002: Every Cycle is selected by exactly one Loop decision
    C-003: Every Cycle operates against exactly one source Thread revision
