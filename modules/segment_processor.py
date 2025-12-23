# File: modules/segment_processor.py

from typing import Dict, List, Any


class SegmentProcessor:
    """Processes transcription segments and formats output."""
    
    def __init__(self, logger):
        self.logger = logger
    
    def process_segments(self, segments: Any, info: Any, include_word_timestamps: bool = False) -> Dict:
        """
        Process transcription segments into structured format.
        
        Args:
            segments: Transcription segments from Whisper
            info: Transcription info from Whisper
            include_word_timestamps: Whether to include word-level timestamps
            
        Returns:
            Formatted transcript dictionary
        """
        try:
            transcript_segments = []
            full_text = []
            
            for segment in segments:
                segment_data = self._process_single_segment(segment, include_word_timestamps)
                transcript_segments.append(segment_data)
                full_text.append(segment.text.strip())
            
            transcript = {
                'language': info.language,
                'language_probability': info.language_probability,
                'duration': info.duration,
                'segments': transcript_segments,
                'full_text': ' '.join(full_text)
            }
            
            return transcript
            
        except Exception as e:
            self.logger.error(f"Error processing segments: {str(e)}")
            raise
    
    def _process_single_segment(self, segment: Any, include_word_timestamps: bool) -> Dict:
        """
        Process a single segment.
        
        Args:
            segment: Single segment from Whisper
            include_word_timestamps: Whether to include word-level timestamps
            
        Returns:
            Formatted segment dictionary
        """
        segment_data = {
            'id': segment.id,
            'start': segment.start,
            'end': segment.end,
            'text': segment.text.strip()
        }
        
        # Add word-level timestamps if requested and available
        if include_word_timestamps and hasattr(segment, 'words') and segment.words:
            segment_data['words'] = self._process_words(segment.words)
        
        return segment_data
    
    def _process_words(self, words: List[Any]) -> List[Dict]:
        """
        Process word-level timestamps.
        
        Args:
            words: List of word objects from Whisper
            
        Returns:
            List of word dictionaries
        """
        processed_words = []
        
        for word in words:
            word_data = {
                'word': word.word,
                'start': word.start,
                'end': word.end,
                'probability': word.probability
            }
            processed_words.append(word_data)
        
        return processed_words
    
    def filter_segments_by_time(self, segments: List[Dict], start_time: float, end_time: float) -> List[Dict]:
        """
        Filter segments by time range.
        
        Args:
            segments: List of segment dictionaries
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            Filtered list of segments
        """
        filtered = []
        
        for segment in segments:
            seg_start = segment['start']
            seg_end = segment['end']
            
            # Check if segment overlaps with time range
            if seg_end >= start_time and seg_start <= end_time:
                # Adjust timestamps relative to start_time
                adjusted_segment = segment.copy()
                adjusted_segment['start'] = max(0, seg_start - start_time)
                adjusted_segment['end'] = min(end_time - start_time, seg_end - start_time)
                filtered.append(adjusted_segment)
        
        return filtered
    
    def merge_segments(self, segments: List[Dict], max_duration: float = 5.0) -> List[Dict]:
        """
        Merge short segments together.
        
        Args:
            segments: List of segment dictionaries
            max_duration: Maximum duration for merged segment
            
        Returns:
            List of merged segments
        """
        if not segments:
            return []
        
        merged = []
        current_segment = segments[0].copy()
        
        for next_segment in segments[1:]:
            current_duration = current_segment['end'] - current_segment['start']
            next_duration = next_segment['end'] - current_segment['start']
            
            # Check if we can merge
            if next_duration <= max_duration:
                current_segment['end'] = next_segment['end']
                current_segment['text'] += ' ' + next_segment['text']
                
                # Merge words if available
                if 'words' in current_segment and 'words' in next_segment:
                    current_segment['words'].extend(next_segment['words'])
            else:
                merged.append(current_segment)
                current_segment = next_segment.copy()
        
        # Add last segment
        merged.append(current_segment)
        
        return merged