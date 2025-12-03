import os
from typing import Dict, List


class SubtitleGenerator:
    """Generates SRT subtitle files."""
    
    def __init__(self, config: Dict, logger):
        self.config = config
        self.logger = logger
    
    def generate_srt(self, clip_segments: List[Dict], output_dir: str, 
                     clip_index: int) -> str:
        """
        Generate SRT file for a clip.
        
        Args:
            clip_segments: List of transcript segments for the clip
            output_dir: Output directory
            clip_index: Clip number
            
        Returns:
            Path to generated SRT file
        """
        try:
            output_path = os.path.join(output_dir, f"clip_{clip_index:02d}.srt")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for idx, segment in enumerate(clip_segments, 1):
                    start_time = segment['start']
                    end_time = segment['end']
                    text = segment['text'].strip()
                    
                    # Format timestamps
                    start_str = self._format_timestamp(start_time)
                    end_str = self._format_timestamp(end_time)
                    
                    # Write SRT entry
                    f.write(f"{idx}\n")
                    f.write(f"{start_str} --> {end_str}\n")
                    
                    # Split long lines (max 42 chars per line)
                    lines = self._split_text(text, max_chars=42)
                    for line in lines:
                        f.write(f"{line}\n")
                    
                    f.write("\n")
            
            self.logger.info(f"SRT file generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generating SRT: {str(e)}")
            raise
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to SRT timestamp (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _split_text(self, text: str, max_chars: int = 42) -> List[str]:
        """Split text into lines with max character limit."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            
            if current_length + word_length + len(current_line) <= max_chars:
                current_line.append(word)
                current_length += word_length
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines