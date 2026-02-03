#!/usr/bin/env python3
"""Test browser renderer utilities"""
import sys
from pathlib import Path
from amplifier_ux_analyzer.utils.html_utils import HTMLExtractor, BrowserRenderer


def test_html_extraction():
    """Test HTML extraction from markdown"""
    print("🧪 Test 1: HTML Extraction from Markdown")
    
    # Sample markdown with HTML
    markdown = """
Here's the generated code:

```html
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Hello World</h1></body>
</html>
```

That's it!
"""
    
    extractor = HTMLExtractor()
    html = extractor.extract(markdown)
    
    if html and '<h1>Hello World</h1>' in html:
        print("✓ HTML extraction works")
    else:
        print("✗ HTML extraction failed")
        return 1
    
    return 0


def test_browser_renderer():
    """Test browser rendering"""
    print("\n🧪 Test 2: Browser Rendering")
    
    # Check if agent-browser is available
    try:
        renderer = BrowserRenderer()
        print("✓ agent-browser is available")
    except RuntimeError as e:
        print(f"⚠️  Skipping test: {e}")
        return 0
    
    # Create test HTML
    test_html = """<!DOCTYPE html>
<html>
<head>
    <style>
        body { 
            background: #131313; 
            color: #e2e3dd; 
            font-family: Arial, sans-serif;
            padding: 50px;
        }
        h1 { color: #2672cc; }
    </style>
</head>
<body>
    <h1>Browser Renderer Test</h1>
    <p>This is a test page for the browser renderer utilities.</p>
</body>
</html>"""
    
    output_dir = Path("/tmp/ux-analyzer-browser-test")
    
    try:
        html_path, screenshot_path = renderer.save_and_render(
            test_html,
            output_dir,
            dimensions=(800, 600)
        )
        
        print(f"✓ HTML saved: {html_path}")
        print(f"✓ Screenshot saved: {screenshot_path}")
        
        if screenshot_path.exists() and screenshot_path.stat().st_size > 0:
            print("✓ Screenshot generated successfully")
        else:
            print("✗ Screenshot file is empty or missing")
            return 1
        
    except Exception as e:
        print(f"✗ Rendering failed: {e}")
        return 1
    
    return 0


def main():
    """Run all tests"""
    print("📋 Testing Browser Utilities\n")
    
    result = test_html_extraction()
    if result != 0:
        return result
    
    result = test_browser_renderer()
    if result != 0:
        return result
    
    print("\n✅ All tests passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
