"""
Benchmark runner for TOKN generation.

Runs prompts through a model, validates outputs, and runs AI scoring.
Outputs structured results to timestamped directories.
"""

import json
import time
import os
from pathlib import Path
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional
import sys
import re

# Load environment variables from .env.local
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(env_path)

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from validate import validate_tokn, ValidationResult


@dataclass
class PromptResult:
    """Complete result for a single benchmark prompt."""
    # Input
    prompt_id: int
    prompt: str
    prompt_style: str
    required_ics: list = field(default_factory=list)
    required_components: list = field(default_factory=list)

    # Generated output
    generated_tokn: str = ""
    generation_time_ms: float = 0.0

    # Static validation scores
    static_score: float = 0.0
    syntax_valid: bool = False
    semantic_valid: bool = False
    requirement_score: float = 0.0
    matched_requirements: list = field(default_factory=list)
    missing_requirements: list = field(default_factory=list)
    validation_errors: list = field(default_factory=list)
    validation_warnings: list = field(default_factory=list)

    # AI scores (populated later)
    ai_functionality_score: int = 0
    ai_completeness_score: int = 0
    ai_correctness_score: int = 0
    ai_best_practices_score: int = 0
    ai_overall_score: float = 0.0
    ai_issues: list = field(default_factory=list)
    ai_suggestions: list = field(default_factory=list)
    ai_explanation: str = ""

    # Metadata
    subcircuit_name: str = ""
    model_name: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BenchmarkSummary:
    """Summary of benchmark run."""
    timestamp: str
    model_name: str
    total_prompts: int

    # Counts by difficulty
    easy_count: int = 0
    medium_count: int = 0
    hard_count: int = 0

    # Static validation summary
    syntax_valid_count: int = 0
    semantic_valid_count: int = 0
    avg_static_score: float = 0.0
    avg_requirement_score: float = 0.0

    # AI scoring summary
    avg_ai_functionality: float = 0.0
    avg_ai_completeness: float = 0.0
    avg_ai_correctness: float = 0.0
    avg_ai_best_practices: float = 0.0
    avg_ai_overall: float = 0.0

    # Timing
    avg_generation_time_ms: float = 0.0
    total_run_time_s: float = 0.0

    # Scores by difficulty
    scores_by_difficulty: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


# System prompt for TOKN generation
SYSTEM_PROMPT = """You are an expert electronics design assistant that generates TOKN format schematics.

TOKN (Token-Optimised KiCad Notation) is a compact format for representing electronic schematics.

## TOKN Format Specification

```
# TOKN v1
title: <descriptive schematic name>

components[N]{ref,type,value,fp,x,y,w,h,a}:
  <reference>,<type>,<value>,<footprint>,<x>,<y>,<width>,<height>,<angle>

pins{REF}[N]:
  <pin_number>,<pin_name>

nets[N]{name,pins}:
  <net_name>,"<ref.pin>,<ref.pin>,..."

wires[N]{net,pts}:
  <net_name>,"<x1> <y1>,<x2> <y2>"
```

## Field Definitions

### Components Section
- **ref**: Reference designator (R1, R2, C1, C2, U1, IC1, D1, L1, J1, TP1, etc.)
- **type**: Component type or part number (R, C, CP for polarized cap, LED, LM7805, STM32F405, etc.)
- **value**: Component value (10k, 0.1u, 100n, 4.7uF, 22uH, etc.)
- **fp**: Footprint (0402, 0603, 0805, SOIC-8, TSSOP-16, QFP-48, etc.)
- **x,y**: Position in mm (typical range: 100-200mm)
- **w,h**: Symbol width/height in mm (typical: 0-40mm)
- **a**: Rotation angle in degrees (0, 90, 180, 270)

### Pins Section
Define pin mappings for ICs and multi-pin components:
- **pin_number**: Physical pin number (1, 2, 3... or A1, B1 for BGA)
- **pin_name**: Functional name (VCC, GND, IN+, OUT, SCL, TX, etc.)

### Nets Section
- **name**: Net name - use descriptive names for signals, standard names for power
  - Power: +5V, +3V3, +12V, GND, VBAT
  - Signals: SCL, SDA, MOSI, MISO, TX, RX, or descriptive like MCU-UART-TX
  - Anonymous: N1, N2, N3 for internal connections
- **pins**: Comma-separated list of "REF.PIN" connections

### Wires Section
Physical routing paths for each net:
- **net**: Must match a net name from nets section
- **pts**: Coordinate pairs "x1 y1,x2 y2" for wire segments

## Complete Example

```
# TOKN v1
title: MAX9926 Dual VR Conditioner Analog Front End

components[10]{ref,type,value,fp,x,y,w,h,a}:
  C66,C,1n,,160.02,73.66,0.00,7.62,0
  C67,C,1n,,160.02,102.87,0.00,7.62,0
  C68,C,0.01u,,156.21,88.90,0.00,7.62,0
  C69,C,0.1u,,167.64,88.90,0.00,7.62,0
  C70,C,1u,,179.07,88.90,0.00,7.62,0
  IC16,MAX9926UAEE_V+,MAX9926UAEE_V+,SOP64P602X175-16N,129.54,88.90,38.10,17.78,0
  R75,R,10k,0603,168.91,67.31,7.62,0.00,90
  R76,R,10k,0603,168.91,80.01,7.62,0.00,90
  R77,R,10k,0603,168.91,97.79,7.62,0.00,90
  R78,R,10k,0603,168.91,109.22,7.62,0.00,90

pins{IC16}[16]:
  1,IN_THRS1
  2,EXT1
  3,BIAS1
  4,COUT1
  5,COUT2
  6,BIAS2
  7,EXT2
  8,INT_THRS2
  9,IN2+
  10,IN2-
  11,GND
  12,DIRN
  13,ZERO_EN
  14,VCC
  15,IN1-
  16,IN1+

nets[12]{name,pins}:
  +5VD,"C68.1,C69.1,C70.1,IC16.14"
  GND,"C68.2,C69.2,C70.2,IC16.1,IC16.3,IC16.6,IC16.8,IC16.11,IC16.13"
  DIN0-VR1-IN+,R75.2
  DIN0-VR1-IN-,R76.2
  DIN1-VR2-IN+,R78.2
  DIN1-VR2-IN-,R77.2
  MCU-DIN0-VR1-FTM0,IC16.4
  MCU-DIN1-VR2-FTM1,IC16.5
  N1,"C67.2,IC16.9,R78.1"
  N2,"C66.1,IC16.16,R75.1"
  N3,"C66.2,IC16.15,R76.1"
  N4,"C67.1,IC16.10,R77.1"

wires[45]{net,pts}:
  +5VD,"156.21 85.09,167.64 85.09"
  +5VD,"148.59 85.09,156.21 85.09"
  +5VD,"167.64 85.09,179.07 85.09"
  GND,"179.07 92.71,191.77 92.71"
  GND,"151.13 92.71,156.21 92.71"
  GND,"148.59 87.63,151.13 87.63"
  N1,"160.02 109.22,165.10 109.22"
  N1,"156.21 97.79,156.21 109.22"
  N2,"156.21 80.01,148.59 80.01"
  N2,"156.21 67.31,160.02 67.31"
```

## Design Rules
1. Every IC must have its pins defined in a pins{} section
2. All IC power pins (VCC, VDD, GND, VSS) must be connected
3. Include decoupling capacitors: 0.1uF ceramic per IC minimum, plus bulk caps (10uF+) for power entry
4. Use appropriate values: pull-ups typically 4.7k-10k, current limiting resistors calculated for application
5. Wire coordinates should form connected paths between component pins
6. Use consistent net naming: power rails (+5V, GND), bus signals (SCL, SDA), descriptive names for custom signals

Generate complete, valid TOKN schematics with all sections populated."""


def extract_tokn(text: str) -> str:
    """Extract TOKN content from a model response."""
    if not text:
        return ""

    # Try to find ```tokn or ```toon or ``` block containing # TOKN v1
    code_block_match = re.search(r'```(?:tokn|toon)?\s*\n(.*?)```', text, re.DOTALL)
    if code_block_match:
        content = code_block_match.group(1).strip()
        if '# TOKN v1' in content:
            return content

    # Try to find # TOKN v1 directly
    if '# TOKN v1' in text:
        start = text.find('# TOKN v1')
        content = text[start:]

        # Find where TOKN ends
        end_markers = ['\n## ', '\n# ', '\n---', '\nThis ', '\nThe ', '\nNote:']
        for marker in end_markers:
            if marker in content[10:]:
                end = content.find(marker, 10)
                content = content[:end]
                break

        return content.strip()

    return ""


def generate_tokn_openrouter(prompt: str, model: str) -> tuple[str, float]:
    """Generate TOKN using OpenRouter API.

    Returns: (generated_text, generation_time_ms)
    """
    try:
        import openai
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")

    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")

    client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    start_time = time.time()

    try:
        response = client.chat.completions.create(
            model=model,
            max_tokens=4096,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            extra_headers={
                "HTTP-Referer": "https://github.com/MichaelAyles/tokn",
                "X-Title": "TOKN Benchmark"
            }
        )
        generated = response.choices[0].message.content
    except Exception as e:
        print(f"  Error: {e}")
        generated = ""

    generation_time = (time.time() - start_time) * 1000
    return generated, generation_time


def run_ai_scoring(prompt: str, tokn: str, model: str = "google/gemini-2.5-flash") -> dict:
    """Run AI scoring on a generated TOKN circuit."""
    try:
        from ai_scorer import ai_score_circuit
        result = ai_score_circuit(prompt, tokn, model=model)
        return result.to_dict()
    except Exception as e:
        print(f"  AI scoring error: {e}")
        return {
            "functionality_score": 0,
            "completeness_score": 0,
            "correctness_score": 0,
            "best_practices_score": 0,
            "overall_score": 0.0,
            "issues": [str(e)],
            "suggestions": [],
            "explanation": "AI scoring failed"
        }


def load_prompts(easy: int, medium: int, hard: int) -> list[dict]:
    """Load prompts from difficulty-tier files."""
    import random

    base_dir = Path(__file__).parent
    all_prompts = []

    # Load easy prompts
    if easy != 0:
        easy_path = base_dir / 'prompts_easy.jsonl'
        if easy_path.exists():
            with open(easy_path, 'r', encoding='utf-8') as f:
                prompts = [json.loads(line) for line in f]
                for p in prompts:
                    p['difficulty'] = 'easy'
                if easy > 0:
                    prompts = random.sample(prompts, min(easy, len(prompts)))
                all_prompts.extend(prompts)

    # Load medium prompts
    if medium != 0:
        medium_path = base_dir / 'prompts_medium.jsonl'
        if medium_path.exists():
            with open(medium_path, 'r', encoding='utf-8') as f:
                prompts = [json.loads(line) for line in f]
                for p in prompts:
                    p['difficulty'] = 'medium'
                if medium > 0:
                    prompts = random.sample(prompts, min(medium, len(prompts)))
                all_prompts.extend(prompts)

    # Load hard prompts
    if hard != 0:
        hard_path = base_dir / 'prompts_hard.jsonl'
        if hard_path.exists():
            with open(hard_path, 'r', encoding='utf-8') as f:
                prompts = [json.loads(line) for line in f]
                for p in prompts:
                    p['difficulty'] = 'hard'
                if hard > 0:
                    prompts = random.sample(prompts, min(hard, len(prompts)))
                all_prompts.extend(prompts)

    random.shuffle(all_prompts)
    return all_prompts


def run_benchmark(
    easy: int = 0,
    medium: int = 0,
    hard: int = 0,
    model: str = "google/gemini-2.5-flash",
    run_ai_scores: bool = True,
    prompts_file: str = None,
) -> str:
    """Run the full benchmark pipeline.

    Returns: Path to output directory
    """
    # Create output directory
    timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
    output_dir = Path(__file__).parent / "output" / f"{timestamp}_results"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load prompts
    if prompts_file:
        with open(prompts_file, 'r', encoding='utf-8') as f:
            prompts = [json.loads(line) for line in f]
            for p in prompts:
                if 'difficulty' not in p:
                    p['difficulty'] = p.get('prompt_style', 'unknown')
    else:
        prompts = load_prompts(easy, medium, hard)

    if not prompts:
        raise ValueError("No prompts loaded. Use -e, -m, -H flags or --prompts")

    # Count by difficulty
    diff_counts = {'easy': 0, 'medium': 0, 'hard': 0}
    for p in prompts:
        diff = p.get('difficulty', 'unknown')
        if diff in diff_counts:
            diff_counts[diff] += 1

    print(f"\n{'='*60}")
    print(f"TOKN Benchmark - {timestamp}")
    print(f"{'='*60}")
    print(f"Model: {model}")
    print(f"Prompts: {len(prompts)} total (easy={diff_counts['easy']}, medium={diff_counts['medium']}, hard={diff_counts['hard']})")
    print(f"Output: {output_dir}")
    print(f"AI Scoring: {'enabled' if run_ai_scores else 'disabled'}")
    print(f"{'='*60}\n")

    results = []
    start_run_time = time.time()

    for i, prompt_data in enumerate(prompts):
        prompt = prompt_data['prompt']
        difficulty = prompt_data.get('difficulty', 'unknown')
        print(f"[{i+1}/{len(prompts)}] [{difficulty}] {prompt[:60]}...")

        # Generate TOKN
        raw_response, gen_time = generate_tokn_openrouter(prompt, model)
        tokn_text = extract_tokn(raw_response)

        # Static validation
        required_ics = prompt_data.get('required_ics', [])
        required_components = prompt_data.get('required_components', [])

        if tokn_text:
            validation = validate_tokn(tokn_text, required_ics=required_ics, required_components=required_components)
        else:
            validation = ValidationResult(valid=False, syntax_valid=False, requirement_score=0.0)

        # Build result
        result = PromptResult(
            prompt_id=i,
            prompt=prompt,
            prompt_style=difficulty,
            required_ics=required_ics,
            required_components=required_components,
            generated_tokn=tokn_text,
            generation_time_ms=gen_time,
            static_score=validation.score(),
            syntax_valid=validation.syntax_valid,
            semantic_valid=validation.semantic_valid,
            requirement_score=validation.requirement_score,
            matched_requirements=validation.matched_requirements,
            missing_requirements=validation.missing_requirements,
            validation_errors=validation.semantic_errors + validation.syntax_errors,
            validation_warnings=validation.semantic_warnings + validation.completeness_warnings,
            subcircuit_name=prompt_data.get('metadata', {}).get('subcircuit_name', ''),
            model_name=model,
        )

        # Print static scores
        req_pct = f"Req:{validation.requirement_score:.0%}" if required_components else ""
        print(f"  Static: {validation.score():.2f} {req_pct} ({gen_time:.0f}ms)")

        # AI scoring
        if run_ai_scores and tokn_text:
            print(f"  Running AI scoring...")
            ai_result = run_ai_scoring(prompt, tokn_text, model)
            result.ai_functionality_score = ai_result.get('functionality_score', 0)
            result.ai_completeness_score = ai_result.get('completeness_score', 0)
            result.ai_correctness_score = ai_result.get('correctness_score', 0)
            result.ai_best_practices_score = ai_result.get('best_practices_score', 0)
            result.ai_overall_score = ai_result.get('overall_score', 0.0)
            result.ai_issues = ai_result.get('issues', [])
            result.ai_suggestions = ai_result.get('suggestions', [])
            result.ai_explanation = ai_result.get('explanation', '')
            print(f"  AI: {result.ai_overall_score:.0f}/100 (func={result.ai_functionality_score}, comp={result.ai_completeness_score}, corr={result.ai_correctness_score}, bp={result.ai_best_practices_score})")

        results.append(result)

        # Save individual result
        result_dir = output_dir / f"{i:03d}_{difficulty}"
        result_dir.mkdir(exist_ok=True)

        # Save prompt
        with open(result_dir / "prompt.txt", 'w', encoding='utf-8') as f:
            f.write(prompt)

        # Save generated TOKN
        with open(result_dir / "output.tokn", 'w', encoding='utf-8') as f:
            f.write(tokn_text if tokn_text else "# Generation failed")

        # Save full result JSON
        with open(result_dir / "result.json", 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)

    total_run_time = time.time() - start_run_time

    # Calculate summary
    summary = BenchmarkSummary(
        timestamp=timestamp,
        model_name=model,
        total_prompts=len(results),
        easy_count=diff_counts['easy'],
        medium_count=diff_counts['medium'],
        hard_count=diff_counts['hard'],
        syntax_valid_count=sum(1 for r in results if r.syntax_valid),
        semantic_valid_count=sum(1 for r in results if r.semantic_valid),
        avg_static_score=sum(r.static_score for r in results) / len(results) if results else 0,
        avg_requirement_score=sum(r.requirement_score for r in results) / len(results) if results else 0,
        avg_ai_functionality=sum(r.ai_functionality_score for r in results) / len(results) if results else 0,
        avg_ai_completeness=sum(r.ai_completeness_score for r in results) / len(results) if results else 0,
        avg_ai_correctness=sum(r.ai_correctness_score for r in results) / len(results) if results else 0,
        avg_ai_best_practices=sum(r.ai_best_practices_score for r in results) / len(results) if results else 0,
        avg_ai_overall=sum(r.ai_overall_score for r in results) / len(results) if results else 0,
        avg_generation_time_ms=sum(r.generation_time_ms for r in results) / len(results) if results else 0,
        total_run_time_s=total_run_time,
    )

    # Scores by difficulty
    for diff in ['easy', 'medium', 'hard']:
        diff_results = [r for r in results if r.prompt_style == diff]
        if diff_results:
            summary.scores_by_difficulty[diff] = {
                'count': len(diff_results),
                'avg_static_score': sum(r.static_score for r in diff_results) / len(diff_results),
                'avg_ai_overall': sum(r.ai_overall_score for r in diff_results) / len(diff_results),
            }

    # Save summary
    with open(output_dir / "summary.json", 'w', encoding='utf-8') as f:
        json.dump(summary.to_dict(), f, indent=2)

    # Save all results as JSONL
    with open(output_dir / "all_results.jsonl", 'w', encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r.to_dict(), ensure_ascii=False) + '\n')

    # Print summary
    print(f"\n{'='*60}")
    print("BENCHMARK SUMMARY")
    print(f"{'='*60}")
    print(f"Model: {model}")
    print(f"Total prompts: {len(results)}")
    print(f"Run time: {total_run_time:.1f}s")
    print(f"\nStatic Validation:")
    print(f"  Syntax valid: {summary.syntax_valid_count}/{len(results)} ({100*summary.syntax_valid_count/len(results):.1f}%)")
    print(f"  Semantic valid: {summary.semantic_valid_count}/{len(results)} ({100*summary.semantic_valid_count/len(results):.1f}%)")
    print(f"  Avg static score: {summary.avg_static_score:.3f}")
    print(f"  Avg requirement score: {summary.avg_requirement_score:.3f}")

    if run_ai_scores:
        print(f"\nAI Scoring:")
        print(f"  Avg functionality: {summary.avg_ai_functionality:.1f}/100")
        print(f"  Avg completeness: {summary.avg_ai_completeness:.1f}/100")
        print(f"  Avg correctness: {summary.avg_ai_correctness:.1f}/100")
        print(f"  Avg best practices: {summary.avg_ai_best_practices:.1f}/100")
        print(f"  Avg overall: {summary.avg_ai_overall:.1f}/100")

    print(f"\nScores by difficulty:")
    for diff, scores in summary.scores_by_difficulty.items():
        print(f"  {diff}: static={scores['avg_static_score']:.3f}, ai={scores['avg_ai_overall']:.1f}/100 (n={scores['count']})")

    print(f"\nOutput saved to: {output_dir}")

    return str(output_dir)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Run TOKN generation benchmark',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python runner.py -e 5 -m 3 -H 2    # 5 easy, 3 medium, 2 hard prompts
  python runner.py -e                 # All 100 easy prompts
  python runner.py -e 10 -H 5        # 10 easy + 5 hard (no medium)
  python runner.py --prompts file.jsonl  # Custom prompts file
  python runner.py -e 2 -m 2 -H 2 --no-ai  # Skip AI scoring

Prompt counts:
  Easy:   100 prompts (single IC, basic circuits)
  Medium: 100 prompts (2-3 ICs, subsystems)
  Hard:   50 prompts (4+ ICs, complex systems)

Output structure:
  benchmark/output/YYMMDD_HHMMSS_results/
    summary.json          # Overall benchmark summary
    all_results.jsonl     # All results as JSONL
    000_easy/             # Individual result folder
      prompt.txt          # The prompt
      output.tokn         # Generated TOKN
      result.json         # Full result with scores
    001_medium/
    ...
        """
    )
    parser.add_argument('--prompts', help='Custom prompts file (overrides -e/-m/-H)')
    parser.add_argument('--model', default='google/gemini-2.5-flash', help='Model to use')
    parser.add_argument('--no-ai', action='store_true', help='Skip AI scoring')

    # Difficulty flags
    parser.add_argument('-e', '--easy', type=int, nargs='?', const=-1, default=0,
                        help='Number of easy prompts (-1 or no value = all 100)')
    parser.add_argument('-m', '--medium', type=int, nargs='?', const=-1, default=0,
                        help='Number of medium prompts (-1 or no value = all 100)')
    parser.add_argument('-H', '--hard', type=int, nargs='?', const=-1, default=0,
                        help='Number of hard prompts (-1 or no value = all 50)')

    args = parser.parse_args()

    # Default to small sample if nothing specified
    if not args.prompts and not args.easy and not args.medium and not args.hard:
        args.easy = 2
        args.medium = 2
        args.hard = 2
        print("No prompts specified, using default: 2 easy, 2 medium, 2 hard")

    run_benchmark(
        easy=args.easy,
        medium=args.medium,
        hard=args.hard,
        model=args.model,
        run_ai_scores=not args.no_ai,
        prompts_file=args.prompts,
    )


if __name__ == '__main__':
    main()
