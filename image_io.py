"""Image input/output utilities."""
import os
import sys
import logging
from skimage import io
import numpy as np

# Try to import rawpy for RAW format support
try:
    import rawpy
    RAWPY_AVAILABLE = True
except ImportError:
    RAWPY_AVAILABLE = False

logger = logging.getLogger(__name__)

# Standard image formats
STANDARD_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif')

# RAW formats (only if rawpy is available)
RAW_EXTENSIONS = ('.nef', '.cr2', '.cr3', '.arw', '.dng', '.raf', '.orf', '.rw2', '.raw')

# All supported extensions
SUPPORTED_EXTENSIONS = STANDARD_EXTENSIONS + (RAW_EXTENSIONS if RAWPY_AVAILABLE else ())


def is_rawpy_available():
    """Check if rawpy library is available for RAW processing."""
    return RAWPY_AVAILABLE


def get_image_files(folder_path):
    """Get list of image files from folder.
    
    Args:
        folder_path: Path to folder containing images
    
    Returns:
        List of image filenames
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    
    all_files = [f for f in os.listdir(folder_path) 
                 if os.path.splitext(f.lower())[1] in SUPPORTED_EXTENSIONS]
    
    # Check for RAW files
    raw_files = [f for f in all_files if os.path.splitext(f.lower())[1] in RAW_EXTENSIONS]
    
    if raw_files and not RAWPY_AVAILABLE:
        logger.warning(f"Found {len(raw_files)} RAW files but rawpy is not installed.")
        logger.warning(f"RAW files will be skipped. To enable RAW support:")
        logger.warning(f"  - Requires Python 3.8-3.13 (you have {sys.version.split()[0]})")
        logger.warning(f"  - Install with: pip install rawpy")
        
        # Filter out RAW files if rawpy is not available
        files = [f for f in all_files if os.path.splitext(f.lower())[1] not in RAW_EXTENSIONS]
        logger.info(f"Skipping {len(raw_files)} RAW files, processing {len(files)} standard format images")
        return files
    
    return all_files


def load_image(file_path, raw_mode='full'):
    """Load image from file, including RAW formats.
    
    Args:
        file_path: Path to image file
        raw_mode: RAW processing mode ('full', 'preview', or 'half')
            - 'full': Full resolution processing (slow, best quality)
            - 'half': Half resolution processing (faster, good quality)
            - 'preview': Extract embedded JPEG preview (fastest, lower quality)
    
    Returns:
        Image array (RGB, uint8 or uint16 depending on source)
    """
    ext = os.path.splitext(file_path.lower())[1]
    
    # Check if it's a RAW file
    if ext in RAW_EXTENSIONS:
        if not RAWPY_AVAILABLE:
            raise ImportError(
                f"RAW file detected ({ext}) but rawpy is not installed. "
                "Install with: pip install rawpy"
            )
        
        return _load_raw_image(file_path, raw_mode)
    else:
        # Load standard image format
        return io.imread(file_path)


def _load_raw_image(file_path, mode='full'):
    """Load and process RAW image file.
    
    Args:
        file_path: Path to RAW file
        mode: Processing mode ('full', 'half', or 'preview')
    
    Returns:
        Processed RGB image array
    """
    logger.info(f"  Loading RAW file (mode: {mode})...")
    
    with rawpy.imread(file_path) as raw:
        if mode == 'preview':
            # Extract embedded JPEG preview (fastest)
            try:
                thumb = raw.extract_thumb()
                if thumb.format == rawpy.ThumbFormat.JPEG:
                    from io import BytesIO
                    return io.imread(BytesIO(thumb.data))
                else:
                    logger.warning("  No JPEG preview found, using half-size processing")
                    mode = 'half'
            except Exception as e:
                logger.warning(f"  Failed to extract preview: {e}, using half-size processing")
                mode = 'half'
        
        # Full or half-size processing
        if mode == 'full':
            rgb = raw.postprocess(
                use_camera_wb=True,       # Use camera white balance
                half_size=False,          # Full resolution
                no_auto_bright=True,      # Preserve exposure
                output_bps=16,            # 16-bit output for quality
                output_color=rawpy.ColorSpace.sRGB
            )
        else:  # half
            rgb = raw.postprocess(
                use_camera_wb=True,
                half_size=True,           # Half resolution (faster)
                no_auto_bright=True,
                output_bps=16,
                output_color=rawpy.ColorSpace.sRGB
            )
        
        # Convert 16-bit to 8-bit for consistency with other formats
        # (denoising algorithms work better with normalized values)
        if rgb.dtype == np.uint16:
            rgb = (rgb / 256).astype(np.uint8)
        
        return rgb


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
