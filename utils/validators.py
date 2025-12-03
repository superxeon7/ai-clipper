import os
from pathlib import Path


def validate_input_video(video_path: str, config: dict, logger):
    """
    Validate input video file.
    
    Args:
        video_path: Path to video file
        config: Configuration dictionary
        logger: Logger instance
        
    Raises:
        ValueError: If validation fails
    """
    logger.info(f"Validating input video: {video_path}")
    
    # Check file exists
    if not os.path.exists(video_path):
        raise ValueError(f"Video file not found: {video_path}")
    
    # Check file extension
    ext = Path(video_path).suffix.lower().replace('.', '')
    supported = config['video']['supported_formats']
    
    if ext not in supported:
        raise ValueError(
            f"Unsupported video format: {ext}. "
            f"Supported formats: {', '.join(supported)}"
        )
    
    # Check file size (at least 1MB)
    file_size = os.path.getsize(video_path)
    if file_size < 1024 * 1024:
        raise ValueError(f"Video file too small: {file_size} bytes")
    
    logger.info("✓ Video validation passed")