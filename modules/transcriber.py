# File: modules/transcriber.py

import os
import json
from typing import Dict, List, Optional
from faster_whisper import WhisperModel

from .device_manager import DeviceManager
from .model_loader import ModelLoader
from .segment_processor import SegmentProcessor
from .file_handler import FileHandler


class Transcriber:
    """Handles speech-to-text transcription using Faster-Whisper."""
    
    def __init__(self, config: Dict, logger):
        self.config = config
        self.logger = logger
        self.model = None
        
        # Initialize components
        self.device_manager = DeviceManager(logger)
        self.model_loader = ModelLoader(config, logger)
        self.segment_processor = SegmentProcessor(logger)
        self.file_handler = FileHandler(logger)
        
        self._load_model()
    
    def _load_model(self):
        """Load Faster-Whisper model."""
        try:
            self.logger.info("Initializing Whisper model...")
            
            # Setup CUDA/CUDNN if needed
            self.device_manager.setup_cuda_environment()
            
            # Validate and get device
            device = self.device_manager.get_available_device(
                self.config['transcription']['device']
            )
            
            # Load model with validated device
            self.model = self.model_loader.load_model(device)
            
            self.logger.info("Whisper model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading Whisper model: {str(e)}")
            raise
    
    def transcribe(self, audio_path: str) -> Dict:
        """
        Transcribe audio file with improved accuracy.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with full transcript and segments
        """
        try:
            self.logger.info(f"Starting transcription for: {audio_path}")
            
            # Validate audio file
            self.file_handler.validate_audio_file(audio_path)
            
            model_config = self.config['transcription']
            
            # FIXED VAD parameters - only use supported ones
            vad_params = {
                'threshold': 0.5,
                'min_speech_duration_ms': 250,
                'max_speech_duration_s': float('inf'),
                'min_silence_duration_ms': 2000,
                'speech_pad_ms': 400,
            }
            
            # IMPROVED SETTINGS for better accuracy
            segments, info = self.model.transcribe(
                audio_path,
                beam_size=model_config.get('beam_size', 5),
                best_of=5,  # Generate 5 candidates, pick best
                temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],  # Multiple temperatures
                language=model_config['language'] if model_config['language'] != 'auto' else None,
                word_timestamps=True,  # ALWAYS enable for better subtitles
                vad_filter=True,  # Remove silence
                vad_parameters=vad_params,
                condition_on_previous_text=True,  # Use context
                compression_ratio_threshold=2.4,
                log_prob_threshold=-1.0,
                no_speech_threshold=0.6,
            )
            
            # Process segments
            transcript = self.segment_processor.process_segments(
                segments, 
                info,
                include_word_timestamps=True
            )
            
            self.logger.info(f"Transcription complete: {len(transcript['segments'])} segments")
            self.logger.info(f"Detected language: {info.language} (prob: {info.language_probability:.2f})")
            
            return transcript
            
        except Exception as e:
            self.logger.error(f"Error during transcription: {str(e)}")
            raise
    
    def save_transcript(self, transcript: Dict, output_path: str):
        """Save transcript to JSON file."""
        try:
            self.file_handler.save_json(transcript, output_path)
            self.logger.info(f"Transcript saved to: {output_path}")
        except Exception as e:
            self.logger.error(f"Error saving transcript: {str(e)}")
            raise
    
    def transcribe_and_save(self, audio_path: str, output_path: str) -> Dict:
        """
        Convenience method to transcribe and save in one call.
        
        Args:
            audio_path: Path to audio file
            output_path: Path to save transcript JSON
            
        Returns:
            Transcript dictionary
        """
        transcript = self.transcribe(audio_path)
        self.save_transcript(transcript, output_path)
        return transcript