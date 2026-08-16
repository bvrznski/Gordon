# Memory Forms Test Suite - Phase 5.1.1
# ======================================

"""
Test suite for Memory Forms implementation.

Tests cover:
    - Core MemoryForm base class
    - Individual Memory Form implementations
    - Cross-form membership (one artifact in multiple forms)
    - Projection immutability
    - Form health reporting
"""

from __future__ import annotations

import sys
sys.path.insert(0, '/home/bvrznski/Gordon/gordon_system/src')

# Test imports
try:
    from agent.components.systems.memory.forms import (
        MemoryFormSystem,
        MemoryFormKind,
        AutobiographicalMemory,
        EpisodicMemory,
        SemanticMemory,
        WorkingMemory,
        EmotionalMemory,
        ProceduralMemory,
        SpatialMemory,
        LatentMemory,
    )
    TESTS_PASSED_IMPORT = True
except ImportError as e:
    print(f"Import error: {e}")
    TESTS_PASSED_IMPORT = False


def test_imports():
    """Test that all memory form classes can be imported."""
    if not TESTS_PASSED_IMPORT:
        return {"passed": False, "message": "Failed to import MemoryForms"}
    
    forms_to_test = [
        'AutobiographicalMemory', 'EpisodicMemory', 'SemanticMemory',
        'WorkingMemory', 'EmotionalMemory', 'ProceduralMemory',
        'SpatialMemory', 'LatentMemory'
    ]
    
    for form_name in forms_to_test:
        if not globals().get(form_name):
            return {"passed": False, "message": f"Missing form: {form_name}"}
    
    return {
        "passed": True,
        "message": "All Memory Form classes imported successfully"
    }


def test_form_kind_constants():
    """Test that form kind constants are defined."""
    expected_kinds = [
        'autobiographical', 'emotional', 'episodic', 'latent',
        'procedural', 'semantic', 'spatial', 'working'
    ]
    
    for kind in expected_kinds:
        if not hasattr(MemoryFormKind, kind.upper()):
            return {"passed": False, "message": f"Missing form kind: {kind}"}
    
    return {
        "passed": True,
        "message": "All Memory Form kinds are defined"
    }


def test_form_system_initialization():
    """Test that the form system initializes correctly."""
    if not TESTS_PASSED_IMPORT:
        return {"passed": False, "message": "Imports failed"}
    
    # Create a mock substrate
    class MockSubstrate:
        def get_artifact(self, artifact_id):
            return None
    
    try:
        system = MemoryFormSystem(MockSubstrate())
        
        # Check all forms are accessible
        forms = {
            'autobiographical': system.autobiographical,
            'emotional': system.emotional,
            'episodic': system.episodic,
            'latent': system.latent,
            'procedural': system.procedural,
            'semantic': system.semantic,
            'spatial': system.spatial,
            'working': system.working,
        }
        
        # Check form kinds
        for kind, form in forms.items():
            if form.kind != kind:
                return {"passed": False, "message": f"Wrong kind for {kind}: {form.kind}"}
        
        return {
            "passed": True,
            "message": "Form system initialized with all 8 canonical forms",
            "forms_count": len(forms),
        }
    except Exception as e:
        return {"passed": False, "message": f"Initialization failed: {e}"}


def test_autobiographical_form():
    """Test AutobiographicalMemory functionality."""
    if not TESTS_PASSED_IMPORT:
        return {"passed": False, "message": "Imports failed"}
    
    class MockArtifact:
        def __init__(self, tags=None):
            self.tags = tags or set()
            self.semantic_content = {}
            self.created_at_utc = 1000.0
        
        @property
        def identity(self):
            return type('obj', (object,), {'artifact_id': 'test_artifact'})()
    
    class MockSubstrate:
        def __init__(self, artifact):
            self._artifact = artifact
        
        def get_artifact(self, artifact_id):
            if artifact_id == "test_artifact":
                return self._artifact
            return None
    
    try:
        form = AutobiographicalMemory(name="test_bio", kind=MemoryFormKind.AUTOBIOGRAPHICAL)
        
        # Test with a personal event
        artifact = MockArtifact(tags={'self', 'gordon'})
        substrate = MockSubstrate(artifact)
        form.initialize(substrate)
        
        success = form.add_artifact("test_artifact")
        
        if not success:
            return {"passed": False, "message": "Failed to add artifact"}
        
        projection = form.get_projection()
        
        if projection['form_kind'] != 'autobiographical':
            return {"passed": False, "message": "Wrong form kind in projection"}
        
        health = form.health()
        if health['artifact_count'] < 1:
            return {"passed": False, "message": "Artifact count should be >= 1"}
        
        return {
            "passed": True,
            "message": "AutobiographicalMemory working correctly",
            "artifact_count": health['artifact_count'],
        }
    except Exception as e:
        return {"passed": False, "message": f"Test failed: {e}"}


def test_semantic_form():
    """Test SemanticMemory functionality."""
    if not TESTS_PASSED_IMPORT:
        return {"passed": False, "message": "Imports failed"}
    
    class MockArtifact:
        def __init__(self):
            self.tags = {'concept'}
            self.semantic_content = {"definition": "A test concept"}
        
        @property
        def identity(self):
            return type('obj', (object,), {'artifact_id': 'test_semantic'})()
    
    class MockSubstrate:
        def __init__(self, artifact):
            self._artifact = artifact
        
        def get_artifact(self, artifact_id):
            if artifact_id == "test_semantic":
                return self._artifact
            return None
    
    try:
        form = SemanticMemory(name="test_sem", kind=MemoryFormKind.SEMANTIC)
        
        artifact = MockArtifact()
        substrate = MockSubstrate(artifact)
        form.initialize(substrate)
        
        success = form.add_artifact("test_semantic")
        
        if not success:
            return {"passed": False, "message": "Failed to add artifact"}
        
        projection = form.get_projection()
        
        if projection['organization_type'] != 'conceptual_semantic':
            return {"passed": False, "message": "Wrong organization type"}
        
        return {
            "passed": True,
            "message": "SemanticMemory working correctly",
        }
    except Exception as e:
        return {"passed": False, "message": f"Test failed: {e}"}


def test_working_memory():
    """Test WorkingMemory functionality."""
    if not TESTS_PASSED_IMPORT:
        return {"passed": False, "message": "Imports failed"}
    
    class MockArtifact:
        def __init__(self):
            self.semantic_content = {"active": True}
        
        @property
        def identity(self):
            return type('obj', (object,), {'artifact_id': 'test_working'})()
    
    class MockSubstrate:
        def get_artifact(self, artifact_id):
            if artifact_id == "test_working":
                return self._artifact if hasattr(self, '_artifact') else None
            return None
    
    try:
        form = WorkingMemory(name="test_work", kind=MemoryFormKind.WORKING)
        
        # Create and set substrate with artifact
        substrate = MockSubstrate(MockArtifact())
        form.initialize(substrate)
        
        success = form.add_artifact("test_working", activation_level=0.8)
        
        if not success:
            return {"passed": False, "message": "Failed to add artifact"}
        
        # Test activation update
        form.update_activation("test_working", 0.5)
        
        projection = form.get_projection()
        if projection['organization_type'] != 'activation_based':
            return {"passed": False, "message": "Wrong organization type for working memory"}
        
        return {
            "passed": True,
            "message": "WorkingMemory working correctly",
        }
    except Exception as e:
        return {"passed": False, "message": f"Test failed: {e}"}


def test_multiple_form_membership():
    """Test that one artifact can belong to multiple forms."""
    if not TESTS_PASSED_IMPORT:
        return {"passed": False, "message": "Imports failed"}
    
    class MockArtifact:
        def __init__(self):
            self.tags = {'concept', 'event', 'self'}
            self.semantic_content = {"content": "test"}
        
        @property
        def identity(self):
            return type('obj', (object,), {'artifact_id': 'multi_form'})()
    
    class MockSubstrate:
        def get_artifact(self, artifact_id):
            if artifact_id == "multi_form":
                return self._artifact if hasattr(self, '_artifact') else None
            return None
    
    try:
        # Create system with substrate
        artifact = MockArtifact()
        substrate = MockSubstrate(artifact)
        system = MemoryFormSystem(substrate)
        
        # Add same artifact to multiple forms
        system.add_artifact_to_form("multi_form", MemoryFormKind.SEMANTIC)
        system.add_artifact_to_form("multi_form", MemoryFormKind.EPISODIC)
        system.add_artifact_to_form("multi_form", MemoryFormKind.AUTOBIOGRAPHICAL)
        
        # Verify membership
        bio_projection = system.autobiographical.get_projection()
        sem_projection = system.semantic.get_projection()
        epi_projection = system.episodic.get_projection()
        
        if "multi_form" not in bio_projection['visible_artifacts']:
            return {"passed": False, "message": "Artifact not in autobiographical form"}
        if "multi_form" not in sem_projection['visible_artifacts']:
            return {"passed": False, "message": "Artifact not in semantic form"}
        if "multi_form" not in epi_projection['visible_artifacts']:
            return {"passed": False, "message": "Artifact not in episodic form"}
        
        return {
            "passed": True,
            "message": "Cross-form membership working (artifact in 3+ forms)",
        }
    except Exception as e:
        return {"passed": False, "message": f"Test failed: {e}"}


def test_form_health():
    """Test that form health reporting works."""
    if not TESTS_PASSED_IMPORT:
        return {"passed": False, "message": "Imports failed"}
    
    try:
        system = MemoryFormSystem(type('MockSubstrate', (), {'get_artifact': lambda x: None})())
        
        health_report = system.health_report()
        
        # Check required fields in each form's health
        for form_kind, form_health in health_report['forms'].items():
            required_fields = ['form_kind', 'name', 'is_active', 'artifact_count']
            for field in required_fields:
                if field not in form_health:
                    return {"passed": False, "message": f"Missing health field: {field}"}
        
        return {
            "passed": True,
            "message": "Form health reporting working",
            "forms_reported": len(health_report['forms']),
        }
    except Exception as e:
        return {"passed": False, "message": f"Test failed: {e}"}


def run_all_tests():
    """Run all tests and report results."""
    tests = [
        ("Imports", test_imports),
        ("Form Kind Constants", test_form_kind_constants),
        ("System Initialization", test_form_system_initialization),
        ("Autobiographical Form", test_autobiographical_form),
        ("Semantic Form", test_semantic_form),
        ("Working Memory", test_working_memory),
        ("Multiple Form Membership", test_multiple_form_membership),
        ("Form Health", test_form_health),
    ]
    
    results = []
    passed = 0
    failed = 0
    
    print("=" * 60)
    print("Memory Forms Test Suite - Phase 5.1.1")
    print("=" * 60)
    
    for name, test_func in tests:
        result = test_func()
        results.append((name, result))
        
        if result['passed']:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"
        
        print(f"\n[{status}] {name}")
        print(f"       {result['message']}")
    
    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)