# check_cuda.py

import torch
import os
import subprocess

print("=" * 60)
print("CUDA DIAGNOSTIC TOOL")
print("=" * 60)

# 1. Check PyTorch CUDA
print("\n[1] PyTorch CUDA Info:")
print(f"    PyTorch Version: {torch.__version__}")
print(f"    CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"    CUDA Version (PyTorch): {torch.version.cuda}")
    print(f"    cuDNN Version: {torch.backends.cudnn.version()}")
    print(f"    GPU Count: {torch.cuda.device_count()}")
    print(f"    GPU Name: {torch.cuda.get_device_name(0)}")
else:
    print("    ✗ CUDA not available in PyTorch!")

# 2. Check NVIDIA-SMI
print("\n[2] NVIDIA Driver Info:")
try:
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
    print(result.stdout)
except Exception as e:
    print(f"    ✗ nvidia-smi not found: {e}")

# 3. Check CUDA Toolkit
print("\n[3] CUDA Toolkit Paths:")
cuda_paths = [
    "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA",
    "C:\\Program Files\\NVIDIA\\CUDNN",
]

for base_path in cuda_paths:
    if os.path.exists(base_path):
        print(f"    ✓ Found: {base_path}")
        for item in os.listdir(base_path):
            full_path = os.path.join(base_path, item)
            if os.path.isdir(full_path):
                print(f"      → {item}")
    else:
        print(f"    ✗ Not found: {base_path}")

# 4. Check DLL Paths
print("\n[4] Checking for CUDA DLLs:")
dll_paths = [
    "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.6\\bin",
    "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v12.1\\bin",
    "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v11.8\\bin",
    "C:\\Program Files\\NVIDIA\\CUDNN\\v9.6\\bin\\13.0",
    "C:\\Program Files\\NVIDIA\\CUDNN\\v9.6\\bin",
    "C:\\Program Files\\NVIDIA\\CUDNN\\v9\\bin",
    "C:\\Program Files\\NVIDIA\\CUDNN\\v8\\bin",
]

found_paths = []
for path in dll_paths:
    if os.path.exists(path):
        dll_count = len([f for f in os.listdir(path) if f.endswith('.dll')])
        print(f"    ✓ {path} ({dll_count} DLLs)")
        found_paths.append(path)
    else:
        print(f"    ✗ {path}")

# 5. Recommendations
print("\n" + "=" * 60)
print("RECOMMENDATIONS:")
print("=" * 60)

if not torch.cuda.is_available():
    print("\n⚠️  PyTorch cannot detect CUDA!")
    print("\nSOLUTION:")
    print("1. Uninstall current PyTorch:")
    print("   pip uninstall torch torchaudio -y")
    print("\n2. Install PyTorch with CUDA 11.8:")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118")
    print("\n   OR with CUDA 12.1:")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121")

if found_paths:
    print(f"\n✓ Found {len(found_paths)} CUDA/CUDNN path(s)")
    print("\nAdd these to device_manager.py:")
    print("cuda_paths = [")
    for path in found_paths:
        print(f'    "{path}",')
    print("]")
else:
    print("\n✗ No CUDA/CUDNN paths found!")
    print("\nYou need to install:")
    print("1. CUDA Toolkit: https://developer.nvidia.com/cuda-downloads")
    print("2. cuDNN: https://developer.nvidia.com/cudnn")

print("\n" + "=" * 60)