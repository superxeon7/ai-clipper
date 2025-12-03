
# AI Clipper 🎬✂️

Automatically create viral-ready clips from long videos using AI.

## Overview

AI Clipper is a production-grade Python application that analyzes long-form videos (30-90 minutes) and automatically:
- Extracts the most engaging segments
- Scores content for virality potential
- Cuts and edits clips
- Generates captions, titles, and hashtags
- Prepares videos for TikTok, Instagram Reels, and YouTube Shorts
- Creates upload-ready configurations

## Features

✅ **Speech-to-Text**: Faster-Whisper for accurate transcription with timestamps  
✅ **AI Analysis**: Sentence-transformers + Local LLM (Ollama) for intelligent clip selection  
✅ **Multi-Format Export**: 9:16 (shorts) and 16:9 (YouTube) formats  
✅ **Subtitle Burning**: Automatic caption overlay with modern styling  
✅ **Content Generation**: AI-powered captions, titles, descriptions, and hashtags  
✅ **API Ready**: Prepared upload configurations for YouTube, TikTok, Instagram  
✅ **Modular Architecture**: Easy to extend and customize  
✅ **Production Ready**: Error handling, logging, configuration management  

## System Requirements

### Hardware
- **GPU**: NVIDIA GPU with CUDA support (recommended for Whisper)
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 50GB+ free space for models and processing
- **CPU**: Modern multi-core processor (Intel i7/AMD Ryzen 7+)

### Software
- **OS**: Linux (Ubuntu 20.04+), macOS 12+, Windows 10/11 with WSL2
- **Python**: 3.9 or higher
- **FFmpeg**: 4.4 or higher
- **CUDA**: 11.8+ (for GPU acceleration)
- **Ollama**: Latest version

## Installation

### 1. Install System Dependencies

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install -y ffmpeg python3-pip python3-venv git
```

#### macOS
```bash
brew install ffmpeg python@3.11
```

#### Windows (WSL2)
```bash
sudo apt update && sudo apt install -y ffmpeg python3-pip python3-venv
```

### 2. Install Ollama
```bash
# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama
ollama serve &

# Pull required model
ollama pull llama3.1:8b
```

### 3. Clone and Setup
```bash
# Clone repository (or create new directory with files)
mkdir ai-clipper && cd ai-clipper

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Download Whisper Model

The model will download automatically on first run, but you can pre-download:
```python
from faster_whisper import WhisperModel
model = WhisperModel("large-v3", device="cuda", compute_type="float16")
```

### 5. Create Required Directories
```bash
mkdir -p output temp logs models
```

## Usage

### Basic Usage
```bash
python main.py path/to/your/video.mp4
```

### With Custom Config
```bash
python main.py path/to/video.mp4 --config custom_config.yaml
```

### With Custom Output Directory
```bash
python main.py path/to/video.mp4 --output /path/to/output
```

### Full Example
```bash
# Process a podcast episode
python main.py podcast_episode_142.mp4

# Output will be in: ./output/podcast_episode_142_20241204_153045/
```

## Configuration

Edit `config.yaml` to customize:
```yaml
# Key settings to adjust

transcription:
  model_size: "large-v3"  # Options: tiny, base, small, medium, large-v3
  device: "cuda"          # "cuda" for GPU, "cpu" for CPU
  
ai_analysis:
  top_n_clips: 5          # Number of clips to generate
  min_clip_duration: 15   # Minimum clip length in seconds
  max_clip_duration: 60   # Maximum clip length in seconds

content_generation:
  temperature: 0.7        # LLM creativity (0.0-1.0)
  max_caption_length: 150
```

## Output Structure
````
output/
└── your_video_20241204_153045/
    ├── SUMMARY.txt                    # Human-readable summary
    ├── metadata.json                  # All metadata in JSON
    ├── transcript.json                # Full transcript
    ├── upload_configs.json            # API upload configurations
    ├── clip_01_shorts_final.mp4       # 9:16 format with subtitles
    ├── clip_01_youtube_final.mp4      # 16:9 format with subtitles
    ├── clip_01.srt                    # Subtitle file
    ├── clip_02_shorts_final.mp4
    ├── clip_02_youtube_final.mp4
    ├── clip_02.srt
    └── ...