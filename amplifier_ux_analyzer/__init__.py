"""Amplifier UX Analyzer - AI-powered screenshot analysis

This package provides tools for analyzing UI screenshots and extracting
structured information about layout, colors, elements, and text.

Basic usage:
    from amplifier_ux_analyzer import UXAnalyzer
    
    analyzer = UXAnalyzer("screenshot.png")
    result = analyzer.analyze()
    
    # Save to JSON
    analyzer.save_json("output.json")
    
    # Create visualization
    analyzer.visualize("annotated.png")
"""

from .core.analyzer import UXAnalyzer, HAS_OCR
from .core.elements import UIElement
from .utils.colors import rgb_to_hex

__version__ = "0.2.0"

__all__ = [
    "UXAnalyzer",
    "UIElement",
    "rgb_to_hex",
    "HAS_OCR",
]
