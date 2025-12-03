import json
import requests
from typing import Dict, List
from sentence_transformers import SentenceTransformer
import numpy as np

from prompts.virality_prompt import VIRALITY_PROMPT


class AIAnalyzer:
    """AI-powered content analysis using embeddings and LLM."""
    
    def __init__(self, config: Dict, logger):
        self.config = config
        self.logger = logger
        self.embedding_model = None
        self.ollama_host = config['ai_analysis']['ollama_host']
        self.llm_model = config['ai_analysis']['llm_model']
        self._load_embedding_model()
    
    def _load_embedding_model(self):
        """Load sentence transformer model."""
        try:
            model_name = self.config['ai_analysis']['embedding_model']
            self.logger.info(f"Loading embedding model: {model_name}")
            self.embedding_model = SentenceTransformer(model_name)
            self.logger.info("Embedding model loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading embedding model: {str(e)}")
            raise
    
    def generate_candidates(self, transcript: Dict) -> List[Dict]:
        """
        Generate candidate clips from transcript.
        
        Args:
            transcript: Full transcript with segments
            
        Returns:
            List of candidate clip dictionaries
        """
        try:
            self.logger.info("Generating candidate clips...")
            
            segments = transcript['segments']
            min_duration = self.config['ai_analysis']['min_clip_duration']
            max_duration = self.config['ai_analysis']['max_clip_duration']
            overlap = self.config['ai_analysis']['overlap_seconds']
            
            candidates = []
            
            # Use sliding window approach
            for i, start_segment in enumerate(segments):
                start_time = start_segment['start']
                
                # Try to build clips of varying lengths
                for target_duration in [30, 45, 60]:
                    if target_duration < min_duration or target_duration > max_duration:
                        continue
                    
                    end_time = start_time + target_duration
                    
                    # Collect segments within this window
                    clip_segments = []
                    clip_text = []
                    
                    for seg in segments[i:]:
                        if seg['start'] < end_time:
                            clip_segments.append(seg)
                            clip_text.append(seg['text'])
                        else:
                            break
                    
                    # Only consider if we have meaningful content
                    if len(clip_segments) >= 2:
                        actual_end = clip_segments[-1]['end']
                        actual_duration = actual_end - start_time
                        
                        if min_duration <= actual_duration <= max_duration:
                            candidates.append({
                                'start_time': start_time,
                                'end_time': actual_end,
                                'duration': actual_duration,
                                'text': ' '.join(clip_text),
                                'segments': clip_segments,
                                'start_segment_id': start_segment['id']
                            })
            
            # Remove duplicates (same start_time)
            unique_candidates = {}
            for candidate in candidates:
                key = candidate['start_time']
                if key not in unique_candidates:
                    unique_candidates[key] = candidate
                elif candidate['duration'] > unique_candidates[key]['duration']:
                    unique_candidates[key] = candidate
            
            candidates = list(unique_candidates.values())
            
            self.logger.info(f"Generated {len(candidates)} candidate clips")
            return candidates
            
        except Exception as e:
            self.logger.error(f"Error generating candidates: {str(e)}")
            raise
    
    def score_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """
        Score candidates using embeddings and LLM.
        
        Args:
            candidates: List of candidate clips
            
        Returns:
            List of scored candidates
        """
        try:
            self.logger.info("Scoring candidates with AI...")
            
            for idx, candidate in enumerate(candidates, 1):
                if idx % 5 == 0:
                    self.logger.info(f"Scoring candidate {idx}/{len(candidates)}...")
                
                # Get embedding-based scores
                embedding_scores = self._score_with_embeddings(candidate)
                
                # Get LLM-based scores
                llm_scores = self._score_with_llm(candidate)
                
                # Combine scores
                weights = self.config['ai_analysis']['weights']
                composite_score = (
                    llm_scores['virality'] * weights['virality'] +
                    llm_scores['emotion'] * weights['emotion'] +
                    llm_scores['hook'] * weights['hook'] +
                    llm_scores['completeness'] * weights['completeness'] +
                    embedding_scores['coherence'] * weights['standalone']
                )
                
                candidate['scores'] = {
                    **llm_scores,
                    **embedding_scores,
                    'composite': composite_score
                }
            
            # Sort by composite score
            candidates.sort(key=lambda x: x['scores']['composite'], reverse=True)
            
            self.logger.info("Candidate scoring complete")
            return candidates
            
        except Exception as e:
            self.logger.error(f"Error scoring candidates: {str(e)}")
            raise
    
    def _score_with_embeddings(self, candidate: Dict) -> Dict:
        """Score candidate using semantic embeddings."""
        try:
            text = candidate['text']
            
            # Split into sentences
            sentences = [seg['text'] for seg in candidate['segments']]
            
            if len(sentences) < 2:
                return {'coherence': 50.0}
            
            # Get embeddings
            embeddings = self.embedding_model.encode(sentences)
            
            # Calculate coherence (average cosine similarity between consecutive sentences)
            similarities = []
            for i in range(len(embeddings) - 1):
                sim = np.dot(embeddings[i], embeddings[i+1]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[i+1])
                )
                similarities.append(sim)
            
            coherence = np.mean(similarities) * 100 if similarities else 50.0
            
            return {
                'coherence': float(coherence)
            }
            
        except Exception as e:
            self.logger.warning(f"Error in embedding scoring: {str(e)}")
            return {'coherence': 50.0}
    
    def _score_with_llm(self, candidate: Dict) -> Dict:
        """Score candidate using local LLM via Ollama."""
        try:
            text = candidate['text']
            
            # Build prompt
            prompt = VIRALITY_PROMPT.format(content=text)
            
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.llm_model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                output = result.get('response', '')
                
                # Parse scores from output
                scores = self._parse_llm_scores(output)
                return scores
            else:
                self.logger.warning(f"Ollama API error: {response.status_code}")
                return self._default_scores()
                
        except Exception as e:
            self.logger.warning(f"Error in LLM scoring: {str(e)}")
            return self._default_scores()
    
    def _parse_llm_scores(self, output: str) -> Dict:
        """Parse scores from LLM output."""
        try:
            # Try to parse JSON if present
            if '{' in output and '}' in output:
                json_start = output.index('{')
                json_end = output.rindex('}') + 1
                json_str = output[json_start:json_end]
                scores = json.loads(json_str)
                
                return {
                    'virality': float(scores.get('virality', 50)),
                    'emotion': float(scores.get('emotion', 50)),
                    'hook': float(scores.get('hook', 50)),
                    'completeness': float(scores.get('completeness', 50))
                }
            else:
                # Fallback: extract numbers
                import re
                numbers = re.findall(r'\b\d+\b', output)
                numbers = [int(n) for n in numbers if 0 <= int(n) <= 100]
                
                if len(numbers) >= 4:
                    return {
                        'virality': float(numbers[0]),
                        'emotion': float(numbers[1]),
                        'hook': float(numbers[2]),
                        'completeness': float(numbers[3])
                    }
                else:
                    return self._default_scores()
                    
        except Exception as e:
            self.logger.warning(f"Error parsing LLM scores: {str(e)}")
            return self._default_scores()
    
    def _default_scores(self) -> Dict:
        """Return default scores if LLM fails."""
        return {
            'virality': 50.0,
            'emotion': 50.0,
            'hook': 50.0,
            'completeness': 50.0
        }



