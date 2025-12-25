"""
Configuration settings for novel scene image generation system.
"""

import os

# Paths (relative to project root)
CHAPTER_DIR = "../docs/manuscript"
OUTPUT_DIR = "../images"
LOG_DIR = "../logs"
PROMPT_CACHE_DIR = "../prompt_cache"

# Audio directories
AUDIO_DIR = "../audio"
AUDIO_CACHE_DIR = "../audio_cache"
VOICES_DIR = "../voices"

# Ensure directories exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PROMPT_CACHE_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)
os.makedirs(VOICES_DIR, exist_ok=True)

# Model settings
DEFAULT_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
DEVICE = "cuda"

# Generation parameters
# 9:16 Vertical (Portrait) format - optimized for mobile viewing and YouTube Shorts
DEFAULT_WIDTH = 1080
DEFAULT_HEIGHT = 1920
DEFAULT_STEPS = 30
DEFAULT_GUIDANCE = 7.5

# Style template - Graphic novel style (optimized for 77-token limit)
BASE_STYLE = "graphic novel art, detailed linework, cel shading, dramatic lighting"

# Negative prompt - Avoid photorealism and low quality
NEGATIVE_PROMPT = "photorealistic, photo, photograph, 3d render, blurry, low quality, distorted anatomy, extra limbs, deformed, ugly, oversaturated, watermark, signature, amateur, sketch, unfinished"

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
    "12": 12
}

# Audio generation parameters
DEFAULT_AUDIO_FORMAT = "wav"
DEFAULT_SAMPLE_RATE = 22050
DEFAULT_TTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
MAX_TTS_CHUNK_SIZE = 240  # Characters per TTS call (under 250 char limit for Coqui TTS)

# Character-to-voice mapping
CHARACTER_VOICES = {
    "narrator": "voices/narrator_neutral.wav",
    "emma": "voices/emma_american.wav",
    "maxim": "voices/maxim_russian.wav",
    "amara": "voices/amara_kenyan.wav",
    "tyler": "voices/tyler_teen.wav",
    "elena": "voices/elena_russian.wav",
    # Secondary characters fall back to narrator
    "mark": "voices/narrator_neutral.wav",
    "diane": "voices/narrator_neutral.wav",
    "ramirez": "voices/narrator_neutral.wav"
}
