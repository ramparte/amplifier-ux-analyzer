#!/usr/bin/env python3
"""
UX Analyzer - Screenshot to structured UI description

Analyzes UI screenshots and extracts:
- Layout regions (toolbar, content, status bar)
- UI elements (buttons, inputs, text)
- Colors, spacing, typography
- Text content via OCR

Output: JSON description suitable for HTML generation and regression testing
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
import argparse

try:
    import cv2
    import numpy as np
    from PIL import Image, ImageDraw
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("\nInstall with: pip install opencv-python-headless pillow numpy")
    sys.exit(1)

# Optional: OCR for text extraction
try:
    import easyocr
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    print("Warning: easyocr not available. Text extraction will be limited.")
    print("Install with: pip install easyocr")


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


class UXAnalyzer:
    """Analyzes screenshots and extracts UI structure"""
    
    def __init__(self, image_path: str, use_ocr: bool = True):
        self.image_path = Path(image_path)
        self.use_ocr = use_ocr and HAS_OCR
        
        # Load image
        self.pil_image = Image.open(image_path)
        self.cv_image = cv2.imread(str(image_path))
        self.gray = cv2.cvtColor(self.cv_image, cv2.COLOR_BGR2GRAY)
        
        self.width = self.pil_image.width
        self.height = self.pil_image.height
        
        # Initialize OCR reader if available
        self.ocr_reader = None
        if self.use_ocr:
            try:
                self.ocr_reader = easyocr.Reader(['en'], gpu=False)
            except Exception as e:
                print(f"Warning: Could not initialize OCR: {e}")
                self.use_ocr = False
    
    def rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    def get_dominant_colors(self, n_colors: int = 10) -> List[Dict[str, Any]]:
        """Extract dominant colors from the image"""
        # Reshape image to list of pixels
        pixels = self.cv_image.reshape(-1, 3)
        pixels = np.float32(pixels)
        
        # K-means clustering to find dominant colors
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(pixels, n_colors, None, criteria, 10, 
                                        cv2.KMEANS_PP_CENTERS)
        
        # Convert to hex and calculate frequency
        colors = []
        for i, center in enumerate(centers):
            rgb = tuple(int(c) for c in center)
            hex_color = self.rgb_to_hex(rgb)
            frequency = np.sum(labels == i) / len(labels)
            colors.append({
                "hex": hex_color,
                "rgb": rgb,
                "frequency": float(frequency)
            })
        
        return sorted(colors, key=lambda x: x['frequency'], reverse=True)
    
    def detect_regions(self) -> List[Dict[str, Any]]:
        """Detect major layout regions using edge detection and contours"""
        # Apply edge detection
        edges = cv2.Canny(self.gray, 50, 150)
        
        # Dilate to connect nearby edges
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        
        regions = []
        
        # Analyze image in horizontal bands to detect typical UI regions
        # Top band: likely toolbar/ribbon (0-15%)
        top_band = self.height * 0.15
        # Bottom band: likely status bar (85-100%)
        bottom_band = self.height * 0.85
        
        # Sample colors from each band
        top_sample = self.pil_image.crop((0, 0, self.width, int(top_band)))
        top_colors = self._get_region_color(top_sample)
        
        middle_sample = self.pil_image.crop((0, int(top_band), 
                                            self.width, int(bottom_band)))
        middle_colors = self._get_region_color(middle_sample)
        
        bottom_sample = self.pil_image.crop((0, int(bottom_band), 
                                            self.width, self.height))
        bottom_colors = self._get_region_color(bottom_sample)
        
        regions = [
            {
                "type": "toolbar",
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "width": self.width,
                    "height": int(top_band)
                },
                "background_color": top_colors["dominant"],
                "avg_color": top_colors["average"]
            },
            {
                "type": "content",
                "bounds": {
                    "x": 0,
                    "y": int(top_band),
                    "width": self.width,
                    "height": int(bottom_band - top_band)
                },
                "background_color": middle_colors["dominant"],
                "avg_color": middle_colors["average"]
            },
            {
                "type": "status_bar",
                "bounds": {
                    "x": 0,
                    "y": int(bottom_band),
                    "width": self.width,
                    "height": int(self.height - bottom_band)
                },
                "background_color": bottom_colors["dominant"],
                "avg_color": bottom_colors["average"]
            }
        ]
        
        return regions
    
    def _get_region_color(self, region_image: Image.Image) -> Dict[str, str]:
        """Get dominant and average color for a region"""
        # Get average color
        avg_color = region_image.resize((1, 1)).getpixel((0, 0))
        if isinstance(avg_color, int):
            avg_color = (avg_color, avg_color, avg_color)
        
        # Simple dominant color: most common color in downsampled image
        small = region_image.resize((50, 50))
        colors = small.getcolors(2500)
        if colors:
            dominant = max(colors, key=lambda x: x[0])[1]
            if isinstance(dominant, int):
                dominant = (dominant, dominant, dominant)
        else:
            dominant = avg_color
        
        return {
            "dominant": self.rgb_to_hex(dominant[:3]),
            "average": self.rgb_to_hex(avg_color[:3])
        }
    
    def detect_ui_elements(self, region: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect UI elements within a region (buttons, inputs, etc.)"""
        bounds = region["bounds"]
        
        # Extract region from image
        x, y = bounds["x"], bounds["y"]
        w, h = bounds["width"], bounds["height"]
        region_gray = self.gray[y:y+h, x:x+w]
        
        # Detect rectangles (potential buttons, inputs)
        edges = cv2.Canny(region_gray, 100, 200)
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, 
                                       cv2.CHAIN_APPROX_SIMPLE)
        
        elements = []
        
        for contour in contours:
            # Get bounding rectangle
            cx, cy, cw, ch = cv2.boundingRect(contour)
            
            # Filter small noise
            if cw < 20 or ch < 15:
                continue
            
            # Filter very large rectangles (likely borders, not elements)
            if cw > w * 0.9 or ch > h * 0.9:
                continue
            
            # Classify element type based on aspect ratio
            aspect_ratio = cw / ch
            
            if aspect_ratio > 3:
                element_type = "horizontal_group"
            elif 1.5 <= aspect_ratio <= 3:
                element_type = "button"
            elif 0.5 <= aspect_ratio < 1.5:
                element_type = "button"
            elif aspect_ratio < 0.5:
                element_type = "vertical_group"
            else:
                element_type = "container"
            
            # Get element color
            element_region = self.pil_image.crop((x+cx, y+cy, x+cx+cw, y+cy+ch))
            element_colors = self._get_region_color(element_region)
            
            element = {
                "type": element_type,
                "bounds": {
                    "x": x + cx,
                    "y": y + cy,
                    "width": cw,
                    "height": ch
                },
                "background_color": element_colors["dominant"],
                "text": ""  # Will be filled by OCR if available
            }
            
            elements.append(element)
        
        return elements
    
    def extract_text(self) -> List[Dict[str, Any]]:
        """Extract text from image using OCR"""
        if not self.use_ocr or not self.ocr_reader:
            return []
        
        try:
            results = self.ocr_reader.readtext(str(self.image_path))
            
            text_elements = []
            for detection in results:
                bbox, text, confidence = detection
                
                # Get bounding box
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                
                x = int(min(x_coords))
                y = int(min(y_coords))
                width = int(max(x_coords) - x)
                height = int(max(y_coords) - y)
                
                text_elements.append({
                    "text": text,
                    "confidence": float(confidence),
                    "bounds": {
                        "x": x,
                        "y": y,
                        "width": width,
                        "height": height
                    }
                })
            
            return text_elements
        except Exception as e:
            print(f"Warning: OCR extraction failed: {e}")
            return []
    
    def analyze(self) -> Dict[str, Any]:
        """Perform complete UI analysis"""
        print(f"Analyzing {self.image_path}...")
        print(f"Dimensions: {self.width}x{self.height}")
        
        # Extract dominant colors
        print("Extracting color palette...")
        colors = self.get_dominant_colors(10)
        
        # Detect regions
        print("Detecting layout regions...")
        regions = self.detect_regions()
        
        # Detect UI elements in each region
        print("Detecting UI elements...")
        for region in regions:
            if region["type"] == "toolbar":
                region["elements"] = self.detect_ui_elements(region)
                print(f"  Found {len(region['elements'])} elements in {region['type']}")
        
        # Extract text
        print("Extracting text (OCR)...")
        text_elements = self.extract_text()
        print(f"  Found {len(text_elements)} text elements")
        
        # Build final structure
        result = {
            "metadata": {
                "source": str(self.image_path),
                "dimensions": {
                    "width": self.width,
                    "height": self.height
                }
            },
            "colors": colors,
            "regions": regions,
            "text_elements": text_elements
        }
        
        return result
    
    def save_json(self, output_path: str):
        """Analyze and save to JSON file"""
        result = self.analyze()
        
        output = Path(output_path)
        with output.open('w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\nAnalysis saved to: {output}")
        return result
    
    def visualize(self, output_path: str):
        """Create annotated visualization of detected elements"""
        # Create a copy for drawing
        vis_image = self.pil_image.copy()
        draw = ImageDraw.Draw(vis_image)
        
        # Analyze
        result = self.analyze()
        
        # Draw regions
        for region in result["regions"]:
            b = region["bounds"]
            # Draw region outline
            draw.rectangle([b["x"], b["y"], b["x"]+b["width"], b["y"]+b["height"]],
                          outline="red", width=2)
            # Draw label
            draw.text((b["x"]+5, b["y"]+5), region["type"], fill="red")
        
        # Draw UI elements
        for region in result["regions"]:
            if "elements" in region:
                for element in region["elements"]:
                    b = element["bounds"]
                    draw.rectangle([b["x"], b["y"], b["x"]+b["width"], b["y"]+b["height"]],
                                  outline="blue", width=1)
        
        # Draw text elements
        for text_elem in result["text_elements"]:
            b = text_elem["bounds"]
            draw.rectangle([b["x"], b["y"], b["x"]+b["width"], b["y"]+b["height"]],
                          outline="green", width=2)
            # Draw text label
            draw.text((b["x"], b["y"]-15), text_elem["text"][:20], fill="green")
        
        vis_image.save(output_path)
        print(f"Visualization saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="UX Analyzer - Screenshot to UI description")
    parser.add_argument("image", help="Path to screenshot image")
    parser.add_argument("-o", "--output", help="Output JSON file", default=None)
    parser.add_argument("-v", "--visualize", help="Create annotated visualization", 
                       default=None)
    parser.add_argument("--no-ocr", action="store_true", help="Disable OCR text extraction")
    
    args = parser.parse_args()
    
    # Set default output path
    if args.output is None:
        input_path = Path(args.image)
        args.output = input_path.stem + "-analysis.json"
    
    # Analyze
    analyzer = UXAnalyzer(args.image, use_ocr=not args.no_ocr)
    analyzer.save_json(args.output)
    
    # Create visualization if requested
    if args.visualize:
        analyzer.visualize(args.visualize)


if __name__ == "__main__":
    main()
