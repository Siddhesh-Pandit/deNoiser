"""Color space utilities for preserving color during denoising."""
import numpy as np
from skimage import color


def _denoise_luminance_only(image, denoise_func):
    """Apply denoising only to luminance channel, preserving color.
    
    This converts RGB to LAB color space, denoises only the L (luminance) channel,
    then converts back to RGB. This preserves saturation, hue, and color information.
    
    Args:
        image: RGB image array
        denoise_func: Function that takes an image and returns denoised version
    
    Returns:
        Denoised image with preserved color
    """
    # Store original dtype
    original_dtype = image.dtype
    
    # Convert to float [0, 1] for color space conversion
    if image.dtype == np.uint8:
        img_float = image.astype(np.float64) / 255.0
    elif image.dtype == np.uint16:
        img_float = image.astype(np.float64) / 65535.0
    else:
        img_float = image.astype(np.float64)
        if img_float.max() > 1.0:
            img_float = img_float / img_float.max()
    
    # Convert RGB to LAB color space
    # L: Lightness (0-100)
    # A: Green-Red axis
    # B: Blue-Yellow axis
    lab = color.rgb2lab(img_float)
    
    # Extract channels
    l_channel = lab[:, :, 0]
    a_channel = lab[:, :, 1]
    b_channel = lab[:, :, 2]
    
    # Work with L channel directly in LAB range [0, 100]
    # Most denoising functions work better with normalized data
    # So we'll create a temporary RGB-like representation
    
    # Create a grayscale "image" from L channel for denoising
    # Normalize to [0, 255] range like a regular grayscale image
    l_as_gray = (l_channel / 100.0 * 255.0).astype(np.uint8)
    
    # Denoise the grayscale representation
    l_denoised_gray = denoise_func(l_as_gray)
    
    # Convert back to LAB L range [0, 100]
    if l_denoised_gray.dtype == np.uint8:
        l_denoised_lab = (l_denoised_gray.astype(np.float64) / 255.0) * 100.0
    elif l_denoised_gray.dtype == np.uint16:
        l_denoised_lab = (l_denoised_gray.astype(np.float64) / 65535.0) * 100.0
    else:
        # Already float, assume [0, 1] range
        l_denoised_lab = l_denoised_gray * 100.0
    
    # Clip L channel to valid range
    l_denoised_lab = np.clip(l_denoised_lab, 0, 100)
    
    # Reconstruct LAB image with denoised L and original A, B
    lab_denoised = np.stack([l_denoised_lab, a_channel, b_channel], axis=2)
    
    # Convert back to RGB
    rgb_denoised = color.lab2rgb(lab_denoised)
    
    # Clip to valid range [0, 1] before converting to int
    rgb_denoised = np.clip(rgb_denoised, 0, 1)
    
    # Convert back to original dtype
    if original_dtype == np.uint8:
        return np.clip((rgb_denoised * 255 + 0.5), 0, 255).astype(np.uint8)
    elif original_dtype == np.uint16:
        return np.clip((rgb_denoised * 65535 + 0.5), 0, 65535).astype(np.uint16)
    else:
        return rgb_denoised
