"""Create application icon for Image Denoiser."""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Create a simple but professional icon for the app."""
    
    # Create base image (256x256 for high quality)
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw rounded rectangle background (blue gradient effect)
    margin = 20
    # Main background - blue
    draw.rounded_rectangle(
        [margin, margin, size-margin, size-margin],
        radius=30,
        fill='#2196F3'
    )
    
    # Add subtle gradient effect with lighter blue overlay
    draw.rounded_rectangle(
        [margin, margin, size-margin, size//2],
        radius=30,
        fill='#42A5F5'
    )
    
    # Draw sparkle/clean effect (white circles)
    sparkle_positions = [
        (size*0.25, size*0.3, 8),
        (size*0.75, size*0.35, 6),
        (size*0.65, size*0.7, 10),
        (size*0.35, size*0.75, 7),
    ]
    
    for x, y, r in sparkle_positions:
        draw.ellipse([x-r, y-r, x+r, y+r], fill='white')
    
    # Draw image frame icon in center
    frame_margin = size * 0.3
    frame_thickness = 8
    
    # Outer frame (white)
    draw.rectangle(
        [frame_margin, frame_margin, size-frame_margin, size-frame_margin],
        outline='white',
        width=frame_thickness
    )
    
    # Inner content (lighter blue to show "cleaned" image)
    inner_margin = frame_margin + frame_thickness + 5
    draw.rectangle(
        [inner_margin, inner_margin, size-inner_margin, size-inner_margin],
        fill='#E3F2FD'
    )
    
    # Save as PNG
    img.save('icon.png', 'PNG')
    print("✓ Created icon.png (256x256)")
    
    # Create multiple sizes for ICO
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icons = []
    
    for icon_size in sizes:
        resized = img.resize(icon_size, Image.Resampling.LANCZOS)
        icons.append(resized)
    
    # Save as ICO with multiple sizes
    icons[0].save('icon.ico', format='ICO', sizes=[(s[0], s[1]) for s in sizes], append_images=icons[1:])
    print("✓ Created icon.ico (multi-size)")
    
    # Create smaller preview
    preview = img.resize((64, 64), Image.Resampling.LANCZOS)
    preview.save('icon_preview.png', 'PNG')
    print("✓ Created icon_preview.png (64x64 preview)")
    
    print("\nIcon files created successfully!")
    print("The application will now use these icons automatically.")


if __name__ == "__main__":
    try:
        create_icon()
    except ImportError:
        print("Error: Pillow (PIL) is required to create icons.")
        print("Install with: pip install Pillow")
        print("\nAlternatively, download an icon manually:")
        print("1. Visit https://flaticon.com")
        print("2. Search for 'image denoise' or 'photo clean'")
        print("3. Download as ICO and PNG")
        print("4. Save as icon.ico and icon.png in project root")
