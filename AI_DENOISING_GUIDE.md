# AI Denoising User Guide

## What is AI Denoising?

AI denoising uses neural networks (deep learning) to remove noise from images. It provides better quality than classical methods, especially for:
- Heavy noise (high ISO photos)
- Low-light images
- Preserving fine details and textures

## Installation

### Method 1: In-GUI Installation (Easiest) ⭐

**Initial Installation:**
1. Install basic dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the GUI:
   ```bash
   python gui.py
   ```

3. Enable "AI Denoiser 🤖" checkbox

4. Click "Yes" when prompted to install AI dependencies

5. Wait for installation to complete (~500MB download)

6. Restart the application

**Adding GPU Support Later:**
1. Click **"⚙️ Update PyTorch"** button in the AI Denoiser section

2. Select your hardware:
   - CPU Only (works everywhere)
   - NVIDIA GPU (CUDA) - for GeForce/RTX
   - AMD GPU (ROCm) - for Radeon RX 6000/7000 (Linux)
   - Apple Silicon - for M1/M2/M3 Macs

3. Click "Install" and wait

4. Restart the application

5. GPU will be automatically detected!

### Method 2: Installation Scripts

**Windows**:
```bash
# Install everything (will prompt for AI)
install_dependencies.bat

# Or install AI separately
install_ai.bat
```

**Mac/Linux**:
```bash
# Install everything (will prompt for AI)
./install_dependencies.sh

# Or install AI separately
./install_ai.sh
```

### Method 3: Manual Installation

**Basic + AI**:
```bash
pip install -r requirements.txt
pip install -r requirements-ai.txt
```

**Note**: AI dependencies add ~500MB-1GB (PyTorch)

### GPU Support (Optional but Recommended)

**NVIDIA GPU (CUDA)**:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**AMD GPU (ROCm)** - Linux only:
```bash
# See AMD_GPU_SETUP.md for detailed instructions
pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm5.7
```

**Apple Silicon (M1/M2/M3)**:
```bash
pip install torch torchvision
# MPS support is automatic in PyTorch 2.0+
```

**Note**: AMD GPU support requires ROCm. See `AMD_GPU_SETUP.md` for details.

## Using AI Denoising

### In the GUI

1. **Enable AI Denoiser**:
   - Check "Enable AI Denoiser 🤖" in the Filters section
   - First use will download the model (~3-9MB)

2. **Choose Model**:
   - **SCUNet** (Recommended): Faster, 3MB, good quality
   - **NAFNet**: Slower, 9MB, better quality

3. **Check Device**:
   - Status shows: "✓ Available (NVIDIA GPU/AMD GPU/Apple Silicon GPU/CPU)"
   - GPU is much faster than CPU

4. **Update PyTorch** (if needed):
   - Click "⚙️ Update PyTorch" to change GPU support
   - Useful if you:
     - Installed CPU version but have a GPU
     - Upgraded your GPU
     - Want to switch between CUDA/ROCm versions

5. **Process Images**:
   - Works like classical methods
   - Progress shows AI denoising steps
   - Results saved with `_ai` suffix

### Performance

| Device | Speed (per image) | Quality |
|--------|------------------|---------|
| NVIDIA GPU | 2-5 seconds | Excellent |
| AMD GPU (ROCm) | 3-8 seconds | Excellent |
| Apple Silicon | 5-10 seconds | Excellent |
| CPU | 30-60 seconds | Excellent |

**Note**: AMD GPU requires ROCm installation (Linux). See `AMD_GPU_SETUP.md`.

### Tips

1. **Disable Classical Filters**: AI works best alone
   - GUI will prompt you to disable Gaussian/Median/Non-local Means
   
2. **Use with Masks**: AI respects selective denoising masks
   - Edit mask → Paint areas → AI denoises only masked areas

3. **Post-Processing**: Sharpening and saturation boost work with AI
   - Enable sharpening to restore structure
   - Boost saturation if colors look dull

4. **Compare Results**: Use comparison window
   - Process with classical methods
   - Process with AI
   - Compare side-by-side

## Troubleshooting

### "PyTorch not installed"
```bash
pip install -r requirements-ai.txt
```
Then restart the application.

### "AI denoising failed"
- Check if model downloaded successfully
- Models stored in: `~/.imagedenoiser/models/`
- Try deleting models and re-downloading
- Check logs for specific error

### Slow on CPU
- This is normal - AI is compute-intensive
- Consider using GPU or classical methods
- SCUNet is faster than NAFNet on CPU

### Out of Memory (GPU)
- Reduce image size before processing
- Use CPU instead (slower but works)
- Close other GPU-using applications

## Model Details

### SCUNet (Recommended)
- **Size**: 3MB
- **Speed**: Fast
- **Quality**: Very good
- **Best for**: General use, CPU users, quick processing

### NAFNet
- **Size**: 9MB  
- **Speed**: Slower
- **Quality**: Excellent
- **Best for**: GPU users, maximum quality, important photos

## When to Use AI vs Classical

### Use AI When:
- ✅ Heavy noise (ISO 3200+)
- ✅ Low-light photos
- ✅ Need maximum quality
- ✅ Have GPU available
- ✅ Processing important photos

### Use Classical When:
- ✅ Light to moderate noise
- ✅ Need fast processing
- ✅ Batch processing many images
- ✅ No GPU available
- ✅ Quick edits

## Examples

### Example 1: Night Photo
```
Settings:
- Enable AI Denoiser: ✓
- Model: SCUNet
- Sharpening: ✓ (amount: 0.8)
- Brightness: ✓ (amount: 1.1)

Result: Clean image with preserved stars and details
```

### Example 2: Portrait with Selective Denoising
```
Settings:
- Enable AI Denoiser: ✓
- Model: NAFNet
- Edit Mask: Paint face/skin areas
- Sharpening: ✓ (amount: 0.5)

Result: Smooth skin, sharp eyes and hair
```

### Example 3: Landscape
```
Settings:
- Enable AI Denoiser: ✓
- Model: SCUNet
- Preserve Color: ✓
- Saturation: ✓ (amount: 1.2)

Result: Clean sky, detailed foliage, vibrant colors
```

## FAQ

**Q: Do I need a GPU?**
A: No, but it's much faster. CPU works but takes longer.

**Q: Can I use AI with masks?**
A: Yes! AI respects selective denoising masks.

**Q: Which model is better?**
A: SCUNet for speed, NAFNet for quality. Try both!

**Q: Does AI work offline?**
A: Yes, after initial model download.

**Q: Can I use AI with classical filters?**
A: Not recommended. AI works best alone.

**Q: How much RAM/VRAM needed?**
A: ~2GB RAM for CPU, ~1GB VRAM for GPU.

## Support

For issues or questions:
1. Check logs in the GUI
2. See AI_DENOISER_IMPLEMENTATION.md for technical details
3. Report issues on GitHub
