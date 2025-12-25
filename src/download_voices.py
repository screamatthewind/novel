#!/usr/bin/env python3
"""
Download young, energetic, friendly voice samples from VCTK Corpus for TTS voice cloning.

This script downloads voice samples from the VCTK dataset on Hugging Face,
focusing on young speakers (ages 18-25) with clear, energetic voices.
"""

import os
import sys
from pathlib import Path
from datasets import load_dataset
from pydub import AudioSegment
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import VOICES_DIR, DEFAULT_SAMPLE_RATE

# Curated list of young, energetic, friendly VCTK speakers
# Format: (speaker_id, age, gender, accent, description)
YOUNG_SPEAKERS = [
    # Young American-sounding females (good for Emma)
    ("p269", 20, "female", "Newcastle", "energetic, clear, youthful"),
    ("p240", 21, "female", "Southern England", "friendly, warm, enthusiastic"),
    ("p248", 23, "female", "Irish", "bright, energetic, expressive"),
    ("p252", 22, "female", "London", "clear, friendly, professional"),

    # Young American-sounding males
    ("p254", 21, "male", "Surrey", "energetic, clear, youthful"),
    ("p270", 21, "male", "Yorkshire", "friendly, warm, engaging"),
    ("p226", 22, "male", "Surrey", "professional, clear, energetic"),
    ("p245", 25, "male", "Irish", "expressive, friendly, dynamic"),

    # Additional diverse voices
    ("p262", 23, "female", "Edinburgh", "articulate, friendly, warm"),
    ("p273", 23, "male", "Northern Ireland", "engaging, clear, energetic"),
]

def download_vctk_voice(speaker_id, gender, age, accent, description, target_duration=10):
    """
    Download and prepare a voice sample from VCTK dataset.

    Args:
        speaker_id: VCTK speaker ID (e.g., "p269")
        gender: "male" or "female"
        age: Speaker age
        accent: Speaker accent/region
        description: Voice description
        target_duration: Target duration in seconds (default: 10)
    """
    print(f"\n{'='*70}")
    print(f"Downloading {speaker_id}: {age}y {gender}, {accent}")
    print(f"Description: {description}")
    print(f"{'='*70}")

    try:
        # Load VCTK dataset from Hugging Face
        print("Loading VCTK dataset from Hugging Face...")
        dataset = load_dataset("CSTR-Edinburgh/vctk", split="train", streaming=True)

        # Filter for specific speaker
        speaker_samples = []
        print(f"Searching for speaker {speaker_id} samples...")

        for i, example in enumerate(dataset):
            if example['speaker_id'] == speaker_id:
                speaker_samples.append(example)
                if len(speaker_samples) >= 20:  # Get 20 samples max
                    break

            # Progress indicator
            if i % 1000 == 0:
                print(f"  Processed {i} samples, found {len(speaker_samples)} from {speaker_id}...")

        if not speaker_samples:
            print(f"❌ No samples found for speaker {speaker_id}")
            return False

        print(f"✅ Found {len(speaker_samples)} samples from {speaker_id}")

        # Combine audio segments to reach target duration
        combined_audio = None
        total_duration = 0
        texts = []

        # Shuffle to get variety
        random.shuffle(speaker_samples)

        for sample in speaker_samples:
            # Get audio from sample
            audio_array = sample['audio']['array']
            sample_rate = sample['audio']['sampling_rate']

            # Convert to AudioSegment
            audio_segment = AudioSegment(
                audio_array.tobytes(),
                frame_rate=sample_rate,
                sample_width=audio_array.dtype.itemsize,
                channels=1
            )

            if combined_audio is None:
                combined_audio = audio_segment
            else:
                # Add 200ms silence between sentences
                silence = AudioSegment.silent(duration=200)
                combined_audio = combined_audio + silence + audio_segment

            total_duration = len(combined_audio) / 1000.0  # Convert to seconds
            texts.append(sample['text'])

            if total_duration >= target_duration:
                break

        # Trim to exact target duration
        combined_audio = combined_audio[:target_duration * 1000]

        # Resample to 24kHz (Chatterbox sample rate)
        combined_audio = combined_audio.set_frame_rate(DEFAULT_SAMPLE_RATE)

        # Generate filename
        filename = f"{speaker_id}_{gender}_{age}y_{accent.replace(' ', '_').lower()}.wav"
        output_path = os.path.join(VOICES_DIR, filename)

        # Ensure voices directory exists
        os.makedirs(VOICES_DIR, exist_ok=True)

        # Export
        combined_audio.export(output_path, format="wav")

        print(f"\n✅ Success!")
        print(f"   Duration: {total_duration:.2f} seconds")
        print(f"   Sample rate: {DEFAULT_SAMPLE_RATE} Hz")
        print(f"   Saved to: {output_path}")
        print(f"   Sample text: \"{texts[0][:100]}...\"")

        # Save metadata
        metadata_path = output_path.replace('.wav', '_metadata.txt')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            f.write(f"Speaker ID: {speaker_id}\n")
            f.write(f"Gender: {gender}\n")
            f.write(f"Age: {age}\n")
            f.write(f"Accent: {accent}\n")
            f.write(f"Description: {description}\n")
            f.write(f"Duration: {total_duration:.2f} seconds\n")
            f.write(f"Sample rate: {DEFAULT_SAMPLE_RATE} Hz\n")
            f.write(f"\nText samples:\n")
            for i, text in enumerate(texts[:5], 1):
                f.write(f"{i}. {text}\n")

        return True

    except Exception as e:
        print(f"❌ Error downloading {speaker_id}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Download all young, energetic voice samples."""
    print("\n" + "="*70)
    print("VCTK Voice Sample Downloader")
    print("Downloading young, energetic, friendly voices for TTS")
    print("="*70)

    # Create voices directory if it doesn't exist
    os.makedirs(VOICES_DIR, exist_ok=True)
    print(f"\nOutput directory: {VOICES_DIR}")

    # Download each speaker
    successful = 0
    failed = 0

    for speaker_id, age, gender, accent, description in YOUNG_SPEAKERS:
        success = download_vctk_voice(speaker_id, gender, age, accent, description)
        if success:
            successful += 1
        else:
            failed += 1

    # Summary
    print("\n" + "="*70)
    print("DOWNLOAD COMPLETE")
    print("="*70)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"\nVoice files saved to: {VOICES_DIR}")
    print("\nNext steps:")
    print("1. Listen to the voice samples to evaluate quality")
    print("2. Choose your favorites for different characters")
    print("3. Update config.py CHARACTER_VOICES with selected voices")
    print("4. Test with: cd src && ../venv/Scripts/python audio_generator.py")

if __name__ == "__main__":
    main()
