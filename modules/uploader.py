import json
from typing import Dict, List


class Uploader:
    """Prepares upload configurations for social media platforms."""

    def __init__(self, config: Dict, logger):
        self.config = config
        self.logger = logger

    def prepare_uploads(self, clips: List[Dict]) -> List[Dict]:
        """
        Prepare upload configurations for all clips.

        Args:
            clips: List of clip information dictionaries

        Returns:
            List of upload configuration dictionaries
        """
        try:
            self.logger.info("Preparing upload configurations...")

            upload_configs = []

            for clip in clips:
                platform_config = {
                    'clip_index': clip['index'],
                    'platforms': {}
                }

                # YouTube
                if self.config['upload']['youtube']['enabled']:
                    platform_config['platforms']['youtube'] = self._prepare_youtube(clip)

                # TikTok
                if self.config['upload']['tiktok']['enabled']:
                    platform_config['platforms']['tiktok'] = self._prepare_tiktok(clip)

                # Instagram
                if self.config['upload']['instagram']['enabled']:
                    platform_config['platforms']['instagram'] = self._prepare_instagram(clip)

                upload_configs.append(platform_config)

            return upload_configs

        except Exception as e:
            self.logger.error(f"Error preparing uploads: {str(e)}")
            raise

    # ======================== PLATFORM PREPARATION ========================

    def _prepare_youtube(self, clip: Dict) -> Dict:
        """Prepare YouTube upload configuration."""

        content = clip['content']
        video_path = clip['paths']['shorts']  # Using shorts format

        return {
            'video_file': video_path,
            'title': content['title'],
            'description': content['description'],
            'tags': [tag.replace('#', '') for tag in content['hashtags']],
            'category_id': self.config['upload']['youtube']['category_id'],
            'privacy_status': self.config['upload']['youtube']['privacy'],
            'api_endpoint': 'https://www.googleapis.com/upload/youtube/v3/videos',
            'instructions': self._youtube_instructions()
        }

    def _prepare_tiktok(self, clip: Dict) -> Dict:
        """Prepare TikTok upload configuration."""

        content = clip['content']
        video_path = clip['paths']['shorts']

        return {
            'video_file': video_path,
            'caption': f"{content['caption']} {' '.join(content['hashtags'])}",
            'privacy_level': self.config['upload']['tiktok']['privacy'],
            'api_endpoint': 'https://open-api.tiktok.com/share/video/upload/',
            'instructions': self._tiktok_instructions()
        }

    def _prepare_instagram(self, clip: Dict) -> Dict:
        """Prepare Instagram upload configuration."""

        content = clip['content']
        video_path = clip['paths']['shorts']

        return {
            'video_file': video_path,
            'caption': f"{content['caption']} {' '.join(content['hashtags'])}",
            'location_id': self.config['upload']['instagram']['location_id'],
            'api_endpoint': 'https://graph.facebook.com/v18.0/me/media',
            'instructions': self._instagram_instructions()
        }

    # ======================== SAVE FUNCTION ========================

    def save_upload_configs(self, configs: List[Dict], output_path: str):
        """Save upload configurations to JSON file."""

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(configs, f, indent=2, ensure_ascii=False)

        self.logger.info(f"✅ Upload configurations saved: {output_path}")

    # ======================== INSTRUCTIONS ========================

    def _youtube_instructions(self) -> str:
        return """
1. Go to Google Cloud Console
2. Create a new project
3. Enable YouTube Data API v3
4. Create OAuth 2.0 credentials
5. Download client_secret.json
6. Use it in uploader module
"""

    def _tiktok_instructions(self) -> str:
        return """
1. Go to https://developers.tiktok.com
2. Create an app
3. Get client_key and secret
4. Enable Video Upload API
5. Use OAuth for publishing
"""

    def _instagram_instructions(self) -> str:
        return """
1. Go to Meta Developer Console
2. Create Facebook App
3. Connect Instagram Business Account
4. Get Page Access Token
5. Use Graph API /media + /publish endpoints
"""
