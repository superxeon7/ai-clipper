# File: modules/transcriber.py

import os
import json
from typing import Dict, List, Optional
from faster_whisper import WhisperModel


class Transcriber:
    """Handles speech-to-text transcription using Faster-Whisper."""
    
    def __init__(self, config: Dict, logger):
        self.config = config
        self.logger = logger
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Faster-Whisper model."""
        try:
            model_config = self.config['transcription']
            
            self.logger.info(f"Loading Whisper model: {model_config['model_size']}")
            self.logger.info(f"Device: {model_config['device']}")
            
            self.model = WhisperModel(
                model_config['model_size'],
                device=model_config['device'],
                compute_type=model_config['compute_type']
            )
            
            self.logger.info("Whisper model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading Whisper model: {str(e)}")
            raise
    
    def transcribe(self, audio_path: str) -> Dict:
        """
        Transcribe audio file.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with full transcript and segments
        """
        try:
            self.logger.info("Starting transcription...")
            
            model_config = self.config['transcription']
            
            segments, info = self.model.transcribe(
                audio_path,
                beam_size=model_config['beam_size'],
                language=model_config['language'] if model_config['language'] != 'auto' else None,
                word_timestamps=model_config['word_timestamps']
            )
            
            # Convert segments to list and extract data
            transcript_segments = []
            full_text = []
            
            for segment in segments:
                segment_data = {
                    'id': segment.id,
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip()
                }
                
                # Add word-level timestamps if available
                if hasattr(segment, 'words') and segment.words:
                    segment_data['words'] = [
                        {
                            'word': word.word,
                            'start': word.start,
                            'end': word.end,
                            'probability': word.probability
                        }
                        for word in segment.words
                    ]
                
                transcript_segments.append(segment_data)
                full_text.append(segment.text.strip())
            
            transcript = {
                'language': info.language,
                'language_probability': info.language_probability,
                'duration': info.duration,
                'segments': transcript_segments,
                'full_text': ' '.join(full_text)
            }
            
            self.logger.info(f"Transcription complete: {len(transcript_segments)} segments")
            self.logger.info(f"Detected language: {info.language} (prob: {info.language_probability:.2f})")
            
            return transcript
            
        except Exception as e:
            self.logger.error(f"Error during transcription: {str(e)}")
            raise
    
    def save_transcript(self, transcript: Dict, output_path: str):
        """Save transcript to JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(transcript, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Transcript saved to: {output_path}")
        except Exception as e:
            self.logger.error(f"Error saving transcript: {str(e)}")
            raise