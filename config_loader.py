"""Configuration management for image denoising."""
import configparser
import os
import logging
from dataclasses import dataclass


@dataclass
class OutputConfig:
    """Output settings configuration."""
    format: str
    jpeg_quality: int
    preserve_original_format: bool


@dataclass
class FilterConfig:
    """Filter enable/disable configuration."""
    enable_gaussian: bool
    enable_median: bool
    enable_nonlocal: bool


@dataclass
class GaussianConfig:
    """Gaussian filter parameters."""
    sigma: float


@dataclass
class MedianConfig:
    """Median filter parameters."""
    size: int


@dataclass
class NonLocalMeansConfig:
    """Non-local means filter parameters."""
    h_multiplier: float
    fast_mode: bool
    patch_size: int
    patch_distance: int


@dataclass
class DenoiserConfig:
    """Complete denoiser configuration."""
    input_path: str
    output_path: str
    output: OutputConfig
    filters: FilterConfig
    gaussian: GaussianConfig
    median: MedianConfig
    nonlocal: NonLocalMeansConfig


def load_config(config_path='config.ini'):
    """Load and parse configuration file.
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        DenoiserConfig object with all settings
    
    Raises:
        FileNotFoundError: If config file doesn't exist
        configparser.Error: If config file is malformed
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    # Load paths
    input_path = config.get('Paths', 'input_file_path')
    output_path = config.get('Paths', 'output_file_path')
    
    # Load output settings
    output = OutputConfig(
        format=config.get('Output', 'format', fallback='png'),
        jpeg_quality=config.getint('Output', 'jpeg_quality', fallback=95),
        preserve_original_format=config.getboolean('Output', 'preserve_original_format', fallback=False)
    )
    
    # Load filter toggles
    filters = FilterConfig(
        enable_gaussian=config.getboolean('Filters', 'enable_gaussian', fallback=True),
        enable_median=config.getboolean('Filters', 'enable_median', fallback=True),
        enable_nonlocal=config.getboolean('Filters', 'enable_nonlocal', fallback=True)
    )
    
    # Load filter parameters
    gaussian = GaussianConfig(
        sigma=config.getfloat('GaussianFilter', 'sigma', fallback=0.75)
    )
    
    median = MedianConfig(
        size=config.getint('MedianFilter', 'size', fallback=3)
    )
    
    nonlocal = NonLocalMeansConfig(
        h_multiplier=config.getfloat('NonLocalMeans', 'h_multiplier', fallback=1.15),
        fast_mode=config.getboolean('NonLocalMeans', 'fast_mode', fallback=True),
        patch_size=config.getint('NonLocalMeans', 'patch_size', fallback=5),
        patch_distance=config.getint('NonLocalMeans', 'patch_distance', fallback=6)
    )
    
    return DenoiserConfig(
        input_path=input_path,
        output_path=output_path,
        output=output,
        filters=filters,
        gaussian=gaussian,
        median=median,
        nonlocal=nonlocal
    )
