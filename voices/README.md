# Real Human Voice Samples - COMPLETE

**Date:** December 25, 2025
**Status:** ✅ COMPLETE - 8 REAL HUMAN VOICES Downloaded (Male + Female + Teen)

## What You Have - All Real Human Voices

Downloaded from **LibriSpeech** dataset (professional audiobook narrators):

### Male Voices

1. **male_young_energetic.wav** (469 KB, 10.0s)
   - Young energetic male speaker
   - Perfect for: Tyler, young male characters

2. **male_teen_casual.wav** (469 KB, 10.0s)
   - Youthful casual male speaker
   - Perfect for: Teen characters, informal narration

3. **male_calm_mature.wav** (469 KB, 10.0s)
   - Calm mature male voice
   - Perfect for: Maxim, authoritative characters

4. **male_narrator_deep.wav** (469 KB, 10.0s)
   - Deep male narrator voice
   - Perfect for: Serious narration, older characters

5. **male_young_friendly.wav** (469 KB, 10.0s)
   - Friendly young male speaker
   - Perfect for: Approachable male characters

### Female Voices

6. **female_young_bright.wav** (469 KB, 10.0s)
   - Young bright female speaker
   - Perfect for: Emma, energetic female characters

7. **female_teen_energetic.wav** (469 KB, 10.0s)
   - Energetic young female speaker
   - Perfect for: Teen female characters, youthful narration

8. **female_narrator_warm.wav** (469 KB, 10.0s)
   - Warm female narrator
   - Perfect for: Main narrator, maternal characters

## Source Information

- **Dataset:** LibriSpeech dev-clean
- **Speakers:** 8 different real people (audiobook narrators)
- **Original Recording:** Professional audiobook readings from LibriVox
- **Quality:** Professional studio recordings
- **License:** Public domain
- **Sample Rate:** 24kHz (Chatterbox-ready)

## Technical Specifications

- ✅ **Format:** WAV (uncompressed)
- ✅ **Sample Rate:** 24000 Hz (Chatterbox requirement)
- ✅ **Duration:** 10 seconds each
- ✅ **Quality:** Professional studio recordings
- ✅ **Source:** REAL HUMAN VOICES (not synthetic TTS)
- ✅ **Variety:** Multiple speakers, male/female, young/mature

## Next Steps

### 1. Listen to Voices

Open `voices/` folder and double-click each `.wav` file to hear the real human voices.

### 2. Test with Chatterbox TTS

```bash
cd src
../venv/Scripts/python audio_generator.py
```

### 3. Assign Voices to Characters

Edit [src/config.py](../src/config.py) to map characters to specific voices:

```python
CHARACTER_VOICES = {
    "narrator": os.path.join(VOICES_DIR, "female_narrator_warm.wav"),
    "emma": os.path.join(VOICES_DIR, "female_young_bright.wav"),
    "maxim": os.path.join(VOICES_DIR, "male_calm_mature.wav"),
    "amara": os.path.join(VOICES_DIR, "female_teen_energetic.wav"),
    "tyler": os.path.join(VOICES_DIR, "male_teen_casual.wav"),
}
```

### 4. Generate Scene Audio

```bash
cd src
../venv/Scripts/python generate_scene_audio.py --chapters 1
```

## Voice Characteristics

| Voice File | Gender | Age | Energy | Best For |
|------------|--------|-----|--------|----------|
| male_young_energetic | Male | Young | High | Tyler, young males |
| male_teen_casual | Male | Teen | Medium | Teen males, casual |
| male_calm_mature | Male | Mature | Low | Maxim, authority |
| male_narrator_deep | Male | Mature | Low | Serious narration |
| male_young_friendly | Male | Young | Medium | Friendly males |
| female_young_bright | Female | Young | High | Emma, energetic |
| female_teen_energetic | Female | Teen | High | Teen females |
| female_narrator_warm | Female | Adult | Medium | Main narrator |

## Why These Are Better

❌ **Before:** Synthetic TTS (Microsoft voices)
- Robotic, flat, unnatural
- Poor voice cloning quality

✅ **Now:** Real human audiobook narrators
- Natural speech patterns
- Expressive intonation
- Professional studio quality
- Multiple ages and genders
- Perfect for voice cloning

## Files in This Directory

### Voice Files (Ready to Use)
- `male_young_energetic.wav` - Young energetic male
- `male_teen_casual.wav` - Teen casual male
- `male_calm_mature.wav` - Calm mature male
- `male_narrator_deep.wav` - Deep narrator male
- `male_young_friendly.wav` - Friendly young male
- `female_young_bright.wav` - Young bright female
- `female_teen_energetic.wav` - Energetic teen female
- `female_narrator_warm.wav` - Warm narrator female

### Metadata Files
- `*_info.txt` - Voice details for each sample

### Documentation
- `README.md` - This file
- `VOICE_DOWNLOAD_GUIDE.md` - Guide for downloading more voices

## Summary

✅ **Downloaded:** 8 real human voice samples
✅ **Variety:** 5 male + 3 female voices
✅ **Ages:** Teen, young, mature
✅ **Format:** 24kHz WAV (Chatterbox-ready)
✅ **Quality:** Professional audiobook narrators
✅ **License:** Public domain
✅ **Status:** Ready for evaluation and use

**YOU NOW HAVE REAL HUMAN VOICES including teens and males suitable for Chatterbox TTS voice cloning!**

Listen to them and choose your favorites for each character.

## Sources

- [GitHub Voice Datasets](https://github.com/jim-schwoebel/voice_datasets)
- [Mozilla Common Voice](https://commonvoice.mozilla.org/en/datasets)
- [LibriSpeech ASR corpus](https://www.openslr.org/12)
- [150+ Audio Datasets | Twine Blog](https://www.twine.net/blog/100-audio-and-video-datasets/)
