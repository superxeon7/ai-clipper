import requests
from typing import Dict

from prompts.caption_prompt import CAPTION_PROMPT
from prompts.title_prompt import TITLE_PROMPT
from prompts.hashtag_prompt import HASHTAG_PROMPT


class ContentGenerator:
    """Generates captions, titles, descriptions, and hashtags using LLM."""
    
    def __init__(self, config: Dict, logger):
        self.config = config
        self.logger = logger
        self.ollama_host = config['ai_analysis']['ollama_host']
        self.llm_model = config['ai_analysis']['llm_model']
        self.temperature = config['content_generation']['temperature']
    
    def generate_all(self, clip_text: str) -> Dict:
        """
        Generate all content for a clip.
        
        Args:
            clip_text: Text content of the clip
            
        Returns:
            Dictionary with caption, title, description, and hashtags
        """
        try:
            self.logger.info("Generating content...")
            
            caption = self.generate_caption(clip_text)
            title = self.generate_title(clip_text)
            description = self.generate_description(clip_text)
            hashtags = self.generate_hashtags(clip_text)
            
            return {
                'caption': caption,
                'title': title,
                'description': description,
                'hashtags': hashtags
            }
            
        except Exception as e:
            self.logger.error(f"Error generating content: {str(e)}")
            raise
    
    def generate_caption(self, clip_text: str) -> str:
        """Generate short caption for social media."""
        prompt = CAPTION_PROMPT.format(
            content=clip_text,
            max_length=self.config['content_generation']['max_caption_length']
        )
        return self._call_llm(prompt).strip()
    
    def generate_title(self, clip_text: str) -> str:
        """Generate title for the clip."""
        prompt = TITLE_PROMPT.format(
            content=clip_text,
            max_length=self.config['content_generation']['max_title_length']
        )
        return self._call_llm(prompt).strip()
    
    def generate_description(self, clip_text: str) -> str:
        """Generate longer description."""
        prompt = f"""Based on this video content, write a compelling description for social media (max {self.config['content_generation']['max_description_length']} characters):

Content: {clip_text}

Write a description that:
1. Hooks the viewer in the first sentence
2. Provides context
3. Encourages engagement
4. Is optimized for the platform

Description:"""
        return self._call_llm(prompt).strip()
    
    def generate_hashtags(self, clip_text: str) -> list:
        """Generate relevant hashtags."""
        prompt = HASHTAG_PROMPT.format(
            content=clip_text,
            num_hashtags=self.config['content_generation']['num_hashtags']
        )
        response = self._call_llm(prompt).strip()
        
        # Parse hashtags
        hashtags = []
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                hashtags.extend([tag.strip() for tag in line.split() if tag.startswith('#')])
        
        # Ensure we have the right number
        if len(hashtags) < self.config['content_generation']['num_hashtags']:
            # Add generic ones
            generic = ['#viral', '#trending', '#fyp', '#foryou', '#explore']
            hashtags.extend(generic[:self.config['content_generation']['num_hashtags'] - len(hashtags)])
        
        return hashtags[:self.config['content_generation']['num_hashtags']]
    
    def _call_llm(self, prompt: str) -> str:
        """Call Ollama API."""
        try:
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.llm_model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": self.temperature
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                self.logger.warning(f"Ollama API error: {response.status_code}")
                return ""
                
        except Exception as e:
            self.logger.warning(f"Error calling LLM: {str(e)}")
            return ""