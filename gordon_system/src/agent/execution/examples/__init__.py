# Agentic Flow Examples (Phase 3.10.10)
# =======================================

"""
Example execution flows demonstrating the agentic loop pattern.

These examples show how Threads advance through their active Loops,
one bounded Cycle at a time, as orchestrated by the ExecutionCoordinator.

The Gordon agentic loop is NOT a concrete ExecutionLoop subtype.
It is the repeated orchestration of Threads through their active Loops,
one bounded Cycle at a time.

Example Flows:
    - conversation_flow.py: ConversationThread advancement
    - task_flow.py: TaskThread advancement (planning → execution)
    - monitoring_flow.py: MonitoringThread advancement  
    - recovery_flow.py: RecoveryLoop usage
    - idle_flow.py: IdleThread advancement

Usage:
    from agent.execution.examples import (
        run_conversation_example,
        run_task_example,
        run_monitoring_example,
        run_recovery_example,
        run_idle_example,
    )
    
Each example returns a list of ExecutionIterationResult objects showing
the complete flow of advancement decisions.
"""