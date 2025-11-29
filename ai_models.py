# Copyright (c) 2025 Adwait Godbole and Siddhesh Pandit
# Licensed under CC BY-NC 4.0 (Attribution-NonCommercial 4.0 International)
# https://creativecommons.org/licenses/by-nc/4.0/
# For commercial use, please contact the authors.

"""Neural network architectures for AI denoising."""
import torch
import torch.nn as nn
import torch.nn.functional as F


class SCUNet(nn.Module):
    """Simplified SCUNet architecture for image denoising.
    
    SCUNet (Swin-Conv-UNet) is a lightweight denoising network that combines
    convolutional layers with attention mechanisms.
    """
    
    def __init__(self, in_channels=3, out_channels=3, num_features=48):
        """Initialize SCUNet.
        
        Args:
            in_channels: Number of input channels (3 for RGB, 1 for grayscale)
            out_channels: Number of output channels
            num_features: Number of features in intermediate layers
        """
        super(SCUNet, self).__init__()
        
        # Encoder
        self.conv_first = nn.Conv2d(in_channels, num_features, 3, 1, 1)
        
        self.encoder1 = self._make_layer(num_features, num_features, 2)
        self.down1 = nn.Conv2d(num_features, num_features * 2, 3, 2, 1)
        
        self.encoder2 = self._make_layer(num_features * 2, num_features * 2, 2)
        self.down2 = nn.Conv2d(num_features * 2, num_features * 4, 3, 2, 1)
        
        # Bottleneck
        self.bottleneck = self._make_layer(num_features * 4, num_features * 4, 2)
        
        # Decoder
        self.up2 = nn.ConvTranspose2d(num_features * 4, num_features * 2, 2, 2)
        self.decoder2 = self._make_layer(num_features * 4, num_features * 2, 2)
        
        self.up1 = nn.ConvTranspose2d(num_features * 2, num_features, 2, 2)
        self.decoder1 = self._make_layer(num_features * 2, num_features, 2)
        
        # Output
        self.conv_last = nn.Conv2d(num_features, out_channels, 3, 1, 1)
    
    def _make_layer(self, in_channels, out_channels, num_blocks):
        """Create a sequence of residual blocks."""
        layers = []
        for _ in range(num_blocks):
            layers.append(ResidualBlock(in_channels, out_channels))
            in_channels = out_channels
        return nn.Sequential(*layers)
    
    def forward(self, x):
        """Forward pass.
        
        Args:
            x: Input tensor (B, C, H, W)
        
        Returns:
            Denoised tensor (B, C, H, W)
        """
        # Store input for residual connection
        identity = x
        
        # Encoder
        x1 = self.conv_first(x)
        x1 = self.encoder1(x1)
        
        x2 = self.down1(x1)
        x2 = self.encoder2(x2)
        
        x3 = self.down2(x2)
        
        # Bottleneck
        x3 = self.bottleneck(x3)
        
        # Decoder with skip connections
        x = self.up2(x3)
        x = torch.cat([x, x2], dim=1)
        x = self.decoder2(x)
        
        x = self.up1(x)
        x = torch.cat([x, x1], dim=1)
        x = self.decoder1(x)
        
        # Output with residual connection
        x = self.conv_last(x)
        x = x + identity
        
        return x


class ResidualBlock(nn.Module):
    """Residual block with two convolutional layers."""
    
    def __init__(self, in_channels, out_channels):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, 1, 1)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, 1, 1)
        
        # Adjust channels if needed
        self.shortcut = nn.Identity()
        if in_channels != out_channels:
            self.shortcut = nn.Conv2d(in_channels, out_channels, 1, 1, 0)
    
    def forward(self, x):
        identity = self.shortcut(x)
        
        out = self.conv1(x)
        out = self.relu(out)
        out = self.conv2(out)
        
        out = out + identity
        out = self.relu(out)
        
        return out


class NAFNet(nn.Module):
    """Simplified NAFNet (Nonlinear Activation Free Network) for denoising.
    
    NAFNet uses simple operations without complex activations for efficiency.
    """
    
    def __init__(self, in_channels=3, out_channels=3, width=32, num_blocks=8):
        """Initialize NAFNet.
        
        Args:
            in_channels: Number of input channels
            out_channels: Number of output channels
            width: Channel width
            num_blocks: Number of NAF blocks
        """
        super(NAFNet, self).__init__()
        
        self.intro = nn.Conv2d(in_channels, width, 3, 1, 1)
        
        self.blocks = nn.ModuleList([
            NAFBlock(width) for _ in range(num_blocks)
        ])
        
        self.outro = nn.Conv2d(width, out_channels, 3, 1, 1)
    
    def forward(self, x):
        """Forward pass."""
        identity = x
        
        x = self.intro(x)
        
        for block in self.blocks:
            x = block(x)
        
        x = self.outro(x)
        x = x + identity
        
        return x


class NAFBlock(nn.Module):
    """NAF Block - simple gated block without complex activations."""
    
    def __init__(self, channels):
        super(NAFBlock, self).__init__()
        
        self.conv1 = nn.Conv2d(channels, channels * 2, 1)
        self.conv2 = nn.Conv2d(channels, channels, 3, 1, 1)
        self.conv3 = nn.Conv2d(channels, channels, 1)
        
        self.norm = nn.GroupNorm(1, channels)
    
    def forward(self, x):
        identity = x
        
        x = self.norm(x)
        x = self.conv1(x)
        
        # Simple gating
        x1, x2 = torch.chunk(x, 2, dim=1)
        x = x1 * x2
        
        x = self.conv2(x)
        x = self.conv3(x)
        
        return x + identity


def load_scunet_model(model_path, device='cpu'):
    """Load SCUNet model from checkpoint.
    
    Args:
        model_path: Path to model checkpoint
        device: Device to load model on
    
    Returns:
        Loaded model
    """
    model = SCUNet(in_channels=3, out_channels=3, num_features=48)
    
    try:
        checkpoint = torch.load(model_path, map_location=device)
        
        # Handle different checkpoint formats
        if isinstance(checkpoint, dict):
            if 'model' in checkpoint:
                state_dict = checkpoint['model']
            elif 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            elif 'params' in checkpoint:
                state_dict = checkpoint['params']
            else:
                state_dict = checkpoint
        else:
            state_dict = checkpoint
        
        # Load state dict
        model.load_state_dict(state_dict, strict=False)
    except Exception as e:
        # If loading fails, use untrained model (will still denoise somewhat)
        print(f"Warning: Could not load pretrained weights: {e}")
        print("Using randomly initialized model (results will be poor)")
    
    model.eval()
    return model


def load_nafnet_model(model_path, device='cpu'):
    """Load NAFNet model from checkpoint.
    
    Args:
        model_path: Path to model checkpoint
        device: Device to load model on
    
    Returns:
        Loaded model
    """
    model = NAFNet(in_channels=3, out_channels=3, width=32, num_blocks=8)
    
    try:
        checkpoint = torch.load(model_path, map_location=device)
        
        # Handle different checkpoint formats
        if isinstance(checkpoint, dict):
            if 'model' in checkpoint:
                state_dict = checkpoint['model']
            elif 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            elif 'params' in checkpoint:
                state_dict = checkpoint['params']
            else:
                state_dict = checkpoint
        else:
            state_dict = checkpoint
        
        model.load_state_dict(state_dict, strict=False)
    except Exception as e:
        print(f"Warning: Could not load pretrained weights: {e}")
        print("Using randomly initialized model (results will be poor)")
    
    model.eval()
    return model
