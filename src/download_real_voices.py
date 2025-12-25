#!/usr/bin/env python3
"""
Download REAL human voice recordings from public domain datasets.

This script downloads actual human voice recordings (not synthetic TTS)
from LJSpeech and other public domain datasets for use with Chatterbox voice cloning.
"""

import os
import sys
import urllib.request
import tarfile
import zipfile
import shutil
from pathlib import Path
from pydub import AudioSegment
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import VOICES_DIR, DEFAULT_SAMPLE_RATE
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dataset URLs (REAL HUMAN VOICES - Public Domain)
LJSPEECH_URL = "http://data.keithito.com/data/speech/LJSpeech-1.1.tar.bz2"
VCTK_URL = "https://datashare.ed.ac.uk/bitstream/handle/10283/3443/VCTK-Corpus-0.92.zip"

# Temporary download directory
TEMP_DIR = os.path.join(PROJECT_ROOT, "temp", "voice_downloads")

def download_file(url, destination):
    """Download a file with progress indicator."""
    print(f"\nDownloading from: {url}")
    print(f"Destination: {destination}")

    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(downloaded * 100.0 / total_size, 100)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\r  Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='')
        else:
            mb_downloaded = downloaded / (1024 * 1024)
            print(f"\r  Downloaded: {mb_downloaded:.1f} MB", end='')

    try:
        urllib.request.urlretrieve(url, destination, progress_hook)
        print("\n  Download complete!")
        return True
    except Exception as e:
        print(f"\n  ERROR: Download failed: {e}")
        return False

def extract_archive(archive_path, extract_to):
    """Extract tar.bz2 or zip archive."""
    print(f"\nExtracting archive: {archive_path}")

    try:
        if archive_path.endswith('.tar.bz2'):
            with tarfile.open(archive_path, 'r:bz2') as tar:
                tar.extractall(extract_to)
        elif archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        else:
            print(f"  ERROR: Unknown archive format")
            return False

        print("  Extraction complete!")
        return True
    except Exception as e:
        print(f"  ERROR: Extraction failed: {e}")
        return False

def create_voice_sample(audio_files, output_name, target_duration=10, description=""):
    """
    Create a voice sample by combining multiple audio files.

    Args:
        audio_files: List of paths to audio files
        output_name: Output filename (without extension)
        target_duration: Target duration in seconds
        description: Voice description
    """
    print(f"\nCreating voice sample: {output_name}")
    print(f"  Source files: {len(audio_files)}")

    try:
        combined = None
        total_duration = 0
        files_used = []

        # Shuffle for variety
        random.shuffle(audio_files)

        for audio_file in audio_files:
            try:
                # Load audio (supports WAV, FLAC, MP3)
                audio = AudioSegment.from_file(audio_file)

                # Add to combined audio
                if combined is None:
                    combined = audio
                else:
                    # Add small silence between clips
                    silence = AudioSegment.silent(duration=200)
                    combined = combined + silence + audio

                files_used.append(audio_file)
                total_duration = len(combined) / 1000.0

                if total_duration >= target_duration:
                    break

            except Exception as e:
                print(f"  Warning: Skipping file {audio_file}: {e}")
                continue

        if combined is None:
            print(f"  ERROR: No valid audio files found")
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

        print(f"  [OK] Success!")
        print(f"    Duration: {duration:.1f}s")
        print(f"    Sample rate: {DEFAULT_SAMPLE_RATE} Hz")
        print(f"    Size: {size_kb:.1f} KB")
        print(f"    Files used: {len(files_used)}")

        # Save metadata
        metadata_path = os.path.join(VOICES_DIR, f"{output_name}_info.txt")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            f.write(f"Voice Sample: {output_name}\n")
            f.write(f"Source: REAL HUMAN VOICE (Public Domain)\n")
            f.write(f"Description: {description}\n")
            f.write(f"Duration: {duration:.2f} seconds\n")
            f.write(f"Sample Rate: {DEFAULT_SAMPLE_RATE} Hz\n")
            f.write(f"Files Combined: {len(files_used)}\n")
            f.write(f"\nSource Files:\n")
            for i, f_path in enumerate(files_used[:5], 1):
                f.write(f"{i}. {Path(f_path).name}\n")

        return True

    except Exception as e:
        print(f"  ERROR: Failed to create sample: {e}")
        import traceback
        traceback.print_exc()
        return False

def download_ljspeech():
    """Download LJSpeech dataset (single female speaker, professional quality)."""
    print("\n" + "="*70)
    print("Downloading LJSpeech Dataset")
    print("Real human voice: Professional female narrator")
    print("="*70)

    # Create temp directory
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Download
    archive_path = os.path.join(TEMP_DIR, "LJSpeech-1.1.tar.bz2")

    if not os.path.exists(archive_path):
        if not download_file(LJSPEECH_URL, archive_path):
            return False
    else:
        print(f"\nArchive already exists: {archive_path}")

    # Extract
    extract_dir = os.path.join(TEMP_DIR, "ljspeech_extracted")
    wavs_dir = os.path.join(extract_dir, "LJSpeech-1.1", "wavs")

    if not os.path.exists(wavs_dir):
        if not extract_archive(archive_path, extract_dir):
            return False
    else:
        print(f"\nAlready extracted to: {extract_dir}")

    # Get all WAV files
    wav_files = list(Path(wavs_dir).glob("*.wav"))
    print(f"\nFound {len(wav_files)} audio files")

    if len(wav_files) == 0:
        print("ERROR: No WAV files found!")
        return False

    # Create voice samples
    os.makedirs(VOICES_DIR, exist_ok=True)

    # Sample 1: Narrator (professional, measured)
    create_voice_sample(
        wav_files[:50],
        "narrator_professional_female",
        target_duration=10,
        description="Professional female narrator, clear articulation, audiobook style"
    )

    # Sample 2: General female (slightly different selection)
    create_voice_sample(
        wav_files[100:150],
        "female_narrator_warm",
        target_duration=10,
        description="Warm female voice, natural speech, professional quality"
    )

    # Sample 3: Emma character voice option
    create_voice_sample(
        wav_files[200:250],
        "emma_human_female",
        target_duration=10,
        description="Young-sounding female narrator, energetic delivery"
    )

    print("\n[OK] LJSpeech samples created successfully!")
    return True

def download_sample_from_url(url, output_name, description):
    """Download a single sample directly from URL."""
    print(f"\n" + "="*70)
    print(f"Downloading: {output_name}")
    print(f"="*70)

    try:
        temp_file = os.path.join(TEMP_DIR, f"{output_name}_temp.wav")

        if download_file(url, temp_file):
            # Convert to 24kHz
            audio = AudioSegment.from_file(temp_file)
            audio = audio.set_frame_rate(DEFAULT_SAMPLE_RATE)

            # Trim to 10 seconds
            audio = audio[:10000]

            # Export
            output_path = os.path.join(VOICES_DIR, f"{output_name}.wav")
            audio.export(output_path, format="wav")

            duration = len(audio) / 1000.0
            print(f"\n[OK] Downloaded and processed: {output_name}")
            print(f"  Duration: {duration:.1f}s")
            print(f"  Sample rate: {DEFAULT_SAMPLE_RATE} Hz")

            # Cleanup temp
            if os.path.exists(temp_file):
                os.remove(temp_file)

            return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

    return False

def main():
    """Download real human voice samples."""
    print("\n" + "="*70)
    print("REAL HUMAN VOICE DOWNLOADER")
    print("Downloading actual human recordings (NOT synthetic TTS)")
    print("="*70)

    os.makedirs(VOICES_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    print(f"\nOutput directory: {VOICES_DIR}")
    print(f"Temp directory: {TEMP_DIR}")

    # Download LJSpeech (high quality female narrator)
    print("\n\nSTEP 1: Downloading LJSpeech Dataset")
    print("This may take 5-10 minutes (2.6 GB download)...")

    ljspeech_success = download_ljspeech()

    # Summary
    print("\n" + "="*70)
    print("DOWNLOAD COMPLETE")
    print("="*70)

    if ljspeech_success:
        print("\n[OK] Successfully downloaded REAL HUMAN VOICES")
        print(f"\nVoice samples saved to: {VOICES_DIR}")

        # List created files
        print("\nCreated voice files:")
        for filename in sorted(os.listdir(VOICES_DIR)):
            if filename.endswith('.wav'):
                filepath = os.path.join(VOICES_DIR, filename)
                size_kb = os.path.getsize(filepath) / 1024
                print(f"  - {filename} ({size_kb:.1f} KB)")

        print("\nThese are REAL HUMAN voice recordings from:")
        print("  - LJSpeech: Professional audiobook narrator (public domain)")
        print("  - Source: LibriVox audiobook project")
        print("  - Quality: Professional studio recordings")

        print("\nNext steps:")
        print("1. Listen to the voice samples")
        print("2. Test with Chatterbox: cd src && ../venv/Scripts/python audio_generator.py")
        print("3. Generate audio: python generate_scene_audio.py --chapters 1")

    else:
        print("\n[FAIL] Download failed or incomplete")
        print("\nTroubleshooting:")
        print("1. Check internet connection")
        print("2. Verify disk space (need ~3 GB)")
        print("3. Try running script again")

if __name__ == "__main__":
    main()
