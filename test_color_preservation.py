"""Test script to verify color preservation is working correctly."""
import numpy as np
from PIL import Image
from color_utils import _denoise_luminance_only
from scipy import ndimage as nd

# Create a test image with vibrant colors
def create_test_image():
    """Create a colorful test image."""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Red square
    img[0:50, 0:50] = [255, 0, 0]
    
    # Green square
    img[0:50, 50:100] = [0, 255, 0]
    
    # Blue square
    img[50:100, 0:50] = [0, 0, 255]
    
    # Yellow square
    img[50:100, 50:100] = [255, 255, 0]
    
    return img

# Test color preservation
def test_color_preservation():
    """Test that color preservation maintains saturation."""
    print("Testing color preservation...")
    
    # Create test image
    original = create_test_image()
    
    # Apply denoising with color preservation
    def simple_denoise(img):
        return nd.gaussian_filter(img, sigma=1.0)
    
    preserved = _denoise_luminance_only(original, simple_denoise)
    
    # Check that colors are still vibrant
    # Red square should still be red
    red_pixel = preserved[25, 25]
    print(f"Red pixel (should be ~[255, 0, 0]): {red_pixel}")
    
    # Green square should still be green
    green_pixel = preserved[25, 75]
    print(f"Green pixel (should be ~[0, 255, 0]): {green_pixel}")
    
    # Blue square should still be blue
    blue_pixel = preserved[75, 25]
    print(f"Blue pixel (should be ~[0, 0, 255]): {blue_pixel}")
    
    # Yellow square should still be yellow
    yellow_pixel = preserved[75, 75]
    print(f"Yellow pixel (should be ~[255, 255, 0]): {yellow_pixel}")
    
    # Save images for visual inspection
    Image.fromarray(original).save('test_original.png')
    Image.fromarray(preserved).save('test_preserved.png')
    
    print("\nSaved test_original.png and test_preserved.png")
    print("Compare them visually - colors should be equally vibrant!")
    
    # Check if colors are washed out
    red_saturation = red_pixel[0] / max(red_pixel[1], red_pixel[2], 1)
    green_saturation = green_pixel[1] / max(green_pixel[0], green_pixel[2], 1)
    blue_saturation = blue_pixel[2] / max(blue_pixel[0], blue_pixel[1], 1)
    
    print(f"\nSaturation ratios (should be high):")
    print(f"  Red: {red_saturation:.2f}")
    print(f"  Green: {green_saturation:.2f}")
    print(f"  Blue: {blue_saturation:.2f}")
    
    if red_saturation < 10 or green_saturation < 10 or blue_saturation < 10:
        print("\n❌ FAIL: Colors are washed out!")
        return False
    else:
        print("\n✅ PASS: Colors are preserved!")
        return True

if __name__ == "__main__":
    test_color_preservation()
