#!/usr/bin/env python3
"""Test spec parser with word-clone-spec.yaml"""
import sys
from pathlib import Path
from amplifier_ux_analyzer.generators.spec_parser import SpecParser

def test_word_clone_spec():
    """Test parsing word-clone-spec.yaml"""
    spec_path = Path("~/dev/ANext/word3/UI/word-clone-spec.yaml").expanduser()
    
    if not spec_path.exists():
        print(f"ERROR: Spec file not found: {spec_path}")
        return 1
    
    parser = SpecParser()
    
    print("📋 Loading spec...")
    try:
        spec = parser.load(str(spec_path))
        print(f"✓ Spec loaded successfully")
        print(f"  Dimensions: {spec.dimensions}")
        print(f"  Colors: {len(spec.visual_design.color_palette)}")
        print(f"  Components: {len(spec.component_structure)}")
        
    except Exception as e:
        print(f"✗ Failed to load spec: {e}")
        return 1
    
    print("\n📝 Generating LLM prompt...")
    try:
        prompt = parser.to_prompt(spec)
        print(f"✓ Prompt generated ({len(prompt)} characters)")
        print("\nPrompt preview (first 500 chars):")
        print("-" * 50)
        print(prompt[:500])
        print("-" * 50)
        
    except Exception as e:
        print(f"✗ Failed to generate prompt: {e}")
        return 1
    
    print("\n✅ All tests passed!")
    return 0

if __name__ == "__main__":
    sys.exit(test_word_clone_spec())
