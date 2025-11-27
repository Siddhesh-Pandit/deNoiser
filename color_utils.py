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
    
    # Normalize L channel to [0, 1] for denoising
    l_normalized = l_channel / 100.0
    
    # Convert to original dtype for denoising
    if original_dtype == np.uint8:
        l_for_denoise = (l_normalized * 255).astype(np.uint8)
    elif original_dtype == np.uint16:
        l_for_denoise = (l_normalized * 65535).astype(np.uint16)
    else:
        l_for_denoise = l_normalized
    
    # Denoise only the luminance channel
    l_denoised = denoise_func(l_for_denoise)
    
    # Convert back to float [0, 1]
    if original_dtype == np.uint8:
        l_denoised_float = l_denoised.astype(np.float64) / 255.0
    elif original_dtype == np.uint16:
        l_denoised_float = l_denoised.astype(np.float64) / 65535.0
    else:
        l_denoised_float = l_denoised.astype(np.float64)
    
    # Scale back to LAB L range [0, 100]
    l_denoised_lab = l_denoised_float * 100.0
    
    # Reconstruct LAB image with denoised L and original A, B
    lab_denoised = np.stack([l_denoised_lab, a_channel, b_channel], axis=2)
    
    # Convert back to RGB
    rgb_denoised = color.lab2rgb(lab_denoised)
    
    # Convert back to original dtype
    if original_dtype == np.uint8:
        return (rgb_denoised * 255).astype(np.uint8)
    elif original_dtype == np.uint16:
        return (rgb_denoised * 65535).astype(np.uint16)
    else:
        return rgb_denoised
