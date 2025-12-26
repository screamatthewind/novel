"""
Quick test script to compare prompt generation methods on a single sentence.
"""

import os
import sys
from datetime import datetime
from scene_parser import parse_all_chapters, parse_scene_sentences
from prompt_generator import generate_prompt, generate_prompt_with_ollama, generate_prompt_with_haiku, get_negative_prompt
from cost_tracker import CostTracker

def main():
    # Parse Chapter 1
    print("Parsing Chapter 1...")
    scenes = parse_all_chapters(chapter_numbers=[1])
    print(f"Found {len(scenes)} scenes")

    # Get sentences - parse_scene_sentences takes a single scene
    all_sentences = []
    for scene in scenes:
        scene_sentences = parse_scene_sentences(scene)
        all_sentences.extend(scene_sentences)
    print(f"Found {len(all_sentences)} sentences\n")

    # Check command line arguments for method
    if len(sys.argv) > 1:
        method = sys.argv[1].lower()
        if method not in ['keyword', 'ollama', 'haiku', 'all']:
            print("Usage: python test_prompt_comparison.py [keyword|ollama|haiku|all]")
            print("  keyword - Test keyword-based method (default)")
            print("  ollama  - Test Ollama local LLM")
            print("  haiku   - Test Claude Haiku API")
            print("  all     - Test all three methods")
            sys.exit(1)
    else:
        method = 'all'

    # Test on first sentence
    sentence = all_sentences[0]
    print("="*80)
    print(f"SENTENCE (Chapter {sentence.chapter_num}, Scene {sentence.scene_num}, Sentence {sentence.sentence_num}):")
    print(f'"{sentence.content}"')
    print("="*80)
    print()

    # Create cost tracker for this test
    with CostTracker(f"test_prompt_comparison_{method}") as cost_tracker:
        # Generate prompts based on selected method
        prompts = {}
        tokens = {}  # Track tokens for haiku

        if method in ['keyword', 'all']:
            print("Generating keyword-based prompt...")
            prompts['keyword'] = generate_prompt(sentence.content, scene_context=sentence.scene_context)
            print()

        if method in ['ollama', 'all']:
            print("Generating Ollama prompt...")
            prompts['ollama'] = generate_prompt_with_ollama(sentence.content, scene_context=sentence.scene_context)
            print()

        if method in ['haiku', 'all']:
            print("Generating Haiku prompt...")
            haiku_prompt, input_tokens, output_tokens = generate_prompt_with_haiku(
                sentence.content,
                scene_context=sentence.scene_context,
                cost_tracker=cost_tracker
            )
            prompts['haiku'] = haiku_prompt
            tokens['haiku'] = {'input': input_tokens, 'output': output_tokens}
            print()

    # Display results
    print("="*80)
    print("RESULTS:")
    print("="*80)

    for method_name, prompt in prompts.items():
        print(f"\n[{method_name.upper()}]")
        if prompt:
            print(f"{prompt}")
            print(f"\nLength: {len(prompt)} chars")
            # Show token usage for haiku
            if method_name == 'haiku' and method_name in tokens:
                print(f"Tokens: {tokens[method_name]['input']} in / {tokens[method_name]['output']} out")
        else:
            print("FAILED")
            if method_name == 'ollama':
                print("Make sure Ollama is running: ollama serve")
                print("And model is downloaded: ollama pull llama3.1:8b")
            elif method_name == 'haiku':
                print("Set ANTHROPIC_API_KEY in .env file (see .env.example)")

    # Summary if testing all
    if len(prompts) > 1:
        print("\n" + "="*80)
        print("SUMMARY:")
        print("="*80)
        success_count = sum(1 for p in prompts.values() if p)
        print(f"Successful: {success_count}/{len(prompts)}")
        for method_name, prompt in prompts.items():
            if prompt:
                print(f"  [OK] {method_name}: {len(prompt)} chars")
            else:
                print(f"  [FAIL] {method_name}")

    # Write output to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "test-results")
    os.makedirs(output_dir, exist_ok=True)

    output_filename = f"prompt_test_{method}_{timestamp}.txt"
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write(f"PROMPT GENERATION TEST - {method.upper()}\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")

        f.write(f"SENTENCE (Chapter {sentence.chapter_num}, Scene {sentence.scene_num}, Sentence {sentence.sentence_num}):\n")
        f.write(f'"{sentence.content}"\n\n')

        f.write("="*80 + "\n")
        f.write("RESULTS:\n")
        f.write("="*80 + "\n\n")

        for method_name, prompt in prompts.items():
            f.write(f"[{method_name.upper()}]\n")
            if prompt:
                f.write(f"{prompt}\n")
                f.write(f"\nLength: {len(prompt)} chars\n\n")
            else:
                f.write("FAILED\n")
                if method_name == 'ollama':
                    f.write("Make sure Ollama is running: ollama serve\n")
                    f.write("And model is downloaded: ollama pull llama3.1:8b\n")
                elif method_name == 'haiku':
                    f.write("Set ANTHROPIC_API_KEY in .env file (see .env.example)\n")
                f.write("\n")

        if len(prompts) > 1:
            f.write("="*80 + "\n")
            f.write("SUMMARY:\n")
            f.write("="*80 + "\n")
            success_count = sum(1 for p in prompts.values() if p)
            f.write(f"Successful: {success_count}/{len(prompts)}\n")
            for method_name, prompt in prompts.items():
                if prompt:
                    f.write(f"  [OK] {method_name}: {len(prompt)} chars\n")
                else:
                    f.write(f"  [FAIL] {method_name}\n")

    # Simple status message
    print("\n" + "="*80)
    print("STATUS:")
    print("="*80)
    success_count = sum(1 for p in prompts.values() if p)
    total_count = len(prompts)

    if success_count == total_count:
        print(f"✓ SUCCESS: All {total_count} method(s) completed")
    elif success_count > 0:
        print(f"⚠ PARTIAL: {success_count}/{total_count} method(s) completed")
    else:
        print(f"✗ FAILED: All {total_count} method(s) failed")

    print(f"\nOutput saved to: output/test-results/{output_filename}")
    print("="*80)

    # Print cost summary if haiku was used
    if method in ['haiku', 'all'] and 'haiku' in tokens and tokens['haiku']['input'] > 0:
        print()
        # Manually create summary since we're outside context manager
        from cost_tracker import calculate_cost, get_total_cost
        session_cost = calculate_cost(tokens['haiku']['input'], tokens['haiku']['output'])
        total_input, total_output, total_cost = get_total_cost()

        print("="*80)
        print("HAIKU API COST SUMMARY")
        print("="*80)
        print(f"\nThis Test:")
        print(f"  API Calls: 1")
        print(f"  Input Tokens: {tokens['haiku']['input']:,}")
        print(f"  Output Tokens: {tokens['haiku']['output']:,}")
        print(f"  Total Tokens: {tokens['haiku']['input'] + tokens['haiku']['output']:,}")
        print(f"  Test Cost: ${session_cost:.6f} USD")
        print(f"\nCumulative Total (All Time):")
        print(f"  Total Input Tokens: {total_input:,}")
        print(f"  Total Output Tokens: {total_output:,}")
        print(f"  Total Tokens: {total_input + total_output:,}")
        print(f"  Total Cost: ${total_cost:.6f} USD")
        print("="*80)

if __name__ == "__main__":
    main()
