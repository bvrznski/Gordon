# Phase 3.13.1 - Core Functionality Marker Hierarchy

## MARKER HIERARCHY DIAGRAM

```mermaid
graph TD
    subgraph "Canonical Marker Hierarchy"
        CoreFunctionality[CoreFunctionality<br/>Abstract Base Class]
        
        ForCore[ForCore<br/>Core Infrastructure Services]
        ForExecution[ForExecution<br/>Execution Layer Components]
        ForEntrypoint[ForEntrypoint<br/>Application Entry Points]
        ForArchitecture[ForArchitecture<br/>Architecture Reflection]
        ForNetworks[ForNetworks<br/>Transport/Stream Layer]
        ForCapabilities[ForCapabilities<br/>Agent Capabilities]
        ForSystems[ForSystems<br/>System Subsystems]
    end
    
    CoreFunctionality -->|extends| ForCore
    CoreFunctionality -->|extends| ForExecution
    CoreFunctionality -->|extends| ForEntrypoint
    CoreFunctionality -->|extends| ForArchitecture
    CoreFunctionality -->|extends| ForNetworks
    CoreFunctionality -->|extends| ForCapabilities
    CoreFunctionality -->|extends| ForSystems
    
    style CoreFunctionality fill:#f9f,stroke:#333,stroke-width:2px
```

## USAGE EXAMPLES

### Example 1: Core Infrastructure Component
```python
class ExecutionScheduler(
    CoreService,
    ForExecution,
):
    """Scheduler primarily serves the execution layer."""
    ...
```

### Example 2: Architecture Reflection Component
```python
class DependencyInspector(
    ComponentBase,
    ForArchitecture,
):
    """Inspector primarily serves architectural analysis."""
    ...
```

## COMPONENT CLASSIFICATION

| Layer | Marker | Examples |
|-------|--------|----------|
| Core Infrastructure | `ForCore` | Registry, StateStore, SyncPrimitives |
| Execution | `ForExecution` | Scheduler, Executor, TaskDispatcher |
| Entry Points | `ForEntrypoint` | ApplicationMain, BootstrapLoader |
| Architecture | `ForArchitecture` | DependencyInspector, GraphBuilder |
| Transport Layer | `ForNetworks` | StreamRegistry, MessageRouter |
| Capabilities | `ForCapabilities` | CognitiveEngine, LearningModule |
| System Subsystems | `ForSystems` | VisionSystem, MemorySystem |

## ARCHITECTURAL VALIDATION

The marker system enables:
- **Static validation**: Tools can verify correct marker inheritance
- **Architecture documentation**: Automatic generation from code
- **Repository analysis**: Component discovery by architectural layer
- **AI-assisted development**: Clear intent communication