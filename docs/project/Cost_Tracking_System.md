# Cost Tracking System for Claude Haiku API Usage

## Overview

The cost tracking system automatically monitors and reports token usage and costs for all Claude Haiku API calls used in prompt generation. All costs are tracked in **tokens** and converted to **USD** based on current Haiku pricing.

**Pricing is centrally configured in `src/config.py`** to make updates easy when API pricing changes.

## Pricing (Claude Haiku 3.5)

Current pricing is defined in **[src/config.py](../../src/config.py)** as:

```python
HAIKU_INPUT_COST_PER_MILLION = 0.80   # $0.80 per million input tokens
HAIKU_OUTPUT_COST_PER_MILLION = 4.00  # $4.00 per million output tokens
```

- **Input tokens**: $0.80 per million tokens
- **Output tokens**: $4.00 per million tokens

## Storage Location

All cost data is stored in the `.costs/` directory in the project root:

```
.costs/
└── haiku_usage.json    # Cumulative cost history
```

**Note**: The `.costs/` folder is ignored by git (see `.gitignore`) to keep cost data local.

## Cost Data Structure

The `haiku_usage.json` file contains:

```json
{
  "total_input_tokens": 15000,
  "total_output_tokens": 3000,
  "total_cost_usd": 0.024,
  "sessions": [
    {
      "timestamp": "2024-01-15T14:30:00",
      "session_name": "generate_images_chapters_1",
      "input_tokens": 5000,
      "output_tokens": 1000,
      "api_calls": 10,
      "cost_usd": 0.008
    }
  ]
}
```

## Using Cost Tracking in Scripts

### Automatic Tracking

All programs that use Haiku are **already configured** to track costs automatically:

1. **`generate_scene_images.py`** - Tracks costs when using `--llm haiku` or `--llm compare`
2. **`test_prompt_comparison.py`** - Tracks costs when testing Haiku prompts

### Cost Reports

When a program uses Haiku, it will display a cost summary at the end:

```
================================================================================
HAIKU API COST SUMMARY
================================================================================

Current Session: generate_images_chapters_1
  API Calls: 25
  Input Tokens: 12,500
  Output Tokens: 2,500
  Total Tokens: 15,000
  Session Cost: $0.020000 USD

Cumulative Total (All Time):
  Total Input Tokens: 50,000
  Total Output Tokens: 10,000
  Total Tokens: 60,000
  Total Cost: $0.080000 USD

================================================================================
```

## Using the Cost Tracker Module

### In Your Own Scripts

```python
from cost_tracker import CostTracker

# Create a session with a descriptive name
with CostTracker("my_custom_session") as tracker:
    # Generate prompts (tracker is passed to functions)
    prompt, input_tokens, output_tokens = generate_prompt_with_haiku(
        sentence="The robot stood in the factory.",
        cost_tracker=tracker
    )

    # Cost is automatically tracked!

# When the context exits, costs are saved and summary is printed
```

### Manual Cost Tracking

```python
from cost_tracker import CostTracker

tracker = CostTracker("manual_session")

# Manually add API call results
tracker.add_api_call(input_tokens=500, output_tokens=100)
tracker.add_api_call(input_tokens=600, output_tokens=120)

# Get session statistics
stats = tracker.get_session_stats()
print(f"Session cost: ${stats['cost_usd']:.6f}")

# Save session data
tracker.save_session()

# Print full summary
tracker.print_summary()
```

### Viewing Cost History

```python
from cost_tracker import print_cost_history, get_total_cost

# Show last 10 sessions
print_cost_history(limit=10)

# Get total cumulative cost
total_input, total_output, total_cost = get_total_cost()
print(f"Total cost across all sessions: ${total_cost:.6f} USD")
```

## Command-Line Usage

### Generate Images with Haiku (with cost tracking)

```bash
# Dry run with Haiku prompts (shows costs without generating images)
cd src
../venv/Scripts/python generate_scene_images.py --dry-run --llm haiku

# Generate Chapter 1 images with Haiku prompts
../venv/Scripts/python generate_scene_images.py --chapters 1 --llm haiku

# Compare all three methods (keyword, Ollama, Haiku)
../venv/Scripts/python generate_scene_images.py --chapters 1 --llm compare
```

### Test Prompt Generation

```bash
# Test Haiku prompt generation on a single sentence
cd src
../venv/Scripts/python test_prompt_comparison.py haiku

# Compare all methods (includes cost tracking for Haiku)
../venv/Scripts/python test_prompt_comparison.py all
```

### Test Cost Tracker Directly

```bash
cd src
../venv/Scripts/python cost_tracker.py
```

This will run a simulation and show how cost tracking works.

## Cost Estimation

### Pricing Reference (Claude Haiku 3.5)

- **Input tokens**: $0.80 per million tokens
- **Output tokens**: $4.00 per million tokens

Source: [Anthropic Pricing Documentation](https://platform.claude.com/docs/en/about-claude/pricing)

### Per Prompt Estimate

Each image prompt generation typically uses:
- **Input tokens**: 500-600 tokens (scene context + character descriptions + instructions)
- **Output tokens**: 80-120 tokens (generated SDXL prompt)
- **Cost per prompt**: ~$0.00084 USD (roughly 0.084 cents, or about 1/12th of a cent)

**Calculation example:**
- Input: 550 tokens × ($0.80 / 1,000,000) = $0.00044
- Output: 100 tokens × ($4.00 / 1,000,000) = $0.00040
- Total: $0.00084 per prompt

### Chapter Estimate

For a chapter with 50 sentences:
- **Total API calls**: 50
- **Total tokens**: ~32,500 tokens (27,500 input + 5,000 output)
- **Total cost**: ~$0.042 USD (about 4.2 cents)

### Full Novel Estimate (12 chapters, ~600 sentences)

- **Total API calls**: 600
- **Total tokens**: ~390,000 tokens (330,000 input + 60,000 output)
- **Total cost**: ~$0.50 USD (about 50 cents)

### Cost Optimization Options

**Batch API (50% discount):**
- Available for non-urgent workloads with 24-hour processing window
- Haiku 3.5 Batch: $0.40 / MTok input, $2.00 / MTok output
- Full novel cost with batch: ~$0.25 USD (25 cents)

**Prompt Caching (90% discount on cached tokens):**
- Useful for repeated scene context or character descriptions
- Cache read tokens: $0.08 / MTok (vs $0.80 / MTok regular input)
- Potential savings: Up to 40% on repeated context

## Benefits

1. **Transparency**: Know exactly how much each session costs
2. **Cumulative tracking**: See total costs across all time
3. **Session history**: Review past usage patterns
4. **Budget management**: Monitor spending before it happens
5. **Automatic**: No manual tracking required

## Files Modified

The following files include cost tracking:

- **`src/config.py`** - Centralized pricing configuration (UPDATE HERE if prices change)
- **`src/cost_tracker.py`** - Cost tracking module (imports pricing from config)
- **`src/prompt_generator.py`** - Updated to return token counts
- **`src/generate_scene_images.py`** - Integrated cost tracking
- **`src/test_prompt_comparison.py`** - Integrated cost tracking
- **`.gitignore`** - Added `.costs/` to ignore list
- **`.vscode/launch.json`** - Added cost tracker launch configuration

### Updating Pricing

If Claude Haiku pricing changes in the future, update **only** these two values in `src/config.py`:

```python
HAIKU_INPUT_COST_PER_MILLION = 0.80   # Update this
HAIKU_OUTPUT_COST_PER_MILLION = 4.00  # Update this
```

All cost calculations will automatically use the new values.

## Notes

- Cost tracking is **automatic** when using Haiku
- Costs are tracked **locally** (not shared via git)
- No API calls are made to track costs (it's all local)
- Token counts come directly from the Anthropic API response
- Costs are calculated based on official Haiku pricing
