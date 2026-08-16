# Simple Memory Forms Test
# =========================

import sys
sys.path.insert(0, '/home/bvrznski/Gordon/gordon_system/src')

# Direct import from forms module (bypass package init)
from gordon_system.src.agent.components.systems.memory.forms.autobiographical import AutobiographicalMemory
from gordon_system.src.agent.components.systems.memory.forms.semantic import SemanticMemory
from gordon_system.src.agent.components.systems.memory.forms.episodic import EpisodicMemory
from gordon_system.src.agent.components.systems.memory.forms.working import WorkingMemory

print("Testing individual form imports...")

# Test Autobiographical Memory
form1 = AutobiographicalMemory(name="test_bio", kind="autobiographical")
assert form1.kind == "autobiographical"
print("✓ AutobiographicalMemory imported and initialized")

# Test Semantic Memory  
form2 = SemanticMemory(name="test_sem", kind="semantic")
assert form2.kind == "semantic"
print("✓ SemanticMemory imported and initialized")

# Test Episodic Memory
form3 = EpisodicMemory(name="test_epi", kind="episodic")
assert form3.kind == "episodic"
print("✓ EpisodicMemory imported and initialized")

# Test Working Memory
form4 = WorkingMemory(name="test_work", kind="working")
assert form4.kind == "working"
print("✓ WorkingMemory imported and initialized")

print("\nAll individual forms work correctly!")
print("\nForm kinds:")
print(f"  Autobiographical: {form1.kind}")
print(f"  Semantic: {form2.kind}")
print(f"  Episodic: {form3.kind}")
print(f"  Working: {form4.kind}")