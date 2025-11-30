"""Quick test to check if AI denoising works."""
import sys

print("Testing AI denoising...")
print()

# Test 1: Check if PyTorch is available
print("1. Checking PyTorch...")
try:
    import torch
    print(f"   ✓ PyTorch {torch.__version__} installed")
except ImportError as e:
    print(f"   ✗ PyTorch not installed: {e}")
    sys.exit(1)

# Test 2: Check if ai_denoiser module works
print("2. Checking ai_denoiser module...")
try:
    from ai_denoiser import is_ai_available, AIDenoiser
    print(f"   ✓ ai_denoiser module loaded")
except ImportError as e:
    print(f"   ✗ Failed to import ai_denoiser: {e}")
    sys.exit(1)

# Test 3: Check if AI is available
print("3. Checking AI availability...")
if is_ai_available():
    print("   ✓ AI is available")
else:
    print("   ✗ AI is not available")
    sys.exit(1)

# Test 4: Try to create AI denoiser
print("4. Creating AI denoiser...")
try:
    denoiser = AIDenoiser(model_name='scunet', device='cpu')
    print("   ✓ AI denoiser created")
except Exception as e:
    print(f"   ✗ Failed to create AI denoiser: {e}")
    sys.exit(1)

# Test 5: Try to load model
print("5. Loading AI model (this may take a while)...")
try:
    denoiser.load_model(progress_callback=lambda c, t, m: print(f"   {m}"))
    print("   ✓ Model loaded successfully")
except Exception as e:
    print(f"   ✗ Failed to load model: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("✓ All tests passed! AI denoising should work.")
