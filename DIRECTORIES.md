# Directory Quick Reference

All directories defined in [src/config.py](src/config.py). See [docs/project/directory_structure.md](docs/project/directory_structure.md) for details.

## Source (Never Delete)
- `docs/manuscript/` - Chapter files
- `docs/reference/` - Novel Bible, Outline
- `src/` - Python scripts
- `voices/` - Voice samples
- `venv/` - Virtual environment

## Generated (Safe to Delete)
- `audio/` - TTS audio files
- `audio_cache/` - Audio metadata
- `images/` - Scene images
- `videos/` - YouTube videos
- `logs/` - Generation logs
- `prompt_cache/` - Image prompts
- `temp/` - Temporary files

## Cleanup
```bash
# Preview
./venv/Scripts/python src/cleanup.py --dry-run

# Execute
./venv/Scripts/python src/cleanup.py
```

## Regenerate Everything
```bash
# 1. Clean
./venv/Scripts/python src/cleanup.py --yes

# 2. Generate images (all chapters)
./venv/Scripts/python src/generate_scene_images.py

# 3. Generate audio (all chapters)
./venv/Scripts/python src/generate_scene_audio.py

# 4. Generate videos (all chapters, combined)
./venv/Scripts/python src/generate_video.py --all --combine
```
