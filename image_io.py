"""Image input/output utilities."""
import os
from skimage import io


SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif')


def get_image_files(folder_path):
    """Get list of image files from folder.
    
    Args:
        folder_path: Path to folder containing images
    
    Returns:
        List of image filenames
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    return [f for f in os.listdir(folder_path) 
            if os.path.splitext(f.lower())[1] in SUPPORTED_EXTENSIONS]


def load_image(file_path):
    """Load image from file.
    
    Args:
        file_path: Path to image file
    
    Returns:
        Image array
    """
    return io.imread(file_path)


def save_image(output_path, image, output_format='png', jpeg_quality=95):
    """Save image with appropriate quality settings.
    
    Args:
        output_path: Path to save the image
        image: Image array to save
        output_format: Output format (png, jpg, tiff)
        jpeg_quality: JPEG quality (1-100)
    """
    if output_format.lower() in ['jpg', 'jpeg']:
        io.imsave(output_path, image, quality=jpeg_quality, check_contrast=False)
    else:
        io.imsave(output_path, image, check_contrast=False)


def get_output_filename(original_filename, suffix, output_format, preserve_original=False):
    """Creates output filename by adding suffix before extension.
    
    Args:
        original_filename: Original filename with extension
        suffix: Suffix to add (e.g., "_gaussian")
        output_format: Output format (png, jpg, tiff)
        preserve_original: If True, use original file extension
    
    Returns:
        New filename with suffix
    """
    base_name = os.path.splitext(original_filename)[0]
    
    if preserve_original:
        original_ext = os.path.splitext(original_filename)[1]
        return f"{base_name}{suffix}{original_ext}"
    else:
        return f"{base_name}{suffix}.{output_format}"
