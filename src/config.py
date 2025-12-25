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
    "12": 12
}

# Audio generation parameters
DEFAULT_AUDIO_FORMAT = "wav"
DEFAULT_SAMPLE_RATE = 22050
DEFAULT_TTS_MODEL = "tts_models/multilingual/multi-dataset/xtts_v2"
MAX_TTS_CHUNK_SIZE = 240  # Characters per TTS call (under 250 char limit for Coqui TTS)

# Character-to-voice mapping (for voice cloning with reference files)
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

# XTTS v2 built-in speaker mapping (used when voice files don't exist)
# These are pre-trained speaker voices available in XTTS v2
CHARACTER_SPEAKERS = {
    "narrator": "Claribel Dervla",    # Young, upbeat female voice - energetic and clear
    "emma": "Sofia Hellen",           # Warm, professional female - perfect for friendly manager
    "maxim": "Viktor Eka",            # Deep, authoritative male voice
    "amara": "Daisy Studious",        # Intelligent, warm female voice
    "tyler": "Royston Min",           # Young, energetic male voice
    "elena": "Elisabeth Whitmore",    # Mature, wise female voice
    "mark": "Dionisio Schuyler",      # Neutral male voice
    "diane": "Tanja Adelina",         # Professional female voice
    "ramirez": "Claribel Dervla"      # Default voice
}
