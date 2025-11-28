"""Quick test for the before/after comparison window."""
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
import os

# Create test images if they don't exist
def create_test_images():
    """Create simple test images for comparison."""
    # Create a noisy "before" image
    before = Image.new('RGB', (400, 300), color='lightblue')
    draw = ImageDraw.Draw(before)
    
    # Add some text
    draw.text((50, 100), "BEFORE IMAGE", fill='black')
    draw.text((50, 150), "With some noise", fill='darkblue')
    
    # Add noise effect (simple pattern)
    for i in range(0, 400, 10):
        for j in range(0, 300, 10):
            if (i + j) % 20 == 0:
                draw.point((i, j), fill='gray')
    
    before.save('test_before.png')
    
    # Create a "denoised" after image
    after = Image.new('RGB', (400, 300), color='skyblue')
    draw = ImageDraw.Draw(after)
    
    draw.text((50, 100), "AFTER IMAGE", fill='black')
    draw.text((50, 150), "Denoised & cleaner", fill='darkblue')
    
    after.save('test_after.png')
    
    print("✓ Created test images: test_before.png and test_after.png")

# Import the comparison window
try:
    from gui import BeforeAfterWindow
    
    # Create test images
    create_test_images()
    
    # Create root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    # Open comparison window
    print("Opening comparison window...")
    comparison = BeforeAfterWindow(root, 'test_before.png', 'test_after.png', 
                                   title="Test: Before/After Comparison")
    
    print("✓ Comparison window opened successfully!")
    print("  Drag the slider to compare images")
    
    root.mainloop()
    
    # Cleanup
    if os.path.exists('test_before.png'):
        os.remove('test_before.png')
    if os.path.exists('test_after.png'):
        os.remove('test_after.png')
    print("✓ Test completed and cleaned up")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
