# Gordon Core - Architecture Inventory Report

**Repository**: /home/bvrznski/Gordon/gordon-system
**Discovered At**: 2026-08-03 18:17:45
**Version**: 1.0.0

---

## Executive Summary

| Metric | Count |
|--------|-------|
| Total Packages | 84 |
| Total Modules | 619 |
| Total Classes | 3549 |
| Total Functions | 319 |
| Runtime Authorities | 61 |

---

## Package Inventory (by Category)

| Name | Path | Category |
|------|------|----------|
| engine | `src/agent/components/core/engine` | execution |
| execution | `src/agent/components/core/execution` | execution |
| executor | `src/agent/components/core/executor` | execution |
| manager | `src/agent/components/core/manager` | execution |
| architecture | `src/agent/architecture` | infrastructure |
| capability_map | `src/agent/architecture/capability_map` | infrastructure |
| contracts | `src/agent/components/core/contracts` | infrastructure |
| dependency | `src/agent/components/core/dependency` | infrastructure |
| dependency_graph | `src/agent/architecture/dependency_graph` | infrastructure |
| discovery | `src/agent/architecture/discovery` | infrastructure |
| exceptions | `src/agent/components/core/exceptions` | infrastructure |
| ownership | `src/agent/architecture/ownership` | infrastructure |
| topology | `src/agent/architecture/topology` | infrastructure |
| types | `src/agent/components/core/types` | infrastructure |
| kernel | `src/agent/components/core/kernel` | kernel |
| lifecycle | `src/agent/components/core/lifecycle` | kernel |
| observability | `src/agent/components/core/observability` | observability |
| integrity | `src/agent/components/core/integrity` | recovery |
| recovery_v2 | `src/agent/components/core/recovery_v2` | recovery |
| bootstrap | `src/agent/components/core/bootstrap` | runtime |
| configuration | `src/agent/components/core/configuration` | runtime |
| context | `src/agent/components/core/context` | runtime |
| reconfiguration | `src/agent/components/core/reconfiguration` | runtime |
| registry | `src/agent/components/core/registry` | runtime |
| runtime | `src/agent/components/core/runtime` | runtime |
| runtime_monitoring | `src/agent/components/core/runtime_monitoring` | runtime |
| runtime_state | `src/agent/components/core/runtime_state` | runtime |
| scheduling | `src/agent/components/core/scheduling` | runtime |
| state | `src/agent/components/core/state` | runtime |
| synchronization | `src/agent/components/core/synchronization` | runtime |
| certification | `src/agent/components/core/testing/certification` | testing |
| data | `src/agent/components/core/testing/data` | testing |
| doubles | `src/agent/components/core/testing/doubles` | testing |
| environments | `src/agent/components/core/testing/environments` | testing |
| evidence | `src/agent/components/core/testing/evidence` | testing |
| fault_injection | `src/agent/components/core/testing/fault_injection` | testing |
| fixtures | `src/agent/components/core/testing/fixtures` | testing |
| quality | `src/agent/components/core/testing/quality` | testing |
| testing | `src/agent/components/core/testing` | testing |
| validation | `src/agent/components/core/testing/validation` | testing |
| verification | `src/agent/components/core/testing/verification` | testing |
| action | `src/agent/capabilities/action` | unknown |
| admission | `src/agent/components/core/admission` | unknown |
| agency | `src/agent/capabilities/agency` | unknown |
| agent | `src/agent` | unknown |
| authority | `src/agent/components/core/authority` | unknown |
| capabilities | `src/agent/components/core/capabilities` | unknown |
| capabilities | `src/agent/capabilities` | unknown |
| causality | `src/agent/components/core/causality` | unknown |
| cognition | `src/agent/capabilities/cognition` | unknown |
| communication | `src/agent/components/core/communication` | unknown |
| components | `src/agent/components` | unknown |
| continuity | `src/agent/components/core/continuity` | unknown |
| core | `src/agent/components/core` | unknown |
| creativity | `src/agent/capabilities/creativity` | unknown |
| data_governance | `src/agent/components/core/data_governance` | unknown |
| evolution | `src/agent/capabilities/evolution` | unknown |
| failure | `src/agent/components/core/failure` | unknown |
| feature_flags | `src/agent/components/core/feature_flags` | unknown |
| federation | `src/agent/components/core/federation` | unknown |
| knowledge | `src/agent/capabilities/knowledge` | unknown |
| learning | `src/agent/capabilities/learning` | unknown |
| lineage | `src/agent/components/core/lineage` | unknown |
| memory | `src/agent/systems/memory` | unknown |
| motivation | `src/agent/capabilities/motivation` | unknown |
| obligations | `src/agent/components/core/obligations` | unknown |
| operational | `src/agent/components/core/operational` | unknown |
| perception | `src/agent/systems/perception` | unknown |
| performance | `src/agent/components/core/performance` | unknown |
| persistence | `src/agent/components/core/persistence` | unknown |
| personality | `src/agent/capabilities/personality` | unknown |
| policies | `src/agent/components/core/policies` | unknown |
| provenance | `src/agent/components/core/provenance` | unknown |
| readiness | `src/agent/components/core/readiness` | unknown |
| resources | `src/agent/components/core/resources` | unknown |
| restart | `src/agent/components/core/restart` | unknown |
| retry | `src/agent/components/core/retry` | unknown |
| rollback | `src/agent/components/core/rollback` | unknown |
| security | `src/agent/components/core/security` | unknown |
| shutdown | `src/agent/components/core/shutdown` | unknown |
| systems | `src/agent/systems` | unknown |
| tasks | `src/agent/components/core/tasks` | unknown |
| temporal | `src/agent/components/core/temporal` | unknown |
| workers | `src/agent/components/core/workers` | unknown |

---

## Runtime Authority Inventory

| Name | Category | Implementation |
|------|----------|----------------|
| CleanupCoordinator | Cancellation | `gordon.system.components.core.execution.CleanupCoordinator` |
| ExecutionState | Cancellation | `gordon.system.components.core.execution.ExecutionState` |
| SchedulerState | Cancellation | `gordon.system.components.core.execution.SchedulerState` |
| TaskState | Cancellation | `gordon.system.components.core.execution.TaskState` |
| ConfigurationSourceRegistry | Configuration | `gordon.system.components.core.configuration.ConfigurationSourceRegistry` |
| SchemaRegistry | Configuration | `gordon.system.components.core.configuration.SchemaRegistry` |
| SchemaRegistryId | Configuration | `gordon.system.components.core.configuration.SchemaRegistryId` |
| CleanupCoordinator | Execution | `gordon.system.components.core.execution.CleanupCoordinator` |
| ExecutionState | Execution | `gordon.system.components.core.execution.ExecutionState` |
| SchedulerState | Execution | `gordon.system.components.core.execution.SchedulerState` |
| TaskState | Execution | `gordon.system.components.core.execution.TaskState` |
| KernelState | Kernel | `gordon.system.components.core.kernel.KernelState` |
| LifecycleController | Lifecycle | `gordon.system.components.core.lifecycle.LifecycleController` |
| ComponentRegistry | Registry | `gordon.system.components.core.registry.ComponentRegistry` |
| Registry | Registry | `gordon.system.components.core.registry.Registry` |
| RegistryEntry | Registry | `gordon.system.components.core.registry.RegistryEntry` |
| RegistryMetadata | Registry | `gordon.system.components.core.registry.RegistryMetadata` |
| RegistryObserver | Registry | `gordon.system.components.core.registry.RegistryObserver` |
| RegistrySnapshot | Registry | `gordon.system.components.core.registry.RegistrySnapshot` |
| RuntimeRegistry | Registry | `gordon.system.components.core.registry.RuntimeRegistry` |
| RuntimeRegistryEntry | Registry | `gordon.system.components.core.registry.RuntimeRegistryEntry` |
| RuntimeRegistrySnapshot | Registry | `gordon.system.components.core.registry.RuntimeRegistrySnapshot` |
| ServiceRegistry | Registry | `gordon.system.components.core.registry.ServiceRegistry` |
| ActivationState | Runtime State | `gordon.system.components.core.runtime_state.ActivationState` |
| ActivationTransactionState | Runtime State | `gordon.system.components.core.runtime_state.ActivationTransactionState` |
| GuardManager | Runtime State | `gordon.system.components.core.runtime_state.GuardManager` |
| LifecycleCoordinatorSnapshot | Runtime State | `gordon.system.components.core.runtime_state.LifecycleCoordinatorSnapshot` |
| Registry | Runtime State | `gordon.system.components.core.runtime_state.Registry` |
| RegistryPhase | Runtime State | `gordon.system.components.core.runtime_state.RegistryPhase` |
| RegistryReader | Runtime State | `gordon.system.components.core.runtime_state.RegistryReader` |
| RegistryRevision | Runtime State | `gordon.system.components.core.runtime_state.RegistryRevision` |
| RegistrySealedError | Runtime State | `gordon.system.components.core.runtime_state.RegistrySealedError` |
| RegistrySnapshot | Runtime State | `gordon.system.components.core.runtime_state.RegistrySnapshot` |
| RegistryWriter | Runtime State | `gordon.system.components.core.runtime_state.RegistryWriter` |
| ResourceState | Runtime State | `gordon.system.components.core.runtime_state.ResourceState` |
| RuntimeLifecycleCoordinator | Runtime State | `gordon.system.components.core.runtime_state.RuntimeLifecycleCoordinator` |
| RuntimeState | Runtime State | `gordon.system.components.core.runtime_state.RuntimeState` |
| RuntimeStateStore | Runtime State | `gordon.system.components.core.runtime_state.RuntimeStateStore` |
| SignalState | Runtime State | `gordon.system.components.core.runtime_state.SignalState` |
| _ContextManager | Runtime State | `gordon.system.components.core.runtime_state._ContextManager` |
| RecurringTaskState | Scheduler | `gordon.system.components.core.scheduling.RecurringTaskState` |
| ActivationState | Shutdown | `gordon.system.components.core.runtime_state.ActivationState` |
| ActivationTransactionState | Shutdown | `gordon.system.components.core.runtime_state.ActivationTransactionState` |
| GuardManager | Shutdown | `gordon.system.components.core.runtime_state.GuardManager` |
| LifecycleCoordinatorSnapshot | Shutdown | `gordon.system.components.core.runtime_state.LifecycleCoordinatorSnapshot` |
| ProcessExitCoordinator | Shutdown | `gordon.system.components.core.shutdown.ProcessExitCoordinator` |
| Registry | Shutdown | `gordon.system.components.core.runtime_state.Registry` |
| RegistryPhase | Shutdown | `gordon.system.components.core.runtime_state.RegistryPhase` |
| RegistryReader | Shutdown | `gordon.system.components.core.runtime_state.RegistryReader` |
| RegistryRevision | Shutdown | `gordon.system.components.core.runtime_state.RegistryRevision` |
| RegistrySealedError | Shutdown | `gordon.system.components.core.runtime_state.RegistrySealedError` |
| RegistrySnapshot | Shutdown | `gordon.system.components.core.runtime_state.RegistrySnapshot` |
| RegistryWriter | Shutdown | `gordon.system.components.core.runtime_state.RegistryWriter` |
| ResourceState | Shutdown | `gordon.system.components.core.runtime_state.ResourceState` |
| RuntimeLifecycleCoordinator | Shutdown | `gordon.system.components.core.runtime_state.RuntimeLifecycleCoordinator` |
| RuntimeState | Shutdown | `gordon.system.components.core.runtime_state.RuntimeState` |
| RuntimeStateStore | Shutdown | `gordon.system.components.core.runtime_state.RuntimeStateStore` |
| ShutdownCoordinator | Shutdown | `gordon.system.components.core.shutdown.ShutdownCoordinator` |
| ShutdownState | Shutdown | `gordon.system.components.core.shutdown.ShutdownState` |
| SignalState | Shutdown | `gordon.system.components.core.runtime_state.SignalState` |
| _ContextManager | Shutdown | `gordon.system.components.core.runtime_state._ContextManager` |

---

## Metrics Summary

| Metric | Count |
|--------|-------|
| Packages | 84 |
| Modules | 619 |
| Classes | 3549 |
| Functions | 319 |

---

*Generated by Phase 3.7.1-A Architecture Inventory*
