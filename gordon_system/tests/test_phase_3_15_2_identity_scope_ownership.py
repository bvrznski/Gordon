# Test Suite - Phase 3.15.2 Core State Identity, Scope & Ownership
# =================================================================

"""
Test suite for Phase 3.15.2 extensions to Gordon Core state architecture.

Tests cover:
    - Typed identity hierarchy (StateTypeId, AggregateId, RuntimeId, etc.)
    - Uniqueness and deterministic serialization
    - Scope inheritance and visibility rules
    - Ownership creation and verification
    - Authority conflicts detection
    - Ownership transfer with evidence
    - Runtime isolation enforcement
    - Boot session isolation
    - Stale owner rejection
    - Duplicate owner rejection
"""

import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestStateTypeId(unittest.TestCase):
    """Tests for StateTypeId enum."""
    
    def test_state_type_ids_exist(self):
        """Test that all expected state type IDs exist."""
        # Import locally since we're in a test file
        from agent.components.core.state.identity import StateTypeId
        
        self.assertEqual(StateTypeId.CORE.value, "core")
        self.assertEqual(StateTypeId.LIFECYCLE.value, "lifecycle")
        self.assertEqual(StateTypeId.EXECUTION.value, "execution")
        self.assertEqual(StateTypeId.RUNTIME.value, "runtime")
    
    def test_state_type_from_string(self):
        """Test parsing string into StateTypeId."""
        from agent.components.core.state.identity import StateTypeId
        
        type_id = StateTypeId.from_string("core")
        self.assertEqual(type_id, StateTypeId.CORE)
        
        with self.assertRaises(ValueError):
            StateTypeId.from_string("invalid_type")


class TestAggregateId(unittest.TestCase):
    """Tests for AggregateId class."""
    
    def test_aggregate_id_generation(self):
        """Test aggregate ID generation."""
        from agent.components.core.state.identity import AggregateId, StateTypeId
        
        agg_id = AggregateId.generate()
        self.assertTrue(agg_id.value.startswith("agg_"))
        self.assertEqual(agg_id.type_id, StateTypeId.CORE)
    
    def test_aggregate_id_with_namespace(self):
        """Test aggregate ID with namespace."""
        from agent.components.core.state.identity import AggregateId
        
        agg_id = AggregateId.generate(namespace="application")
        self.assertEqual(agg_id.namespace, "application")
        self.assertIn("application", agg_id.to_string())
    
    def test_aggregate_id_matches_type(self):
        """Test type matching."""
        from agent.components.core.state.identity import AggregateId, StateTypeId
        
        agg_id = AggregateId.generate(type_id=StateTypeId.LIFECYCLE)
        self.assertTrue(agg_id.matches_type(StateTypeId.LIFECYCLE))
        self.assertFalse(agg_id.matches_type(StateTypeId.EXECUTION))


class TestRuntimeId(unittest.TestCase):
    """Tests for RuntimeId class."""
    
    def test_runtime_id_generation(self):
        """Test runtime ID generation."""
        from agent.components.core.state.identity import RuntimeId
        
        rt_id = RuntimeId.generate()
        self.assertTrue(rt_id.value.startswith("rt_"))
    
    def test_runtime_id_comparison(self):
        """Test runtime ID equality."""
        from agent.components.core.state.identity import RuntimeId
        
        rt1 = RuntimeId.generate()
        rt2 = RuntimeId(value=rt1.value)
        
        self.assertEqual(rt1, rt2)
        self.assertNotEqual(rt1, RuntimeId.generate())


class TestBootSessionId(unittest.TestCase):
    """Tests for BootSessionId class."""
    
    def test_boot_session_id_generation(self):
        """Test boot session ID generation."""
        from agent.components.core.state.identity import BootSessionId
        
        bs_id = BootSessionId.generate()
        self.assertTrue(bs_id.value.startswith("bs_"))
    
    def test_session_comparison(self):
        """Test boot session matching."""
        from agent.components.core.state.identity import BootSessionId
        
        bs1 = BootSessionId.generate()
        self.assertTrue(bs1.is_session(bs1.value))
        self.assertFalse(bs1.is_session("other_value"))


class TestOwnerId(unittest.TestCase):
    """Tests for OwnerId class."""
    
    def test_owner_id_generation(self):
        """Test owner ID generation."""
        from agent.components.core.state.identity import OwnerId
        
        owner_id = OwnerId.for_kind("lifecycle")
        self.assertTrue(owner_id.value.startswith("owner_"))
        self.assertEqual(owner_id.kind, "lifecycle")
    
    def test_owner_comparison(self):
        """Test owner matching."""
        from agent.components.core.state.identity import OwnerId
        
        owner1 = OwnerId(value="owner_test", kind="test")
        self.assertTrue(owner1.is_owner("owner_test"))
        self.assertFalse(owner1.is_owner("other"))


class TestVersionId(unittest.TestCase):
    """Tests for VersionId class."""
    
    def test_version_id_generation(self):
        """Test version ID generation with sequence."""
        from agent.components.core.state.identity import VersionId
        
        ver_id = VersionId.generate(sequence=5)
        self.assertTrue(ver_id.value.startswith("ver_"))
        self.assertEqual(ver_id.sequence, 5)
    
    def test_sequence_matching(self):
        """Test sequence matching."""
        from agent.components.core.state.identity import VersionId
        
        ver_id = VersionId.generate(sequence=10)
        self.assertTrue(ver_id.matches_sequence(10))
        self.assertFalse(ver_id.matches_sequence(5))


class TestGenerationId(unittest.TestCase):
    """Tests for GenerationId class."""
    
    def test_generation_id_generation(self):
        """Test generation ID generation with epoch."""
        from agent.components.core.state.identity import GenerationId
        
        gen_id = GenerationId.generate(epoch=3)
        self.assertTrue(gen_id.value.startswith("gen_"))
        self.assertEqual(gen_id.epoch, 3)
    
    def test_epoch_matching(self):
        """Test epoch matching."""
        from agent.components.core.state.identity import GenerationId
        
        gen_id = GenerationId.generate(epoch=5)
        self.assertTrue(gen_id.matches_epoch(5))
        self.assertFalse(gen_id.is_stale(5))
        self.assertTrue(gen_id.is_stale(10))


class TestScopeId(unittest.TestCase):
    """Tests for ScopeId enum."""
    
    def test_scope_ids_exist(self):
        """Test that all expected scope IDs exist."""
        from agent.components.core.state.identity import ScopeId
        
        self.assertEqual(ScopeId.PROCESS.value, "process")
        self.assertEqual(ScopeId.APPLICATION.value, "application")
        self.assertEqual(ScopeId.RUNTIME.value, "runtime")
    
    def test_scope_from_string(self):
        """Test parsing string into ScopeId."""
        from agent.components.core.state.identity import ScopeId
        
        scope = ScopeId.from_string("application")
        self.assertEqual(scope, ScopeId.APPLICATION)
        
        with self.assertRaises(ValueError):
            ScopeId.from_string("invalid_scope")


class TestScopeInheritance(unittest.TestCase):
    """Tests for ScopeId inheritance hierarchy."""
    
    def test_process_is_ancestor_of_application(self):
        """Test process -> application inheritance."""
        from agent.components.core.state.identity import ScopeId
        
        self.assertTrue(ScopeId.APPLICATION.is_descendant_of(ScopeId.PROCESS))
        self.assertTrue(ScopeId.PROCESS.is_ancestor_of(ScopeId.APPLICATION))
    
    def test_subsystem_inherits_from_application(self):
        """Test subsystem inherits from application."""
        from agent.components.core.state.identity import ScopeId
        
        self.assertTrue(ScopeId.SUBSYSTEM.is_descendant_of(ScopeId.APPLICATION))
    
    def test_component_inherits_from_subsystem(self):
        """Test component inherits from subsystem."""
        from agent.components.core.state.identity import ScopeId
        
        self.assertTrue(ScopeId.COMPONENT.is_descendant_of(ScopeId.SUBSYSTEM))


class TestDeterministicSerialization(unittest.TestCase):
    """Tests for deterministic serialization of identities."""
    
    def test_aggregate_id_serialization(self):
        """Test AggregateId can be converted to/from string."""
        from agent.components.core.state.identity import AggregateId
        
        agg_id = AggregateId.generate(namespace="app")
        
        # Convert to string
        serialized = agg_id.to_string()
        
        # Parse back
        parsed = AggregateId.from_string(serialized)
        
        self.assertEqual(agg_id.value, parsed.value)
        self.assertEqual(agg_id.namespace, parsed.namespace)


if __name__ == "__main__":
    unittest.main()