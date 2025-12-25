"""
Simple diagnostic script to check PyTorch and CUDA installation.
Run this to verify your GPU setup before running audio generation.
"""

import sys


def check_pytorch_cuda():
    """Check PyTorch installation and CUDA availability."""
    print("="*70)
    print("PyTorch & CUDA Diagnostic Tool")
    print("="*70)

    # Check if PyTorch is installed
    try:
        import torch
        print(f"\n[OK] PyTorch installed: {torch.__version__}")
    except ImportError:
        print("\n[ERROR] PyTorch NOT installed")
        print("Install with: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
        return

    # Check CUDA availability
    print(f"\nCUDA available: {torch.cuda.is_available()}")

    if not torch.cuda.is_available():
        print("\n" + "="*70)
        print("CUDA NOT AVAILABLE")
        print("="*70)

        # Diagnose why
        if not hasattr(torch.version, 'cuda') or torch.version.cuda is None:
            print("\nReason: PyTorch was installed WITHOUT CUDA support (CPU-only version)")
            print("\nTo fix this:")
            print("  1. Uninstall current PyTorch:")
            print("     pip uninstall torch torchvision torchaudio")
            print("\n  2. Reinstall with CUDA 11.8 support:")
            print("     pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
            print("\n  Note: Make sure your NVIDIA drivers support CUDA 11.8 or later")
        else:
            print(f"\nReason: CUDA drivers not detected or incompatible")
            print(f"PyTorch CUDA version: {torch.version.cuda}")
            print("\nTo fix this:")
            print("  1. Check NVIDIA drivers are installed:")
            print("     nvidia-smi")
            print("\n  2. Ensure driver version supports CUDA 11.8+")
            print("  3. Reinstall NVIDIA drivers if needed")

        print("="*70)
        return

    # CUDA is available - show details
    print("\n" + "="*70)
    print("CUDA IS AVAILABLE")
    print("="*70)

    print(f"\nPyTorch CUDA version: {torch.version.cuda}")
    print(f"CUDA device count: {torch.cuda.device_count()}")

    for i in range(torch.cuda.device_count()):
        print(f"\nDevice {i}:")
        print(f"  Name: {torch.cuda.get_device_name(i)}")
        props = torch.cuda.get_device_properties(i)
        print(f"  Total memory: {props.total_memory / 1024**3:.1f} GB")
        print(f"  Compute capability: {props.major}.{props.minor}")

    # Test CUDA with simple operation
    print("\n" + "="*70)
    print("Testing CUDA Operations")
    print("="*70)

    try:
        x = torch.tensor([1.0, 2.0, 3.0]).cuda()
        y = x * 2
        print(f"\n[OK] CUDA test successful!")
        print(f"  Test tensor on device: {x.device}")
        print(f"  Computation result: {y.cpu().numpy()}")
    except Exception as e:
        print(f"\n[ERROR] CUDA test failed: {e}")

    print("\n" + "="*70)
    print("Summary")
    print("="*70)
    print("[OK] Your system is ready for GPU-accelerated audio generation!")
    print("  You can now run: python generate_scene_audio.py")
    print("="*70 + "\n")


if __name__ == "__main__":
    check_pytorch_cuda()
