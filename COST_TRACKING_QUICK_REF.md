# Cost Tracking - Quick Reference

## 📊 Current Pricing (Claude Haiku 3.5)

- **Input**: $0.80 per million tokens
- **Output**: $4.00 per million tokens
- **Defined in**: `src/config.py` lines 132-133

## 💰 Actual Costs

- **Per prompt**: ~$0.00084 USD (less than 1/10th of a cent)
- **Per chapter**: ~$0.04 USD (4 cents for 50 sentences)
- **Full novel**: ~$0.50 USD (50 cents for 600 sentences)

## 🚀 Usage

```bash
# Generate with Haiku (automatic cost tracking)
cd src
../venv/Scripts/python generate_scene_images.py --chapters 1 --llm haiku

# Test prompt generation (with cost tracking)
../venv/Scripts/python test_prompt_comparison.py haiku
```

## 📁 Cost Data Location

`.costs/haiku_usage.json` (git-ignored, local only)

## 🔧 Update Pricing

If Haiku pricing changes:

1. Edit `src/config.py`
2. Update lines 132-133:
   ```python
   HAIKU_INPUT_COST_PER_MILLION = 0.80   # Update this
   HAIKU_OUTPUT_COST_PER_MILLION = 4.00  # Update this
   ```
3. Done! All programs automatically use new values.

## 📖 Full Documentation

- **User Guide**: `docs/project/Cost_Tracking_System.md`
- **Implementation Summary**: `docs/project/Cost_Tracking_Implementation_Summary.md`

## ✅ Status

**Production Ready** - All code implemented and tested.
