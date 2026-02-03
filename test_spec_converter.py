#!/usr/bin/env python3
"""Test spec converter"""
import sys
import json
from pathlib import Path
from amplifier_ux_analyzer.generators.spec_converter import SpecConverter


def test_converter():
    """Test JSON to YAML conversion"""
    # Check if we have reference analysis
    json_path = Path("~/dev/ANext/word3/UI/reference-clipped-analysis.json").expanduser()
    screenshot_path = Path("~/dev/ANext/word3/UI/reference-clipped.png").expanduser()
    output_path = Path("/tmp/test-converted-spec.yaml")
    
    if not json_path.exists():
        print(f"⚠️  Test JSON not found: {json_path}")
        print("Skipping test - run analyzer first to generate JSON")
        return 0
    
    print("📋 Loading analyzer JSON...")
    with open(json_path, 'r') as f:
        analyzer_json = json.load(f)
    print(f"✓ Loaded ({len(json.dumps(analyzer_json))} bytes)")
    
    print("\n🔄 Converting to spec YAML...")
    converter = SpecConverter()
    spec = converter.json_to_spec(analyzer_json, str(screenshot_path))
    
    print(f"✓ Converted")
    print(f"  - metadata: {len(spec['metadata'])} fields")
    print(f"  - visual_design: {len(spec['visual_design'])} sections")
    print(f"  - component_structure: {len(spec['component_structure'])} components")
    print(f"  - design_intent: {len(spec['design_intent'])} fields")
    print(f"  - implementation_notes: {len(spec['implementation_notes'])} fields")
    
    # Show some details
    print(f"\n📊 Spec Details:")
    print(f"  - Dimensions: {spec['visual_design']['dimensions']['width']}x{spec['visual_design']['dimensions']['height']}")
    print(f"  - Colors: {len(spec['visual_design']['color_palette'])} palette entries")
    print(f"  - Components: {list(spec['component_structure'].keys())}")
    
    print(f"\n💾 Saving to {output_path}...")
    converter.save_yaml(spec, str(output_path))
    print(f"✓ Saved ({output_path.stat().st_size} bytes)")
    
    print("\n✅ Conversion successful!")
    print(f"📁 Output: {output_path}")
    
    # Show a preview
    print("\n📄 Preview (first 20 lines):")
    print("-" * 60)
    with open(output_path, 'r') as f:
        for i, line in enumerate(f):
            if i >= 20:
                print("...")
                break
            print(line.rstrip())
    print("-" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(test_converter())
