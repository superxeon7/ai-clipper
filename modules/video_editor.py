import os
import ffmpeg
from pathlib import Path
from typing import Dict, List


class VideoEditor:
    """Handles video editing operations."""
    
    def __init__(self, config: Dict, logger):
        self.config = config
        self.logger = logger
    
    def cut_clip(self, video_path: str, start_time: float, end_time: float,
                 output_dir: str, clip_index: int) -> Dict[str, str]:
        """
        Cut a clip from video and create multiple format versions.
        
        Args:
            video_path: Input video path
            start_time: Start time in seconds
            end_time: End time in seconds
            output_dir: Output directory
            clip_index: Clip number
            
        Returns:
            Dictionary mapping format names to output paths
        """
        try:
            self.logger.info(f"Cutting clip {clip_index}: {start_time:.1f}s - {end_time:.1f}s")
            
            duration = end_time - start_time
            clip_paths = {}
            
            # Create each output format
            for format_config in self.config['video_editing']['output_formats']:
                format_name = format_config['name']
                width = format_config['width']
                height = format_config['height']
                
                output_filename = f"clip_{clip_index:02d}_{format_name}_raw.mp4"
                output_path = os.path.join(output_dir, output_filename)
                
                # Cut and resize
                self._cut_and_resize(
                    video_path, 
                    start_time, 
                    duration, 
                    output_path,
                    width, 
                    height
                )
                
                clip_paths[format_name] = output_path
                self.logger.info(f"Created {format_name} version: {output_path}")
            
            return clip_paths
            
        except Exception as e:
            self.logger.error(f"Error cutting clip: {str(e)}")
            raise
    
    def _cut_and_resize(self, input_path: str, start_time: float, duration: float,
                       output_path: str, target_width: int, target_height: int):
        """Cut and resize video using ffmpeg."""
        try:
            # Get input video dimensions
            probe = ffmpeg.probe(input_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            input_width = int(video_info['width'])
            input_height = int(video_info['height'])
            
            # Calculate scaling
            input_ratio = input_width / input_height
            target_ratio = target_width / target_height
            
            if abs(input_ratio - target_ratio) < 0.01:
                # Same ratio, just scale
                scale_filter = f"scale={target_width}:{target_height}"
            elif input_ratio > target_ratio:
                # Input is wider, crop width
                scale_height = target_height
                scale_width = int(scale_height * input_ratio)
                crop_width = target_width
                crop_x = (scale_width - crop_width) // 2
                scale_filter = f"scale={scale_width}:{scale_height},crop={crop_width}:{scale_height}:{crop_x}:0"
            else:
                # Input is taller, crop height
                scale_width = target_width
                scale_height = int(scale_width / input_ratio)
                crop_height = target_height
                crop_y = (scale_height - crop_height) // 2
                scale_filter = f"scale={scale_width}:{scale_height},crop={scale_width}:{crop_height}:0:{crop_y}"
            
            # Build ffmpeg command
            stream = ffmpeg.input(input_path, ss=start_time, t=duration)
            
            # Apply video filters
            stream = ffmpeg.filter(stream.video, 'fps', fps=30)
            for filter_str in scale_filter.split(','):
                if 'scale' in filter_str:
                    w, h = filter_str.replace('scale=', '').split(':')
                    stream = ffmpeg.filter(stream, 'scale', w, h)
                elif 'crop' in filter_str:
                    parts = filter_str.replace('crop=', '').split(':')
                    stream = ffmpeg.filter(stream, 'crop', parts[0], parts[1], parts[2], parts[3])
            
            # Audio normalization if enabled
            if self.config['video_editing']['audio_normalization']:
                audio = stream.audio
                target_level = self.config['video_editing']['target_audio_level']
                audio = ffmpeg.filter(audio, 'loudnorm', I=target_level, TP=-1.5, LRA=11)
                stream = ffmpeg.output(stream, audio, output_path, vcodec='libx264', acodec='aac')
            else:
                stream = ffmpeg.output(stream, output_path, vcodec='libx264', acodec='aac')
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
        except Exception as e:
            self.logger.error(f"Error in cut_and_resize: {str(e)}")
            raise
    
    def burn_subtitles(self, video_path: str, srt_path: str, format_name: str) -> str:
        """
        Burn subtitles into video.
        
        Args:
            video_path: Input video path
            srt_path: Path to SRT file
            format_name: Format name (for styling)
            
        Returns:
            Path to output video with burned subtitles
        """
        try:
            output_path = video_path.replace('_raw.mp4', '_final.mp4')
            
            self.logger.info(f"Burning subtitles: {srt_path}")
            
            # Get subtitle style config
            style = self.config['video_editing']['subtitle_style']
            
            # Build subtitle filter
            subtitle_filter = (
                f"subtitles={srt_path}:force_style='"
                f"FontName={style['font']},"
                f"FontSize={style['fontsize']},"
                f"PrimaryColour=&H{self._color_to_hex(style['fontcolor'])},"
                f"OutlineColour=&H{self._color_to_hex(style['bordercolor'])},"
                f"BorderStyle=1,"
                f"Outline={style['borderw']},"
                f"Alignment=2"  # Bottom center
                f"'"
            )
            
            # Apply filter
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.filter(stream, 'subtitles', srt_path, force_style=(
                f"FontName={style['font']},"
                f"FontSize={style['fontsize']},"
                f"PrimaryColour=&HFFFFFF,"
                f"OutlineColour=&H000000,"
                f"BorderStyle=1,"
                f"Outline={style['borderw']},"
                f"Alignment=2"
            ))
            stream = ffmpeg.output(stream, output_path, vcodec='libx264', acodec='copy')
            
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
            self.logger.info(f"Subtitles burned: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error burning subtitles: {str(e)}")
            raise
    
    def _color_to_hex(self, color: str) -> str:
        """Convert color name to hex for ffmpeg."""
        colors = {
            'white': 'FFFFFF',
            'black': '000000',
            'yellow': 'FFFF00',
            'red': 'FF0000',
            'blue': '0000FF'
        }
        return colors.get(color.lower(), 'FFFFFF')