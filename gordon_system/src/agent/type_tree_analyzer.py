#!/usr/bin/env python3
"""
Pre-Migration Forensic Inventory Generator for Type Tree Normalization.
Generates comprehensive analysis of flattened class families that need normalization.
"""

import os
import re
import json
import ast
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set

AGENT_SRC_PATH = "/home/bvrznski/Gordon/gordon_system/src/agent"

class ClassInfo:
    def __init__(self, name: str, module_path: str, line_no: int):
        self.name = name
        self.module_path = module_path
        self.line_no = line_no
        self.nested_classes: List[str] = []
        self.is_enum = False
        
class SemanticFamily:
    def __init__(self, base_name: str = None):
        self.base_name = base_name or ""
        self.members: Dict[str, ClassInfo] = {}
        
def extract_classes_from_file(file_path: Path) -> Tuple[List[ClassInfo], Set[str]]:
    """Extract all class definitions from a Python file."""
    classes = []
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = ClassInfo(
                        name=node.name,
                        module_path=str(file_path.relative_to(Path(AGENT_SRC_PATH).parent)),
                        line_no=node.lineno
                    )
                    
                    # Check for enum inheritance
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            if 'Enum' in base.id or 'Flag' in base.id:
                                class_info.is_enum = True
                                break
                    
                    classes.append(class_info)
                    
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        imports.add(alias.name)
                        
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        
    return classes, imports


def identify_flattened_families(classes: List[ClassInfo]) -> Dict[str, SemanticFamily]:
    """Identify families of classes that share semantic prefixes and need nesting."""
    
    # Key patterns for flattened class names
    patterns = [
        # ExecutiveDecision patterns - these should be nested under ExecutiveDecision
        (r'^ExecutiveDecision(\w*)$', 'ExecutiveDecision'),
        (r'^ExecutiveConflict(\w*)$', 'ExecutiveConflict'),
        (r'^ExecutiveState(\w*)$', 'ExecutiveState'),
        (r'^ExecutiveControlAllocation(\w*)$', 'ExecutiveControl'),
        (r'^ExecutiveProgram(\w*)$', 'ExecutiveProgram'),
        (r'^ExecutiveStrategy(\w*)$', 'ExecutiveStrategy'),
        (r'^ExecutiveDemand(\w*)$', 'ExecutiveDemand'),
        (r'^ExecutiveGoal(\w*)$', 'ExecutiveGoal'),
        
        # Network patterns
        (r'^NetworkActivation(\w*)$', 'NetworkActivation'),
        (r'^DefaultNetwork(\w*)$', 'DefaultNetwork'),
        
        # ExecutiveDecision Coordination family
        (r'^ExecutiveDecisionCoordination(\w*)$', 'ExecutiveDecisionCoordination'),
        
        # ExecutiveControlAllocation family
        (r'^ExecutiveControlAllocation(\w*)$', 'ExecutiveControl'),
    ]
    
    families = defaultdict(SemanticFamily)
    
    for cls in classes:
        name = cls.name
        
        # Check if this class is part of a flattened family
        for pattern, canonical_base in patterns:
            match = re.match(pattern, name)
            if match:
                semantic_key = f"{canonical_base}."
                families[semantic_key].base_name = canonical_base
                families[semantic_key].members[name] = cls
                break
    
    return dict(families)


def analyze_directory(src_path: str) -> Dict:
    """Analyze entire source directory for type tree normalization."""
    
    results = {
        'total_files': 0,
        'total_classes': 0,
        'top_level_classes': [],
        'nested_classes': [],
        'flattened_families': {},
        'imports_found': set(),
    }
    
    agent_path = Path(src_path)
    
    for py_file in agent_path.rglob('*.py'):
        if py_file.name.startswith('__') and py_file.name.endswith('.py'):
            continue
            
        classes, imports = extract_classes_from_file(py_file)
        results['total_files'] += 1
        results['total_classes'] += len(classes)
        
        for cls in classes:
            results['top_level_classes'].append(cls)
            
        results['imports_found'].update(imports)
    
    # Identify flattened families
    results['flattened_families'] = identify_flattened_families(results['top_level_classes'])
    
    return results


def generate_inventory(src_path: str, output_file: str):
    """Generate comprehensive pre-migration inventory."""
    
    print(f"Analyzing {src_path}...")
    results = analyze_directory(src_path)
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=lambda x: x.__dict__ if hasattr(x, '__dict__') else str(x))
    
    print(f"Total files analyzed: {results['total_files']}")
    print(f"Total classes found: {results['total_classes']}")
    print(f"Flattened families identified: {len(results['flattened_families'])}")
    
    # Print top flattened families
    print("\n=== Top Flattened Families by Member Count ===")
    sorted_families = sorted(
        results['flattened_families'].items(),
        key=lambda x: len(x[1].members),
        reverse=True
    )
    
    for family_key, family in sorted_families[:30]:
        if len(family.members) > 1:
            print(f"\n{family_key}: {len(family.members)} members")
            for name, cls_info in list(family.members.items())[:5]:
                print(f"  - {name} ({cls_info.module_path}:{cls_info.line_no})")


if __name__ == '__main__':
    output_file = "/tmp/type_tree_inventory.json"
    generate_inventory(AGENT_SRC_PATH, output_file)
    
    print(f"\nInventory saved to: {output_file}")