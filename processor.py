# Copyright (c) 2025 Adwait Godbole and Siddhesh Pandit
# Licensed under CC BY-NC 4.0 (Attribution-NonCommercial 4.0 International)
# https://creativecommons.org/licenses/by-nc/4.0/
# For commercial use, please contact the authors.

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
    
    def _log_settings(self):
        """Log all current processing settings."""
        self.logger.info("=" * 60)
        self.logger.info("PROCESSING SETTINGS:")
        self.logger.info("=" * 60)
        
        # Output settings
        self.logger.info(f"Output format: {self.config.output.format.upper()}" + 
                        (f" (quality: {self.config.output.jpeg_quality})" 
                         if self.config.output.format == 'jpg' else ""))
        self.logger.info(f"Preserve color: {'ON' if self.config.output.preserve_color else 'OFF'}")
        self.logger.info(f"Apply sharpening: {'ON' if self.config.output.apply_sharpening else 'OFF'}")
        if self.config.output.apply_sharpening:
            self.logger.info(f"  • Sharpen amount: {self.config.output.sharpen_amount}")
            self.logger.info(f"  • Sharpen radius: {self.config.output.sharpen_radius}")
        self.logger.info(f"Boost saturation: {'ON' if self.config.output.boost_saturation else 'OFF'}")
        if self.config.output.boost_saturation:
            self.logger.info(f"  • Saturation amount: {self.config.output.saturation_amount}")
        
        # Enabled filters
        enabled_filters = []
        if self.config.filters.enable_gaussian:
            enabled_filters.append(f"Gaussian (σ={self.config.gaussian.sigma})")
        if self.config.filters.enable_median:
            enabled_filters.append(f"Median (size={self.config.median.size})")
        if self.config.filters.enable_nonlocal:
            enabled_filters.append(f"Non-local (h={self.config.nonlocal_means.h_multiplier}×σ, " +
                                  f"patch={self.config.nonlocal_means.patch_size}, " +
                                  f"distance={self.config.nonlocal_means.patch_distance}, " +
                                  f"fast={'ON' if self.config.nonlocal_means.fast_mode else 'OFF'})")
        
        self.logger.info(f"Enabled filters: {', '.join(enabled_filters) if enabled_filters else 'None'}")
        
        # Log RAW support status
        if is_rawpy_available():
            self.logger.info(f"RAW support: Enabled (mode: {self.config.raw.processing_mode})")
        else:
            import sys
            py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            self.logger.info(f"RAW support: Disabled (Python {py_version})")
            if sys.version_info >= (3, 14):
                self.logger.info("  Note: Python 3.14+ detected - rawpy not yet available")
            else:
                self.logger.info("  Install with: pip install rawpy")
        
        self.logger.info("=" * 60)
    
    def process_batch(self, progress_callback=None):
        """Process all images in input folder.
        
        Args:
            progress_callback: Optional callback function(current, total, filename)
        
        Returns:
            Tuple of (processed_count, metrics_list)
        """
        os.makedirs(self.config.output_path, exist_ok=True)
        
        # Log all current settings
        self._log_settings()
        
        image_files = get_image_files(self.config.input_path)
        total_files = len(image_files)
        
        if total_files == 0:
            self.logger.warning("No supported images found in input folder")
        else:
            self.logger.info(f"Found {total_files} images to process")
        
        processed_count = 0
        metrics_list = []
        
        for idx, filename in enumerate(image_files, 1):
            try:
                # Update progress if callback provided
                if progress_callback:
                    progress_callback(idx, total_files, filename)
                
                metrics = self._process_single_image(filename, idx, total_files)
                metrics_list.append(metrics)
                processed_count += 1
            except Exception as e:
                self.logger.error(f"  ✗ Error processing {filename}: {str(e)}")
                continue
        
        return processed_count, metrics_list
    
    def process_files(self, file_paths, progress_callback=None, mask=None):
        """Process specific image files.
        
        Args:
            file_paths: List of full file paths to process
            progress_callback: Optional callback function(current, total, filename)
            mask: Optional numpy array mask for selective denoising (0-1 float)
        
        Returns:
            Tuple of (processed_count, metrics_list)
        """
        os.makedirs(self.config.output_path, exist_ok=True)
        
        # Log all current settings
        self._log_settings()
        
        total_files = len(file_paths)
        processed_count = 0
        metrics_list = []
        
        for idx, file_path in enumerate(file_paths, 1):
            filename = os.path.basename(file_path)
            try:
                # Update progress if callback provided
                if progress_callback:
                    progress_callback(idx, total_files, filename)
                
                self.logger.info(f"[{idx}/{total_files}] Processing: {filename}")
                
                img = load_image(file_path, raw_mode=self.config.raw.processing_mode)
                img_float = normalize_image(img)
                
                image_metrics = {'filename': filename}
                
                filters_attempted = 0
                filters_succeeded = 0
                
                # Apply Gaussian filter
                if self.config.filters.enable_gaussian:
                    filters_attempted += 1
                    try:
                        self._apply_and_save_filter(
                            img, img_float, filename, image_metrics,
                            filter_func=lambda: apply_gaussian_filter(img, self.config.gaussian.sigma, self.config.output.preserve_color),
                            filter_name='gaussian',
                            filter_params=f"σ={self.config.gaussian.sigma}" + (" [color-preserving]" if self.config.output.preserve_color else ""),
                            mask=mask
                        )
                        filters_succeeded += 1
                    except Exception:
                        pass
                
                # Apply Median filter
                if self.config.filters.enable_median:
                    filters_attempted += 1
                    try:
                        self._apply_and_save_filter(
                            img, img_float, filename, image_metrics,
                            filter_func=lambda: apply_median_filter(img, self.config.median.size, self.config.output.preserve_color),
                            filter_name='median',
                            filter_params=f"size={self.config.median.size}" + (" [color-preserving]" if self.config.output.preserve_color else ""),
                            mask=mask
                        )
                        filters_succeeded += 1
                    except Exception:
                        pass
                
                # Apply Non-local means
                if self.config.filters.enable_nonlocal:
                    filters_attempted += 1
                    try:
                        self._apply_and_save_filter(
                            img, img_float, filename, image_metrics,
                            filter_func=lambda: apply_nonlocal_means(
                                img, 
                                self.config.nonlocal_means.h_multiplier,
                                self.config.nonlocal_means.fast_mode,
                                self.config.nonlocal_means.patch_size,
                                self.config.nonlocal_means.patch_distance,
                                self.config.output.preserve_color
                            ),
                            filter_name='nonlocal',
                            filter_params=f"h={self.config.nonlocal_means.h_multiplier}×σ" + (" [color-preserving]" if self.config.output.preserve_color else ""),
                            mask=mask
                        )
                        filters_succeeded += 1
                    except Exception:
                        pass
                
                # Log summary for this image
                if filters_succeeded == 0:
                    self.logger.warning(f"  ⚠ All filters failed for {filename}")
                elif filters_succeeded < filters_attempted:
                    self.logger.info(f"  ℹ {filters_succeeded}/{filters_attempted} filters succeeded")
                
                metrics_list.append(image_metrics)
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
        
        filters_attempted = 0
        filters_succeeded = 0
        
        # Apply Gaussian filter
        if self.config.filters.enable_gaussian:
            filters_attempted += 1
            try:
                self._apply_and_save_filter(
                    img, img_float, filename, image_metrics,
                    filter_func=lambda: apply_gaussian_filter(img, self.config.gaussian.sigma, self.config.output.preserve_color),
                    filter_name='gaussian',
                    filter_params=f"σ={self.config.gaussian.sigma}" + (" [color-preserving]" if self.config.output.preserve_color else "")
                )
                filters_succeeded += 1
            except Exception:
                pass  # Error already logged in _apply_and_save_filter
        
        # Apply Median filter
        if self.config.filters.enable_median:
            filters_attempted += 1
            try:
                self._apply_and_save_filter(
                    img, img_float, filename, image_metrics,
                    filter_func=lambda: apply_median_filter(img, self.config.median.size, self.config.output.preserve_color),
                    filter_name='median',
                    filter_params=f"size={self.config.median.size}" + (" [color-preserving]" if self.config.output.preserve_color else "")
                )
                filters_succeeded += 1
            except Exception:
                pass  # Error already logged in _apply_and_save_filter
        
        # Apply Non-local means
        if self.config.filters.enable_nonlocal:
            filters_attempted += 1
            try:
                self._apply_and_save_filter(
                    img, img_float, filename, image_metrics,
                    filter_func=lambda: apply_nonlocal_means(
                        img, 
                        self.config.nonlocal_means.h_multiplier,
                        self.config.nonlocal_means.fast_mode,
                        self.config.nonlocal_means.patch_size,
                        self.config.nonlocal_means.patch_distance,
                        self.config.output.preserve_color
                    ),
                    filter_name='nonlocal',
                    filter_params=f"h={self.config.nonlocal_means.h_multiplier}×σ" + (" [color-preserving]" if self.config.output.preserve_color else "")
                )
                filters_succeeded += 1
            except Exception:
                pass  # Error already logged in _apply_and_save_filter
        
        # Log summary for this image
        if filters_succeeded == 0:
            self.logger.warning(f"  ⚠ All filters failed for {filename}")
        elif filters_succeeded < filters_attempted:
            self.logger.info(f"  ℹ {filters_succeeded}/{filters_attempted} filters succeeded")
        
        return image_metrics
    
    def _apply_and_save_filter(self, img, img_float, filename, metrics_dict, 
                               filter_func, filter_name, filter_params, mask=None):
        """Apply filter, save result, and calculate metrics.
        
        Args:
            img: Original image array
            img_float: Normalized original image
            filename: Original filename
            metrics_dict: Dictionary to store metrics
            filter_func: Function that applies the filter
            filter_name: Name of filter for output
            filter_params: Parameter string for logging
            mask: Optional mask array for selective denoising (0-1 float)
        """
        try:
            # Check if AI denoising is enabled
            if self.config.ai_denoiser.enable_ai:
                try:
                    from ai_denoiser import denoise_with_ai, is_ai_available
                    
                    if is_ai_available():
                        self.logger.info(f"  Using AI denoiser: {self.config.ai_denoiser.model_name}")
                        
                        # Determine device
                        device = None if self.config.ai_denoiser.device == 'auto' else self.config.ai_denoiser.device
                        
                        # AI denoise
                        filtered_img = denoise_with_ai(
                            img,
                            model_name=self.config.ai_denoiser.model_name,
                            device=device,
                            progress_callback=lambda c, t, m: self.logger.info(f"    {m}")
                        )
                        
                        filter_name = f"{filter_name}_ai"
                        self.logger.info(f"  ✓ AI denoising complete")
                    else:
                        self.logger.warning("  AI dependencies not available, using classical filters")
                        filtered_img = filter_func()
                except Exception as e:
                    self.logger.error(f"  AI denoising failed: {e}")
                    self.logger.info("  Falling back to classical filters")
                    filtered_img = filter_func()
            else:
                # Classical denoising
                filtered_img = filter_func()
            
            # Apply mask if provided (selective denoising - works for both AI and classical)
            if mask is not None:
                import numpy as np
                # Ensure mask matches image dimensions
                if mask.shape[:2] != img.shape[:2]:
                    from PIL import Image as PILImage
                    mask_pil = PILImage.fromarray((mask * 255).astype(np.uint8))
                    mask_pil = mask_pil.resize((img.shape[1], img.shape[0]), PILImage.Resampling.LANCZOS)
                    mask = np.array(mask_pil).astype(np.float32) / 255.0
                
                # Expand mask to match image channels if needed
                if img.ndim == 3 and mask.ndim == 2:
                    mask = np.expand_dims(mask, axis=2)
                
                # Blend: result = filtered * mask + original * (1 - mask)
                filtered_img = (filtered_img * mask + img * (1 - mask)).astype(img.dtype)
                self.logger.info(f"  ✓ Applied selective denoising mask")
            
            # Apply optional sharpening to restore structure
            if self.config.output.apply_sharpening:
                from image_filters import apply_unsharp_mask
                import numpy as np
                
                # Apply sharpening
                sharpened_img = apply_unsharp_mask(
                    filtered_img, 
                    radius=self.config.output.sharpen_radius,
                    amount=self.config.output.sharpen_amount,
                    preserve_color=self.config.output.preserve_color
                )
                
                # If mask is present, only sharpen masked areas
                if mask is not None:
                    # Expand mask to match image channels if needed
                    mask_for_sharpen = mask
                    if filtered_img.ndim == 3 and mask_for_sharpen.ndim == 2:
                        mask_for_sharpen = np.expand_dims(mask_for_sharpen, axis=2)
                    
                    # Blend: sharpened in masked areas, original filtered in unmasked areas
                    filtered_img = (sharpened_img * mask_for_sharpen + filtered_img * (1 - mask_for_sharpen)).astype(filtered_img.dtype)
                    sharpen_tag = " [masked areas only]"
                else:
                    filtered_img = sharpened_img
                    sharpen_tag = ""
                
                if self.config.output.preserve_color:
                    sharpen_tag += " [color-preserving]"
                
                self.logger.info(f"  ✓ Applied sharpening (amount={self.config.output.sharpen_amount}, " +
                               f"radius={self.config.output.sharpen_radius}){sharpen_tag}")
            
            # Apply optional saturation boost
            if self.config.output.boost_saturation:
                from image_filters import boost_saturation
                import numpy as np
                
                # Apply saturation boost
                boosted_img = boost_saturation(
                    filtered_img,
                    amount=self.config.output.saturation_amount
                )
                
                # If mask is present, only boost saturation in masked areas
                if mask is not None:
                    # Expand mask to match image channels if needed
                    mask_for_saturation = mask
                    if filtered_img.ndim == 3 and mask_for_saturation.ndim == 2:
                        mask_for_saturation = np.expand_dims(mask_for_saturation, axis=2)
                    
                    # Blend: boosted in masked areas, original filtered in unmasked areas
                    filtered_img = (boosted_img * mask_for_saturation + filtered_img * (1 - mask_for_saturation)).astype(filtered_img.dtype)
                    saturation_tag = " [masked areas only]"
                else:
                    filtered_img = boosted_img
                    saturation_tag = ""
                
                self.logger.info(f"  ✓ Boosted saturation (amount={self.config.output.saturation_amount}){saturation_tag}")
            
            # Apply optional brightness boost
            if self.config.output.boost_brightness:
                from image_filters import boost_brightness
                import numpy as np
                
                # Apply brightness boost
                brightened_img = boost_brightness(
                    filtered_img,
                    amount=self.config.output.brightness_amount
                )
                
                # If mask is present, only boost brightness in masked areas
                if mask is not None:
                    # Expand mask to match image channels if needed
                    mask_for_brightness = mask
                    if filtered_img.ndim == 3 and mask_for_brightness.ndim == 2:
                        mask_for_brightness = np.expand_dims(mask_for_brightness, axis=2)
                    
                    # Blend: brightened in masked areas, original filtered in unmasked areas
                    filtered_img = (brightened_img * mask_for_brightness + filtered_img * (1 - mask_for_brightness)).astype(filtered_img.dtype)
                    brightness_tag = " [masked areas only]"
                else:
                    filtered_img = brightened_img
                    brightness_tag = ""
                
                self.logger.info(f"  ✓ Boosted brightness (amount={self.config.output.brightness_amount}){brightness_tag}")
            
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
            
        except Exception as e:
            # Log filter-specific error
            self.logger.error(f"  ✗ {filter_name.capitalize()} filter failed: {str(e)}")
            
            # Store N/A for failed filter metrics
            metrics_dict[f'{filter_name}_noise_reduction'] = "N/A"
            metrics_dict[f'{filter_name}_psnr'] = "N/A"
            
            # Provide helpful error messages based on error type
            error_msg = str(e).lower()
            if "data type" in error_msg or "dtype" in error_msg:
                self.logger.error(f"    Hint: Image format incompatible with {filter_name} filter")
            elif "memory" in error_msg or "allocation" in error_msg:
                self.logger.error(f"    Hint: Image too large for {filter_name} filter, try reducing size")
            elif "shape" in error_msg or "dimension" in error_msg:
                self.logger.error(f"    Hint: Image dimensions incompatible with {filter_name} filter")
            
            # Don't raise - continue with other filters
