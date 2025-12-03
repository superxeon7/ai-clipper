# File: modules/video_processor.py

import os
import subprocess
import ffmpeg
from pathlib import Path
from typing import Dict, Optional, Tuple


class VideoProcessor:
    """Handles video processing operations using ffmpeg."""
    
    def __init__(self, config: Dict, logger):
        self.config = config
        self.logger = logger
        self.temp_dir = config['output']['temp_dir']
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def extract_audio(self, video_path: str) -> str:
        """
        Extract audio from video file.
        
        Args:
            video_path: Path to input video
            
        Returns:
            Path to extracted audio file (WAV)
        """
        try:
            video_name = Path(video_path).stem
            audio_path = os.path.join(self.temp_dir, f"{video_name}_audio.wav")
            
            # Extract audio using ffmpeg
            self.logger.info(f"Extracting audio to: {audio_path}")
            
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream,
                audio_path,
                acodec='pcm_s16le',
                ac=self.config['video']['audio_channels'],
                ar=self.config['video']['audio_sample_rate']
            )
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            self.logger.info("Audio extraction complete")
            return audio_path
            
        except Exception as e:
            self.logger.error(f"Error extracting audio: {str(e)}")
            raise
    
    def get_video_info(self, video_path: str) -> Dict:
        """
        Get video metadata.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video metadata
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            audio_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
            
            duration = float(probe['format']['duration'])
            
            return {
                'duration': duration,
                'width': int(video_info['width']),
                'height': int(video_info['height']),
                'fps': eval(video_info['r_frame_rate']),
                'codec': video_info['codec_name'],
                'has_audio': audio_info is not None,
                'format': probe['format']['format_name']
            }
            
        except Exception as e:
            self.logger.error(f"Error getting video info: {str(e)}")
            raise
    
    def validate_video(self, video_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            if not os.path.exists(video_path):
                return False, "Video file does not exist"
            
            # Check file extension
            ext = Path(video_path).suffix.lower().replace('.', '')
            if ext not in self.config['video']['supported_formats']:
                return False, f"Unsupported format: {ext}"
            
            # Get video info
            info = self.get_video_info(video_path)
            
            # Check duration
            duration_minutes = info['duration'] / 60
            min_duration = self.config['video']['min_duration_minutes']
            max_duration = self.config['video']['max_duration_minutes']
            
            if duration_minutes < min_duration:
                return False, f"Video too short: {duration_minutes:.1f} min (min: {min_duration} min)"
            
            if duration_minutes > max_duration:
                return False, f"Video too long: {duration_minutes:.1f} min (max: {max_duration} min)"
            
            # Check has audio
            if not info['has_audio']:
                return False, "Video has no audio track"
            
            return True, None
            
        except Exception as e:
            return False, f"Error validating video: {str(e)}"