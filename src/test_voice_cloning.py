"""
Simple test script to verify voice cloning works with Coqui TTS
"""

import os
import sys
from pathlib import Path
import torch

def main():
    # Debug: Print environment info
    print("=" * 60)
    print("VOICE CLONING TEST")
    print("=" * 60)
    print(f"Python: {sys.version}")
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    print("=" * 60)

    # Setup paths
    project_root = Path(__file__).parent.parent
    voice_file = project_root / "voices" / "female_young_bright.wav"
    output_dir = project_root / "audio" / "test"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "voice_clone_test.wav"

    # Debug: Check voice file
    print(f"\nVoice file: {voice_file}")
    print(f"Voice file exists: {voice_file.exists()}")
    if voice_file.exists():
        print(f"Voice file size: {voice_file.stat().st_size:,} bytes")
    else:
        print("ERROR: Voice file not found!")
        return

    print(f"\nOutput file: {output_file}")

    # Test text
    test_text = "Hello! This is a test of voice cloning. If you can hear this in a young, bright female voice, then voice cloning is working perfectly."

    print(f"\nTest text: '{test_text}'")
    print(f"Text length: {len(test_text)} characters")

    # Initialize TTS
    print("\n" + "=" * 60)
    print("Initializing TTS model...")
    print("=" * 60)

    try:
        # Patch TTS library to use weights_only=False for PyTorch 2.6+
        import TTS.utils.io
        original_load = TTS.utils.io.torch.load
        def patched_load(*args, **kwargs):
            kwargs['weights_only'] = False
            return original_load(*args, **kwargs)
        TTS.utils.io.torch.load = patched_load

        # Use XTTS-v2 for voice cloning
        from TTS.api import TTS
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
        print("[OK] TTS model loaded successfully")

        # Move to GPU if available
        if torch.cuda.is_available():
            print("[OK] Moving model to GPU...")
            tts.to("cuda")
        else:
            print("[WARNING] Using CPU (this will be slower)")

    except Exception as e:
        print(f"[ERROR] Failed to initialize TTS: {e}")
        return

    # Generate speech with voice cloning
    print("\n" + "=" * 60)
    print("Generating speech with voice cloning...")
    print("=" * 60)

    try:
        tts.tts_to_file(
            text=test_text,
            speaker_wav=str(voice_file),
            language="en",
            file_path=str(output_file)
        )
        print(f"[OK] Audio generated successfully!")
        print(f"[OK] Saved to: {output_file}")

        # Check output file
        if output_file.exists():
            file_size = output_file.stat().st_size
            print(f"[OK] Output file size: {file_size:,} bytes")

            if file_size > 0:
                print("\n" + "=" * 60)
                print("SUCCESS! Voice cloning test completed.")
                print("=" * 60)
                print(f"\nPlay the audio file to verify: {output_file}")
            else:
                print("\n[ERROR] Output file is empty!")
        else:
            print("\n[ERROR] Output file was not created!")

    except Exception as e:
        print(f"\n[ERROR] Failed to generate speech: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
