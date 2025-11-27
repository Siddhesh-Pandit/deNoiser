"""Image batch processing logic."""
import os
import logging
from image_io import get_image_files, load_image, save_image, get_output_filename, is_rawpy_available
from image_filters import apply_gaussian_filter, apply_median_filter, apply_nonlocal_means
from metrics import normalize_image, calculate_noise_metrics


class ImageProcessor:
    """Handles batch processing of images with denoising filters."""
    
    def __init__(self, config):
        """Initialize processor with configuration.
        
        Args:
            config: DenoiserConfig object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def process_batch(self):
        """Process all images in input folder.
        
        Returns:
            Tuple of (processed_count, metrics_list)
        """
        os.makedirs(self.config.output_path, exist_ok=True)
        
        self.logger.info(f"Output format: {self.config.output.format.upper()}" + 
                        (f" (quality: {self.config.output.jpeg_quality})" 
                         if self.config.output.format == 'jpg' else ""))
        
        # Log RAW support status
        if is_rawpy_available():
            self.logger.info(f"RAW support: Enabled (mode: {self.config.raw.processing_mode})")
        else:
            self.logger.info("RAW support: Disabled (install rawpy to enable)")
        
        image_files = get_image_files(self.config.input_path)
        total_files = len(image_files)
        self.logger.info(f"Found {total_files} images to process")
        
        processed_count = 0
        metrics_list = []
        
        for idx, filename in enumerate(image_files, 1):
            try:
                metrics = self._process_single_image(filename, idx, total_files)
                metrics_list.append(metrics)
                processed_count += 1
            except Exception as e:
                self.logger.error(f"  ✗ Error processing {filename}: {str(e)}")
                continue
        
        return processed_count, metrics_list
    
    def _process_single_image(self, filename, idx, total):
        """Process a single image with all enabled filters.
        
        Args:
            filename: Name of image file
            idx: Current image index
            total: Total number of images
        
        Returns:
            Dictionary with metrics for this image
        """
        self.logger.info(f"[{idx}/{total}] Processing: {filename}")
        
        img_path = os.path.join(self.config.input_path, filename)
        img = load_image(img_path, raw_mode=self.config.raw.processing_mode)
        img_float = normalize_image(img)
        
        image_metrics = {'filename': filename}
        
        # Apply Gaussian filter
        if self.config.filters.enable_gaussian:
            self._apply_and_save_filter(
                img, img_float, filename, image_metrics,
                filter_func=lambda: apply_gaussian_filter(img, self.config.gaussian.sigma),
                filter_name='gaussian',
                filter_params=f"σ={self.config.gaussian.sigma}"
            )
        
        # Apply Median filter
        if self.config.filters.enable_median:
            self._apply_and_save_filter(
                img, img_float, filename, image_metrics,
                filter_func=lambda: apply_median_filter(img, self.config.median.size),
                filter_name='median',
                filter_params=f"size={self.config.median.size}"
            )
        
        # Apply Non-local means
        if self.config.filters.enable_nonlocal:
            self._apply_and_save_filter(
                img, img_float, filename, image_metrics,
                filter_func=lambda: apply_nonlocal_means(
                    img, 
                    self.config.nonlocal.h_multiplier,
                    self.config.nonlocal.fast_mode,
                    self.config.nonlocal.patch_size,
                    self.config.nonlocal.patch_distance
                ),
                filter_name='nonlocal',
                filter_params=f"h={self.config.nonlocal.h_multiplier}×σ"
            )
        
        return image_metrics
    
    def _apply_and_save_filter(self, img, img_float, filename, metrics_dict, 
                               filter_func, filter_name, filter_params):
        """Apply filter, save result, and calculate metrics.
        
        Args:
            img: Original image array
            img_float: Normalized original image
            filename: Original filename
            metrics_dict: Dictionary to store metrics
            filter_func: Function that applies the filter
            filter_name: Name of filter for output
            filter_params: Parameter string for logging
        """
        # Apply filter
        filtered_img = filter_func()
        
        # Save filtered image
        output_filename = get_output_filename(
            filename, 
            f"_{filter_name}", 
            self.config.output.format,
            self.config.output.preserve_original_format
        )
        output_path = os.path.join(self.config.output_path, output_filename)
        save_image(output_path, filtered_img, self.config.output.format, 
                  self.config.output.jpeg_quality)
        
        # Calculate metrics
        filtered_float = normalize_image(filtered_img)
        filter_metrics = calculate_noise_metrics(img_float, filtered_float)
        
        # Store metrics
        metrics_dict[f'{filter_name}_noise_reduction'] = f"{filter_metrics['noise_reduction_pct']:.2f}%"
        metrics_dict[f'{filter_name}_psnr'] = f"{filter_metrics['psnr']:.2f} dB"
        
        # Log results
        self.logger.info(
            f"  ✓ {filter_name.capitalize()} ({filter_params}): "
            f"{filter_metrics['noise_reduction_pct']:.1f}% noise reduction, "
            f"PSNR: {filter_metrics['psnr']:.2f} dB"
        )
