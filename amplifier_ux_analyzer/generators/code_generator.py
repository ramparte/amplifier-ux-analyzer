"""LLM-powered code generator for UI implementations"""
import subprocess
import re
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class GeneratedCode:
    """Container for generated code artifacts"""
    html_path: Path
    generation_log: str
    success: bool
    error: Optional[str] = None


class CodeGenerator:
    """Generate HTML/CSS/JS from UI specifications using LLM"""
    
    def __init__(self, 
                 model: str = "claude-sonnet-4-20250514",
                 provider: str = "anthropic"):
        """
        Initialize code generator.
        
        Args:
            model: LLM model to use
            provider: LLM provider (anthropic, openai, etc.)
        """
        self.model = model
        self.provider = provider
    
    def generate(self,
                 prompt: str,
                 output_dir: Path,
                 iteration_context: Optional[str] = None) -> GeneratedCode:
        """
        Generate UI code from specification prompt.
        
        Args:
            prompt: Complete specification prompt (from spec_parser.to_prompt())
            output_dir: Directory to write generated files
            iteration_context: Feedback from previous attempt (if iterating)
        
        Returns:
            GeneratedCode with paths and metadata
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Build complete prompt with iteration feedback if provided
        full_prompt = prompt
        if iteration_context:
            full_prompt = f"{prompt}\n\n# ITERATION FEEDBACK\n\n{iteration_context}"
        
        # Invoke Amplifier CLI to generate code
        try:
            response = self._invoke_llm(full_prompt)
            
            # Extract HTML from response
            html_code = self._extract_html(response)
            
            if not html_code:
                return GeneratedCode(
                    html_path=output_dir / "generated.html",
                    generation_log=response,
                    success=False,
                    error="No HTML code block found in response"
                )
            
            # Write HTML file
            html_path = output_dir / "generated.html"
            html_path.write_text(html_code)
            
            return GeneratedCode(
                html_path=html_path,
                generation_log=response,
                success=True
            )
            
        except Exception as e:
            return GeneratedCode(
                html_path=output_dir / "generated.html",
                generation_log=str(e),
                success=False,
                error=str(e)
            )
    
    def _invoke_llm(self, prompt: str) -> str:
        """
        Invoke Amplifier CLI to get LLM response.
        
        Args:
            prompt: Complete prompt text
        
        Returns:
            str: LLM response
        """
        # Write prompt to temp file to avoid shell quoting issues
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(prompt)
            prompt_file = f.name
        
        try:
            # Use amplifier run with prompt from stdin
            cmd = [
                "amplifier", "run",
                "--provider", self.provider,
                "--model", self.model,
                "--mode", "single",
                "--output-format", "text"
            ]
            
            with open(prompt_file, 'r') as f:
                result = subprocess.run(
                    cmd,
                    stdin=f,
                    capture_output=True,
                    text=True,
                    timeout=180  # 3 minute timeout for generation
                )
            
            if result.returncode != 0:
                raise RuntimeError(f"Amplifier command failed: {result.stderr}")
            
            return result.stdout
        finally:
            # Clean up temp file
            import os
            if os.path.exists(prompt_file):
                os.unlink(prompt_file)
    
    def _extract_html(self, response: str) -> Optional[str]:
        """
        Extract HTML code from markdown code blocks.
        
        Looks for ```html ... ``` blocks and extracts content.
        
        Args:
            response: LLM response text
        
        Returns:
            str: Extracted HTML code, or None if not found
        """
        # Pattern to match ```html ... ``` blocks
        pattern = r'```html\s*(.*?)\s*```'
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        
        if matches:
            # Return the first (or longest) HTML block
            return max(matches, key=len)
        
        return None
