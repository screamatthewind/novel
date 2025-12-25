# TTS Alternatives Research & Recommendation

## Executive Summary

**Goal:** Replace Coqui XTTS v2 narrator voice with younger, more pleasant, relatable female voice for audiobook narration.

**Current Setup:**
- Engine: Coqui XTTS v2 (43.8k ⭐, Non-commercial license)
- Narrator: "Claribel Dervla" built-in speaker
- Issue: Voice not ideal, non-commercial license restricts usage

**🏆 TOP RECOMMENDATION: Chatterbox by Resemble AI (Self-Hosted)**
- **Why:** MIT license (free), emotion control, 6× real-time speed, outperforms ElevenLabs
- **Requires:** GPU with adequate VRAM (RTX 3090/4090 or cloud GPU)
- **Cost:** FREE when self-hosted (download from Hugging Face)
- **Note:** Resemble AI's managed cloud API has limits (50k chars/month free, then paid)

**Runner-Up Options:**
1. **Dia 1.6B** - Best audiobook quality (slower generation, Apache 2.0)
2. **StyleTTS 2** - Human-level quality (robotic pacing, MIT license)
3. **Quick Fix** - Change XTTS v2 voice to "Ana Florence" (1 line change in config.py)

---

## Current Setup Details
- **Current TTS Engine**: Coqui XTTS v2
- **Current Narrator Voice**: "Claribel Dervla" (built-in XTTS speaker)
  - Described as: "Young, upbeat female voice - energetic and clear"
  - Using fallback system (no voice file exists)
- **Configuration Files**:
  - [src/config.py](src/config.py) - CHARACTER_SPEAKERS and CHARACTER_VOICES mappings
  - [src/voice_config.py](src/voice_config.py) - Voice selection logic

---

## TTS Alternatives Comparison

| TTS Solution | GitHub Stars | License | Quality Rating | Pros | Cons | Best For |
|--------------|-------------|---------|----------------|------|------|----------|
| **Coqui XTTS v2** (Current) | 43.8k ⭐ | Coqui Public License (Non-commercial) | ⭐⭐⭐⭐ | • Excellent prosody & expressiveness<br>• 17 languages supported<br>• Voice cloning with 6s audio<br>• Already integrated<br>• Strong community support | • Non-commercial license restriction<br>• Current narrator voice not ideal<br>• Company shut down (community-maintained)<br>• Requires 12GB VRAM | Long-form narration, multilingual projects |
| **Chatterbox** by Resemble AI | 15,965 ⭐ | MIT (Commercial use ✅) | ⭐⭐⭐⭐⭐ | • **MIT License - free to self-host**<br>• Emotion control tags [laugh], [cough]<br>• Zero-shot voice cloning<br>• 6× faster than real-time<br>• Built-in watermarking<br>• 23 languages (Multilingual version)<br>• Available on Hugging Face<br>• Outperforms ElevenLabs (63.75% preference) | • **Requires GPU hardware to self-host**<br>• Cloud API has limits (50k chars/month free)<br>• Newer project (less battle-tested)<br>• Moderate VRAM requirements | **🏆 RECOMMENDED** - Self-hosted audiobooks, commercial projects |
| **StyleTTS 2** | 6.1k ⭐ | MIT (Commercial use ✅) | ⭐⭐⭐⭐⭐ | • Human-level quality (surpasses human recordings)<br>• ElevenLabs-comparable quality<br>• 95× faster than real-time (RTX 4090)<br>• Multi-speaker support<br>• Zero-shot speaker adaptation<br>• MIT License | • Robotic pacing (less expressive)<br>• Smaller community than top options<br>• Setup complexity | High-quality single-voice narration |
| **Kokoro-82M** | ~500-1k ⭐ | Apache 2.0 (Commercial use ✅) | ⭐⭐⭐⭐ | • Tiny model (82M params)<br>• Fast inference (<0.3s)<br>• Low VRAM requirements<br>• 54+ voices across 9 languages<br>• Runs on Raspberry Pi | • Emotionless, stilted delivery<br>• Obviously AI-generated<br>• Limited expressiveness<br>• Smaller community | Fast generation, embedded devices, batch processing |
| **Bark** by Suno AI | 38.5k ⭐ | MIT (Commercial use ✅) | ⭐⭐⭐⭐ | • Non-verbal sounds (laughing, crying)<br>• Music & sound effects capable<br>• 100+ speaker presets<br>• Strong community (Discord)<br>• Commercial use allowed | • **Limited to 13-14 seconds output**<br>• Requires chunking for long content<br>• 12GB VRAM (8GB version available)<br>• Slower generation | Short-form audio, sound effects, variety |
| **Piper TTS** | 10.4k ⭐ | Various (check per-voice) | ⭐⭐⭐ | • Very fast (CPU-capable)<br>• Low resource requirements<br>• Many voice options<br>• ONNX format (portable)<br>• Multiple quality levels | • **Repository archived Oct 2025**<br>• Slightly robotic<br>• Lower quality than top options<br>• Development moved to fork | Offline use, low-resource environments |
| **Dia 1.6B** | ~1-2k ⭐ | Apache 2.0 (Commercial use ✅) | ⭐⭐⭐⭐⭐ | • Ultra-realistic dialogue quality<br>• Non-verbal cues (laughter, sighs)<br>• Emotion & naturalness optimized<br>• Multi-speaker conversations<br>• **Best for audiobook narration** | • Slower generation (optimizes quality)<br>• 1.6B params (higher VRAM)<br>• Smaller community<br>• Newer project | Premium audiobook narration, dialogue-heavy content |
| **ElevenLabs API** | N/A (Commercial) | Proprietary | ⭐⭐⭐⭐⭐ | • Industry-leading quality<br>• Most realistic voices<br>• Excellent female narrator options<br>• Easy API integration<br>• Emotion-aware | • **Costs $5-$1,320/month**<br>• Credit-based pricing (confusing)<br>• Hidden costs (previews, failures)<br>• Requires internet connection<br>• Not self-hosted | Commercial audiobooks with budget |

---

## Community Support & Ratings Summary

**Most Supported (by GitHub Stars)**:
1. Coqui XTTS v2 (43.8k ⭐)
2. Bark by Suno AI (38.5k ⭐)
3. Chatterbox by Resemble AI (15.9k ⭐)
4. Piper TTS (10.4k ⭐) - *Archived, development moved*
5. StyleTTS 2 (6.1k ⭐)

**Highest Rated for Quality**:
1. **Dia 1.6B** - Ultra-realistic dialogue, audiobook-optimized
2. **StyleTTS 2** - Human-level quality, surpasses human recordings
3. **Chatterbox** - SoTA quality with emotion control
4. **ElevenLabs** - Industry-leading (but paid)
5. **Coqui XTTS v2** - Excellent prosody

**Best for Commercial Use**:
- ✅ **Chatterbox** (MIT) - Best balance of quality, features, and license
- ✅ **StyleTTS 2** (MIT) - High quality, fast
- ✅ **Dia** (Apache 2.0) - Premium audiobook quality
- ✅ **Kokoro** (Apache 2.0) - Fast, lightweight
- ✅ **Bark** (MIT) - Creative audio

---

## Recommendations

### 🏆 Top Choice: **Chatterbox by Resemble AI** (Self-Hosted)

**Why Chatterbox:**
1. **MIT License - Free to Self-Host** - Download from Hugging Face, run on your own GPU
2. **Emotion Control** - Native support for [laugh], [cough], [sigh] tags
3. **6× Real-time Speed** - Fast generation for full novel
4. **Zero-shot Voice Cloning** - Can use custom voice samples
5. **Strong Growth** - 15.9k stars, 1M+ Hugging Face downloads
6. **Built-in Watermarking** - PerTh watermarking for authenticity
7. **Multiple Variants** - Original, Multilingual (23 langs), Turbo (350M params)
8. **Outperforms ElevenLabs** - 63.75% preference in blind tests

**Important Clarification on "Free":**
- ✅ **Open-source model is FREE** - MIT licensed, download from Hugging Face
- ✅ **No API fees when self-hosted** - Run locally on your own GPU
- ⚠️ **Requires GPU hardware** - Need adequate VRAM (RTX 3090/4090 recommended)
- 💰 **Managed cloud service has limits** - Resemble AI's API: 50k chars/month free, then paid
- 💰 **Third-party hosting costs apply** - Replicate, DeepInfra charge per run (~$0.029/run)

### 🥈 Alternative: **Dia 1.6B**

**Why Dia for Premium Quality:**
1. **Audiobook-Specific** - Optimized for long-form narration
2. **Ultra-realistic** - Best dialogue quality, emotion, naturalness
3. **Apache 2.0 License** - Commercial use allowed
4. **Non-verbal Cues** - Natural laughter, sighs, breathing

**Trade-off:** Slower generation (optimizes for quality over speed)

### 🥉 Budget/Fast Option: **Kokoro-82M**

**Why Kokoro for Speed:**
1. **Extremely Fast** - <0.3s processing time
2. **Low Resources** - 82M params, runs on Raspberry Pi
3. **Apache 2.0 License** - Commercial use
4. **54+ Voices** - Good selection

**Trade-off:** More robotic, emotionless delivery

---

## Implementation Plan

### Option A: Switch to Chatterbox (Recommended - Self-Hosted)

**Prerequisites:**
- GPU with adequate VRAM (RTX 3090/4090 recommended, or cloud GPU)
- Download model from Hugging Face: `ResembleAI/chatterbox-turbo`

**Files to Modify:**
1. **[src/config.py](src/config.py)**
   - Update `DEFAULT_TTS_MODEL` from Coqui to Chatterbox
   - Revise voice mappings to use Chatterbox voices
   - Add emotion tag support configuration

2. **[src/voice_config.py](src/voice_config.py)**
   - Refactor `get_voice_for_speaker()` for Chatterbox API
   - Add emotion tag handling
   - Update voice cloning logic

3. **[src/audio_generator.py](src/audio_generator.py)** (if exists)
   - Replace Coqui TTS calls with Chatterbox
   - Integrate emotion tags from scene parsing
   - Update audio generation pipeline

4. **Dependencies**
   - Install from Hugging Face: `from chatterbox.tts import ChatterboxTTS`
   - Alternative: Use community server (github.com/devnen/Chatterbox-TTS-Server)
   - Update `requirements.txt`

**Cost Analysis:**
- ✅ Model: Free (MIT License)
- ✅ Self-hosted usage: Unlimited, no API fees
- ⚠️ Hardware: Requires local GPU or cloud compute costs
- 💰 Managed API alternative: 50k chars/month free, then paid tiers

### Option B: Switch to Dia 1.6B (Premium Quality)

Similar file modifications but with Dia-specific API integration, optimized for slower but higher-quality generation.

### Option C: Try Multiple Female Voices in Current XTTS v2

**Quick Fix - No Code Changes:**

Available XTTS v2 female speakers (younger/more pleasant alternatives):
- **Ana Florence** - Warm, natural (most popular for audiobooks)
- **Gracie Wise** - Thoughtful, intelligent tone
- **Sofia Hellen** - Currently used for Emma; warm & professional
- **Alison Dietlinde** - Unique sound
- **Tammie Ema** - Alternative option
- **Annmarie Nele** - Alternative option

**Simple Change in [src/config.py](src/config.py) line 84:**
```python
# Change from:
"narrator": "Claribel Dervla",

# To one of:
"narrator": "Ana Florence",        # Recommended
"narrator": "Gracie Wise",         # For philosophical tone
"narrator": "Sofia Hellen",        # Professional & warm
```

**Pros:** Zero code rewrite, immediate testing
**Cons:** Still non-commercial license, limited to XTTS capabilities

---

## Testing Strategy

1. **Generate Sample Audio** - Test each option with a paragraph from Chapter 1
2. **Voice Comparison** - Compare naturalness, emotion, pacing
3. **Performance Benchmark** - Measure generation time for full chapter
4. **VRAM Assessment** - Check memory requirements on current hardware
5. **License Verification** - Confirm commercial use terms
6. **Integration Effort** - Estimate development time for each option

---

## Sources

### Research References

1. [The Best Open-Source Text-to-Speech Models in 2026](https://www.bentoml.com/blog/exploring-the-world-of-open-source-text-to-speech-models)
2. [Top Open Source Text to Speech Alternatives Compared](https://smallest.ai/blog/open-source-tts-alternatives-compared)
3. [Coqui TTS GitHub Repository](https://github.com/coqui-ai/TTS)
4. [Chatterbox by Resemble AI](https://www.resemble.ai/chatterbox/)
5. [Chatterbox GitHub Repository](https://github.com/resemble-ai/chatterbox)
6. [StyleTTS 2 GitHub Repository](https://github.com/yl4579/StyleTTS2)
7. [Kokoro-82M Hugging Face](https://huggingface.co/hexgrad/Kokoro-82M)
8. [Bark by Suno AI GitHub](https://github.com/suno-ai/bark)
9. [Piper TTS GitHub](https://github.com/rhasspy/piper)
10. [Dia TTS GitHub](https://github.com/nari-labs/dia)
11. [ElevenLabs Pricing](https://elevenlabs.io/pricing/api)
12. [12 Best Open-Source TTS Models Compared (2025)](https://www.inferless.com/learn/comparing-different-text-to-speech---tts--models-part-2)

---

## Next Steps - Decision Required

**Choose ONE of the following approaches:**

### Option 1: Quick Test (5 minutes) ⚡
- Change narrator voice in [src/config.py](src/config.py) line 84
- Try "Ana Florence", "Gracie Wise", or "Sofia Hellen"
- Zero code changes, immediate testing
- **Limitation:** Still non-commercial license

### Option 2: Migrate to Chatterbox (Recommended) 🏆
- Self-host on your GPU (RTX 3090/4090 recommended)
- Download from Hugging Face: `ResembleAI/chatterbox-turbo`
- MIT license - commercial use allowed
- Requires code changes in config.py, voice_config.py, audio_generator.py
- **Cost:** FREE when self-hosted

### Option 3: Use Dia 1.6B (Premium Quality) 💎
- Best audiobook quality available
- Apache 2.0 license - commercial use allowed
- Slower generation (quality over speed)
- Requires code changes and GPU with higher VRAM

### Option 4: Quick Win - Keep XTTS, Try Better Voice 🎯
- Change 1 line: `"narrator": "Ana Florence"`
- Test immediately with existing setup
- Decide on full migration later
- **Benefit:** Lowest effort, immediate improvement

---

## Implementation Status

**Date:** 2025-12-25
**Status:** Research Complete - Awaiting User Decision
**Comparison Table:** Complete with 8 TTS options analyzed
**Files Ready to Modify:** src/config.py, src/voice_config.py, src/audio_generator.py
