# File: main.py

import os
import sys
import yaml
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from modules.video_processor import VideoProcessor
from modules.transcriber import Transcriber
from modules.ai_analyzer import AIAnalyzer
from modules.clip_selector import ClipSelector
from modules.video_editor import VideoEditor
from modules.content_generator import ContentGenerator
from modules.subtitle_generator_modern import ModernSubtitleGenerator
from modules.uploader import Uploader
from utils.logger import setup_logger
from utils.validators import validate_input_video


class AIClipper:
    """Main orchestrator for AI Clipper application."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize AI Clipper with configuration."""
        self.config = self._load_config(config_path)
        self.logger = setup_logger(
            level=self.config['logging']['level'],
            log_file=self.config['logging']['file'],
            console=self.config['logging']['console_output']
        )
        
        # Initialize modules
        self.video_processor = VideoProcessor(self.config, self.logger)
        self.transcriber = Transcriber(self.config, self.logger)
        self.ai_analyzer = AIAnalyzer(self.config, self.logger)
        self.clip_selector = ClipSelector(self.config, self.logger)
        self.video_editor = VideoEditor(self.config, self.logger)
        self.content_generator = ContentGenerator(self.config, self.logger)
        self.subtitle_generator = ModernSubtitleGenerator(self.config, self.logger)
        self.uploader = Uploader(self.config, self.logger)
        
        self.logger.info("AI Clipper initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            sys.exit(1)
    
    def process_video(self, video_path: str, output_dir: Optional[str] = None) -> Dict:
        """
        Main processing pipeline for a video.
        
        Args:
            video_path: Path to input video file
            output_dir: Optional custom output directory
            
        Returns:
            Dictionary with processing results and output paths
        """
        try:
            # Step 1: Validate input
            self.logger.info(f"Processing video: {video_path}")
            validate_input_video(video_path, self.config, self.logger)
            
            # Step 2: Setup output directory
            if output_dir is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                video_name = Path(video_path).stem
                output_dir = os.path.join(
                    self.config['output']['base_dir'],
                    f"{video_name}_{timestamp}"
                )
            os.makedirs(output_dir, exist_ok=True)
            self.logger.info(f"Output directory: {output_dir}")
            
            # Step 3: Extract audio
            self.logger.info("Step 1/8: Extracting audio...")
            audio_path = self.video_processor.extract_audio(video_path)
            
            # Step 4: Transcribe
            self.logger.info("Step 2/8: Transcribing audio...")
            transcript = self.transcriber.transcribe(audio_path)
            
            # Save transcript
            transcript_path = os.path.join(output_dir, "transcript.json")
            self.transcriber.save_transcript(transcript, transcript_path)
            
            # Step 5: AI Analysis
            self.logger.info("Step 3/8: Analyzing content with AI...")
            candidates = self.ai_analyzer.generate_candidates(transcript)
            scored_candidates = self.ai_analyzer.score_candidates(candidates)
            
            # Step 6: Select best clips
            self.logger.info("Step 4/8: Selecting best clips...")
            selected_clips = self.clip_selector.select_clips(scored_candidates)
            
            if not selected_clips:
                self.logger.error("No suitable clips found!")
                return {"success": False, "error": "No clips selected"}
            
            self.logger.info(f"Selected {len(selected_clips)} clips")
            
            # Step 7: Cut and edit videos with MODERN SUBTITLES
            self.logger.info("Step 5/8: Cutting and editing videos...")
            edited_clips = []
            
            for idx, clip in enumerate(selected_clips, 1):
                self.logger.info(f"Processing clip {idx}/{len(selected_clips)}...")
                
                # Cut clip
                clip_paths = self.video_editor.cut_clip(
                    video_path=video_path,
                    start_time=clip['start_time'],
                    end_time=clip['end_time'],
                    output_dir=output_dir,
                    clip_index=idx
                )
                
                # Generate clip transcript
                clip_transcript = self._extract_clip_transcript(
                    transcript, 
                    clip['start_time'], 
                    clip['end_time']
                )
                
                # Generate MODERN ANIMATED subtitles for each format
                self.logger.info(f"  Generating modern subtitles for clip {idx}...")
                subtitle_paths = {}
                
                for format_name in clip_paths.keys():
                    # Generate ASS subtitle (animated with karaoke effect)
                    ass_path = self.subtitle_generator.generate_animated_ass(
                        clip_transcript,
                        output_dir,
                        clip_index=idx,
                        video_format=format_name
                    )
                    subtitle_paths[format_name] = ass_path
                
                # Also generate simple SRT (fallback for compatibility)
                srt_path = self.subtitle_generator.generate_simple_srt(
                    clip_transcript,
                    output_dir,
                    clip_index=idx
                )
                
                # Burn subtitles into video
                self.logger.info(f"  Burning subtitles for clip {idx}...")
                final_paths = {}
                
                for format_name, clip_path in clip_paths.items():
                    ass_path = subtitle_paths[format_name]
                    
                    # Use ASS subtitle (supports animations)
                    subtitled_path = self.video_editor.burn_subtitles_ass(
                        clip_path,
                        ass_path,
                        format_name
                    )
                    final_paths[format_name] = subtitled_path
                
                edited_clips.append({
                    'index': idx,
                    'paths': final_paths,
                    'subtitle_ass': subtitle_paths,
                    'subtitle_srt': srt_path,
                    'clip_data': clip
                })
            
            # Step 8: Generate content
            self.logger.info("Step 6/8: Generating captions, titles, and hashtags...")
            for clip_info in edited_clips:
                clip_text = clip_info['clip_data']['text']
                
                content = self.content_generator.generate_all(clip_text)
                clip_info['content'] = content
            
            # Step 9: Save metadata
            self.logger.info("Step 7/8: Saving metadata...")
            metadata_path = os.path.join(output_dir, "metadata.json")
            self._save_metadata(edited_clips, metadata_path)
            
            # Step 10: Prepare for upload (but don't upload)
            self.logger.info("Step 8/8: Preparing upload configurations...")
            upload_configs = self.uploader.prepare_uploads(edited_clips)
            
            upload_config_path = os.path.join(output_dir, "upload_configs.json")
            self.uploader.save_upload_configs(upload_configs, upload_config_path)
            
            # Generate summary
            summary = {
                "success": True,
                "video_input": video_path,
                "output_directory": output_dir,
                "clips_generated": len(edited_clips),
                "transcript_path": transcript_path,
                "metadata_path": metadata_path,
                "upload_configs_path": upload_config_path,
                "clips": edited_clips
            }
            
            # Save summary
            summary_path = os.path.join(output_dir, "SUMMARY.txt")
            self._write_summary(summary, summary_path)
            
            self.logger.info("=" * 60)
            self.logger.info("PROCESSING COMPLETE!")
            self.logger.info(f"Output saved to: {output_dir}")
            self.logger.info(f"Clips generated: {len(edited_clips)}")
            self.logger.info("=" * 60)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error processing video: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _extract_clip_transcript(self, full_transcript: Dict, 
                                  start_time: float, end_time: float) -> List[Dict]:
        """Extract transcript segments for a specific clip."""
        clip_segments = []
        
        for segment in full_transcript['segments']:
            seg_start = segment['start']
            seg_end = segment['end']
            
            # Check if segment overlaps with clip
            if seg_end >= start_time and seg_start <= end_time:
                # Adjust timestamps relative to clip start
                adjusted_segment = segment.copy()
                adjusted_segment['start'] = max(0, seg_start - start_time)
                adjusted_segment['end'] = min(end_time - start_time, seg_end - start_time)
                
                # Adjust word timestamps if available
                if 'words' in adjusted_segment and adjusted_segment['words']:
                    adjusted_words = []
                    for word in adjusted_segment['words']:
                        if word['end'] >= start_time and word['start'] <= end_time:
                            adjusted_word = word.copy()
                            adjusted_word['start'] = max(0, word['start'] - start_time)
                            adjusted_word['end'] = min(end_time - start_time, word['end'] - start_time)
                            adjusted_words.append(adjusted_word)
                    adjusted_segment['words'] = adjusted_words
                
                clip_segments.append(adjusted_segment)
        
        return clip_segments
    
    def _save_metadata(self, clips: List[Dict], output_path: str):
        """Save metadata to JSON file."""
        import json
        
        # Convert to JSON-serializable format
        serializable_clips = []
        for clip in clips:
            serializable_clip = {
                'index': clip['index'],
                'paths': clip['paths'],
                'subtitle_ass': clip['subtitle_ass'],
                'subtitle_srt': clip['subtitle_srt'],
                'content': clip.get('content', {}),
                'clip_data': {
                    'start_time': clip['clip_data']['start_time'],
                    'end_time': clip['clip_data']['end_time'],
                    'duration': clip['clip_data']['duration'],
                    'text': clip['clip_data']['text'],
                    'scores': clip['clip_data'].get('scores', {})
                }
            }
            serializable_clips.append(serializable_clip)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_clips, f, indent=2, ensure_ascii=False)
    
    def _write_summary(self, summary: Dict, output_path: str):
        """Write human-readable summary file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("AI CLIPPER - PROCESSING SUMMARY\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Input Video: {summary['video_input']}\n")
            f.write(f"Output Directory: {summary['output_directory']}\n")
            f.write(f"Clips Generated: {summary['clips_generated']}\n\n")
            
            f.write("-" * 70 + "\n")
            f.write("GENERATED CLIPS\n")
            f.write("-" * 70 + "\n\n")
            
            for clip in summary['clips']:
                idx = clip['index']
                content = clip.get('content', {})
                
                f.write(f"CLIP #{idx}\n")
                f.write(f"  Title: {content.get('title', 'N/A')}\n")
                f.write(f"  Caption: {content.get('caption', 'N/A')}\n")
                f.write(f"  Hashtags: {' '.join(content.get('hashtags', []))}\n")
                f.write(f"  Files:\n")
                for format_name, path in clip['paths'].items():
                    f.write(f"    - {format_name}: {path}\n")
                f.write(f"  Subtitles:\n")
                for format_name, ass_path in clip['subtitle_ass'].items():
                    f.write(f"    - ASS ({format_name}): {ass_path}\n")
                f.write(f"    - SRT (simple): {clip['subtitle_srt']}\n")
                f.write("\n")
            
            f.write("-" * 70 + "\n")
            f.write("SUBTITLE FEATURES\n")
            f.write("-" * 70 + "\n")
            f.write("+ Modern animated subtitles with karaoke effect\n")
            f.write("+ Word-by-word highlighting (active word = purple)\n")
            f.write("+ 2-3 words per line for readability\n")
            f.write("+ Smart word grouping with punctuation detection\n")
            f.write("+ Optimized for both Shorts (9:16) and YouTube (16:9)\n\n")
            
            f.write("-" * 70 + "\n")
            f.write("NEXT STEPS\n")
            f.write("-" * 70 + "\n")
            f.write("1. Review generated clips\n")
            f.write("2. Check upload_configs.json for API upload configuration\n")
            f.write("3. Run uploader module with appropriate credentials\n")
            f.write("4. Monitor upload status\n")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Clipper - Automatically create viral clips from long videos"
    )
    parser.add_argument(
        "video",
        help="Path to input video file"
    )
    parser.add_argument(
        "-c", "--config",
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Custom output directory (optional)"
    )
    
    args = parser.parse_args()
    
    # Initialize and run
    clipper = AIClipper(config_path=args.config)
    result = clipper.process_video(args.video, args.output)
    
    if result['success']:
        print("\n" + "="*60)
        print("SUCCESS! Processing completed successfully!")
        print("="*60)
        print(f"\nOutput directory: {result['output_directory']}")
        print(f"Clips generated: {result['clips_generated']}")
        print(f"\nFeatures:")
        print("  + Modern animated subtitles")
        print("  + Word-by-word purple highlighting")
        print("  + 2-3 words per line")
        print("  + Optimized for viral content")
        print("\n" + "="*60)
        sys.exit(0)
    else:
        print(f"\nERROR: Processing failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()