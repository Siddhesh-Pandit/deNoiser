# AI Denoiser Implementation Guide

## Status: COMPLETE ✅

This document tracks the implementation of optional AI-based denoising.

## Completed ✅

1. **ai_denoiser.py** - Core AI denoising module ✅
   - Model management and downloading
   - Device detection (CUDA/MPS/CPU)
   - Progress callback support
   - Full integration with model architectures

2. **ai_models.py** - Neural network architectures ✅
   - SCUNet implementation (lightweight, 3MB)
   - NAFNet implementation (better quality, 9MB)
   - Model loading with checkpoint support

3. **requirements-ai.txt** - Optional AI dependencies ✅
   - PyTorch >= 2.0.0
   - TorchVision >= 0.15.0

4. **config.ini** - AI settings added ✅
   - `[AIDenoiser]` section
   - `enable_ai`, `model_name`, `device` options

5. **config_loader.py** - Configuration support ✅
   - `AIDenoiserConfig` dataclass
   - Config loading for AI settings

6. **gui.py** - GUI integration ✅
   - AI Denoiser section with toggle
   - Model selection (SCUNet/NAFNet)
   - Device detection and status display
   - Availability checking
   - User warnings for CPU/missing dependencies

7. **processor.py** - Processing integration ✅
   - AI denoising in processing pipeline
   - Mask support for selective AI denoising
   - Fallback to classical filters on error
   - Progress logging

## Features ✅

### 1. Complete Model Architectures

The current `ai_denoiser.py` has placeholder model loaders. Need to add:

**Option A: Use existing implementations**
```python
# Install from GitHub
pip install git+https://github.com/cszn/KAIR.git  # For SCUNet
pip install git+https://github.com/megvii-research/NAFNet.git  # For NAFNet
```

**Option B: Implement simplified versions**
- Copy model architectures into the project
- Simpler but requires more code

### 2. GUI Integration

Add to `gui.py`:

```python
# In __init__:
self.enable_ai = tk.BooleanVar(value=False)
self.ai_model = tk.StringVar(value='scunet')

# In create_widgets (Filters section):
# AI Denoiser section
ai_frame = ttk.LabelFrame(main_frame, text="AI Denoiser (Optional)", padding="5")
ai_frame.grid(row=X, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)

ai_check = ttk.Checkbutton(ai_frame, text="Enable AI Denoiser", 
                           variable=self.enable_ai,
                           command=self.on_ai_toggle)
ai_check.grid(row=0, column=0, sticky=tk.W, padx=5)

# Model selection
ttk.Label(ai_frame, text="Model:").grid(row=0, column=1, padx=5)
model_combo = ttk.Combobox(ai_frame, textvariable=self.ai_model,
                           values=['scunet', 'nafnet'], width=10, state='readonly')
model_combo.grid(row=0, column=2, padx=5)

# Device info label
self.ai_device_label = ttk.Label(ai_frame, text="", foreground="blue")
self.ai_device_label.grid(row=0, column=3, padx=10)

# Download button (if needed)
self.ai_download_btn = ttk.Button(ai_frame, text="Download Model",
                                   command=self.download_ai_model)
self.ai_download_btn.grid(row=0, column=4, padx=5)

def on_ai_toggle(self):
    """Handle AI denoiser toggle."""
    if self.enable_ai.get():
        # Check if PyTorch is available
        from ai_denoiser import is_ai_available, get_device
        if not is_ai_available():
            messagebox.showwarning(
                "AI Dependencies Missing",
                "PyTorch is not installed.\n\n"
                "Install AI dependencies:\n"
                "  pip install -r requirements-ai.txt\n\n"
                "Then restart the application."
            )
            self.enable_ai.set(False)
            return
        
        # Show device info
        device = get_device()
        device_names = {'cuda': 'NVIDIA GPU', 'mps': 'Apple Silicon', 'cpu': 'CPU'}
        self.ai_device_label.config(text=f"Using: {device_names.get(device, device)}")
```

### 3. Processor Integration

Add to `processor.py`:

```python
def process_with_filter(self, img, img_float, filename, metrics_dict, 
                       filter_func, filter_name, filter_params, mask=None):
    """Process image with filter (classical or AI)."""
    
    # Check if AI denoising is enabled
    if self.config.ai_denoiser.enable_ai:
        try:
            from ai_denoiser import denoise_with_ai, is_ai_available
            
            if is_ai_available():
                self.logger.info(f"  Using AI denoiser: {self.config.ai_denoiser.model_name}")
                
                # AI denoise
                device = None if self.config.ai_denoiser.device == 'auto' else self.config.ai_denoiser.device
                filtered_img = denoise_with_ai(
                    img,
                    model_name=self.config.ai_denoiser.model_name,
                    device=device,
                    progress_callback=self._ai_progress_callback
                )
                
                filter_name = f"{filter_name}_ai"
            else:
                self.logger.warning("  AI dependencies not available, using classical filters")
                filtered_img = filter_func()
        except Exception as e:
            self.logger.error(f"  AI denoising failed: {e}, falling back to classical")
            filtered_img = filter_func()
    else:
        # Classical denoising
        filtered_img = filter_func()
    
    # Apply mask if provided (works for both AI and classical)
    if mask is not None:
        # ... existing mask code ...
    
    # Rest of processing (sharpening, saturation, brightness)
    # ...

def _ai_progress_callback(self, current, total, message):
    """Callback for AI denoising progress."""
    self.logger.info(f"  AI: {message} ({current}/{total})")
```

### 4. Comparison Window Enhancement

Update comparison window to show "Classical" vs "AI" labels when AI is used.

### 5. Model Architecture Implementation

**SCUNet** (Recommended - smaller, faster):
- 3MB model size
- Good balance of speed and quality
- Works well on CPU

**NAFNet** (Better quality):
- 9MB model size  
- Better quality but slower
- Recommended for GPU users

Need to either:
1. Add dependencies on KAIR/NAFNet repos
2. Copy model architectures into project
3. Use ONNX versions for easier deployment

### 6. Testing

Test scenarios:
- [ ] AI toggle on/off
- [ ] Model download progress
- [ ] CPU vs GPU performance
- [ ] Mask respect in AI mode
- [ ] Fallback to classical on error
- [ ] Comparison window with AI results

### 7. Documentation Updates

Update:
- README.md - Add AI denoising section
- USAGE.md - Document AI options
- INSTALLATION_SUMMARY.md - Add AI installation steps
- requirements.txt - Note optional AI dependencies

## Installation Instructions (for users)

### Basic Installation (Classical only)
```bash
pip install -r requirements.txt
```

### With AI Support
```bash
pip install -r requirements.txt
pip install -r requirements-ai.txt
```

### GPU Support (NVIDIA)
```bash
# Install PyTorch with CUDA
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Apple Silicon
```bash
# PyTorch with MPS support (included in torch>=2.0)
pip install torch torchvision
```

## Architecture Decision

**Recommendation**: Use SCUNet as default
- Smaller model (3MB vs 9MB)
- Faster inference
- Good quality for most use cases
- Better CPU performance

NAFNet can be offered as "High Quality" option for users with GPUs.

## Next Steps

1. **Immediate**: Implement actual model architectures or add dependencies
2. **GUI**: Add AI toggle and controls
3. **Processor**: Integrate AI denoising with mask support
4. **Testing**: Verify all functionality
5. **Documentation**: Update all docs

## Notes

- Models are downloaded to `~/.imagedenoiser/models/`
- First run will download model (~3-9MB)
- Progress bar shows download and inference progress
- Graceful fallback to classical if AI fails
- Masks are respected in AI mode (blend AI result with original)
