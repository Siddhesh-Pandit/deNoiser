"""Noise reduction metrics calculation."""
import numpy as np
import csv
import os
from datetime import datetime
from skimage.restoration import estimate_sigma
from skimage.metrics import peak_signal_noise_ratio as psnr


def normalize_image(image):
    """Normalize image to float64 in range [0, 1].
    
    Args:
        image: Input image array
    
    Returns:
        Normalized image array
    """
    if image.dtype == np.uint8:
        return image.astype(np.float64) / 255.0
    return image.astype(np.float64)


def calculate_noise_metrics(original, denoised):
    """Calculate noise reduction metrics between original and denoised images.
    
    Args:
        original: Original image array (normalized)
        denoised: Denoised image array (normalized)
    
    Returns:
        Dictionary with noise metrics
    """
    # Estimate noise in original and denoised images
    if original.ndim == 3:  # Color image
        original_noise = np.mean(estimate_sigma(original, channel_axis=-1))
        denoised_noise = np.mean(estimate_sigma(denoised, channel_axis=-1))
    else:  # Grayscale
        original_noise = estimate_sigma(original)
        denoised_noise = estimate_sigma(denoised)
    
    # Calculate noise reduction percentage
    noise_reduction = ((original_noise - denoised_noise) / original_noise) * 100 if original_noise > 0 else 0
    
    # Calculate PSNR (higher is better)
    psnr_value = psnr(original, denoised)
    
    return {
        'original_noise': original_noise,
        'denoised_noise': denoised_noise,
        'noise_reduction_pct': noise_reduction,
        'psnr': psnr_value
    }


def save_metrics_to_csv(metrics_list, output_folder_path):
    """Save noise reduction metrics to CSV file.
    
    Args:
        metrics_list: List of dictionaries containing metrics for each image
        output_folder_path: Folder where CSV will be saved
    """
    if not metrics_list:
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(output_folder_path, f"denoising_metrics_{timestamp}.csv")
    
    fieldnames = ['filename', 'gaussian_noise_reduction', 'gaussian_psnr', 
                  'median_noise_reduction', 'median_psnr', 
                  'nonlocal_noise_reduction', 'nonlocal_psnr']
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metrics_list)
    
    return csv_filename
