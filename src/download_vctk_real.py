#!/usr/bin/env python3
"""
Download REAL human voice recordings from VCTK dataset via Hugging Face.

This downloads actual human voice recordings (NOT synthetic) from young, energetic speakers.
"""

import os
import sys
from huggingface_hub import hf_hub_download, list_repo_files
from pydub import AudioSegment
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import VOICES_DIR, DEFAULT_SAMPLE_RATE

# Your HF token - set your own token here or via environment variable
HF_TOKEN = os.environ.get('HF_TOKEN', None)

# Young speakers from VCTK (ages 18-25, energetic voices)
YOUNG_SPEAKERS = [
    # Format: (speaker_id, age, gender, accent, description)
    ("p225", 23, "female", "English", "Clear, professional female"),
    ("p226", 22, "male", "English", "Young energetic male"),
    ("p227", 38, "male", "English", "Professional male"),
    ("p228", 22, "female", "English", "Young friendly female"),
    ("p229", 23, "female", "English", "Energetic young female"),
    ("p230", 22, "female", "English", "Bright young female"),
    ("p231", 23, "female", "English", "Warm young female"),
    ("p232", 23, "male", "English", "Clear young male"),
    ("p233", 23, "female", "English", "Articulate young female"),
    ("p234", 22, "male", "English", "Energetic young male"),
]

def download_speaker_audio(speaker_id, num_files=15):
    """
    Download audio files for a specific speaker from VCTK dataset.

    Args:
        speaker_id: Speaker ID (e.g., "p225")
        num_files: Number of audio files to download

    Returns:
        List of downloaded file paths
    """
    print(f"\nDownloading files for speaker {speaker_id}...")

    try:
        # List all files in the repo
        print("  Fetching file list from Hugging Face...")
        repo_id = "CSTR-Edinburgh/vctk"

        # Try to list files for this speaker
        all_files = list_repo_files(repo_id, token=HF_TOKEN, repo_type="dataset")

        # Filter for this speaker's audio files
        speaker_files = [f for f in all_files if f.startswith(f"wav48_silence_trimmed/{speaker_id}/") and f.endswith(".flac")]

        if not speaker_files:
            print(f"  Warning: No files found for {speaker_id}")
            return []

        print(f"  Found {len(speaker_files)} files for {speaker_id}")

        # Download first N files
        downloaded = []
        for i, file_path in enumerate(speaker_files[:num_files]):
            try:
                print(f"  Downloading {i+1}/{min(num_files, len(speaker_files))}: {file_path}", end='\r')

                local_path = hf_hub_download(
                    repo_id=repo_id,
                    filename=file_path,
                    token=HF_TOKEN,
                    repo_type="dataset"
                )
                downloaded.append(local_path)

            except Exception as e:
                print(f"\n  Warning: Failed to download {file_path}: {e}")
                continue

        print(f"\n  Successfully downloaded {len(downloaded)} files")
        return downloaded

    except Exception as e:
        print(f"  Error downloading speaker {speaker_id}: {e}")
        import traceback
        traceback.print_exc()
        return []

def create_voice_sample(audio_files, output_name, description, target_duration=10):
    """
    Create a voice sample from multiple audio files.

    Args:
        audio_files: List of audio file paths
        output_name: Output filename (without extension)
        description: Voice description
        target_duration: Target duration in seconds
    """
    if not audio_files:
        print(f"  Error: No audio files provided for {output_name}")
        return False

    print(f"\n  Creating voice sample: {output_name}")

    try:
        combined = None
        files_used = []

        # Shuffle for variety
        random.shuffle(audio_files)

        for audio_file in audio_files:
            try:
                # Load FLAC file
                audio = AudioSegment.from_file(audio_file, format="flac")

                # Add to combined
                if combined is None:
                    combined = audio
                else:
                    # Add small pause between sentences
                    silence = AudioSegment.silent(duration=200)
                    combined = combined + silence + audio

                files_used.append(audio_file)

                # Check duration
                duration_sec = len(combined) / 1000.0
                if duration_sec >= target_duration:
                    break

            except Exception as e:
                print(f"    Warning: Skipping file {audio_file}: {e}")
                continue

        if combined is None:
            print(f"  Error: Could not create audio for {output_name}")
            return False

        # Trim to exact duration
        combined = combined[:target_duration * 1000]

        # Resample to 24kHz (Chatterbox requirement)
        combined = combined.set_frame_rate(DEFAULT_SAMPLE_RATE)

        # Export
        output_path = os.path.join(VOICES_DIR, f"{output_name}.wav")
        combined.export(output_path, format="wav")

        duration = len(combined) / 1000.0
        size_kb = os.path.getsize(output_path) / 1024

        print(f"  [OK] Created: {output_name}.wav")
        print(f"    Duration: {duration:.1f}s | Size: {size_kb:.1f} KB | Files: {len(files_used)}")

        # Save metadata
        metadata_path = output_path.replace('.wav', '_metadata.txt')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            f.write(f"Voice Sample: {output_name}\n")
            f.write(f"Source: REAL HUMAN VOICE - VCTK Corpus\n")
            f.write(f"Description: {description}\n")
            f.write(f"Duration: {duration:.2f} seconds\n")
            f.write(f"Sample Rate: {DEFAULT_SAMPLE_RATE} Hz\n")
            f.write(f"Files Combined: {len(files_used)}\n")
            f.write(f"Dataset: VCTK (University of Edinburgh)\n")
            f.write(f"License: Open Data Commons Attribution License (ODC-By) v1.0\n")

        return True

    except Exception as e:
        print(f"  Error creating sample: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Download real human voices from VCTK."""
    print("\n" + "="*70)
    print("REAL HUMAN VOICE DOWNLOADER - VCTK Dataset")
    print("Downloading actual human recordings from young speakers")
    print("="*70)

    os.makedirs(VOICES_DIR, exist_ok=True)
    print(f"\nOutput directory: {VOICES_DIR}")
    print(f"Hugging Face authentication: {'OK - Token provided' if HF_TOKEN else 'ERROR - No token'}")

    successful = 0
    failed = 0

    print("\n" + "="*70)
    print("Downloading Young Speaker Voices")
    print("="*70)

    # Download a selection of young voices
    voices_to_create = [
        ("p228", "emma_young_energetic_female", "Young energetic female, 22 years old"),
        ("p229", "narrator_female_warm", "Warm female narrator, 23 years old"),
        ("p226", "tyler_young_male", "Young energetic male, 22 years old"),
        ("p234", "maxim_young_male", "Clear young male voice, 22 years old"),
        ("p230", "amara_bright_female", "Bright friendly female, 22 years old"),
    ]

    for speaker_id, output_name, description in voices_to_create:
        print(f"\n{'='*70}")
        print(f"Processing: {output_name} (Speaker {speaker_id})")
        print(f"{'='*70}")

        # Download audio files
        audio_files = download_speaker_audio(speaker_id, num_files=15)

        if audio_files:
            # Create voice sample
            if create_voice_sample(audio_files, output_name, description):
                successful += 1
            else:
                failed += 1
        else:
            print(f"  [FAIL] Failed to download audio for {speaker_id}")
            failed += 1

    # Summary
    print("\n" + "="*70)
    print("DOWNLOAD COMPLETE")
    print("="*70)
    print(f"[OK] Successful: {successful}")
    print(f"[FAIL] Failed: {failed}")

    if successful > 0:
        print(f"\nReal human voice samples saved to: {VOICES_DIR}")
        print("\nCreated voice files:")
        for filename in sorted(os.listdir(VOICES_DIR)):
            if filename.endswith('.wav'):
                filepath = os.path.join(VOICES_DIR, filename)
                size_kb = os.path.getsize(filepath) / 1024
                print(f"  - {filename} ({size_kb:.1f} KB)")

        print("\n" + "="*70)
        print("THESE ARE REAL HUMAN VOICES!")
        print("="*70)
        print("Source: VCTK Corpus (University of Edinburgh)")
        print("Speakers: Real people aged 22-23")
        print("Quality: Professional studio recordings")
        print("Format: 24kHz WAV (ready for Chatterbox)")

        print("\nNext steps:")
        print("1. Listen to the voice samples to evaluate")
        print("2. Test with Chatterbox: cd src && ../venv/Scripts/python audio_generator.py")
        print("3. Generate scene audio: python generate_scene_audio.py --chapters 1")

    else:
        print("\n[FAIL] No voices were successfully downloaded")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Verify Hugging Face token is valid")
        print("3. Check if VCTK dataset is accessible")

if __name__ == "__main__":
    main()
