# File: modules/model_loader.py

from typing import Dict
from faster_whisper import WhisperModel


class ModelLoader:
    """Handles loading and configuration of Whisper models."""
    
    def __init__(self, config: Dict, logger):
        self.config = config
        self.logger = logger
    
    def load_model(self, device: str) -> WhisperModel:
        """
        Load Whisper model with specified configuration.
        
        Args:
            device: Device to load model on ('cuda' or 'cpu')
            
        Returns:
            Loaded WhisperModel instance
        """
        try:
            model_config = self.config['transcription']
            model_size = model_config['model_size']
            compute_type = self._get_compute_type(device, model_config.get('compute_type'))
            
            self.logger.info(f"Loading Whisper model: {model_size}")
            self.logger.info(f"Device: {device}")
            self.logger.info(f"Compute type: {compute_type}")
            
            # Additional model parameters
            model_params = {
                'model_size_or_path': model_size,
                'device': device,
                'compute_type': compute_type
            }
            
            # Add optional parameters if present in config
            if 'cpu_threads' in model_config:
                model_params['cpu_threads'] = model_config['cpu_threads']
            
            if 'num_workers' in model_config:
                model_params['num_workers'] = model_config['num_workers']
            
            if 'download_root' in model_config:
                model_params['download_root'] = model_config['download_root']
            
            model = WhisperModel(**model_params)
            
            self.logger.info("Model loaded successfully")
            self._log_model_info(model, model_size)
            
            return model
            
        except Exception as e:
            self.logger.error(f"Failed to load model: {str(e)}")
            raise
    
    def _get_compute_type(self, device: str, config_compute_type: str = None) -> str:
        """
        Determine appropriate compute type based on device and config.
        
        Args:
            device: Device name ('cuda' or 'cpu')
            config_compute_type: Compute type from config
            
        Returns:
            Appropriate compute type
        """
        if config_compute_type:
            return config_compute_type
        
        # Auto-determine based on device
        if device == 'cuda':
            return 'float16'  # Best for GPU
        else:
            return 'int8'  # Best for CPU
    
    def _log_model_info(self, model: WhisperModel, model_size: str):
        """Log information about loaded model."""
        try:
            self.logger.info(f"Model size: {model_size}")
            # Add any additional model info logging here
        except Exception as e:
            self.logger.warning(f"Could not log model info: {str(e)}")
    
    def get_available_models(self) -> list:
        """
        Get list of available Whisper model sizes.
        
        Returns:
            List of model size names
        """
        return [
            'tiny',
            'tiny.en',
            'base',
            'base.en',
            'small',
            'small.en',
            'medium',
            'medium.en',
            'large-v1',
            'large-v2',
            'large-v3',
            'large'
        ]
    
    def validate_model_size(self, model_size: str) -> bool:
        """
        Validate if model size is supported.
        
        Args:
            model_size: Model size to validate
            
        Returns:
            True if valid, False otherwise
        """
        return model_size in self.get_available_models()