"""Convert analyzer JSON output to YAML spec format"""
import yaml
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class SpecConverter:
    """Convert UXAnalyzer JSON to spec YAML format"""
    
    def __init__(self):
        pass
    
    def json_to_spec(self, 
                     analyzer_json: Dict[str, Any],
                     screenshot_path: str) -> Dict[str, Any]:
        """
        Convert analyzer JSON to spec YAML format.
        
        Args:
            analyzer_json: Output from UXAnalyzer.analyze()
            screenshot_path: Path to source screenshot
        
        Returns:
            dict: Spec in YAML-compatible format
        """
        # Extract metadata
        metadata = self._build_metadata(screenshot_path, analyzer_json)
        
        # Extract visual design
        visual_design = self._build_visual_design(analyzer_json)
        
        # Extract component structure
        component_structure = self._build_component_structure(analyzer_json)
        
        # Build design intent
        design_intent = self._infer_design_intent(analyzer_json)
        
        # Build implementation notes
        implementation_notes = self._build_implementation_notes(analyzer_json)
        
        return {
            'metadata': metadata,
            'design_intent': design_intent,
            'visual_design': visual_design,
            'component_structure': component_structure,
            'implementation_notes': implementation_notes
        }
    
    def _build_metadata(self, screenshot_path: str, data: Dict) -> Dict:
        """Build metadata section"""
        return {
            'version': '1.0',
            'created': datetime.now().strftime('%Y-%m-%d'),
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'source_screenshot': Path(screenshot_path).name,
            'generated_by': 'amplifier-ux-analyzer',
            'analysis_method': 'computer_vision'
        }
    
    def _build_visual_design(self, data: Dict) -> Dict:
        """Build visual_design section from analyzer output"""
        # Extract dimensions
        dimensions = {
            'width': data['metadata']['dimensions']['width'],
            'height': data['metadata']['dimensions']['height']
        }
        
        # Build color palette from dominant colors
        color_palette = {}
        if 'colors' in data:
            colors = sorted(data['colors'], key=lambda x: x['frequency'], reverse=True)
            
            # Assign semantic names to most frequent colors
            color_names = [
                'primary_bg', 'secondary_bg', 'border', 
                'text', 'accent', 'accent_hover',
                'muted', 'highlight'
            ]
            
            for i, color in enumerate(colors[:len(color_names)]):
                color_palette[color_names[i]] = color['hex']
        
        # Extract typography if available
        typography = None
        if 'text_elements' in data and data['text_elements']:
            # Infer from text analysis
            typography = {
                'family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif',
                'sizes': {
                    'default': '14px',
                    'small': '12px',
                    'large': '16px'
                }
            }
        
        visual_design = {
            'dimensions': dimensions,
            'color_palette': color_palette
        }
        
        if typography:
            visual_design['typography'] = typography
        
        return visual_design
    
    def _build_component_structure(self, data: Dict) -> Dict:
        """Build component_structure from regions and elements"""
        components = {}
        
        # Process regions
        if 'regions' in data:
            for region in data['regions']:
                region_name = region['type']
                
                # Build component entry
                bounds = region['bounds']
                components[region_name] = {
                    'type': 'container',
                    'bounds': bounds,
                    'width': bounds['width'],
                    'height': bounds['height']
                }
                
                # Add elements that are already nested in the region
                if 'elements' in region:
                    region_elements = []
                    for elem in region['elements']:
                        elem_bounds = elem['bounds']
                        region_elements.append({
                            'type': elem['type'],
                            'bounds': elem_bounds,
                            'width': elem_bounds['width'],
                            'height': elem_bounds['height']
                        })
                    
                    if region_elements:
                        components[region_name]['elements'] = region_elements
        
        # If no regions, create a single main component
        if not components:
            components['main'] = {
                'type': 'container',
                'note': 'No regions detected - single component'
            }
        
        return components
    

    
    def _infer_design_intent(self, data: Dict) -> Dict:
        """Infer design intent from analysis"""
        num_regions = len(data.get('regions', []))
        num_elements = len(data.get('elements', []))
        
        # Simple heuristics
        if num_regions >= 3:
            complexity = "multi-panel interface"
        elif num_regions >= 2:
            complexity = "dual-panel interface"
        else:
            complexity = "single-panel interface"
        
        return {
            'goal': f'Replicate {complexity} with {num_elements} interactive elements',
            'philosophy': 'Pixel-perfect visual replication with event logging scaffold',
            'complexity': complexity,
            'element_count': num_elements
        }
    
    def _build_implementation_notes(self, data: Dict) -> Dict:
        """Build implementation notes from analysis"""
        notes = {
            'scaffolding': True,
            'event_logging': 'All controls post events to designated DOM element',
            'backend': 'Not implemented - frontend only'
        }
        
        # Add text content if available
        if 'text_elements' in data and data['text_elements']:
            notes['text_content'] = [
                item['text'] for item in data['text_elements'][:10]  # First 10 text items
            ]
        
        return notes
    
    def save_yaml(self, spec: Dict[str, Any], output_path: str):
        """
        Save spec to YAML file.
        
        Args:
            spec: Spec dictionary
            output_path: Output YAML file path
        """
        with open(output_path, 'w') as f:
            yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
