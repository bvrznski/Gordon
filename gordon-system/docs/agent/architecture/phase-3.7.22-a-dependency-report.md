# Gordon Dependency Report
## Phase 3.7.22-A Architecture Acceptance Audit

### Dependency Management Location

**File**: `src/agent/components/core/dependency/__init__.py`

### Dependency Graph Implementation

```python
@dataclass(frozen=True)
class DependencyGraph:
    _edges: Dict[str, Set[str]] = field(default_factory=dict)  # from -> set of to
    _reverse_edges: Dict[str, Set[str]] = field(default_factory=dict)  # to -> set of from
    
    @classmethod def create(cls, dependencies: List[Dependency]) -> "DependencyGraph"
    
    @property def nodes(self) -> Set[str]
    @property def edges(self) -> List[Tuple[str, str]]
    
    def get_dependencies(self, entity: str) -> Set[str]
    def get_dependents(self, entity: str) -> Set[str]
```

### Dependency Resolution

```python
def has_cycle(self) -> bool:
    """Check if the graph contains a cycle using DFS with three states."""

def find_cycle(self) -> Optional[List[str]]:
    """Find and return a cycle in the graph if one exists."""

def topological_sort(self) -> List[str]:
    """Perform topological sort (dependencies first)."""

def reverse_topological_sort(self) -> List[str]:
    """Reverse order (dependents first - for shutdown)."""
```

### Dependency Resolver

```python
class DependencyResolver:
    @staticmethod
    def resolve_order(graph: DependencyGraph, entities: List[str]) -> List[str]
    
    @staticmethod
    def find_missing_dependencies(
        graph: DependencyGraph,
        entities: List[str]
    ) -> Dict[str, List[str]]
```

### Allowed Dependency Directions

```
Core packages (same layer):
- configuration → kernel
- dependency → kernel
- registry → kernel
- lifecycle → kernel

Runtime state depends on core types only (no circular dependencies).
```

### Cycles Detection

✅ VERIFIED: The `DependencyGraph.has_cycle()` method uses DFS with three states to detect cycles.
If a cycle is found, `find_cycle()` returns the path.

### Optional Dependencies

```python
@dataclass(frozen=True)
class Dependency:
    from_entity: str  # The dependent entity
    to_entity: str    # The required entity
    required: bool = True
```

The `required` field marks optional vs hard dependencies.

### Hard Dependencies

Dependencies where `required=True` are blocking and will fail if unmet.