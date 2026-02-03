"""Compare command for CLI"""
import argparse
import json
import sys
from pathlib import Path

from ..core.comparison import ImageComparator


def add_compare_command(subparsers):
    """Add compare command to CLI"""
    compare_parser = subparsers.add_parser(
        'compare', 
        help='Compare two UI screenshots',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic comparison
  amplifier-ux-analyzer compare reference.png actual.png
  
  # Generate diff visualization
  amplifier-ux-analyzer compare reference.png actual.png --output diff.png
  
  # JSON output for automation
  amplifier-ux-analyzer compare reference.png actual.png --json
  
  # Custom similarity threshold
  amplifier-ux-analyzer compare reference.png actual.png --threshold 0.98
        """
    )
    compare_parser.add_argument('reference', help='Reference image path')
    compare_parser.add_argument('comparison', help='Comparison image path')
    compare_parser.add_argument('-o', '--output', help='Output diff image path')
    compare_parser.add_argument('-t', '--threshold', type=float, default=0.95,
                                help='Similarity threshold (default: 0.95)')
    compare_parser.add_argument('--json', dest='json_output', action='store_true',
                                help='Output metrics as JSON')
    compare_parser.set_defaults(func=compare_command)
    
    return compare_parser


def compare_command(args):
    """Execute the compare command"""
    try:
        # Create comparator
        comparator = ImageComparator(args.reference, args.comparison)
        
        # Calculate metrics
        metrics = comparator.calculate_similarity()
        
        # Output results
        if args.json_output:
            print(json.dumps(metrics, indent=2))
        else:
            print(f"\n📊 Image Comparison Results")
            print(f"{'='*50}")
            print(f"Reference:  {args.reference}")
            print(f"Comparison: {args.comparison}")
            print(f"\n📈 Similarity Metrics:")
            print(f"  SSIM:       {metrics['ssim']:.2%}")
            print(f"  MSE:        {metrics['mse']:.2f}")
            print(f"  Pixel Diff: {metrics['pixel_diff_percent']:.2%}")
            print(f"\n📐 Dimensions:")
            print(f"  Reference:  {metrics['reference_size'][0]}x{metrics['reference_size'][1]}")
            print(f"  Comparison: {metrics['comparison_size'][0]}x{metrics['comparison_size'][1]}")
            print(f"  Match:      {'✓' if metrics['dimensions_match'] else '✗'}")
            
            # Verdict
            is_similar = comparator.is_similar(args.threshold)
            threshold_pct = args.threshold * 100
            print(f"\n{'='*50}")
            if is_similar:
                print(f"✓ Images are SIMILAR (SSIM >= {threshold_pct:.0f}%)")
            else:
                print(f"✗ Images DIFFER (SSIM < {threshold_pct:.0f}%)")
        
        # Generate diff image if requested
        if args.output:
            comparator.generate_diff_image(args.output)
            if not args.json_output:
                print(f"\n🖼️  Diff visualization saved to: {args.output}")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
