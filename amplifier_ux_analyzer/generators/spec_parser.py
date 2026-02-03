"""UI spec parser and validator"""
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class VisualDesign:
    """Visual design specifications"""
    dimensions: Dict[str, int]
    color_palette: Dict[str, str]
    spacing: Optional[Dict[str, Any]] = None
    typography: Optional[Dict[str, Any]] = None


@dataclass
class ComponentSpec:
    """Single component specification"""
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    children: List['ComponentSpec'] = field(default_factory=list)


@dataclass
class UISpec:
    """Complete UI specification"""
    metadata: Dict[str, Any]
    design_intent: Dict[str, Any]
    visual_design: VisualDesign
    component_structure: Dict[str, ComponentSpec]
    implementation_notes: Dict[str, Any]
    
    @property
    def dimensions(self) -> tuple:
        """Get dimensions as tuple"""
        return (
            self.visual_design.dimensions['width'],
            self.visual_design.dimensions['height']
        )


class SpecParser:
    """Parse and validate UI specifications"""
    
    REQUIRED_FIELDS = [
        'metadata',
        'design_intent', 
        'visual_design',
        'component_structure'
    ]
    
    def __init__(self):
        pass
    
    def load(self, spec_path: str) -> UISpec:
        """
        Load and validate YAML spec.
        
        Args:
            spec_path: Path to YAML spec file
        
        Returns:
            UISpec: Validated specification
        
        Raises:
            FileNotFoundError: If spec file not found
            ValueError: If spec is invalid
        """
        path = Path(spec_path)
        if not path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")
        
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Validate
        validation_result = self.validate(data)
        if not validation_result['valid']:
            errors = '\n  - '.join(validation_result['errors'])
            raise ValueError(f"Invalid spec:\n  - {errors}")
        
        # Build UISpec
        return self._build_spec(data)
    
    def validate(self, spec_data: Dict) -> Dict[str, Any]:
        """
        Validate spec structure and required fields.
        
        Args:
            spec_data: Raw spec dictionary
        
        Returns:
            dict: {'valid': bool, 'errors': List[str]}
        """
        errors = []
        
        # Check required top-level fields
        for field in self.REQUIRED_FIELDS:
            if field not in spec_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate visual_design if present
        if 'visual_design' in spec_data:
            vd = spec_data['visual_design']
            if 'dimensions' not in vd:
                errors.append("visual_design missing 'dimensions'")
            elif not isinstance(vd['dimensions'], dict):
                errors.append("visual_design.dimensions must be a dict")
            elif 'width' not in vd['dimensions'] or 'height' not in vd['dimensions']:
                errors.append("visual_design.dimensions must have 'width' and 'height'")
            
            if 'color_palette' not in vd:
                errors.append("visual_design missing 'color_palette'")
            elif not isinstance(vd['color_palette'], dict):
                errors.append("visual_design.color_palette must be a dict")
            else:
                # Validate hex colors
                for name, color in vd['color_palette'].items():
                    if not isinstance(color, str) or not color.startswith('#'):
                        errors.append(f"color_palette.{name} must be hex color (e.g., #ffffff)")
        
        # Validate component_structure if present
        if 'component_structure' in spec_data:
            cs = spec_data['component_structure']
            if not isinstance(cs, dict):
                errors.append("component_structure must be a dict")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _build_spec(self, data: Dict) -> UISpec:
        """Build UISpec from validated data"""
        # Build VisualDesign
        vd_data = data['visual_design']
        visual_design = VisualDesign(
            dimensions=vd_data['dimensions'],
            color_palette=vd_data['color_palette'],
            spacing=vd_data.get('spacing'),
            typography=vd_data.get('typography')
        )
        
        # Build ComponentSpecs
        components = {}
        for name, comp_data in data['component_structure'].items():
            components[name] = self._build_component(comp_data)
        
        return UISpec(
            metadata=data['metadata'],
            design_intent=data['design_intent'],
            visual_design=visual_design,
            component_structure=components,
            implementation_notes=data.get('implementation_notes', {})
        )
    
    def _build_component(self, comp_data: Dict) -> ComponentSpec:
        """Recursively build ComponentSpec"""
        children = []
        if 'elements' in comp_data and isinstance(comp_data['elements'], list):
            for elem in comp_data['elements']:
                if isinstance(elem, dict):
                    children.append(self._build_component(elem))
        
        return ComponentSpec(
            type=comp_data.get('type', 'container'),
            properties=comp_data,
            children=children
        )
    
    def to_prompt(self, spec: UISpec) -> str:
        """
        Convert spec to LLM generation prompt.
        
        Args:
            spec: Validated UI specification
        
        Returns:
            str: Complete prompt for code generation
        """
        # Build comprehensive prompt
        prompt_parts = [
            "You are a UI implementation expert. Generate pixel-perfect HTML/CSS/JS from this specification.",
            "",
            "# SPECIFICATION",
            "",
            "## Design Intent",
            self._format_dict(spec.design_intent),
            "",
            "## Visual Design",
            f"Dimensions: {spec.visual_design.dimensions['width']}x{spec.visual_design.dimensions['height']}",
            "",
            "### Color Palette",
            self._format_color_palette(spec.visual_design.color_palette),
            "",
        ]
        
        if spec.visual_design.typography:
            prompt_parts.extend([
                "### Typography",
                self._format_dict(spec.visual_design.typography),
                ""
            ])
        
        if spec.visual_design.spacing:
            prompt_parts.extend([
                "### Spacing",
                self._format_dict(spec.visual_design.spacing),
                ""
            ])
        
        prompt_parts.extend([
            "## Component Structure",
            self._format_components(spec.component_structure),
            ""
        ])
        
        if spec.implementation_notes:
            prompt_parts.extend([
                "## Implementation Notes",
                self._format_dict(spec.implementation_notes),
                ""
            ])
        
        prompt_parts.extend([
            "# REQUIREMENTS",
            "- Match all colors exactly using the hex codes provided",
            "- Match dimensions exactly",
            "- Implement all components in the structure",
            "- Use semantic HTML5",
            "- Use modern CSS (flexbox/grid)",
            "- Pure vanilla JavaScript (no frameworks)",
            "- Single-file implementation with inline styles and scripts",
            "",
            "# OUTPUT FORMAT",
            "Generate a complete HTML file with:",
            "1. Embedded CSS in <style> tag",
            "2. Embedded JavaScript in <script> tag",
            "3. All components implemented",
            "",
            "Wrap your code in markdown code blocks:",
            "```html",
            "<!-- Your HTML here -->",
            "```"
        ])
        
        return '\n'.join(prompt_parts)
    
    def _format_dict(self, d: Dict, indent: int = 0) -> str:
        """Format dictionary for prompt"""
        lines = []
        prefix = "  " * indent
        for key, value in d.items():
            if isinstance(value, dict):
                lines.append(f"{prefix}{key}:")
                lines.append(self._format_dict(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        lines.append(self._format_dict(item, indent + 1))
                    else:
                        lines.append(f"{prefix}  - {item}")
            else:
                lines.append(f"{prefix}{key}: {value}")
        return '\n'.join(lines)
    
    def _format_color_palette(self, palette: Dict[str, str]) -> str:
        """Format color palette for prompt"""
        lines = []
        for name, color in palette.items():
            lines.append(f"  {name}: {color}")
        return '\n'.join(lines)
    
    def _format_components(self, components: Dict[str, ComponentSpec]) -> str:
        """Format component structure for prompt"""
        lines = []
        for name, comp in components.items():
            lines.append(f"\n### {name}")
            lines.append(f"Type: {comp.type}")
            if comp.properties:
                lines.append("Properties:")
                lines.append(self._format_dict(comp.properties, indent=1))
            if comp.children:
                lines.append(f"Children: {len(comp.children)} elements")
        return '\n'.join(lines)
