#!/usr/bin/env python3
"""Test that package structure works without external dependencies"""

import sys
sys.path.insert(0, '.')

print("Testing package structure...")
print("-" * 50)

# Test 1: Color utilities (no external dependencies)
print("\n✓ Test 1: Color utilities")
from amplifier_ux_analyzer.utils.colors import rgb_to_hex
result = rgb_to_hex((255, 0, 0))
assert result == '#ff0000', f"Expected #ff0000, got {result}"
print(f"  rgb_to_hex((255,0,0)) = {result}")

# Test 2: UIElement class (no external dependencies)
print("\n✓ Test 2: UIElement class")
from amplifier_ux_analyzer.core.elements import UIElement
elem = UIElement('button', {'x': 10, 'y': 20, 'width': 100, 'height': 30})
elem_dict = elem.to_dict()
assert elem_dict['type'] == 'button'
assert elem_dict['bounds']['x'] == 10
print(f"  UIElement created: {elem_dict['type']} at x={elem_dict['bounds']['x']}")

# Test 3: Package exports
print("\n✓ Test 3: Package exports")
import amplifier_ux_analyzer
assert hasattr(amplifier_ux_analyzer, '__version__')
assert hasattr(amplifier_ux_analyzer, 'rgb_to_hex')
assert hasattr(amplifier_ux_analyzer, 'UIElement')
print(f"  Package version: {amplifier_ux_analyzer.__version__}")
print(f"  Exports: {', '.join(amplifier_ux_analyzer.__all__)}")

# Test 4: CLI module structure
print("\n✓ Test 4: CLI module structure")
from amplifier_ux_analyzer.cli import main
assert callable(main)
print(f"  CLI entry point exists: {main.__name__}")

# Test 5: Analyzer structure (will fail on init without deps, but import should work)
print("\n✓ Test 5: Analyzer module structure")
from amplifier_ux_analyzer.core import analyzer
assert hasattr(analyzer, 'UXAnalyzer')
assert hasattr(analyzer, 'HAS_OCR')
assert hasattr(analyzer, 'HAS_CV2')
print(f"  UXAnalyzer class available")
print(f"  HAS_OCR: {analyzer.HAS_OCR}")
print(f"  HAS_CV2: {analyzer.HAS_CV2}")

print("\n" + "=" * 50)
print("✅ ALL STRUCTURE TESTS PASSED!")
print("=" * 50)
print("\nNote: Full functionality requires installing dependencies:")
print("  pip install opencv-python pillow numpy easyocr")
