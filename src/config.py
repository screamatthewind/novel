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
DEFAULT_SAMPLE_RATE = 24000  # Chatterbox uses 24kHz
DEFAULT_TTS_MODEL = "turbo"  # Options: "chatterbox", "multilingual", "turbo"
MAX_TTS_CHUNK_SIZE = 500  # Characters per TTS call (Chatterbox can handle longer chunks)

# Character-to-voice mapping (for voice cloning with reference files)
# Chatterbox TTS uses reference audio files for voice cloning
# Requires 10-second reference audio clips for best results
CHARACTER_VOICES = {
    "narrator": os.path.join(VOICES_DIR, "narrator_neutral.wav"),
    "emma": os.path.join(VOICES_DIR, "emma_american.wav"),
    "maxim": os.path.join(VOICES_DIR, "maxim_russian.wav"),
    "amara": os.path.join(VOICES_DIR, "amara_kenyan.wav"),
    "tyler": os.path.join(VOICES_DIR, "tyler_teen.wav"),
    "elena": os.path.join(VOICES_DIR, "elena_russian.wav"),
    # Secondary characters fall back to narrator
    "mark": os.path.join(VOICES_DIR, "narrator_neutral.wav"),
    "diane": os.path.join(VOICES_DIR, "narrator_neutral.wav"),
    "ramirez": os.path.join(VOICES_DIR, "narrator_neutral.wav")
}

# Note: Chatterbox does not use built-in speakers like Coqui TTS
# All voices require reference audio files for cloning
