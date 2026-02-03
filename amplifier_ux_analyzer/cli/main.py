"""CLI entry point for UX Analyzer"""
import argparse
import sys
from pathlib import Path

from ..core.analyzer import UXAnalyzer, HAS_OCR
from .compare import add_compare_command
from ..generators.spec_converter import SpecConverter


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="UX Analyzer - Screenshot to UI description",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a screenshot
  amplifier-ux-analyzer analyze screenshot.png
  
  # Specify output file
  amplifier-ux-analyzer analyze screenshot.png --output result.json
  
  # Create visualization
  amplifier-ux-analyzer analyze screenshot.png --visualize annotated.png
  
  # Disable OCR
  amplifier-ux-analyzer analyze screenshot.png --no-ocr
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a screenshot')
    analyze_parser.add_argument('image', help='Path to screenshot image')
    analyze_parser.add_argument('-o', '--output', help='Output JSON file', default=None)
    analyze_parser.add_argument('-v', '--visualize', help='Create annotated visualization', 
                               default=None)
    analyze_parser.add_argument('--no-ocr', action='store_true', 
                               help='Disable OCR text extraction')
    analyze_parser.set_defaults(func=analyze_command)
    
    # Compare command
    add_compare_command(subparsers)
    
    # Convert command
    convert_parser = subparsers.add_parser(
        'convert',
        help='Convert analyzer JSON to spec YAML'
    )
    convert_parser.add_argument('json_file', help='Analyzer JSON file')
    convert_parser.add_argument('screenshot', help='Source screenshot path')
    convert_parser.add_argument('-o', '--output', required=True, help='Output YAML file')
    convert_parser.set_defaults(func=convert_command)
    
    args = parser.parse_args()
    
    # Show help if no command provided
    if not args.command:
        parser.print_help()
        return 0
    
    # Dispatch to command handler using func attribute
    if hasattr(args, 'func'):
        return args.func(args)
    
    return 0


def analyze_command(args):
    """Execute the analyze command"""
    # Check if OCR is available
    if not HAS_OCR and not args.no_ocr:
        print("Warning: easyocr not available. Text extraction will be limited.")
        print("Install with: pip install easyocr\n")
    
    # Set default output path
    if args.output is None:
        input_path = Path(args.image)
        args.output = input_path.stem + "-analysis.json"
    
    try:
        # Analyze
        analyzer = UXAnalyzer(args.image, use_ocr=not args.no_ocr)
        analyzer.save_json(args.output)
        
        # Create visualization if requested
        if args.visualize:
            analyzer.visualize(args.visualize)
        
        print("\n✅ Analysis complete!")
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: Image file not found: {args.image}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def convert_command(args):
    """Execute the convert command"""
    import json
    
    try:
        # Load JSON
        print(f"📋 Loading analyzer JSON from {args.json_file}...")
        with open(args.json_file, 'r') as f:
            analyzer_json = json.load(f)
        
        # Convert
        print("🔄 Converting to spec YAML...")
        converter = SpecConverter()
        spec = converter.json_to_spec(analyzer_json, args.screenshot)
        
        # Save
        print(f"💾 Saving to {args.output}...")
        converter.save_yaml(spec, args.output)
        
        print(f"\n✅ Conversion complete!")
        print(f"📁 Spec saved to: {args.output}")
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
