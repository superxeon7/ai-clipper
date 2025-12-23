# test_gpu_final.py

import sys
sys.path.append('.')

# Setup logger dulu
from utils.logger import setup_logger
logger = setup_logger(level='INFO', console=True)

print("=" * 60)
print("FINAL GPU TEST")
print("=" * 60)

# Test device manager
from modules.device_manager import DeviceManager

dm = DeviceManager(logger)

print("\n[1] Setting up CUDA environment...")
try:
    dm.setup_cuda_environment()
    print("✓ CUDA environment setup successful!")
except Exception as e:
    print(f"✗ Failed: {e}")
    sys.exit(1)

print("\n[2] Checking CUDA availability...")
device = dm.get_available_device('cuda')
print(f"✓ Device selected: {device}")

print("\n[3] Getting device info...")
info = dm.get_device_info()
print(f"✓ CUDA Available: {info['cuda_available']}")
print(f"✓ GPU Count: {info['device_count']}")
if info['devices']:
    print(f"✓ GPU Name: {info['devices'][0]['name']}")
    print(f"✓ GPU Memory: {info['devices'][0]['memory_total_gb']:.2f} GB")

print("\n[4] Testing Faster-Whisper with GPU...")
try:
    from faster_whisper import WhisperModel
    
    print("   Loading tiny model on GPU...")
    model = WhisperModel("tiny", device="cuda", compute_type="float16")
    print("✓ Faster-Whisper model loaded on GPU!")
    
except Exception as e:
    print(f"✗ Failed to load model: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓✓✓ ALL TESTS PASSED! GPU IS READY! ✓✓✓")
print("=" * 60)
print("\nYou can now use GPU in config.yaml:")
print("  device: 'cuda'")
print("  compute_type: 'float16'")
print("=" * 60)