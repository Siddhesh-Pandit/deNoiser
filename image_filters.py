"""Image denoising filter implementations."""
import numpy as np
from scipy import ndimage as nd
from skimage.restoration import denoise_nl_means, estimate_sigma


def apply_gaussian_filter(image, sigma=0.75):
    """Apply Gaussian blur filter for noise reduction.
    
    Args:
        image: Input image array
        sigma: Standard deviation for Gaussian kernel
    
    Returns:
        Filtered image array
    """
    return nd.gaussian_filter(image, sigma=sigma)


def apply_median_filter(image, size=3):
    """Apply median filter for salt-and-pepper noise removal.
    
    Args:
        image: Input image array
        size: Size of the median filter window
    
    Returns:
        Filtered image array
    """
    return nd.median_filter(image, size=size)


def apply_nonlocal_means(image, h_multiplier=1.15, fast_mode=True, 
                        patch_size=5, patch_distance=6):
    """Apply non-local means denoising filter.
    
    Args:
        image: Input image array
        h_multiplier: Multiplier for estimated noise level
        fast_mode: Use fast approximation
        patch_size: Size of patches for comparison
        patch_distance: Maximum distance to search for patches
    
    Returns:
        Filtered image array
    """
    sigma_est = np.mean(estimate_sigma(image, channel_axis=-1))
    return denoise_nl_means(
        image, 
        h=h_multiplier * sigma_est, 
        fast_mode=fast_mode,
        patch_distance=patch_distance, 
        patch_size=patch_size, 
        channel_axis=-1
    )
