# File: modules/subtitle_generator_modern.py

import os
import json
from typing import Dict, List, Tuple


class ModernSubtitleGenerator:
    """Generates modern animated subtitles with word-by-word highlighting."""
    
    def __init__(self, config: Dict, logger):
        self.config = config
        self.logger = logger
        
        # Get subtitle config or use defaults
        self.subtitle_config = config.get('subtitle', {
            'style': 'modern',
            'words_per_line': 3,
            'highlight_color': '#9933FF',  # Purple
            'text_color': '#FFFFFF',       # White
            'outline_color': '#000000',    # Black
            'font': 'Arial Black',
            'fontsize': 58,
            'outline_width': 4,
            'position': 'center',
            'animation': True
        })
    
    def generate_animated_ass(self, clip_segments: List[Dict], output_dir: str, 
                             clip_index: int, video_format: str = 'shorts') -> str:
        """
        Generate ASS subtitle file with word-by-word karaoke animation.
        
        Args:
            clip_segments: List of transcript segments with word timestamps
            output_dir: Output directory
            clip_index: Clip number
            video_format: 'shorts' (9:16) or 'youtube' (16:9)
            
        Returns:
            Path to generated ASS file
        """
        try:
            output_path = os.path.join(output_dir, f"clip_{clip_index:02d}_{video_format}.ass")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                # Write ASS header with styles
                f.write(self._generate_ass_header(video_format))
                
                # Write events section
                f.write("\n[Events]\n")
                f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
                
                event_counter = 0
                
                for segment in clip_segments:
                    if 'words' not in segment or not segment['words']:
                        # Fallback jika tidak ada word timestamps
                        self._write_simple_event(f, segment, event_counter)
                        event_counter += 1
                        continue
                    
                    # Group words (2-3 words per line)
                    words = segment['words']
                    word_groups = self._group_words_smart(words)
                    
                    for group in word_groups:
                        self._write_karaoke_event(f, group, event_counter)
                        event_counter += 1
            
            self.logger.info(f"Modern ASS subtitle generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generating ASS subtitle: {str(e)}")
            raise
    
    def _generate_ass_header(self, video_format: str) -> str:
        """Generate ASS header with custom styles."""
        
        # Position based on format
        if video_format == 'shorts':
            margin_v = 180  # From bottom for 9:16
            alignment = 2   # Bottom center
        else:
            margin_v = 100  # From bottom for 16:9
            alignment = 2   # Bottom center
        
        # Convert colors from hex to ASS format (&HAABBGGRR)
        primary_color = self._hex_to_ass_color(self.subtitle_config['text_color'])
        highlight_color = self._hex_to_ass_color(self.subtitle_config['highlight_color'])
        outline_color = self._hex_to_ass_color(self.subtitle_config['outline_color'])
        
        fontsize = self.subtitle_config['fontsize']
        font = self.subtitle_config['font']
        outline = self.subtitle_config['outline_width']
        
        header = f"""[Script Info]
Title: AI Clipper - Modern Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: {'1920' if video_format == 'shorts' else '1080'}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},{fontsize},{primary_color},&H000000FF,{outline_color},&H80000000,-1,0,0,0,100,100,0,0,1,{outline},2,{alignment},20,20,{margin_v},1
Style: Karaoke,{font},{fontsize},{highlight_color},&H000000FF,{outline_color},&H80000000,-1,0,0,0,105,105,0,0,1,{outline},2,{alignment},20,20,{margin_v},1
"""
        return header
    
    def _group_words_smart(self, words: List[Dict]) -> List[List[Dict]]:
        """
        Group words intelligently (2-3 words, avoid breaking mid-sentence).
        
        Args:
            words: List of word dictionaries
            
        Returns:
            List of word groups
        """
        groups = []
        current_group = []
        max_words = self.subtitle_config['words_per_line']
        
        for i, word in enumerate(words):
            current_group.append(word)
            word_text = word['word'].strip()
            
            # Check if should break
            should_break = False
            
            # Break on max words
            if len(current_group) >= max_words:
                should_break = True
            
            # Break on punctuation if group has 2+ words
            if len(current_group) >= 2:
                if any(p in word_text for p in ['.', '!', '?', ',', ';']):
                    should_break = True
            
            # Break if next word starts with capital (new sentence)
            if i < len(words) - 1:
                next_word = words[i + 1]['word'].strip()
                if next_word and next_word[0].isupper() and len(current_group) >= 2:
                    should_break = True
            
            if should_break:
                groups.append(current_group)
                current_group = []
        
        # Add remaining words
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _write_karaoke_event(self, f, word_group: List[Dict], index: int):
        """
        Write karaoke-style event (word-by-word highlighting).
        
        The magic: \\k<duration> creates word-by-word animation!
        """
        start_time = self._format_ass_time(word_group[0]['start'])
        end_time = self._format_ass_time(word_group[-1]['end'])
        
        # Build karaoke text
        karaoke_parts = []
        
        for word in word_group:
            word_text = word['word'].strip()
            
            # Calculate duration in centiseconds (1 cs = 10 ms)
            duration_cs = int((word['end'] - word['start']) * 100)
            
            # Add karaoke tag: when this word plays, it gets highlighted
            # \\k<duration> = karaoke effect
            karaoke_parts.append(f"{{\\k{duration_cs}}}{word_text}")
        
        # Join words
        text = " ".join(karaoke_parts)
        
        # Write dialogue with karaoke style
        f.write(f"Dialogue: 0,{start_time},{end_time},Karaoke,,0,0,0,,{text}\n")
    
    def _write_simple_event(self, f, segment: Dict, index: int):
        """Fallback for segments without word timestamps."""
        start_time = self._format_ass_time(segment['start'])
        end_time = self._format_ass_time(segment['end'])
        text = segment['text'].strip()
        
        # Split into multiple lines if too long
        words = text.split()
        max_words = self.subtitle_config['words_per_line']
        
        if len(words) <= max_words:
            f.write(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n")
        else:
            # Split into chunks
            for i in range(0, len(words), max_words):
                chunk = " ".join(words[i:i+max_words])
                f.write(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{chunk}\n")
    
    def _format_ass_time(self, seconds: float) -> str:
        """Format seconds to ASS timestamp (H:MM:SS.CC)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds % 1) * 100)
        
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"
    
    def _hex_to_ass_color(self, hex_color: str) -> str:
        """
        Convert hex color to ASS format.
        
        Hex: #RRGGBB
        ASS: &H00BBGGRR (note: reversed!)
        """
        hex_color = hex_color.lstrip('#')
        
        if len(hex_color) == 6:
            r = hex_color[0:2]
            g = hex_color[2:4]
            b = hex_color[4:6]
            
            # ASS format: &H00BBGGRR (BGR reversed)
            return f"&H00{b.upper()}{g.upper()}{r.upper()}"
        
        return "&H00FFFFFF"  # Default white
    
    def generate_simple_srt(self, clip_segments: List[Dict], output_dir: str, clip_index: int) -> str:
        """
        Generate simple SRT subtitle (fallback for compatibility).
        
        Args:
            clip_segments: List of transcript segments
            output_dir: Output directory
            clip_index: Clip number
            
        Returns:
            Path to SRT file
        """
        try:
            output_path = os.path.join(output_dir, f"clip_{clip_index:02d}_simple.srt")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                subtitle_index = 1
                
                for segment in clip_segments:
                    if 'words' not in segment or not segment['words']:
                        continue
                    
                    words = segment['words']
                    word_groups = self._group_words_smart(words)
                    
                    for group in word_groups:
                        start_time = self._format_srt_time(group[0]['start'])
                        end_time = self._format_srt_time(group[-1]['end'])
                        text = " ".join([w['word'].strip() for w in group])
                        
                        f.write(f"{subtitle_index}\n")
                        f.write(f"{start_time} --> {end_time}\n")
                        f.write(f"{text}\n\n")
                        
                        subtitle_index += 1
            
            self.logger.info(f"Simple SRT subtitle generated: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"Error generating SRT: {str(e)}")
            raise
    
    def _format_srt_time(self, seconds: float) -> str:
        """Format seconds to SRT timestamp (HH:MM:SS,mmm)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"