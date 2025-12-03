from typing import Dict, List


class ClipSelector:
    """Selects best clips from scored candidates."""
    
    def __init__(self, config: Dict, logger):
        self.config = config
        self.logger = logger
    
    def select_clips(self, scored_candidates: List[Dict]) -> List[Dict]:
        """
        Select top N non-overlapping clips.
        
        Args:
            scored_candidates: List of scored candidates (sorted by score)
            
        Returns:
            List of selected clips
        """
        try:
            self.logger.info("Selecting best clips...")
            
            top_n = self.config['ai_analysis']['top_n_clips']
            
            selected = []
            used_timeranges = []
            
            for candidate in scored_candidates:
                if len(selected) >= top_n:
                    break
                
                start = candidate['start_time']
                end = candidate['end_time']
                
                # Check for overlap with already selected clips
                has_overlap = False
                for used_start, used_end in used_timeranges:
                    if self._has_overlap(start, end, used_start, used_end):
                        has_overlap = True
                        break
                
                if not has_overlap:
                    selected.append(candidate)
                    used_timeranges.append((start, end))
                    self.logger.info(
                        f"Selected clip: {start:.1f}s - {end:.1f}s "
                        f"(score: {candidate['scores']['composite']:.1f})"
                    )
            
            self.logger.info(f"Selected {len(selected)} clips")
            return selected
            
        except Exception as e:
            self.logger.error(f"Error selecting clips: {str(e)}")
            raise
    
    def _has_overlap(self, start1: float, end1: float, 
                     start2: float, end2: float) -> bool:
        """Check if two time ranges overlap."""
        return not (end1 <= start2 or end2 <= start1)