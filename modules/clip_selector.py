# File: modules/clip_selector.py

from typing import Dict, List


class ClipSelector:
    """Selects best clips from scored candidates with improved algorithm."""
    
    def __init__(self, config: Dict, logger):
        self.config = config
        self.logger = logger
    
    def select_clips(self, scored_candidates: List[Dict]) -> List[Dict]:
        """
        Select top N non-overlapping clips with better spacing.
        
        Args:
            scored_candidates: List of scored candidates (sorted by score)
            
        Returns:
            List of selected clips
        """
        try:
            self.logger.info("Selecting best clips with improved algorithm...")
            
            top_n = self.config['ai_analysis']['top_n_clips']
            min_gap = self.config['ai_analysis'].get('min_gap_between_clips', 10)  # seconds
            
            selected = []
            used_timeranges = []
            
            # Group candidates by score tiers for better distribution
            score_threshold = 70  # Consider clips with score > 70 as "viral"
            viral_clips = [c for c in scored_candidates if c['scores']['composite'] > score_threshold]
            good_clips = [c for c in scored_candidates if c['scores']['composite'] <= score_threshold]
            
            self.logger.info(f"Found {len(viral_clips)} viral clips, {len(good_clips)} good clips")
            
            # First, try to get viral clips
            for candidate in viral_clips:
                if len(selected) >= top_n:
                    break
                
                if self._can_add_clip(candidate, used_timeranges, min_gap):
                    selected.append(candidate)
                    used_timeranges.append((candidate['start_time'], candidate['end_time']))
                    self.logger.info(
                        f"Selected VIRAL clip: {candidate['start_time']:.1f}s - {candidate['end_time']:.1f}s "
                        f"(score: {candidate['scores']['composite']:.1f})"
                    )
            
            # Fill remaining slots with good clips
            for candidate in good_clips:
                if len(selected) >= top_n:
                    break
                
                if self._can_add_clip(candidate, used_timeranges, min_gap):
                    selected.append(candidate)
                    used_timeranges.append((candidate['start_time'], candidate['end_time']))
                    self.logger.info(
                        f"Selected clip: {candidate['start_time']:.1f}s - {candidate['end_time']:.1f}s "
                        f"(score: {candidate['scores']['composite']:.1f})"
                    )
            
            # Sort by start time for better organization
            selected.sort(key=lambda x: x['start_time'])
            
            self.logger.info(f"Selected {len(selected)} clips total")
            return selected
            
        except Exception as e:
            self.logger.error(f"Error selecting clips: {str(e)}")
            raise
    
    def _can_add_clip(self, candidate: Dict, used_ranges: List, min_gap: float) -> bool:
        """Check if clip can be added without overlap or being too close."""
        start = candidate['start_time']
        end = candidate['end_time']
        
        for used_start, used_end in used_ranges:
            # Check overlap
            if self._has_overlap(start, end, used_start, used_end):
                return False
            
            # Check if too close
            if self._too_close(start, end, used_start, used_end, min_gap):
                return False
        
        return True
    
    def _has_overlap(self, start1: float, end1: float, start2: float, end2: float) -> bool:
        """Check if two time ranges overlap."""
        return not (end1 <= start2 or end2 <= start1)
    
    def _too_close(self, start1: float, end1: float, start2: float, end2: float, min_gap: float) -> bool:
        """Check if two clips are too close to each other."""
        # Distance between clips
        if end1 < start2:
            gap = start2 - end1
        elif end2 < start1:
            gap = start1 - end2
        else:
            return True  # Overlapping
        
        return gap < min_gap