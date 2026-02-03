"""HTML utilities for code generation and rendering"""
import re
import subprocess
from pathlib import Path
from typing import Optional, Tuple


class HTMLExtractor:
    """Extract HTML code from LLM responses"""
    
    @staticmethod
    def extract_from_markdown(text: str) -> Optional[str]:
        """
        Extract HTML code from markdown code blocks.
        
        Looks for ```html ... ``` blocks.
        
        Args:
            text: LLM response text
        
        Returns:
            str: Extracted HTML code, or None if not found
        """
        # Pattern to match ```html ... ``` blocks
        pattern = r'```html\s*(.*?)\s*```'
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        
        if matches:
            # Return the longest HTML block
            return max(matches, key=len)
        
        return None
    
    @staticmethod
    def extract_from_tags(text: str) -> Optional[str]:
        """
        Extract HTML if response is just HTML without code blocks.
        
        Args:
            text: Response text
        
        Returns:
            str: HTML if found, None otherwise
        """
        # Check if text starts with <!DOCTYPE or <html
        if text.strip().startswith(('<!DOCTYPE', '<html', '<HTML')):
            return text.strip()
        
        return None
    
    @staticmethod
    def extract(text: str) -> Optional[str]:
        """
        Extract HTML from response using multiple strategies.
        
        Args:
            text: LLM response text
        
        Returns:
            str: Extracted HTML, or None if not found
        """
        # Try markdown code blocks first
        html = HTMLExtractor.extract_from_markdown(text)
        if html:
            return html
        
        # Try direct HTML
        html = HTMLExtractor.extract_from_tags(text)
        if html:
            return html
        
        return None


class BrowserRenderer:
    """Utilities for rendering HTML with agent-browser"""
    
    def __init__(self):
        self.check_browser_available()
    
    @staticmethod
    def check_browser_available() -> bool:
        """
        Check if agent-browser is available.
        
        Returns:
            bool: True if available
        
        Raises:
            RuntimeError: If agent-browser not found
        """
        try:
            result = subprocess.run(
                ['which', 'agent-browser'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError(
                    "agent-browser not found. Install with:\n"
                    "npm install -g agent-browser\n"
                    "agent-browser install"
                )
            return True
        except Exception as e:
            raise RuntimeError(f"Error checking for agent-browser: {e}")
    
    def render_and_screenshot(self,
                             html_path: Path,
                             screenshot_path: Path,
                             width: int = 1920,
                             height: int = 1080) -> bool:
        """
        Render HTML file and take screenshot using agent-browser.
        
        Args:
            html_path: Path to HTML file
            screenshot_path: Path to save screenshot
            width: Browser viewport width
            height: Browser viewport height
        
        Returns:
            bool: True if successful
        """
        html_path = Path(html_path).resolve()
        screenshot_path = Path(screenshot_path).resolve()
        
        if not html_path.exists():
            raise FileNotFoundError(f"HTML file not found: {html_path}")
        
        # Convert to file:// URL
        file_url = f"file://{html_path}"
        
        try:
            # Set viewport size
            subprocess.run(
                ['agent-browser', 'set', 'viewport', str(width), str(height)],
                check=True,
                capture_output=True
            )
            
            # Open the HTML file
            subprocess.run(
                ['agent-browser', 'open', file_url],
                check=True,
                capture_output=True,
                timeout=30
            )
            
            # Wait for page to render
            subprocess.run(
                ['agent-browser', 'wait', '2000'],  # 2 seconds
                check=True,
                capture_output=True,
                timeout=10
            )
            
            # Take screenshot
            subprocess.run(
                ['agent-browser', 'screenshot', str(screenshot_path), '--full'],
                check=True,
                capture_output=True,
                timeout=30
            )
            
            # Close browser
            subprocess.run(
                ['agent-browser', 'close'],
                check=False,  # Don't fail if already closed
                capture_output=True
            )
            
            return screenshot_path.exists()
            
        except subprocess.TimeoutExpired:
            # Try to close on timeout
            subprocess.run(['agent-browser', 'close'], 
                          check=False, capture_output=True)
            raise RuntimeError("Browser operation timed out")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Browser command failed: {e.stderr.decode()}")
    
    def save_and_render(self,
                       html_content: str,
                       output_dir: Path,
                       dimensions: Tuple[int, int] = (1920, 1080)) -> Tuple[Path, Path]:
        """
        Save HTML content and render to screenshot.
        
        Args:
            html_content: HTML code
            output_dir: Directory to save files
            dimensions: (width, height) tuple
        
        Returns:
            Tuple[Path, Path]: (html_path, screenshot_path)
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save HTML
        html_path = output_dir / "generated.html"
        html_path.write_text(html_content)
        
        # Render to screenshot
        screenshot_path = output_dir / "generated-screenshot.png"
        self.render_and_screenshot(
            html_path, 
            screenshot_path,
            width=dimensions[0],
            height=dimensions[1]
        )
        
        return html_path, screenshot_path
