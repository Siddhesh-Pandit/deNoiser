# Copyright (c) 2025 Adwait Godbole and Siddhesh Pandit
# Licensed under CC BY-NC 4.0 (Attribution-NonCommercial 4.0 International)
# https://creativecommons.org/licenses/by-nc/4.0/
# For commercial use, please contact the authors.

"""Image denoising filter implementations."""
import numpy as np
from scipy import ndimage as nd
from skimage.restoration import denoise_nl_means, estimate_sigma
from skimage import color
from color_utils import _denoise_luminance_only


def apply_gaussian_filter(image, sigma=0.75, preserve_color=False):
    """Apply Gaussian blur filter for noise reduction.
    
    Args:
        image: Input image array
        sigma: Standard deviation for Gaussian kernel
        preserve_color: If True, denoise only luminance (preserves color/saturation)
    
    Returns:
        Filtered image array
    """
    if preserve_color and image.ndim == 3:
        return _denoise_luminance_only(image, lambda img: nd.gaussian_filter(img, sigma=sigma))
    return nd.gaussian_filter(image, sigma=sigma)


def apply_median_filter(image, size=3, preserve_color=False):
    """Apply median filter for salt-and-pepper noise removal.
    
    Args:
        image: Input image array
        size: Size of the median filter window
        preserve_color: If True, denoise only luminance (preserves color/saturation)
    
    Returns:
        Filtered image array
    """
    if preserve_color and image.ndim == 3:
        return _denoise_luminance_only(image, lambda img: nd.median_filter(img, size=size))
    return nd.median_filter(image, size=size)


def apply_unsharp_mask(image, radius=1.0, amount=0.5, preserve_color=False):
    """Apply unsharp mask to restore structure and detail.
    
    This sharpens the image by subtracting a blurred version from the original.
    Useful for restoring detail after aggressive denoising.
    
    Args:
        image: Input image array
        radius: Radius of Gaussian blur (higher = more sharpening)
        amount: Strength of sharpening (0.0-2.0, typical: 0.3-1.0)
        preserve_color: If True, sharpen only luminance (preserves color/saturation)
    
    Returns:
        Sharpened image array
    """
    # If preserve_color is enabled and image is RGB, sharpen only luminance
    if preserve_color and image.ndim == 3:
        def sharpen_func(img):
            # img is the L channel as uint8 grayscale (0-255)
            # Convert to float for processing
            img_float = img.astype(np.float64)
            
            # Create blurred version
            blurred = nd.gaussian_filter(img_float, sigma=radius)
            
            # Unsharp mask: original + amount * (original - blurred)
            sharpened = img_float + amount * (img_float - blurred)
            
            # Clip to valid range [0, 255]
            sharpened = np.clip(sharpened, 0, 255)
            
            # Convert back to uint8
            return sharpened.astype(np.uint8)
        
        return _denoise_luminance_only(image, sharpen_func)
    
    # Original full-color sharpening
    # Convert to float for processing
    if image.dtype == np.uint8:
        img_float = image.astype(np.float64)
        max_val = 255.0
    elif image.dtype == np.uint16:
        img_float = image.astype(np.float64)
        max_val = 65535.0
    else:
        img_float = image.astype(np.float64)
        max_val = 1.0 if image.max() <= 1.0 else image.max()
    
    # Create blurred version
    blurred = nd.gaussian_filter(img_float, sigma=radius)
    
    # Unsharp mask: original + amount * (original - blurred)
    sharpened = img_float + amount * (img_float - blurred)
    
    # Clip to valid range
    sharpened = np.clip(sharpened, 0, max_val)
    
    # Convert back to original dtype
    if image.dtype == np.uint8:
        return sharpened.astype(np.uint8)
    elif image.dtype == np.uint16:
        return sharpened.astype(np.uint16)
    else:
        return sharpened


def apply_nonlocal_means(image, h_multiplier=1.15, fast_mode=True, 
                        patch_size=5, patch_distance=6, preserve_color=False):
    """Apply non-local means denoising filter.
    
    Args:
        image: Input image array
        h_multiplier: Multiplier for estimated noise level
        fast_mode: Use fast approximation
        patch_size: Size of patches for comparison
        patch_distance: Maximum distance to search for patches
        preserve_color: If True, denoise only luminance (preserves color/saturation)
    
    Returns:
        Filtered image array
    """
    if preserve_color and image.ndim == 3:
        # Define the denoising function for luminance-only processing
        def denoise_func(img):
            if img.dtype == np.uint8:
                img_for_denoise = img
            elif img.dtype == np.uint16:
                img_for_denoise = (img / 256).astype(np.uint8)
            elif np.issubdtype(img.dtype, np.floating):
                if img.max() > 1.0:
                    img_for_denoise = img / img.max()
                else:
                    img_for_denoise = img
            else:
                img_for_denoise = ((img - img.min()) / (img.max() - img.min()) * 255).astype(np.uint8)
            
            sigma_est = estimate_sigma(img_for_denoise)
            denoised = denoise_nl_means(
                img_for_denoise, 
                h=h_multiplier * sigma_est, 
                fast_mode=fast_mode,
                patch_distance=patch_distance, 
                patch_size=patch_size, 
                channel_axis=None
            )
            
            # denoise_nl_means returns float in [0, 1] range for uint8 input
            if image.dtype == np.uint16:
                return (denoised * 65535).astype(np.uint16)
            elif image.dtype == np.uint8:
                return (denoised * 255).astype(np.uint8)
            else:
                return denoised
        
        return _denoise_luminance_only(image, denoise_func)
    
    # Original full-color denoising
    # Ensure image is in correct format for denoise_nl_means
    # It expects uint8 or float in [0, 1] range
    if image.dtype == np.uint8:
        img_for_denoise = image
    elif image.dtype == np.uint16:
        # Convert uint16 to uint8
        img_for_denoise = (image / 256).astype(np.uint8)
    elif np.issubdtype(image.dtype, np.floating):
        # Ensure float is in [0, 1] range
        if image.max() > 1.0:
            img_for_denoise = image / image.max()
        else:
            img_for_denoise = image
    else:
        # Convert to uint8 as fallback
        img_for_denoise = ((image - image.min()) / (image.max() - image.min()) * 255).astype(np.uint8)
    
    # Estimate sigma
    if img_for_denoise.ndim == 3:
        sigma_est = np.mean(estimate_sigma(img_for_denoise, channel_axis=-1))
    else:
        sigma_est = estimate_sigma(img_for_denoise)
    
    # Apply denoising
    denoised = denoise_nl_means(
        img_for_denoise, 
        h=h_multiplier * sigma_est, 
        fast_mode=fast_mode,
        patch_distance=patch_distance, 
        patch_size=patch_size, 
        channel_axis=-1 if img_for_denoise.ndim == 3 else None
    )
    
    # Convert back to original dtype
    # denoise_nl_means returns float in [0, 1] range for uint8 input
    if image.dtype == np.uint16:
        # If input was uint16, scale back up
        return (denoised * 65535).astype(np.uint16)
    elif image.dtype == np.uint8:
        # If input was uint8, scale from [0, 1] to [0, 255]
        return (denoised * 255).astype(np.uint8)
    else:
        return denoised



def boost_saturation(image, amount=1.3):
    """Boost color saturation to make colors more vivid.
    
    Args:
        image: Input RGB image array
        amount: Saturation multiplier (1.0 = no change, >1.0 = more saturated)
    
    Returns:
        Image with boosted saturation
    """
    if image.ndim != 3:
        # Grayscale image, return as-is
        return image
    
    # Store original dtype
    original_dtype = image.dtype
    
    # Convert to float [0, 1]
    if image.dtype == np.uint8:
        img_float = image.astype(np.float64) / 255.0
    elif image.dtype == np.uint16:
        img_float = image.astype(np.float64) / 65535.0
    else:
        img_float = image.astype(np.float64)
        if img_float.max() > 1.0:
            img_float = img_float / img_float.max()
    
    # Convert RGB to HSV
    hsv = color.rgb2hsv(img_float)
    
    # Boost saturation (S channel)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * amount, 0, 1)
    
    # Convert back to RGB
    rgb_boosted = color.hsv2rgb(hsv)
    
    # Clip to valid range
    rgb_boosted = np.clip(rgb_boosted, 0, 1)
    
    # Convert back to original dtype
    if original_dtype == np.uint8:
        return np.clip((rgb_boosted * 255 + 0.5), 0, 255).astype(np.uint8)
    elif original_dtype == np.uint16:
        return np.clip((rgb_boosted * 65535 + 0.5), 0, 65535).astype(np.uint16)
    else:
        return rgb_boosted


def boost_brightness(image, amount=1.1):
    """Boost image brightness/luminance.
    
    Args:
        image: Input image array (RGB or grayscale)
        amount: Brightness multiplier (1.0 = no change, >1.0 = brighter, <1.0 = darker)
    
    Returns:
        Image with adjusted brightness
    """
    # Store original dtype
    original_dtype = image.dtype
    
    # Convert to float [0, 1]
    if image.dtype == np.uint8:
        img_float = image.astype(np.float64) / 255.0
    elif image.dtype == np.uint16:
        img_float = image.astype(np.float64) / 65535.0
    else:
        img_float = image.astype(np.float64)
        if img_float.max() > 1.0:
            img_float = img_float / img_float.max()
    
    if image.ndim == 3:
        # Color image: adjust brightness in HSV space (V channel)
        hsv = color.rgb2hsv(img_float)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * amount, 0, 1)
        rgb_boosted = color.hsv2rgb(hsv)
        rgb_boosted = np.clip(rgb_boosted, 0, 1)
    else:
        # Grayscale: directly multiply
        rgb_boosted = np.clip(img_float * amount, 0, 1)
    
    # Convert back to original dtype
    if original_dtype == np.uint8:
        return np.clip((rgb_boosted * 255 + 0.5), 0, 255).astype(np.uint8)
    elif original_dtype == np.uint16:
        return np.clip((rgb_boosted * 65535 + 0.5), 0, 65535).astype(np.uint16)
    else:
        return rgb_boosted
