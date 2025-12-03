import os
import shutil
from pathlib import Path
from typing import List


def ensure_dir(directory: str):
    """Create directory if it doesn't exist."""
    os.makedirs(directory, exist_ok=True)


def clean_temp_files(temp_dir: str, logger):
    """Clean temporary files."""
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            logger.info(f"Cleaned temp directory: {temp_dir}")
    except Exception as e:
        logger.warning(f"Could not clean temp directory: {str(e)}")


def get_file_size_mb(file_path: str) -> float:
    """Get file size in MB."""
    return os.path.getsize(file_path) / (1024 * 1024)


def list_files_by_extension(directory: str, extensions: List[str]) -> List[str]:
    """List all files with given extensions in directory."""
    files = []
    for ext in extensions:
        pattern = f"*.{ext}"
        files.extend(Path(directory).glob(pattern))
    return [str(f) for f in files]