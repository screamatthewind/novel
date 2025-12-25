#!/usr/bin/env python3
"""
Download REAL human voices from VCTK using datasets library streaming.
"""

import os
import sys
from datasets import load_dataset
from pydub import AudioSegment
import io
import random
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import VOICES_DIR, DEFAULT_SAMPLE_RATE

# HF Token - set your own token here or via environment variable
# os.environ['HF_TOKEN'] = 'your_token_here'

# Young speakers to download
SPEAKERS_TO_DOWNLOAD = [
    ("p225", "emma_young_energetic_female", "Young energetic female, 23 years"),
    ("p228", "narrator_female_warm", "Warm female narrator, 22 years"),
    ("p226", "tyler_young_male", "Young energetic male, 22 years"),
    ("p232", "maxim_young_male", "Clear young male, 23 years"),
    ("p230", "amara_bright_female", "Bright friendly female, 22 years"),
]

def download_speaker(speaker_id, output_name, description, target_duration=10, max_samples=30):
    """Download and combine audio samples for a speaker."""
    print(f"\n{'='*70}")
    print(f"Downloading: {output_name} (Speaker {speaker_id})")
    print(f"{'='*70}")

    try:
        print("Loading VCTK dataset with trust_remote_code...")
        dataset = load_dataset(
            "CSTR-Edinburgh/vctk",
            split="train",
            streaming=True,
            trust_remote_code=True
        )

        print(f"Searching for speaker {speaker_id}...")
        samples = []
        count = 0

        for item in dataset:
            if item['speaker_id'] == speaker_id:
                samples.append(item)
                count += 1
                print(f"  Found {count} samples...", end='\r')

                if count >= max_samples:
                    break

        print(f"\n  Found {len(samples)} samples for {speaker_id}")

        if not samples:
            print(f"  [FAIL] No samples found")
            return False

        # Combine audio samples
        print("  Combining audio samples...")
        combined = None
        files_used = 0

        # Shuffle for variety
        random.shuffle(samples)

        for sample in samples:
            try:
                # Get audio data
                audio_dict = sample['audio']
                audio_array = np.array(audio_dict['array'], dtype=np.float32)
                sample_rate = audio_dict['sampling_rate']

                # Convert float array to 16-bit PCM
                audio_array_int = (audio_array * 32767).astype(np.int16)

                # Create AudioSegment
                audio_segment = AudioSegment(
                    audio_array_int.tobytes(),
                    frame_rate=sample_rate,
                    sample_width=2,  # 16-bit
                    channels=1
                )

                if combined is None:
                    combined = audio_segment
                else:
                    # Add small pause
                    pause = AudioSegment.silent(duration=200)
                    combined = combined + pause + audio_segment

                files_used += 1

                # Check duration
                duration_sec = len(combined) / 1000.0
                if duration_sec >= target_duration:
                    break

            except Exception as e:
                print(f"\n    Warning: Skipping sample: {e}")
                continue

        if combined is None:
            print(f"  [FAIL] Could not create audio")
            return False

        # Trim to exact duration
        combined = combined[:target_duration * 1000]

        # Resample to 24kHz
        combined = combined.set_frame_rate(DEFAULT_SAMPLE_RATE)

        # Export
        os.makedirs(VOICES_DIR, exist_ok=True)
        output_path = os.path.join(VOICES_DIR, f"{output_name}.wav")
        combined.export(output_path, format="wav")

        duration = len(combined) / 1000.0
        size_kb = os.path.getsize(output_path) / 1024

        print(f"  [OK] Created: {output_name}.wav")
        print(f"    Duration: {duration:.1f}s | Size: {size_kb:.1f} KB | Samples: {files_used}")

        # Save metadata
        metadata_path = output_path.replace('.wav', '_metadata.txt')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            f.write(f"Voice: {output_name}\n")
            f.write(f"Source: REAL HUMAN VOICE - VCTK Corpus\n")
            f.write(f"Speaker ID: {speaker_id}\n")
            f.write(f"Description: {description}\n")
            f.write(f"Duration: {duration:.2f} seconds\n")
            f.write(f"Sample Rate: {DEFAULT_SAMPLE_RATE} Hz\n")
            f.write(f"Samples Combined: {files_used}\n")
            f.write(f"Dataset: VCTK (University of Edinburgh)\n")
            f.write(f"License: ODC-By v1.0\n")

        return True

    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Download real human voices."""
    print("\n" + "="*70)
    print("REAL HUMAN VOICE DOWNLOADER - VCTK Dataset")
    print("Downloading ACTUAL human recordings (NOT synthetic)")
    print("="*70)

    os.makedirs(VOICES_DIR, exist_ok=True)
    print(f"\nOutput: {VOICES_DIR}")

    successful = 0
    failed = 0

    for speaker_id, output_name, description in SPEAKERS_TO_DOWNLOAD:
        if download_speaker(speaker_id, output_name, description):
            successful += 1
        else:
            failed += 1

    # Summary
    print("\n" + "="*70)
    print("DOWNLOAD COMPLETE")
    print("="*70)
    print(f"[OK] Successful: {successful}")
    print(f"[FAIL] Failed: {failed}")

    if successful > 0:
        print(f"\nReal human voices saved to: {VOICES_DIR}")
        print("\nVoice files:")
        for f in sorted(os.listdir(VOICES_DIR)):
            if f.endswith('.wav'):
                size_kb = os.path.getsize(os.path.join(VOICES_DIR, f)) / 1024
                print(f"  - {f} ({size_kb:.1f} KB)")

        print("\n" + "="*70)
        print("THESE ARE REAL HUMAN VOICES!")
        print("="*70)
        print("Source: VCTK Corpus (University of Edinburgh)")
        print("Speakers: Real people aged 22-23")
        print("Quality: Professional studio recordings")

        print("\nNext steps:")
        print("1. Listen to evaluate quality")
        print("2. Test: cd src && ../venv/Scripts/python audio_generator.py")

if __name__ == "__main__":
    main()
