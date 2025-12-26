"""
Configuration settings for novel scene image generation system.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Look for .env in project root (parent of src/)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Paths (relative to project root)
CHAPTER_DIR = "../docs/manuscript"
OUTPUT_DIR = "../images"
LOG_DIR = "../logs"
PROMPT_CACHE_DIR = "../prompt_cache"

# Audio directories
AUDIO_DIR = "../audio"
AUDIO_CACHE_DIR = "../audio_cache"
VOICES_DIR = "../voices"

# Video directories
VIDEO_DIR = "../videos"

# Temporary directories
TEMP_DIR = "../temp"

# Video generation parameters
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 30
VIDEO_CODEC_CPU = 'libx264'
VIDEO_CODEC_GPU = 'h264_nvenc'
VIDEO_PRESET_CPU = 'medium'
VIDEO_PRESET_GPU = 'p5'  # NVENC preset p5 ≈ x264 'medium'
VIDEO_CRF = 18
VIDEO_AUDIO_CODEC = 'aac'
ENABLE_GPU_ENCODING = True  # Auto-fallback to CPU if unavailable

# Character reference directories
CHARACTER_REFERENCES_DIR = "../character_references"

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PROMPT_CACHE_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)
os.makedirs(VOICES_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(CHARACTER_REFERENCES_DIR, exist_ok=True)

# Model settings
DEFAULT_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
DEVICE = "cuda"

# Generation parameters
# SDXL is trained on 1024x1024 - deviating too far causes distortion
# Using 1024x1024 for best quality, will be letterboxed in video if needed
DEFAULT_WIDTH = 1024
DEFAULT_HEIGHT = 1024
DEFAULT_STEPS = 35  # Increased for better quality (was 30)
DEFAULT_GUIDANCE = 7.5

# Style template - Graphic novel style with clarity focus
BASE_STYLE = "clean graphic novel illustration, professional comic book art, sharp focus, highly detailed, clear composition, bold clean lines, single subject focus, uncluttered background, high contrast"

# Negative prompt - Avoid clutter and distortion
NEGATIVE_PROMPT = "cluttered, messy, chaotic, multiple subjects, busy background, blurry, out of focus, low quality, distorted, disfigured, ugly, amateur, unclear, confusing composition, extra limbs, deformed anatomy, watermark, signature, text, oversaturated"

# Chapter mapping (zero-padded numeric strings to integers)
# Format: "01" -> 1, "02" -> 2, etc.
CHAPTER_NAMES = {
    "01": 1,
    "02": 2,
    "03": 3,
    "04": 4,
    "05": 5,
    "06": 6,
    "07": 7,
    "08": 8,
    "09": 9,
    "10": 10,
    "11": 11,
    "12": 12,
}

# Audio generation parameters
DEFAULT_AUDIO_FORMAT = "wav"
DEFAULT_SAMPLE_RATE = 22050
DEFAULT_TTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
MAX_TTS_CHUNK_SIZE = 240  # Characters per TTS call (under 250 char limit for Coqui TTS)

# Get project root (parent of src/) for absolute path resolution
PROJECT_ROOT = Path(__file__).parent.parent

# Character-to-voice mapping (relative paths, will be converted to absolute)
_VOICE_FILES = {
    "narrator": "voices/male_young_friendly.wav",
    "emma": "voices/female_young_bright.wav",
    "maxim": "voices/male_young_friendly.wav",
    "amara": "voices/male_young_friendly.wav",
    "tyler": "voices/male_young_friendly.wav",
    "elena": "voices/male_young_friendly.wav",
    # Secondary characters
    "mark": "voices/male_young_friendly.wav",
    "diane": "voices/male_young_friendly.wav",
    "ramirez": "voices/male_young_friendly.wav",
}

# Convert all voice file paths to absolute paths
# This ensures voice cloning works regardless of current working directory
CHARACTER_VOICES = {
    char: str(PROJECT_ROOT / path)
    for char, path in _VOICE_FILES.items()
}

# XTTS v2 built-in speaker mapping (used when voice files don't exist)
# These are pre-trained speaker voices available in XTTS v2
CHARACTER_SPEAKERS = {
    "narrator": "Claribel Dervla",  # Young, upbeat female voice - energetic and clear
    "emma": "Sofia Hellen",  # Warm, professional female - perfect for friendly manager
    "maxim": "Viktor Eka",  # Deep, authoritative male voice
    "amara": "Daisy Studious",  # Intelligent, warm female voice
    "tyler": "Royston Min",  # Young, energetic male voice
    "elena": "Elisabeth Whitmore",  # Mature, wise female voice
    "mark": "Dionisio Schuyler",  # Neutral male voice
    "diane": "Tanja Adelina",  # Professional female voice
    "ramirez": "Claribel Dervla",  # Default voice
}

# LLM configuration for prompt generation
# Ollama settings (local LLM)
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.1:8b"

# Anthropic Claude settings (API-based LLM)
# Set ANTHROPIC_API_KEY environment variable to use Claude Haiku
ANTHROPIC_MODEL = "claude-3-5-haiku-20241022"
ANTHROPIC_MAX_TOKENS = 200  # Prompts are short, 200 tokens is plenty

# Claude Haiku 3.5 pricing (as of January 2025)
# Source: https://platform.claude.com/docs/en/about-claude/pricing
HAIKU_INPUT_COST_PER_MILLION = 0.80   # $0.80 per million input tokens
HAIKU_OUTPUT_COST_PER_MILLION = 4.00  # $4.00 per million output tokens

# Visual change detection settings (for smart image generation)
ENABLE_SMART_DETECTION = False  # Opt-in initially, set to True once validated
FORCE_NEW_IMAGE_AT_SCENE_START = True  # Always generate new image at scene boundaries
IMAGE_MAPPING_DIR = "../audio_cache"  # Directory for image-audio mapping metadata

# IP-Adapter settings (for character consistency)
IP_ADAPTER_MODEL = "h94/IP-Adapter-FaceID"
IP_ADAPTER_SUBFOLDER = ""  # FaceID weights are in root directory
IP_ADAPTER_WEIGHT_NAME = "ip-adapter-faceid-plusv2_sdxl.bin"  # Correct weight file for FaceID Plus V2 SDXL
IP_ADAPTER_SCALE_DEFAULT = 0.75  # How strongly to apply IP-Adapter (0.0-1.0)
FACEID_SCALE_DEFAULT = 0.6  # How strongly to apply FaceID guidance (0.0-1.0)
ENABLE_IP_ADAPTER = True  # Enable by default for character consistency

# Multi-reference settings (for improved character consistency)
MAX_REFERENCE_IMAGES = 5  # Use up to 5 references (research-backed optimum)
REFERENCE_EMBEDDING_AVERAGING = True  # Average multiple reference embeddings for robust representation
