# AMD Radeon GPU Setup for AI Denoising

## Overview

AMD Radeon GPUs can be used for AI denoising through **ROCm** (Radeon Open Compute). However, setup is more complex than NVIDIA GPUs.

## Current Status

The app now detects AMD GPUs, but you need to install PyTorch with ROCm support.

## Requirements

### Supported GPUs:
- AMD Radeon RX 6000 series (RDNA 2)
- AMD Radeon RX 7000 series (RDNA 3)
- AMD Radeon Pro series
- Some older cards (check ROCm compatibility)

### Operating System:
- **Linux**: Full ROCm support ✅
- **Windows**: Limited support (ROCm 5.5+) ⚠️
- **macOS**: Not supported ❌

## Installation

### Option 1: Linux (Recommended)

#### Step 1: Install ROCm
```bash
# Ubuntu/Debian
wget https://repo.radeon.com/amdgpu-install/latest/ubuntu/jammy/amdgpu-install_5.7.50700-1_all.deb
sudo apt install ./amdgpu-install_5.7.50700-1_all.deb
sudo amdgpu-install --usecase=rocm

# Verify installation
rocm-smi
```

#### Step 2: Install PyTorch with ROCm
```bash
# Install core dependencies first
pip install -r requirements.txt

# Install PyTorch with ROCm support
pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm5.7
```

#### Step 3: Verify
```bash
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"
```

If successful, you should see:
```
CUDA available: True
Device: AMD Radeon RX 7900 XTX (or your GPU model)
```

### Option 2: Windows (Limited Support)

**Why AMD GPUs don't work well on Windows:**

AMD's ROCm (the GPU compute platform) has **very limited Windows support**:

1. **ROCm is primarily Linux-only**
   - AMD focuses ROCm development on Linux
   - Windows support is experimental and incomplete
   - Many features don't work on Windows

2. **PyTorch + ROCm on Windows**
   - Official PyTorch doesn't provide ROCm builds for Windows
   - Only CUDA (NVIDIA) and CPU builds available for Windows
   - Community builds exist but are unreliable

3. **DirectML Alternative (Not Recommended)**
   - Microsoft's DirectML can use AMD GPUs on Windows
   - But PyTorch DirectML support is limited
   - Performance is poor compared to ROCm on Linux
   - Not worth the complexity

**Bottom Line for Windows + AMD GPU:**
- ❌ ROCm doesn't work properly on Windows
- ❌ No official PyTorch ROCm builds for Windows
- ✅ **Use CPU mode instead** - it works reliably
- ✅ Or dual-boot Linux for GPU acceleration

#### If You Want to Try Anyway:

```bash
# This will likely NOT work, but you can try:
pip install -r requirements.txt
pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm5.7
```

**Expected result**: Installation may succeed, but GPU won't be detected.

**Recommended**: Just use CPU mode on Windows with AMD GPU.

### Option 3: Use CPU Mode

If ROCm installation is too complex or doesn't work:

1. Install regular PyTorch (CPU version):
   ```bash
   pip install -r requirements-ai.txt
   ```

2. AI denoising will work on CPU (slower but functional)

3. Performance: 30-60 seconds per image (vs 2-5 seconds on GPU)

## Troubleshooting

### "CUDA not available" after ROCm installation

**Check ROCm installation:**
```bash
rocm-smi
```

**Check PyTorch:**
```bash
python -c "import torch; print(torch.__version__); print(torch.version.hip)"
```

Should show ROCm version (e.g., `5.7.0`)

### "No module named 'torch'"

PyTorch not installed. Run:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm5.7
```

### GPU not detected in app

1. Verify ROCm works:
   ```bash
   rocm-smi
   ```

2. Check PyTorch sees GPU:
   ```bash
   python -c "import torch; print(torch.cuda.is_available())"
   ```

3. If both work but app doesn't detect:
   - Restart the application
   - Check logs for errors

### Performance is slow

- Ensure ROCm drivers are up to date
- Check GPU usage: `rocm-smi` (should show activity during processing)
- Some older AMD GPUs may be slower than expected
- Consider using CPU mode if GPU is not faster

## Performance Comparison

| Device | Speed (1920x1080) | Notes |
|--------|------------------|-------|
| AMD RX 7900 XTX | 3-6 seconds | Excellent |
| AMD RX 6800 XT | 4-8 seconds | Very good |
| AMD RX 6600 | 8-15 seconds | Good |
| CPU (Ryzen 9) | 30-60 seconds | Acceptable |

## Compatibility Matrix

### Linux:
| GPU Series | ROCm Support | Status |
|-----------|--------------|--------|
| RX 7000 (RDNA 3) | ROCm 5.7+ | ✅ Excellent |
| RX 6000 (RDNA 2) | ROCm 5.0+ | ✅ Excellent |
| RX 5000 (RDNA) | ROCm 4.5+ | ⚠️ Limited |
| Vega | ROCm 4.0+ | ⚠️ Limited |

### Windows:
| GPU Series | ROCm Support | Status |
|-----------|--------------|--------|
| RX 7000 (RDNA 3) | Experimental | ⚠️ May work |
| RX 6000 (RDNA 2) | Experimental | ⚠️ May work |
| Older | Not supported | ❌ Use CPU |

## Recommended Approach

### For Linux Users with AMD GPU:
1. ✅ Install ROCm
2. ✅ Install PyTorch with ROCm
3. ✅ Enjoy GPU-accelerated AI denoising

### For Windows Users with AMD GPU:
1. ⚠️ Try ROCm installation (may not work)
2. ✅ If fails, use CPU mode
3. ✅ Still get better quality than classical methods

### For All AMD Users:
- AI denoising quality is the same on AMD/NVIDIA/CPU
- Only speed differs
- CPU mode is perfectly usable for occasional use

## Alternative: Use CPU Mode

Don't want to deal with ROCm complexity?

**CPU mode works great:**
- Same quality as GPU
- Just slower (30-60s vs 3-6s)
- No special installation needed
- Works on any system

**To use CPU mode:**
1. Install regular PyTorch:
   ```bash
   pip install -r requirements-ai.txt
   ```
2. Enable AI Denoiser in GUI
3. Accept slower processing time

## Resources

- **ROCm Documentation**: https://rocm.docs.amd.com/
- **PyTorch ROCm**: https://pytorch.org/get-started/locally/
- **ROCm Compatibility**: https://rocm.docs.amd.com/en/latest/release/gpu_os_support.html

## Why This Limitation Exists

**Technical Explanation:**

1. **ROCm Architecture**
   - ROCm is built on Linux kernel drivers
   - Uses Linux-specific APIs and features
   - Windows has different GPU driver architecture

2. **AMD's Focus**
   - AMD prioritizes Linux for compute workloads
   - Data centers and HPC use Linux
   - Gaming (DirectX) is separate from compute (ROCm)

3. **NVIDIA vs AMD on Windows**
   - NVIDIA CUDA: Full Windows support ✅
   - AMD ROCm: Linux only ❌
   - This is why NVIDIA dominates AI/ML on Windows

**Will This Change?**
- AMD is working on Windows support
- But it's been "experimental" for years
- Don't expect full support soon
- Linux is the way to go for AMD GPU compute

## Summary

**Best case**: Linux + RX 6000/7000 series = Fast GPU acceleration ✅

**Windows + AMD GPU**: Use CPU mode = Slower but reliable ✅

**Windows + NVIDIA GPU**: Use CUDA = Fast GPU acceleration ✅

**Always works**: CPU mode = Slower but reliable ✅

### Recommendations by System:

| Your System | Recommendation | Speed |
|-------------|---------------|-------|
| Windows + AMD GPU | Use CPU mode | 30-60s |
| Windows + NVIDIA GPU | Use CUDA | 2-5s |
| Linux + AMD GPU | Use ROCm | 3-8s |
| Linux + NVIDIA GPU | Use CUDA | 2-5s |
| Mac + Apple Silicon | Use MPS | 5-10s |
| Any + No GPU | Use CPU | 30-60s |

Choose the approach that works best for your system!
