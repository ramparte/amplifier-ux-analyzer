#!/usr/bin/env python3
"""Test code generator with spec parser integration"""
import sys
from pathlib import Path
from amplifier_ux_analyzer.generators.spec_parser import SpecParser
from amplifier_ux_analyzer.generators.code_generator import CodeGenerator


def test_code_generation():
    """Test full pipeline: spec → prompt → code"""
    spec_path = Path("~/dev/ANext/word3/UI/word-clone-spec.yaml").expanduser()
    output_dir = Path("/tmp/ux-analyzer-test-generation")
    
    if not spec_path.exists():
        print(f"ERROR: Spec file not found: {spec_path}")
        return 1
    
    # Parse spec
    print("📋 Step 1: Parse specification...")
    parser = SpecParser()
    try:
        spec = parser.load(str(spec_path))
        print(f"✓ Spec loaded: {spec.dimensions}")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return 1
    
    # Generate prompt
    print("\n📝 Step 2: Generate LLM prompt...")
    try:
        prompt = parser.to_prompt(spec)
        print(f"✓ Prompt ready ({len(prompt)} chars)")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return 1
    
    # Generate code
    print("\n🤖 Step 3: Generate code with LLM...")
    print("   (This may take 30-60 seconds...)")
    generator = CodeGenerator()
    try:
        result = generator.generate(prompt, output_dir)
        
        if result.success:
            print(f"✓ Code generated: {result.html_path}")
            print(f"  File size: {result.html_path.stat().st_size} bytes")
            
            # Check if file has reasonable content
            content = result.html_path.read_text()
            if len(content) < 100:
                print("⚠️  Warning: Generated file seems too small")
            elif '<html' not in content.lower():
                print("⚠️  Warning: Generated file doesn't look like HTML")
            else:
                print("✓ Generated file looks valid")
        else:
            print(f"✗ Generation failed: {result.error}")
            
            # Debug: Save the generation log to see what we got
            log_path = output_dir / "generation_log.txt"
            log_path.write_text(result.generation_log)
            print(f"📝 Generation log saved to: {log_path}")
            print(f"   First 500 chars: {result.generation_log[:500]}")
            return 1
            
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n✅ All tests passed!")
    print(f"📁 Output: {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(test_code_generation())
