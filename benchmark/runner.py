"""
Benchmark runner for TOKN generation.

Runs prompts through a model and validates the outputs.
Supports baseline (untrained) and fine-tuned model comparison.
"""

import json
import time
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, Callable
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from validate import validate_tokn, ValidationResult


@dataclass
class BenchmarkResult:
    """Result for a single benchmark prompt."""
    prompt: str
    prompt_style: str
    generated_tokn: str
    reference_tokn: str

    # Validation
    validation: ValidationResult

    # Timing
    generation_time_ms: float

    # Metadata
    subcircuit_name: str
    file_name: str
    repo: str
    reference_score: float

    # Model info
    model_name: str

    def to_dict(self) -> dict:
        d = asdict(self)
        d['validation_score'] = self.validation.score()
        return d


@dataclass
class BenchmarkSummary:
    """Summary of benchmark run."""
    model_name: str
    total_prompts: int
    successful_generations: int
    syntax_valid: int
    semantic_valid: int
    complete: int

    avg_validation_score: float
    avg_generation_time_ms: float

    # By prompt style
    scores_by_style: dict

    def to_dict(self) -> dict:
        return asdict(self)


# System prompt for TOKN generation
SYSTEM_PROMPT = """You are an expert electronics design assistant that generates TOKN format schematics.

TOKN (Token-Optimised KiCad Notation) is a compact format for representing electronic schematics.

A TOKN document has this structure:

```
# TOKN v1
title: <schematic name>

components[N]{ref,type,value,fp,x,y,w,h,a}:
  <reference>,<type>,<value>,<footprint>,<x>,<y>,<width>,<height>,<angle>

pins{REF}[N]:
  <pin_number>,<pin_name>

nets[N]{name,pins}:
  <net_name>,"<ref.pin>,<ref.pin>,..."

wires[N]{net,pts}:
  <net_name>,"<x1> <y1>,<x2> <y2>"
```

Rules:
- Components: ref (R1, C1, U1), type (R, C, CP, LED, MCP2551, etc.), value, footprint (0402, 0603, SOIC-8)
- Positions in mm, angles in degrees (0, 90, 180, 270)
- Nets connect pins as REF.PIN (e.g., U1.3, R1.1)
- Power nets: +5V, +3V3, GND, etc.
- Include decoupling capacitors for ICs
- Include pull-up/pull-down resistors where needed

Generate valid, complete TOKN schematics based on the user's request."""


def run_benchmark_anthropic(
    prompts_path: str,
    output_path: str,
    model: str = "claude-sonnet-4-20250514",
    limit: int = None,
):
    """Run benchmark using Anthropic API."""
    try:
        import anthropic
    except ImportError:
        print("Error: anthropic package not installed. Run: pip install anthropic")
        return

    client = anthropic.Anthropic()
    results = []

    with open(prompts_path, 'r', encoding='utf-8') as f:
        prompts = [json.loads(line) for line in f]

    if limit:
        prompts = prompts[:limit]

    print(f"Running benchmark with {len(prompts)} prompts using {model}")

    for i, prompt_data in enumerate(prompts):
        prompt = prompt_data['prompt']
        print(f"\n[{i+1}/{len(prompts)}] {prompt[:60]}...")

        start_time = time.time()

        try:
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}]
            )
            generated = response.content[0].text
        except Exception as e:
            print(f"  Error: {e}")
            generated = ""

        generation_time = (time.time() - start_time) * 1000

        # Extract TOKN from response (may have explanation around it)
        tokn_text = extract_tokn(generated)

        # Validate
        validation = validate_tokn(tokn_text) if tokn_text else ValidationResult(valid=False, syntax_valid=False)

        result = BenchmarkResult(
            prompt=prompt,
            prompt_style=prompt_data.get('prompt_style', 'unknown'),
            generated_tokn=tokn_text,
            reference_tokn=prompt_data.get('reference_tokn', ''),
            validation=validation,
            generation_time_ms=generation_time,
            subcircuit_name=prompt_data.get('metadata', {}).get('subcircuit_name', ''),
            file_name=prompt_data.get('metadata', {}).get('file_name', ''),
            repo=prompt_data.get('metadata', {}).get('repo', ''),
            reference_score=prompt_data.get('metadata', {}).get('score', 0),
            model_name=model,
        )
        results.append(result)

        print(f"  Valid: {validation.valid}, Score: {validation.score():.2f}, Time: {generation_time:.0f}ms")

    # Save results
    save_results(results, output_path, model)


def run_benchmark_openai(
    prompts_path: str,
    output_path: str,
    model: str = "gpt-4o",
    limit: int = None,
):
    """Run benchmark using OpenAI API."""
    try:
        import openai
    except ImportError:
        print("Error: openai package not installed. Run: pip install openai")
        return

    client = openai.OpenAI()
    results = []

    with open(prompts_path, 'r', encoding='utf-8') as f:
        prompts = [json.loads(line) for line in f]

    if limit:
        prompts = prompts[:limit]

    print(f"Running benchmark with {len(prompts)} prompts using {model}")

    for i, prompt_data in enumerate(prompts):
        prompt = prompt_data['prompt']
        print(f"\n[{i+1}/{len(prompts)}] {prompt[:60]}...")

        start_time = time.time()

        try:
            response = client.chat.completions.create(
                model=model,
                max_tokens=4096,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            )
            generated = response.choices[0].message.content
        except Exception as e:
            print(f"  Error: {e}")
            generated = ""

        generation_time = (time.time() - start_time) * 1000

        # Extract TOKN from response
        tokn_text = extract_tokn(generated)

        # Validate
        validation = validate_tokn(tokn_text) if tokn_text else ValidationResult(valid=False, syntax_valid=False)

        result = BenchmarkResult(
            prompt=prompt,
            prompt_style=prompt_data.get('prompt_style', 'unknown'),
            generated_tokn=tokn_text,
            reference_tokn=prompt_data.get('reference_tokn', ''),
            validation=validation,
            generation_time_ms=generation_time,
            subcircuit_name=prompt_data.get('metadata', {}).get('subcircuit_name', ''),
            file_name=prompt_data.get('metadata', {}).get('file_name', ''),
            repo=prompt_data.get('metadata', {}).get('repo', ''),
            reference_score=prompt_data.get('metadata', {}).get('score', 0),
            model_name=model,
        )
        results.append(result)

        print(f"  Valid: {validation.valid}, Score: {validation.score():.2f}, Time: {generation_time:.0f}ms")

    # Save results
    save_results(results, output_path, model)


def extract_tokn(text: str) -> str:
    """Extract TOKN content from a model response."""
    if not text:
        return ""

    # Look for code block with TOKN
    import re

    # Try to find ```tokn or ```toon or ``` block containing # TOKN v1
    code_block_match = re.search(r'```(?:tokn|toon)?\s*\n(.*?)```', text, re.DOTALL)
    if code_block_match:
        content = code_block_match.group(1).strip()
        if '# TOKN v1' in content:
            return content

    # Try to find # TOKN v1 directly
    if '# TOKN v1' in text:
        # Find the start
        start = text.find('# TOKN v1')
        # Take everything from there (model might add explanation after)
        content = text[start:]

        # Try to find where TOKN ends (next markdown section or end)
        end_markers = ['\n## ', '\n# ', '\n---', '\nThis ', '\nThe ', '\nNote:']
        for marker in end_markers:
            if marker in content[10:]:  # Skip the header itself
                end = content.find(marker, 10)
                content = content[:end]
                break

        return content.strip()

    return ""


def save_results(results: list[BenchmarkResult], output_path: str, model_name: str):
    """Save benchmark results and summary."""
    # Calculate summary
    valid_results = [r for r in results if r.validation.syntax_valid]

    summary = BenchmarkSummary(
        model_name=model_name,
        total_prompts=len(results),
        successful_generations=len([r for r in results if r.generated_tokn]),
        syntax_valid=len([r for r in results if r.validation.syntax_valid]),
        semantic_valid=len([r for r in results if r.validation.semantic_valid]),
        complete=len([r for r in results if r.validation.complete]),
        avg_validation_score=sum(r.validation.score() for r in results) / len(results) if results else 0,
        avg_generation_time_ms=sum(r.generation_time_ms for r in results) / len(results) if results else 0,
        scores_by_style={},
    )

    # Scores by style
    style_scores = {}
    style_counts = {}
    for r in results:
        style = r.prompt_style
        if style not in style_scores:
            style_scores[style] = 0
            style_counts[style] = 0
        style_scores[style] += r.validation.score()
        style_counts[style] += 1

    summary.scores_by_style = {
        style: style_scores[style] / style_counts[style]
        for style in style_scores
    }

    # Save detailed results
    results_path = output_path.replace('.json', '_results.jsonl')
    with open(results_path, 'w', encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r.to_dict(), ensure_ascii=False, default=str) + '\n')

    # Save summary
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary.to_dict(), f, indent=2)

    print(f"\n{'='*60}")
    print("BENCHMARK SUMMARY")
    print('='*60)
    print(f"Model: {summary.model_name}")
    print(f"Total prompts: {summary.total_prompts}")
    print(f"Successful generations: {summary.successful_generations}")
    print(f"Syntax valid: {summary.syntax_valid} ({100*summary.syntax_valid/summary.total_prompts:.1f}%)")
    print(f"Semantic valid: {summary.semantic_valid} ({100*summary.semantic_valid/summary.total_prompts:.1f}%)")
    print(f"Complete: {summary.complete} ({100*summary.complete/summary.total_prompts:.1f}%)")
    print(f"Avg validation score: {summary.avg_validation_score:.3f}")
    print(f"Avg generation time: {summary.avg_generation_time_ms:.0f}ms")

    print(f"\nScores by prompt style:")
    for style, score in sorted(summary.scores_by_style.items(), key=lambda x: -x[1]):
        print(f"  {style}: {score:.3f}")

    print(f"\nResults saved to: {results_path}")
    print(f"Summary saved to: {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Run TOKN generation benchmark')
    parser.add_argument('--prompts', default='benchmark/test_prompts.jsonl', help='Prompts file')
    parser.add_argument('--output', default='benchmark/results.json', help='Output path')
    parser.add_argument('--model', default='claude-sonnet-4-20250514', help='Model to use')
    parser.add_argument('--provider', choices=['anthropic', 'openai'], default='anthropic')
    parser.add_argument('--limit', type=int, help='Limit number of prompts')

    args = parser.parse_args()

    if args.provider == 'anthropic':
        run_benchmark_anthropic(args.prompts, args.output, args.model, args.limit)
    else:
        run_benchmark_openai(args.prompts, args.output, args.model, args.limit)


if __name__ == '__main__':
    main()
