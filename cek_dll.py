# find_cuda_dlls.py

import os
import glob

print("=" * 60)
print("FINDING CUDA DLL FILES")
print("=" * 60)

base_paths = [
    "C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v13.0",
    "C:\\Program Files\\NVIDIA\\CUDNN\\v9.16",
]

found_dll_paths = []

for base in base_paths:
    print(f"\n📁 Checking: {base}")
    
    if not os.path.exists(base):
        print(f"   ✗ Path not found!")
        continue
    
    # Search for bin folders
    for root, dirs, files in os.walk(base):
        if 'bin' in os.path.basename(root).lower():
            dll_files = [f for f in files if f.endswith('.dll')]
            
            if dll_files:
                print(f"   ✓ Found {len(dll_files)} DLLs in: {root}")
                found_dll_paths.append(root)
                
                # Show some DLL names
                for dll in dll_files[:5]:
                    print(f"      - {dll}")
                if len(dll_files) > 5:
                    print(f"      ... and {len(dll_files) - 5} more")

print("\n" + "=" * 60)
print("SUMMARY - Copy these paths:")
print("=" * 60)

if found_dll_paths:
    print("\ncuda_paths = [")
    for path in found_dll_paths:
        print(f'    r"{path}",')
    print("]")
else:
    print("\n✗ No DLL paths found!")
    print("\nManual check needed:")
    print("1. Open File Explorer")
    print("2. Go to: C:\\Program Files\\NVIDIA GPU Computing Toolkit\\CUDA\\v13.0")
    print("3. Look for 'bin' folder")
    print("4. Check if it contains .dll files")

print("\n" + "=" * 60)