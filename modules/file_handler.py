# File: modules/file_handler.py

import os
import json
from pathlib import Path
from typing import Dict, Any


class FileHandler:
    """Handles file operations for transcription."""
    
    def __init__(self, logger):
        self.logger = logger
        self.supported_audio_formats = ['wav', 'mp3', 'flac', 'ogg', 'm4a', 'aac']
    
    def validate_audio_file(self, audio_path: str) -> bool:
        """
        Validate audio file exists and has supported format.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            True if valid
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If format not supported
        """
        # Check file exists
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Check file extension
        ext = Path(audio_path).suffix.lower().replace('.', '')
        if ext not in self.supported_audio_formats:
            raise ValueError(
                f"Unsupported audio format: {ext}. "
                f"Supported: {', '.join(self.supported_audio_formats)}"
            )
        
        # Check file size
        file_size = os.path.getsize(audio_path)
        if file_size < 1024:  # Less than 1KB
            raise ValueError(f"Audio file too small: {file_size} bytes")
        
        self.logger.info(f"Audio file validated: {audio_path} ({file_size / 1024 / 1024:.2f} MB)")
        return True
    
    def save_json(self, data: Dict, output_path: str):
        """
        Save data to JSON file.
        
        Args:
            data: Dictionary to save
            output_path: Path to output JSON file
        """
        try:
            # Create directory if not exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Save JSON
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"JSON saved: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving JSON: {str(e)}")
            raise
    
    def load_json(self, input_path: str) -> Dict:
        """
        Load JSON file.
        
        Args:
            input_path: Path to JSON file
            
        Returns:
            Loaded dictionary
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"JSON loaded: {input_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"Error loading JSON: {str(e)}")
            raise
    
    def save_text(self, text: str, output_path: str):
        """
        Save text to file.
        
        Args:
            text: Text content
            output_path: Path to output text file
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            self.logger.info(f"Text saved: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error saving text: {str(e)}")
            raise
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file info
        """
        if not os.path.exists(file_path):
            return None
        
        stat = os.stat(file_path)
        
        return {
            'path': file_path,
            'size_bytes': stat.st_size,
            'size_mb': stat.st_size / 1024 / 1024,
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'extension': Path(file_path).suffix.lower()
        }