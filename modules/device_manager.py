# File: modules/device_manager.py

import os
import platform


class DeviceManager:
    """Manages device configuration and CUDA setup."""
    
    def __init__(self, logger):
        self.logger = logger
        self.is_windows = platform.system() == 'Windows'
    
    def setup_cuda_environment(self):
        """Setup CUDA/CUDNN environment if on Windows."""
        if not self.is_windows:
            return
        
        try:
            cuda_paths = [
                r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v13.0\bin",
                r"C:\Program Files\NVIDIA\CUDNN\v9.16\bin",
            ]
            
            added_count = 0
            for path in cuda_paths:
                if os.path.exists(path):
                    try:
                        os.add_dll_directory(path)
                        self.logger.info(f"[OK] Added CUDA path: {path}")
                        added_count += 1
                    except Exception as e:
                        self.logger.warning(f"[WARNING] Could not add {path}: {e}")
                else:
                    self.logger.error(f"[ERROR] Path not found: {path}")
            
            if added_count == 0:
                raise FileNotFoundError("Could not add any CUDA paths!")
            
            self.logger.info(f"[OK] CUDA environment setup complete ({added_count} paths)")
            
        except Exception as e:
            self.logger.error(f"[ERROR] CUDA setup failed: {str(e)}")
            raise
    
    def get_available_device(self, requested_device: str) -> str:
        """Validate and return available device."""
        if requested_device == 'cpu':
            self.logger.info("Using CPU device")
            return 'cpu'
        
        if requested_device in ['cuda', 'auto']:
            if self._is_cuda_available():
                self.logger.info("[OK] CUDA available, using GPU")
                return 'cuda'
            else:
                self.logger.error("[ERROR] CUDA not available!")
                raise RuntimeError("CUDA requested but not available")
        
        self.logger.warning(f"Unknown device '{requested_device}', falling back to CPU")
        return 'cpu'
    
    def _is_cuda_available(self) -> bool:
        """Check if CUDA is available."""
        try:
            import torch
            available = torch.cuda.is_available()
            
            if available:
                self.logger.info(f"CUDA Version: {torch.version.cuda}")
                self.logger.info(f"cuDNN Version: {torch.backends.cudnn.version()}")
                self.logger.info(f"GPU Device: {torch.cuda.get_device_name(0)}")
                
                props = torch.cuda.get_device_properties(0)
                self.logger.info(f"GPU Memory: {props.total_memory / 1024**3:.2f} GB")
            
            return available
            
        except ImportError:
            self.logger.error("PyTorch not installed!")
            return False
        except Exception as e:
            self.logger.error(f"Error checking CUDA: {str(e)}")
            return False
    
    def get_device_info(self) -> dict:
        """Get detailed device information."""
        info = {
            'platform': platform.system(),
            'cuda_available': False,
            'device_count': 0,
            'devices': []
        }
        
        try:
            import torch
            info['cuda_available'] = torch.cuda.is_available()
            
            if info['cuda_available']:
                info['device_count'] = torch.cuda.device_count()
                info['cuda_version'] = torch.version.cuda
                info['cudnn_version'] = torch.backends.cudnn.version()
                
                for i in range(info['device_count']):
                    props = torch.cuda.get_device_properties(i)
                    device_info = {
                        'id': i,
                        'name': props.name,
                        'memory_total_gb': props.total_memory / 1024**3,
                        'memory_allocated_gb': torch.cuda.memory_allocated(i) / 1024**3,
                        'memory_cached_gb': torch.cuda.memory_reserved(i) / 1024**3
                    }
                    info['devices'].append(device_info)
        
        except Exception as e:
            self.logger.warning(f"Could not get device info: {str(e)}")
        
        return info