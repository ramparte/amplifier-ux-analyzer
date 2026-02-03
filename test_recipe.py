#!/usr/bin/env python3
"""Test recipe structure validation"""
import sys
import yaml
from pathlib import Path


def test_recipes():
    """Validate recipe YAML structure"""
    recipe_dir = Path("amplifier_ux_analyzer/recipes")
    
    recipes = [
        recipe_dir / "roundtrip.yaml",
        recipe_dir / "simple-generate.yaml"
    ]
    
    print("🧪 Testing Recipe Structure\n")
    
    all_valid = True
    
    for recipe_path in recipes:
        print(f"📋 Validating {recipe_path.name}...")
        
        if not recipe_path.exists():
            print(f"   ✗ Recipe not found: {recipe_path}")
            all_valid = False
            continue
        
        try:
            with open(recipe_path, 'r') as f:
                recipe = yaml.safe_load(f)
            
            # Check required fields
            required = ['name', 'description', 'steps']
            missing = [field for field in required if field not in recipe]
            
            if missing:
                print(f"   ✗ Missing required fields: {', '.join(missing)}")
                all_valid = False
                continue
            
            # Validate steps structure
            if not isinstance(recipe['steps'], list):
                print(f"   ✗ 'steps' must be a list")
                all_valid = False
                continue
            
            if len(recipe['steps']) == 0:
                print(f"   ✗ Recipe has no steps")
                all_valid = False
                continue
            
            # Check each step has required fields
            for i, step in enumerate(recipe['steps']):
                if 'id' not in step:
                    print(f"   ✗ Step {i} missing 'id' field")
                    all_valid = False
                if 'type' not in step:
                    print(f"   ✗ Step {i} missing 'type' field")
                    all_valid = False
            
            # Check context if present
            if 'context' in recipe:
                if not isinstance(recipe['context'], dict):
                    print(f"   ✗ 'context' must be a dictionary")
                    all_valid = False
            
            # Check deliverable if present
            if 'deliverable' in recipe:
                if 'type' not in recipe['deliverable']:
                    print(f"   ✗ 'deliverable' missing 'type' field")
                    all_valid = False
            
            # All checks passed
            print(f"   ✓ Valid structure")
            print(f"   - Name: {recipe['name']}")
            print(f"   - Steps: {len(recipe['steps'])}")
            if 'context' in recipe:
                print(f"   - Context vars: {len(recipe['context'])}")
            print()
            
        except yaml.YAMLError as e:
            print(f"   ✗ YAML parse error: {e}")
            all_valid = False
        except Exception as e:
            print(f"   ✗ Validation error: {e}")
            all_valid = False
    
    if all_valid:
        print("✅ All recipes valid!\n")
        return 0
    else:
        print("❌ Some recipes have errors\n")
        return 1


if __name__ == "__main__":
    sys.exit(test_recipes())
