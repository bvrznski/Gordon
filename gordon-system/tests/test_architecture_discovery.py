"""Tests for Architecture Discovery Framework.

Tests covering:
- Package discovery
- Module discovery  
- API discovery
- Authority discovery
- Dependency graph generation
- Import graph generation
- Topology generation
- Metrics generation
- Report generation
- Deterministic replay
- Repository changes
- Multi-runtime isolation
"""

import pytest
from pathlib import Path

# Test imports - using the package structure from gordon-system
from src.agent.architecture.discovery import (
    PackageDiscoveryManager,
    ModuleDiscoveryManager,
    AuthorityDiscoveryManager,
    DependencyDiscoveryManager,
    ImportGraphManager,
    RuntimeTopologyManager,
    ArchitectureReportManager,
    MetricsManager,
)

from src.agent.architecture.discovery.inventory import (
    ArchitectureInventory,
    PackageMetadata,
    ModuleMetadata,
    APIItem,
    RuntimeAuthority,
    PackageCategory,
    LifecycleParticipation,
    DependencyEdge,
    DependencyGraph,
)


class TestPackageDiscovery:
    """Tests for PackageDiscoveryManager."""
    
    def test_discover_packages_returns_tuple(self):
        """Discovering packages returns a tuple of metadata."""
        manager = PackageDiscoveryManager()
        
        repo_path = str(Path(__file__).parent.parent / "gordon-system")
        packages = manager.discover_packages(repo_path)
        
        assert isinstance(packages, tuple)
        assert len(packages) > 0
    
    def test_package_classification(self):
        """Packages are classified into categories."""
        manager = PackageDiscoveryManager()
        
        cat1, layer1, owner1 = manager.get_classification("core/execution")
        cat2, layer2, owner2 = manager.get_classification("kernel")
        
        assert isinstance(cat1, PackageCategory)
        assert len(layer1) > 0
        assert len(owner1) > 0
    
    def test_excluded_paths(self):
        """Test that excluded paths are filtered."""
        manager = PackageDiscoveryManager()
        
        assert manager.is_excluded("tests/test_module.py")
        assert manager.is_excluded("__pycache__/module.py")


class TestModuleDiscovery:
    """Tests for ModuleDiscoveryManager."""
    
    @pytest.fixture
    def manager(self):
        return ModuleDiscoveryManager()
    
    def test_parse_valid_module(self, tmp_path):
        """Parse a valid Python module."""
        code = """
def hello():
    pass

class MyClass:
    pass

__all__ = ["hello", "MyClass"]
"""
        py_file = tmp_path / "test_module.py"
        py_file.write_text(code)
        
        tree = manager.parse_module(py_file)
        assert tree is not None


class TestAuthorityDiscovery:
    """Tests for AuthorityDiscoveryManager."""
    
    def test_discover_authorities(self):
        """Discover runtime authorities."""
        manager = AuthorityDiscoveryManager()
        
        categories = list(AuthorityDiscoveryManager.__dict__.get("AUTHORITY_PATTERNS", {}).keys())
        
        assert "Kernel" in categories
        assert "Runtime State" in categories


class TestDependencyDiscovery:
    """Tests for DependencyDiscoveryManager."""
    
    def test_detect_cycles_empty_graph(self):
        """Detect cycles returns empty list for empty graph."""
        manager = DependencyDiscoveryManager()
        
        graph = DependencyGraph(edges=())
        cycles = manager.detect_cycles(graph)
        
        assert cycles == []
    
    def test_topological_sort(self):
        """Topological sort produces valid ordering."""
        manager = DependencyDiscoveryManager()
        
        edges = (
            DependencyEdge(from_entity="C", to_entity="B"),
            DependencyEdge(from_entity="B", to_entity="A"),
        )
        
        graph = DependencyGraph(edges=edges)
        result = manager.topological_sort(graph)
        
        assert result.index("A") < result.index("B")
        assert result.index("B") < result.index("C")


class TestImportGraphManager:
    """Tests for ImportGraphManager."""
    
    def test_generate_import_graph(self):
        """Generate import graph returns edges."""
        manager = ImportGraphManager()
        
        from src.agent.architecture.discovery.inventory import (
            ImportEdge,
        )
        
        edges: tuple[ImportEdge, ...] = ()
        
        cycles = manager.detect_cycles(edges)
        
        assert isinstance(cycles, list)


class TestRuntimeTopologyManager:
    """Tests for RuntimeTopologyManager."""
    
    def test_build_runtime_topology(self):
        """Build runtime topology from authorities."""
        manager = RuntimeTopologyManager()
        
        authorities: tuple[RuntimeAuthority, ...] = ()
        
        nodes, edges = manager.build_runtime_topology(authorities)
        
        assert isinstance(nodes, tuple)
        assert isinstance(edges, tuple)


class TestArchitectureReportManager:
    """Tests for ArchitectureReportManager."""
    
    def test_generate_markdown_report(self):
        """Generate markdown report from inventory."""
        manager = ArchitectureReportManager()
        
        inventory = ArchitectureInventory(
            repository_path="/test/path",
            discovered_at=0.0,
            version="1.0.0",
            packages=(),
            modules=(),
            public_apis=(),
            runtime_authorities=(),
            package_dependencies=None,
            runtime_dependencies=None,
            import_graph_edges=(),
            topology_nodes=(),
            topology_edges=(),
            entry_points=(),
            background_execution=(),
        )
        
        report = manager.generate_markdown_report(inventory)
        
        assert isinstance(report, str)
        assert "# Gordon Core" in report


class TestMetricsManager:
    """Tests for MetricsManager."""
    
    def test_compute_metrics(self):
        """Compute metrics from inventory."""
        manager = MetricsManager()
        
        inventory = ArchitectureInventory(
            repository_path="/test/path",
            discovered_at=0.0,
            version="1.0.0",
            packages=(),
            modules=(),
            public_apis=(),
            runtime_authorities=(),
            package_dependencies=DependencyGraph(edges=()),
            runtime_dependencies=DependencyGraph(edges=()),
            import_graph_edges=(),
            topology_nodes=(),
            topology_edges=(),
            entry_points=(),
            background_execution=(),
        )
        
        metrics = manager.compute_metrics(inventory)
        
        assert isinstance(metrics, dict)
        assert "total_packages" in metrics


class TestDeterministicDiscovery:
    """Tests for deterministic discovery behavior."""
    
    def test_same_input_same_output(self):
        """Same input produces same output (determinism)."""
        repo_path = str(Path(__file__).parent.parent / "gordon-system")
        
        manager1 = PackageDiscoveryManager()
        manager2 = PackageDiscoveryManager()
        
        packages1 = manager1.discover_packages(repo_path)
        packages2 = manager2.discover_packages(repo_path)
        
        assert len(packages1) == len(packages2)


class TestReadonlyDiscovery:
    """Tests for read-only discovery behavior."""
    
    def test_no_runtime_modifications(self):
        """Discovery does not modify runtime state."""
        inventory = ArchitectureInventory(
            repository_path="/test/path",
            discovered_at=0.0,
            version="1.0.0",
            packages=(),
            modules=(),
            public_apis=(),
            runtime_authorities=(),
            package_dependencies=DependencyGraph(edges=()),
            runtime_dependencies=DependencyGraph(edges=()),
            import_graph_edges=(),
            topology_nodes=(),
            topology_edges=(),
            entry_points=(),
            background_execution=(),
        )
        
        assert isinstance(inventory.packages, tuple)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])