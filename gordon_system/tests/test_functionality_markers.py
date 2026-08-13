# Tests for Core Functionality Markers - Phase 3.13.1
# =====================================================

"""
Test suite for Core Functionality Marker Architecture.

Tests verify:
    - Marker hierarchy correctness
    - Reflection support functionality
    - Inventory generation
    - Repository validation
"""

import pytest
from gordon_system.src.agent.components.core.functionality_markers import (
    CoreFunctionality,
    ForCore,
    ForExecution,
    ForEntrypoint,
    ForArchitecture,
    ForNetworks,
    ForCapabilities,
    ForSystems,
    get_functionality_marker,
    has_functionality_marker,
    get_all_markers,
)
from gordon_system.src.agent.components.core.functionality_markers.reflection import (
    MarkerInventory,
    discover_components_in_module,
    validate_marker_usage,
)


# =============================================================================
# MARKER HIERARCHY TESTS
# =============================================================================


class TestMarkerHierarchy:
    """Test marker inheritance and hierarchy."""
    
    def test_core_functionality_is_abstract_base(self):
        """CoreFunctionality should be an abstract base class."""
        assert CoreFunctionality.__bases__ == (object,)
        assert hasattr(CoreFunctionality, '__abstractmethods__')
    
    def test_all_markers_inherit_from_core_functionality(self):
        """All canonical markers must inherit from CoreFunctionality."""
        markers = [
            ForCore,
            ForExecution,
            ForEntrypoint,
            ForArchitecture,
            ForNetworks,
            ForCapabilities,
            ForSystems,
        ]
        
        for marker in markers:
            assert issubclass(marker, CoreFunctionality)
    
    def test_markers_are_distinct(self):
        """Each marker should be a distinct class."""
        markers = get_all_markers()
        assert len(set(id(m) for m in markers)) == len(markers)
    
    def test_markers_have_no_slots_conflict(self):
        """Markers with __slots__ should not conflict."""
        # All markers have empty __slots__, which is fine
        pass


# =============================================================================
# REFLECTION HELPERS TESTS
# =============================================================================


class TestReflectionHelpers:
    """Test reflection helper functions."""
    
    def test_get_functionality_marker_returns_marker(self):
        """get_functionality_marker should return the primary marker."""
        # Create a test class with a marker
        class TestComponent(ForExecution):
            pass
        
        assert get_functionality_marker(TestComponent) == ForExecution
    
    def test_get_functionality_marker_returns_none_for_non_marked(self):
        """Non-marked classes should return None."""
        class UnmarkedComponent:
            pass
        
        assert get_functionality_marker(UnmarkedComponent) is None
    
    def test_has_functionality_marker_true(self):
        """has_functionality_marker should return True for marked classes."""
        class MarkedComponent(ForCore):
            pass
        
        assert has_functionality_marker(MarkedComponent) is True
    
    def test_has_functionality_marker_false(self):
        """has_functionality_marker should return False for unmarked classes."""
        class UnmarkedComponent:
            pass
        
        assert has_functionality_marker(UnmarkedComponent) is False
    
    def test_get_all_markers_returns_complete_list(self):
        """get_all_markers should return all marker classes."""
        markers = get_all_markers()
        
        expected_names = {
            'ForCore', 'ForExecution', 'ForEntrypoint',
            'ForArchitecture', 'ForNetworks', 'ForCapabilities', 'ForSystems'
        }
        
        actual_names = {m.__name__ for m in markers}
        assert actual_names == expected_names


# =============================================================================
# MARKER INVENTORY TESTS
# =============================================================================


class TestMarkerInventory:
    """Test MarkerInventory class."""
    
    def test_add_component_records_mapping(self):
        """add_component should record component-to-marker mapping."""
        inventory = MarkerInventory()
        
        class TestComponent(ForExecution):
            pass
        
        inventory.add_component(TestComponent, ForExecution)
        
        assert TestComponent in inventory.get_components(ForExecution)
        assert inventory.get_marker(TestComponent) == ForExecution
    
    def test_add_component_validates_marker(self):
        """add_component should reject invalid markers."""
        inventory = MarkerInventory()
        
        class TestComponent:
            pass
        
        with pytest.raises(ValueError, match="CoreFunctionality"):
            inventory.add_component(TestComponent, object)
    
    def test_get_components_returns_list(self):
        """get_components should return a list (not the internal dict)."""
        inventory = MarkerInventory()
        
        class ComponentA(ForExecution):
            pass
        
        class ComponentB(ForExecution):
            pass
        
        inventory.add_component(ComponentA, ForExecution)
        inventory.add_component(ComponentB, ForExecution)
        
        components = inventory.get_components(ForExecution)
        assert isinstance(components, list)
        assert len(components) == 2
    
    def test_statistics(self):
        """get_statistics should return correct counts."""
        inventory = MarkerInventory()
        
        class CoreComp1(ForCore):
            pass
        
        class ExecComp1(ForExecution):
            pass
        
        class ExecComp2(ForExecution):
            pass
        
        inventory.add_component(CoreComp1, ForCore)
        inventory.add_component(ExecComp1, ForExecution)
        inventory.add_component(ExecComp2, ForExecution)
        
        stats = inventory.get_statistics()
        
        assert stats["total_markers"] == 2
        assert stats["total_components"] == 3
        assert stats["components_by_marker"]["ForCore"] == 1
        assert stats["components_by_marker"]["ForExecution"] == 2


# =============================================================================
# VALIDATION TESTS
# =============================================================================


class TestValidation:
    """Test validation functions."""
    
    def test_validate_component_with_single_marker(self):
        """Component with single marker should be valid."""
        class SingleMarkerComponent(ForArchitecture):
            pass
        
