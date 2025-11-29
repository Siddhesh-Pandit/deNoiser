# Copyright (c) 2025 Adwait Godbole and Siddhesh Pandit
# Licensed under CC BY-NC 4.0 (Attribution-NonCommercial 4.0 International)
# https://creativecommons.org/licenses/by-nc/4.0/
# For commercial use, please contact the authors.

"""AI-based image denoising using lightweight neural networks."""
import os
import sys
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def is_ai_available():
    """Check if AI denoising dependencies are available.
    
    Returns:
        bool: True if PyTorch is available
    """
    try:
        import torch
        return True
    except ImportError:
        return False


def get_device():
    """Get the best available device (CUDA > ROCm > MPS > CPU).
    
    Returns:
        tuple: (device_name, device_description)
            device_name: 'cuda', 'mps', or 'cpu'
            device_description: Human-readable description
    """
    if not is_ai_available():
        return 'cpu', 'CPU (PyTorch not installed)'
    
    import torch
    
    # Check for NVIDIA CUDA
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        return 'cuda', f'NVIDIA GPU ({device_name})'
    
    # Check for AMD ROCm (uses CUDA API in PyTorch)
    # ROCm-enabled PyTorch reports as CUDA
    try:
        if hasattr(torch.version, 'hip') and torch.version.hip is not None:
            # ROCm detected
            return 'cuda', 'AMD GPU (ROCm)'
    except:
        pass
    
    # Check for Apple Silicon
    if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return 'mps', 'Apple Silicon GPU'
    
    # Fallback to CPU
    return 'cpu', 'CPU'


def get_model_dir():
    """Get directory for storing AI models.
    
    Returns:
        Path: Directory path for models
    """
    model_dir = Path.home() / '.imagedenoiser' / 'models'
    model_dir.mkdir(parents=True, exist_ok=True)
    return model_dir


class AIDenoiser:
    """AI-based image denoiser using lightweight neural networks."""
    
    def __init__(self, model_name='scunet', device=None):
        """Initialize AI denoiser.
        
        Args:
            model_name: Model to use ('scunet' or 'nafnet')
            device: Device to use ('cuda', 'mps', 'cpu', or None for auto)
        """
        if not is_ai_available():
            raise ImportError(
                "PyTorch is not installed. Install AI dependencies:\n"
                "  pip install -r requirements-ai.txt"
            )
        
        import torch
        
        self.model_name = model_name.lower()
        
        if device:
            self.device = device
            self.device_desc = device
        else:
            self.device, self.device_desc = get_device()
        
        self.model = None
        self.model_loaded = False
        
        logger.info(f"AI Denoiser initialized: {model_name} on {self.device_desc}")
    
    def download_model(self, progress_callback=None):
        """Download pre-trained model if not already present.
        
        Args:
            progress_callback: Optional callback(current, total, status_msg)
        
        Returns:
            Path: Path to downloaded model file
        """
        model_dir = get_model_dir()
        
        # Model URLs and filenames
        models = {
            'scunet': {
                'url': 'https://github.com/cszn/KAIR/releases/download/v1.0/scunet_color_real_psnr.pth',
                'filename': 'scunet_color_real_psnr.pth',
                'size_mb': 3.0
            },
            'nafnet': {
                'url': 'https://github.com/megvii-research/NAFNet/releases/download/v1.0/NAFNet-width32.pth',
                'filename': 'nafnet_width32.pth',
                'size_mb': 8.9
            }
        }
        
        if self.model_name not in models:
            raise ValueError(f"Unknown model: {self.model_name}")
        
        model_info = models[self.model_name]
        model_path = model_dir / model_info['filename']
        
        # Check if already downloaded
        if model_path.exists():
            logger.info(f"Model already downloaded: {model_path}")
            if progress_callback:
                progress_callback(100, 100, "Model ready")
            return model_path
        
        # Download model
        logger.info(f"Downloading {self.model_name} model...")
        if progress_callback:
            progress_callback(0, 100, f"Downloading {self.model_name} model...")
        
        try:
            import urllib.request
            
            def report_progress(block_num, block_size, total_size):
                if progress_callback and total_size > 0:
                    downloaded = block_num * block_size
                    percent = min(100, int(downloaded * 100 / total_size))
                    mb_downloaded = downloaded / (1024 * 1024)
                    mb_total = total_size / (1024 * 1024)
                    progress_callback(
                        percent, 100,
                        f"Downloading: {mb_downloaded:.1f}/{mb_total:.1f} MB"
                    )
            
            urllib.request.urlretrieve(
                model_info['url'],
                model_path,
                reporthook=report_progress
            )
            
            logger.info(f"Model downloaded successfully: {model_path}")
            if progress_callback:
                progress_callback(100, 100, "Download complete")
            
            return model_path
            
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            if model_path.exists():
                model_path.unlink()  # Clean up partial download
            raise
    
    def load_model(self, progress_callback=None):
        """Load the AI model into memory.
        
        Args:
            progress_callback: Optional callback(current, total, status_msg)
        """
        if self.model_loaded:
            return
        
        import torch
        
        # Download model if needed
        model_path = self.download_model(progress_callback)
        
        if progress_callback:
            progress_callback(0, 100, "Loading model...")
        
        try:
            if self.model_name == 'scunet':
                self.model = self._load_scunet(model_path)
            elif self.model_name == 'nafnet':
                self.model = self._load_nafnet(model_path)
            else:
                raise ValueError(f"Unknown model: {self.model_name}")
            
            self.model.to(self.device)
            self.model.eval()
            self.model_loaded = True
            
            logger.info(f"Model loaded successfully on {self.device}")
            if progress_callback:
                progress_callback(100, 100, "Model ready")
                
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def _load_scunet(self, model_path):
        """Load SCUNet model architecture and weights."""
        from ai_models import load_scunet_model
        return load_scunet_model(model_path, device=self.device)
    
    def _load_nafnet(self, model_path):
        """Load NAFNet model architecture and weights."""
        from ai_models import load_nafnet_model
        return load_nafnet_model(model_path, device=self.device)
    
    def denoise(self, image, progress_callback=None):
        """Denoise an image using AI.
        
        Args:
            image: Input image array (uint8 or uint16, RGB or grayscale)
            progress_callback: Optional callback(current, total, status_msg)
        
        Returns:
            Denoised image array (same dtype as input)
        """
        if not self.model_loaded:
            self.load_model(progress_callback)
        
        import torch
        
        if progress_callback:
            progress_callback(0, 100, "Preparing image...")
        
        # Store original properties
        original_dtype = image.dtype
        original_shape = image.shape
        
        # Convert to float32 [0, 1]
        if image.dtype == np.uint8:
            img_float = image.astype(np.float32) / 255.0
        elif image.dtype == np.uint16:
            img_float = image.astype(np.float32) / 65535.0
        else:
            img_float = image.astype(np.float32)
        
        # Handle grayscale
        if img_float.ndim == 2:
            img_float = np.expand_dims(img_float, axis=2)
            was_grayscale = True
        else:
            was_grayscale = False
        
        if progress_callback:
            progress_callback(20, 100, "Running AI denoiser...")
        
        try:
            # Convert to tensor: (H, W, C) -> (1, C, H, W)
            img_tensor = torch.from_numpy(img_float).permute(2, 0, 1).unsqueeze(0)
            img_tensor = img_tensor.to(self.device)
            
            # Run inference
            with torch.no_grad():
                output_tensor = self.model(img_tensor)
            
            # Convert back: (1, C, H, W) -> (H, W, C)
            output = output_tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
            
            # Clip to valid range
            output = np.clip(output, 0, 1)
            
            if progress_callback:
                progress_callback(80, 100, "Converting result...")
            
            # Remove channel dimension if was grayscale
            if was_grayscale:
                output = output[:, :, 0]
            
            # Convert back to original dtype
            if original_dtype == np.uint8:
                output = (output * 255 + 0.5).astype(np.uint8)
            elif original_dtype == np.uint16:
                output = (output * 65535 + 0.5).astype(np.uint16)
            
            if progress_callback:
                progress_callback(100, 100, "AI denoising complete")
            
            return output
            
        except Exception as e:
            logger.error(f"AI denoising failed: {e}")
            raise


def denoise_with_ai(image, model_name='scunet', device=None, progress_callback=None):
    """Convenience function to denoise an image with AI.
    
    Args:
        image: Input image array
        model_name: Model to use ('scunet' or 'nafnet')
        device: Device to use (None for auto-detect)
        progress_callback: Optional callback(current, total, status_msg)
    
    Returns:
        Denoised image array
    """
    denoiser = AIDenoiser(model_name=model_name, device=device)
    return denoiser.denoise(image, progress_callback=progress_callback)
