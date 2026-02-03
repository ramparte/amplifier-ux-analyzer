"""Color utilities for image analysis"""
from typing import Tuple


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color
    
    Args:
        rgb: RGB color tuple (r, g, b) with values 0-255
        
    Returns:
        Hex color string in format #RRGGBB
        
    Example:
        >>> rgb_to_hex((255, 0, 0))
        '#ff0000'
    """
    return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
