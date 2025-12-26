"""
Cost tracking system for Claude Haiku API usage.

Tracks token usage (input/output) for all Haiku API calls and maintains
cumulative cost history in the .costs/ directory.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

# Import pricing from centralized config
from config import HAIKU_INPUT_COST_PER_MILLION, HAIKU_OUTPUT_COST_PER_MILLION


# Get project root (parent of src/)
PROJECT_ROOT = Path(__file__).parent.parent

# Cost directory in project root
COST_DIR = PROJECT_ROOT / ".costs"
COST_FILE = COST_DIR / "haiku_usage.json"


def ensure_cost_dir():
    """Ensure .costs directory exists."""
    COST_DIR.mkdir(exist_ok=True)


def load_cost_history() -> Dict:
    """
    Load cost history from JSON file.

    Returns:
        Dictionary with cost history
    """
    ensure_cost_dir()

    if not COST_FILE.exists():
        return {
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cost_usd": 0.0,
            "sessions": []
        }

    with open(COST_FILE, 'r') as f:
        return json.load(f)


def save_cost_history(history: Dict):
    """
    Save cost history to JSON file.

    Args:
        history: Cost history dictionary
    """
    ensure_cost_dir()

    with open(COST_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def get_pricing_info() -> Dict[str, float]:
    """
    Get current Haiku pricing information.

    Returns:
        Dictionary with 'input' and 'output' costs per million tokens
    """
    return {
        'input_per_million': HAIKU_INPUT_COST_PER_MILLION,
        'output_per_million': HAIKU_OUTPUT_COST_PER_MILLION,
        'input_per_thousand': HAIKU_INPUT_COST_PER_MILLION / 1000,
        'output_per_thousand': HAIKU_OUTPUT_COST_PER_MILLION / 1000
    }


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """
    Calculate USD cost for Haiku API call.

    Uses pricing from config.py:
    - Input: ${HAIKU_INPUT_COST_PER_MILLION} per million tokens
    - Output: ${HAIKU_OUTPUT_COST_PER_MILLION} per million tokens

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in USD
    """
    input_cost = (input_tokens / 1_000_000) * HAIKU_INPUT_COST_PER_MILLION
    output_cost = (output_tokens / 1_000_000) * HAIKU_OUTPUT_COST_PER_MILLION
    return input_cost + output_cost


class CostTracker:
    """Context manager for tracking Haiku API costs during a session."""

    def __init__(self, session_name: str = "unnamed_session"):
        """
        Initialize cost tracker.

        Args:
            session_name: Name to identify this session in logs
        """
        self.session_name = session_name
        self.session_input_tokens = 0
        self.session_output_tokens = 0
        self.session_api_calls = 0
        self.session_start_time = None

    def __enter__(self):
        """Start tracking session."""
        self.session_start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End session and save costs."""
        self.save_session()

    def add_api_call(self, input_tokens: int, output_tokens: int):
        """
        Record a single API call.

        Args:
            input_tokens: Input tokens used
            output_tokens: Output tokens generated
        """
        self.session_input_tokens += input_tokens
        self.session_output_tokens += output_tokens
        self.session_api_calls += 1

    def get_session_cost(self) -> float:
        """
        Get cost for current session.

        Returns:
            Cost in USD
        """
        return calculate_cost(self.session_input_tokens, self.session_output_tokens)

    def get_session_stats(self) -> Dict:
        """
        Get current session statistics.

        Returns:
            Dictionary with session stats
        """
        return {
            "input_tokens": self.session_input_tokens,
            "output_tokens": self.session_output_tokens,
            "total_tokens": self.session_input_tokens + self.session_output_tokens,
            "api_calls": self.session_api_calls,
            "cost_usd": self.get_session_cost()
        }

    def save_session(self):
        """Save session data to cost history."""
        if self.session_api_calls == 0:
            # No API calls made, don't save
            return

        # Load existing history
        history = load_cost_history()

        # Update totals
        history["total_input_tokens"] += self.session_input_tokens
        history["total_output_tokens"] += self.session_output_tokens
        history["total_cost_usd"] += self.get_session_cost()

        # Add session record
        session_record = {
            "timestamp": self.session_start_time.isoformat(),
            "session_name": self.session_name,
            "input_tokens": self.session_input_tokens,
            "output_tokens": self.session_output_tokens,
            "api_calls": self.session_api_calls,
            "cost_usd": round(self.get_session_cost(), 6)
        }
        history["sessions"].append(session_record)

        # Save updated history
        save_cost_history(history)

    def print_summary(self):
        """Print session and cumulative cost summary."""
        history = load_cost_history()

        print("\n" + "="*80)
        print("HAIKU API COST SUMMARY")
        print("="*80)

        # Pricing info
        print(f"\nPricing (Claude Haiku 3.5):")
        print(f"  Input:  ${HAIKU_INPUT_COST_PER_MILLION:.2f} / million tokens")
        print(f"  Output: ${HAIKU_OUTPUT_COST_PER_MILLION:.2f} / million tokens")

        # Session costs
        print(f"\nCurrent Session: {self.session_name}")
        print(f"  API Calls: {self.session_api_calls}")
        print(f"  Input Tokens: {self.session_input_tokens:,}")
        print(f"  Output Tokens: {self.session_output_tokens:,}")
        print(f"  Total Tokens: {self.session_input_tokens + self.session_output_tokens:,}")
        print(f"  Session Cost: ${self.get_session_cost():.6f} USD")

        # Cumulative costs (including this session)
        total_input = history["total_input_tokens"] + self.session_input_tokens
        total_output = history["total_output_tokens"] + self.session_output_tokens
        total_cost = history["total_cost_usd"] + self.get_session_cost()

        print(f"\nCumulative Total (All Time):")
        print(f"  Total Input Tokens: {total_input:,}")
        print(f"  Total Output Tokens: {total_output:,}")
        print(f"  Total Tokens: {total_input + total_output:,}")
        print(f"  Total Cost: ${total_cost:.6f} USD")

        print("\n" + "="*80)


def get_total_cost() -> Tuple[int, int, float]:
    """
    Get total cumulative cost across all sessions.

    Returns:
        Tuple of (total_input_tokens, total_output_tokens, total_cost_usd)
    """
    history = load_cost_history()
    return (
        history["total_input_tokens"],
        history["total_output_tokens"],
        history["total_cost_usd"]
    )


def print_cost_history(limit: int = 10):
    """
    Print recent cost history.

    Args:
        limit: Number of recent sessions to show
    """
    history = load_cost_history()

    print("\n" + "="*80)
    print(f"RECENT HAIKU API USAGE (Last {limit} Sessions)")
    print("="*80)

    sessions = history["sessions"][-limit:]

    for session in sessions:
        print(f"\n[{session['timestamp']}] {session['session_name']}")
        print(f"  API Calls: {session['api_calls']}")
        print(f"  Tokens: {session['input_tokens']:,} in / {session['output_tokens']:,} out")
        print(f"  Cost: ${session['cost_usd']:.6f} USD")

    print("\n" + "="*80)
    print(f"Total Cost (All Time): ${history['total_cost_usd']:.6f} USD")
    print("="*80)


def main():
    """Test cost tracking system."""
    # Example: simulate an API session
    with CostTracker("test_session") as tracker:
        # Simulate 3 API calls
        tracker.add_api_call(input_tokens=500, output_tokens=150)
        tracker.add_api_call(input_tokens=450, output_tokens=120)
        tracker.add_api_call(input_tokens=600, output_tokens=180)

        # Print summary
        tracker.print_summary()

    # Show history
    print_cost_history(limit=5)


if __name__ == "__main__":
    main()
