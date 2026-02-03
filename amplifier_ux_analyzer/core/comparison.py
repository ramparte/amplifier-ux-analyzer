"""Image comparison module for UX testing"""
import cv2
import numpy as np
from pathlib import Path
from PIL import Image
from skimage.metrics import structural_similarity as ssim


class ImageComparator:
    """Compares two images and provides similarity metrics."""
    
    def __init__(self, reference_path: str, comparison_path: str):
        """
        Load two images for comparison.
        
        Args:
            reference_path: Path to reference image
            comparison_path: Path to comparison image
        """
        self.reference_path = Path(reference_path)
        self.comparison_path = Path(comparison_path)
        
        # Load images
        self.reference = cv2.imread(str(self.reference_path))
        self.comparison = cv2.imread(str(self.comparison_path))
        
        if self.reference is None:
            raise FileNotFoundError(f"Reference image not found: {reference_path}")
        if self.comparison is None:
            raise FileNotFoundError(f"Comparison image not found: {comparison_path}")
        
        # Store original sizes
        self.reference_size = (self.reference.shape[1], self.reference.shape[0])
        self.comparison_size = (self.comparison.shape[1], self.comparison.shape[0])
        
        # Resize comparison to match reference if needed
        if self.reference_size != self.comparison_size:
            self.comparison = cv2.resize(
                self.comparison,
                self.reference_size,
                interpolation=cv2.INTER_AREA
            )
    
    def calculate_similarity(self) -> dict:
        """
        Calculate multiple similarity metrics.
        
        Returns:
            dict: Similarity metrics including SSIM, MSE, pixel diff
        """
        # Convert to grayscale for SSIM
        ref_gray = cv2.cvtColor(self.reference, cv2.COLOR_BGR2GRAY)
        comp_gray = cv2.cvtColor(self.comparison, cv2.COLOR_BGR2GRAY)
        
        # Calculate SSIM
        ssim_score, _ = ssim(ref_gray, comp_gray, full=True)
        
        # Calculate MSE
        mse = np.mean((self.reference.astype(float) - self.comparison.astype(float)) ** 2)
        
        # Calculate pixel difference percentage
        diff = cv2.absdiff(self.reference, self.comparison)
        diff_pixels = np.sum(diff > 10)  # Threshold for "different"
        total_pixels = diff.size
        pixel_diff_percent = (diff_pixels / total_pixels) * 100
        
        return {
            "ssim": float(ssim_score),
            "mse": float(mse),
            "pixel_diff_percent": float(pixel_diff_percent),
            "dimensions_match": self.reference_size == self.comparison_size,
            "reference_size": self.reference_size,
            "comparison_size": self.comparison_size
        }
    
    def generate_diff_image(self, output_path: str) -> None:
        """
        Generate visual diff highlighting differences.
        
        Args:
            output_path: Where to save the diff image
        """
        # Calculate absolute difference
        diff = cv2.absdiff(self.reference, self.comparison)
        
        # Create mask of differences (threshold at 10 for visibility)
        mask = np.any(diff > 10, axis=2)
        
        # Create red overlay for differences
        overlay = self.comparison.copy()
        overlay[mask] = [0, 0, 255]  # Red in BGR
        
        # Blend overlay with comparison
        highlighted = cv2.addWeighted(self.comparison, 0.7, overlay, 0.3, 0)
        
        # Create side-by-side comparison
        h, w = self.reference.shape[:2]
        side_by_side = np.zeros((h, w * 2, 3), dtype=np.uint8)
        side_by_side[:, :w] = self.reference
        side_by_side[:, w:] = highlighted
        
        # Add similarity metrics as text
        metrics = self.calculate_similarity()
        ssim_text = f"SSIM: {metrics['ssim']:.2%}"
        diff_text = f"Pixel Diff: {metrics['pixel_diff_percent']:.2%}"
        
        cv2.putText(side_by_side, "Reference", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(side_by_side, "Comparison (diffs in red)", (w + 10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(side_by_side, ssim_text, (10, h - 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        cv2.putText(side_by_side, diff_text, (10, h - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        
        # Save
        cv2.imwrite(str(output_path), side_by_side)
    
    def is_similar(self, threshold: float = 0.95) -> bool:
        """
        Quick similarity check.
        
        Args:
            threshold: SSIM threshold (default 0.95)
        
        Returns:
            bool: True if images are similar enough
        """
        metrics = self.calculate_similarity()
        return metrics["ssim"] >= threshold
