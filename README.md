# Amplifier UX Analyzer

A computer vision tool for analyzing UI screenshots and generating structured descriptions. Built to help AI agents understand user interfaces and create pixel-perfect recreations.

## Features

- **Color Palette Extraction** - Identifies dominant colors with RGB/hex values and frequency
- **Layout Region Detection** - Automatically segments toolbar, content, and status bar areas
- **UI Element Detection** - Finds buttons, controls, and interactive elements via contour analysis
- **Text Extraction** - OCR-based text recognition with confidence scores and bounding boxes
- **Visual Output** - Generates annotated screenshots showing detected regions and elements
- **JSON Output** - Structured data format for programmatic consumption

## Installation

### Prerequisites

- Python 3.8+
- System dependencies for OpenCV

### Quick Install

```bash
# Clone the repository
git clone https://github.com/ramparte/amplifier-ux-analyzer.git
cd amplifier-ux-analyzer

# Run setup script (installs system dependencies and Python packages)
chmod +x setup-ux-analyzer.sh
./setup-ux-analyzer.sh
```

### Manual Install

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
    python3-opencv \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-dev

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install opencv-python numpy scikit-learn easyocr pillow
```

## Usage

### Basic Analysis

```bash
# Activate virtual environment
source venv/bin/activate

# Analyze a screenshot
python ux-analyzer.py screenshot.png

# Output: screenshot-analysis.json
```

### With Visualization

```bash
# Generate annotated visualization
python ux-analyzer.py screenshot.png -v output-viz.png

# Custom output filename
python ux-analyzer.py screenshot.png -o custom-analysis.json -v custom-viz.png
```

### Python API

```python
from ux_analyzer import UXAnalyzer

analyzer = UXAnalyzer()
results = analyzer.analyze('screenshot.png')

# Access structured data
print(f"Dimensions: {results['metadata']['dimensions']}")
print(f"Colors found: {len(results['colors'])}")
print(f"Text elements: {len(results['text_elements'])}")

# Generate visualization
analyzer.visualize('screenshot.png', results, 'output-viz.png')
```

## Output Format

The analyzer generates a JSON file with this structure:

```json
{
  "metadata": {
    "source": "screenshot.png",
    "dimensions": {"width": 1920, "height": 1080}
  },
  "colors": [
    {
      "hex": "#131313",
      "rgb": [19, 19, 19],
      "frequency": 0.45
    }
  ],
  "regions": [
    {
      "type": "toolbar",
      "bounds": {"x": 0, "y": 0, "width": 1920, "height": 100},
      "background_color": "#202020",
      "elements": [...]
    }
  ],
  "text_elements": [
    {
      "text": "File",
      "confidence": 0.99,
      "bounds": {"x": 20, "y": 15, "width": 30, "height": 20}
    }
  ]
}
```

## Use Cases

### UI Recreation
Use the structured output to recreate UIs pixel-perfectly:
```bash
python ux-analyzer.py design.png -o design-spec.json
# Use design-spec.json to generate HTML/CSS
```

### Visual Regression Testing
Compare screenshots at the JSON level:
```python
import json

with open('baseline-analysis.json') as f:
    baseline = json.load(f)
with open('current-analysis.json') as f:
    current = json.load(f)

# Compare color palettes, element positions, text content
```

### Design System Documentation
Extract color palettes and component layouts automatically:
```bash
python ux-analyzer.py app-screenshot.png
# Colors and regions extracted for documentation
```

## Integration with Amplifier Browser Bundle

This tool complements the [amplifier-bundle-browser](https://github.com/ramparte/amplifier-bundle-browser) for comprehensive UI testing and automation.

**Workflow:**
1. **Screenshot** - Use agent-browser to capture UI state
2. **Analyze** - Run ux-analyzer to extract structure
3. **Validate** - Compare with expected JSON spec
4. **Automate** - Use agent-browser refs to interact with elements

```bash
# Take screenshot
agent-browser screenshot app.png

# Analyze structure
python ux-analyzer.py app.png -o app-analysis.json

# Compare with spec
python compare-specs.py expected.json app-analysis.json
```

## Performance

- **Color extraction**: ~100ms (scikit-learn k-means)
- **Region detection**: ~200ms (OpenCV contours)
- **OCR text extraction**: ~2-5s (EasyOCR, CPU-bound)
- **Total analysis time**: ~3-6s per screenshot on CPU

GPU acceleration significantly speeds up OCR (10-50x faster).

## Requirements

```
opencv-python>=4.5.0
numpy>=1.19.0
scikit-learn>=0.24.0
easyocr>=1.4.0
pillow>=8.0.0
```

## Troubleshooting

### "libGL.so.1: cannot open shared object file"
```bash
sudo apt-get install -y libgl1-mesa-glx
```

### "ImportError: libgthread-2.0.so.0"
```bash
sudo apt-get install -y libglib2.0-0
```

### OCR is slow
EasyOCR runs faster with GPU. Install with CUDA support:
```bash
pip install easyocr[gpu]
```

## License

MIT

## Contributing

Contributions welcome! Please open an issue or PR.

## Links

- [Amplifier Framework](https://github.com/microsoft/amplifier)
- [Amplifier Browser Bundle](https://github.com/ramparte/amplifier-bundle-browser)
- [Documentation](https://github.com/ramparte/amplifier-ux-analyzer/wiki)
