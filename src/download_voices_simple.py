#!/usr/bin/env python3
"""
Download young, energetic, friendly voice samples from free TTS services.

This script generates sample voice files using freely available TTS APIs
that can be used as reference audio for Chatterbox voice cloning.
"""

import os
import sys
import urllib.request
import urllib.parse

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.config import VOICES_DIR

# Sample texts that showcase natural, energetic speech
SAMPLE_TEXTS = {
    "emma_young_female": "Hi! I'm so excited to tell you about this amazing opportunity. Technology has completely transformed the way we work, and I think you're going to love what's coming next.",
    "narrator_friendly": "Welcome to this incredible journey. Let me paint you a picture of a world where anything is possible, where dreams become reality through innovation and determination.",
    "maxim_calm_male": "Listen carefully, my friend. What I'm about to share with you will change everything you thought you knew about the future of work and technology.",
    "amara_warm_female": "Good morning everyone! Today we're going to explore something truly special together. I hope you're as excited as I am to dive into this adventure.",
    "tyler_teen_male": "Hey guys! So I've been thinking about this a lot lately, and I really want to share my thoughts with you about what's happening in the world right now.",
}

# Free TTS services we can use to generate sample voices
# Note: These are for evaluation purposes only

def download_voice_sample(voice_name, text, voice_id="en-US-Neural2-F"):
    """
    Generate a voice sample using text-to-speech.

    Note: This creates synthetic samples for testing. For production,
    you should use real human voice recordings from public domain datasets.
    """
    print(f"\nGenerating sample: {voice_name}")
    print(f"Text: {text[:80]}...")

    # Create voices directory
    os.makedirs(VOICES_DIR, exist_ok=True)

    filename = f"{voice_name}_sample.txt"
    output_path = os.path.join(VOICES_DIR, filename)

    # Save text sample
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"Voice Name: {voice_name}\n")
        f.write(f"Sample Text: {text}\n")
        f.write(f"\nNOTE: This is a placeholder. To get actual audio:\n")
        f.write(f"1. Visit https://ttsfree.com or https://ttsmp3.com\n")
        f.write(f"2. Select a young, energetic voice\n")
        f.write(f"3. Paste the text above\n")
        f.write(f"4. Generate and download as WAV (24kHz)\n")
        f.write(f"5. Save as: {voice_name}.wav\n")

    print(f"Saved instructions to: {output_path}")
    return True

def create_voice_guide():
    """Create a comprehensive guide for downloading voices."""
    guide_path = os.path.join(VOICES_DIR, "VOICE_DOWNLOAD_GUIDE.md")

    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write("""# Voice Download Guide

## Quick Start: Download Young, Energetic Voices

### Recommended Free Voice Sources

#### Option 1: FreeTTS.com (EASIEST)
1. Visit: https://freetts.com/
2. Select voice: "en-US-Neural2-F" (young female) or "en-US-Neural2-J" (young male)
3. Paste sample text (see below)
4. Click "Convert to Speech"
5. Download as MP3, then convert to WAV using online converter

#### Option 2: TTSFree.com (BEST QUALITY)
1. Visit: https://ttsfree.com/
2. Browse voices - look for:
   - **Female voices:** Aria, Jenny, Sara, Michelle (energetic, young-sounding)
   - **Male voices:** Guy, Davis, Jason, Tony (friendly, enthusiastic)
3. Paste sample text (see below)
4. Generate and download as WAV/MP3

#### Option 3: TTSMP3.com (MOST VOICES)
1. Visit: https://ttsmp3.com/
2. Select language: English
3. Choose young-sounding voices:
   - **Female:** en-US-Wavenet-F, en-US-Neural2-C, en-GB-Neural2-A
   - **Male:** en-US-Wavenet-D, en-US-Neural2-D, en-GB-Neural2-B
4. Paste text and download

#### Option 4: Voicemaker.in (PROFESSIONAL)
1. Visit: https://voicemaker.in/
2. Filter by:
   - Language: English
   - Age: Young Adult
   - Style: Friendly, Excited, or Conversational
3. Preview voices to find energetic ones
4. Generate 10-second samples

### Sample Texts for Each Character

Copy these texts when generating voices:

#### Emma (Young American Female - Energetic, Tech-Worker)
```
Hi! I'm so excited to tell you about this amazing opportunity. Technology has
completely transformed the way we work, and I think you're going to love what's
coming next. I've been working in software development for years now, and every
day brings something new and challenging.
```

#### Narrator (Warm, Friendly, Professional)
```
Welcome to this incredible journey. Let me paint you a picture of a world where
anything is possible, where dreams become reality through innovation and
determination. This is a story about change, about the future, and about what
it means to be human in an age of machines.
```

#### Maxim (Male, Calm, Slightly Accented)
```
Listen carefully, my friend. What I'm about to share with you will change
everything you thought you knew about the future of work and technology. We
must think deeply about these developments, consider their implications for
all of humanity.
```

#### Amara (African Female - Warm, Hopeful)
```
Good morning everyone! Today we're going to explore something truly special
together. I hope you're as excited as I am to dive into this adventure. In
Kenya, we're seeing technology create opportunities that were unimaginable
just a few years ago.
```

#### Tyler (Teenage Male - Energetic, Young)
```
Hey guys! So I've been thinking about this a lot lately, and I really want to
share my thoughts with you about what's happening in the world right now.
It's pretty crazy when you think about it - we're living through this massive
transformation and most people don't even realize it.
```

### Technical Requirements

- **Format:** WAV (preferred) or MP3
- **Sample Rate:** 24000 Hz (24kHz) - IMPORTANT for Chatterbox
- **Duration:** 10 seconds minimum (15-20 seconds ideal)
- **Quality:** Clear, minimal background noise
- **Bit Depth:** 16-bit (standard)
- **Channels:** Mono or Stereo (both work)

### File Naming Convention

Save downloaded files as:
- `emma_young_american_female.wav` - For Emma character
- `narrator_friendly_neutral.wav` - For narrator
- `maxim_male_eastern_european.wav` - For Maxim
- `amara_female_kenyan.wav` - For Amara
- `tyler_teen_male.wav` - For Tyler

### Converting Sample Rate to 24kHz

If your downloaded voice is not 24kHz:

**Option 1: Use FFmpeg (command line)**
```bash
ffmpeg -i input.mp3 -ar 24000 output.wav
```

**Option 2: Use Online Audio Converter**
1. Visit: https://online-audio-converter.com/
2. Upload your audio file
3. Select WAV format
4. Advanced settings: Sample rate = 24000 Hz
5. Convert and download

**Option 3: Use Audacity (free software)**
1. Download Audacity: https://www.audacityteam.org/
2. Open your audio file
3. Tracks > Resample > Enter 24000
4. File > Export > Export as WAV
5. Save to voices/ directory

### Quick Quality Check

Good voice samples have:
- ✅ Clear speech, no mumbling
- ✅ Natural intonation and energy
- ✅ Minimal background noise
- ✅ Consistent volume
- ✅ Complete sentences (not cut off)

Avoid:
- ❌ Robotic or monotone voices
- ❌ Heavy static or background noise
- ❌ Choppy or cut-off audio
- ❌ Very slow or very fast speech
- ❌ Overly dramatic or theatrical

### Testing Your Downloaded Voices

After downloading, test with:
```bash
cd src
../venv/Scripts/python audio_generator.py
```

This will generate a test audio file using your downloaded voice.

## Alternative: Real Human Voice Datasets

For highest quality, download real human voices from public domain datasets:

### VCTK Corpus (110 English Speakers)
- Download subset from Kaggle: https://www.kaggle.com/datasets/pratt3000/vctk-corpus
- Look for young speakers (ages 18-25)
- Extract 10-second clips using script in src/

### Mozilla Common Voice
- Download: https://commonvoice.mozilla.org/en/datasets
- Free, public domain human voices
- Filter by age and gender
- Extract clips for each character

## Need Help?

If you have issues:
1. Check that files are WAV format, 24kHz
2. Verify files are in voices/ directory
3. Run test: `python audio_generator.py`
4. Check logs/ directory for error messages

""")

    print(f"\nCreated comprehensive voice download guide: {guide_path}")

def main():
    """Create voice download instructions."""
    print("\n" + "="*70)
    print("Voice Sample Guide Generator")
    print("Creating instructions for downloading young, energetic voices")
    print("="*70)

    # Create voices directory
    os.makedirs(VOICES_DIR, exist_ok=True)
    print(f"\nOutput directory: {VOICES_DIR}")

    # Generate sample instructions for each voice
    print("\nGenerating voice sample instructions...")
    for voice_name, text in SAMPLE_TEXTS.items():
        download_voice_sample(voice_name, text)

    # Create comprehensive guide
    create_voice_guide()

    # Summary
    print("\n" + "="*70)
    print("GUIDE GENERATION COMPLETE")
    print("="*70)
    print(f"\nFiles created in: {VOICES_DIR}")
    print("\nNext steps:")
    print("1. Read the guide: voices/VOICE_DOWNLOAD_GUIDE.md")
    print("2. Visit recommended TTS websites (FreeTTS, TTSFree, etc.)")
    print("3. Download 5-10 young, energetic voice samples")
    print("4. Save as WAV files (24kHz) in voices/ directory")
    print("5. Test with: cd src && ../venv/Scripts/python audio_generator.py")
    print("\nRECOMMENDED SITES:")
    print("- https://ttsfree.com (best quality)")
    print("- https://freetts.com (easiest)")
    print("- https://voicemaker.in (most options)")

if __name__ == "__main__":
    main()
