"""UI Element data structures"""
from typing import Any, Dict, Optional


class UIElement:
    """Represents a detected UI element"""
    
    def __init__(self, element_type: str, bounds: Dict[str, int], 
                 properties: Optional[Dict[str, Any]] = None):
        self.type = element_type
        self.bounds = bounds
        self.properties = properties or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "bounds": self.bounds,
            "properties": self.properties
        }
