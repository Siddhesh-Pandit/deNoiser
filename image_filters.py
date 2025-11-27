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
            
            if image.dtype == np.uint16:
                return (denoised * 256).astype(np.uint16)
            elif image.dtype == np.uint8:
                return denoised.astype(np.uint8)
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
    if image.dtype == np.uint16:
        return (denoised * 256).astype(np.uint16)
    elif image.dtype == np.uint8:
        return denoised.astype(np.uint8)
    else:
        return denoised
