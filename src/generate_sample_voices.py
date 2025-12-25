#!/usr/bin/env python3
"""
Generate sample voice files using pyttsx3 (Windows SAPI voices) for evaluation.
These can be used as reference audio for Chatterbox voice cloning.
"""

import os
import sys
import pyttsx3
from pydub import AudioSegment

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import VOICES_DIR, DEFAULT_SAMPLE_RATE

# Sample texts that showcase natural, energetic speech (10-15 seconds when spoken)
SAMPLE_TEXTS = {
    "emma_young_female": """Hi! I'm so excited to tell you about this amazing opportunity.
        Technology has completely transformed the way we work, and I think you're going to
        love what's coming next.""",

    "narrator_friendly": """Welcome to this incredible journey. Let me paint you a picture
        of a world where anything is possible, where dreams become reality through innovation
        and determination.""",

    "maxim_calm_male": """Listen carefully, my friend. What I'm about to share with you will
        change everything you thought you knew about the future of work and technology.""",

    "amara_warm_female": """Good morning everyone! Today we're going to explore something
        truly special together. I hope you're as excited as I am to dive into this
        adventure.""",

    "tyler_teen_male": """Hey guys! So I've been thinking about this a lot lately, and I
        really want to share my thoughts with you about what's happening in the world right
        now.""",
}

def list_available_voices():
    """List all available voices on the system."""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    print(f"\nFound {len(voices)} voices on your system:\n")

    female_voices = []
    male_voices = []

    for i, voice in enumerate(voices):
        voice_info = {
            'id': voice.id,
            'name': voice.name,
            'index': i
        }

        # Try to categorize by gender based on name
        name_lower = voice.name.lower()
        if any(word in name_lower for word in ['female', 'zira', 'hazel', 'susan', 'aria', 'jenny']):
            female_voices.append(voice_info)
        else:
            male_voices.append(voice_info)

    print("FEMALE VOICES:")
    for v in female_voices:
        print(f"  [{v['index']}] {v['name']}")

    print("\nMALE VOICES:")
    for v in male_voices:
        print(f"  [{v['index']}] {v['name']}")

    engine.stop()
    return voices

def generate_voice_sample(text, voice_id, output_name, rate=200, volume=0.9):
    """
    Generate a voice sample using pyttsx3.

    Args:
        text: Text to speak
        voice_id: Voice ID from pyttsx3
        output_name: Output filename (without extension)
        rate: Speech rate (words per minute, default 200 for energetic)
        volume: Volume level (0.0 to 1.0)
    """
    try:
        # Initialize engine
        engine = pyttsx3.init()

        # Set voice
        engine.setProperty('voice', voice_id)

        # Set rate (higher = faster = more energetic)
        engine.setProperty('rate', rate)

        # Set volume
        engine.setProperty('volume', volume)

        # Generate temp file
        temp_path = os.path.join(VOICES_DIR, f"{output_name}_temp.wav")
        engine.save_to_file(text, temp_path)
        engine.runAndWait()

        # Convert to 24kHz (Chatterbox requirement)
        audio = AudioSegment.from_wav(temp_path)
        audio = audio.set_frame_rate(DEFAULT_SAMPLE_RATE)

        # Export final file
        final_path = os.path.join(VOICES_DIR, f"{output_name}.wav")
        audio.export(final_path, format="wav")

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        duration = len(audio) / 1000.0  # Convert to seconds
        print(f"  Generated: {output_name}.wav ({duration:.1f}s, {DEFAULT_SAMPLE_RATE}Hz)")

        # Save metadata
        metadata_path = os.path.join(VOICES_DIR, f"{output_name}_info.txt")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            f.write(f"Voice Sample: {output_name}\n")
            f.write(f"Duration: {duration:.2f} seconds\n")
            f.write(f"Sample Rate: {DEFAULT_SAMPLE_RATE} Hz\n")
            f.write(f"Speech Rate: {rate} WPM\n")
            f.write(f"Volume: {volume}\n")
            f.write(f"\nText:\n{text}\n")

        return True

    except Exception as e:
        print(f"  ERROR: Failed to generate {output_name}: {e}")
        return False

def main():
    """Generate voice samples using available system voices."""
    print("\n" + "="*70)
    print("Voice Sample Generator")
    print("Generating young, energetic voice samples for TTS")
    print("="*70)

    # Create voices directory
    os.makedirs(VOICES_DIR, exist_ok=True)
    print(f"\nOutput directory: {VOICES_DIR}")

    # List available voices
    voices = list_available_voices()

    if len(voices) == 0:
        print("\nERROR: No voices found on system!")
        return

    print("\n" + "="*70)
    print("Generating Sample Voices")
    print("="*70)

    # Select best voices (prefer higher-quality neural voices if available)
    # Try to find young-sounding, clear voices
    female_voice = None
    male_voice = None

    for voice in voices:
        name_lower = voice.name.lower()
        # Look for common young-sounding female voices
        if not female_voice and any(word in name_lower for word in ['aria', 'jenny', 'zira', 'hazel']):
            female_voice = voice
        # Look for common young-sounding male voices
        if not male_voice and any(word in name_lower for word in ['david', 'mark', 'guy']):
            male_voice = voice

    # Fallback to first available
    if not female_voice and len(voices) > 0:
        female_voice = voices[0]
    if not male_voice and len(voices) > 1:
        male_voice = voices[1]
    elif not male_voice and len(voices) > 0:
        male_voice = voices[0]

    print(f"\nUsing female voice: {female_voice.name if female_voice else 'None'}")
    print(f"Using male voice: {male_voice.name if male_voice else 'None'}")

    # Generate samples
    successful = 0
    total = 0

    print("\nGenerating voice samples...")

    # Emma - Young female, energetic (faster rate)
    if female_voice:
        total += 1
        if generate_voice_sample(
            SAMPLE_TEXTS["emma_young_female"],
            female_voice.id,
            "emma_young_american_female",
            rate=220,  # Faster = more energetic
            volume=0.95
        ):
            successful += 1

    # Narrator - Friendly, professional (moderate rate)
    if female_voice:
        total += 1
        if generate_voice_sample(
            SAMPLE_TEXTS["narrator_friendly"],
            female_voice.id,
            "narrator_friendly_neutral",
            rate=180,  # Slower = more measured
            volume=0.9
        ):
            successful += 1

    # Maxim - Calm male (slower rate)
    if male_voice:
        total += 1
        if generate_voice_sample(
            SAMPLE_TEXTS["maxim_calm_male"],
            male_voice.id,
            "maxim_male_russian",
            rate=170,  # Slower = more authoritative
            volume=0.9
        ):
            successful += 1

    # Amara - Warm female (moderate rate)
    if female_voice:
        total += 1
        if generate_voice_sample(
            SAMPLE_TEXTS["amara_warm_female"],
            female_voice.id,
            "amara_female_kenyan",
            rate=190,
            volume=0.92
        ):
            successful += 1

    # Tyler - Teen male (fastest rate)
    if male_voice:
        total += 1
        if generate_voice_sample(
            SAMPLE_TEXTS["tyler_teen_male"],
            male_voice.id,
            "tyler_teen_male",
            rate=230,  # Fastest = most energetic/youthful
            volume=0.95
        ):
            successful += 1

    # Summary
    print("\n" + "="*70)
    print("GENERATION COMPLETE")
    print("="*70)
    print(f"Generated: {successful}/{total} voice samples")
    print(f"\nFiles saved to: {VOICES_DIR}")
    print("\nGenerated voices:")
    for filename in os.listdir(VOICES_DIR):
        if filename.endswith('.wav'):
            filepath = os.path.join(VOICES_DIR, filename)
            size_kb = os.path.getsize(filepath) / 1024
            print(f"  - {filename} ({size_kb:.1f} KB)")

    print("\nNext steps:")
    print("1. Listen to the voice samples to evaluate quality")
    print("2. If quality is good, test with Chatterbox TTS")
    print("3. If quality is poor, download better samples from:")
    print("   - https://ttsfree.com (recommended)")
    print("   - https://freetts.com")
    print("   - See voices/VOICE_DOWNLOAD_GUIDE.md for full instructions")
    print("\n4. Test with: cd src && ../venv/Scripts/python audio_generator.py")

if __name__ == "__main__":
    main()
