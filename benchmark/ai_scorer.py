"""
AI-based semantic scoring system for TOKN circuits.

Evaluates generated TOKN against the original prompt using an AI model
to check if the circuit will actually work as intended.
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional
import argparse

# Load environment variables from .env.local
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(env_path)


@dataclass
class AIScoreResult:
    """Result of AI-based circuit evaluation."""
    functionality_score: int       # 0-100: Will this circuit perform the requested function?
    completeness_score: int        # 0-100: Are all necessary components present?
    correctness_score: int         # 0-100: Are connections correct for the ICs used?
    best_practices_score: int      # 0-100: Does it follow good design practices?
    overall_score: float           # Weighted average of all scores
    issues: list[str]              # Specific problems found
    suggestions: list[str]         # Improvements that could be made
    explanation: str               # Overall assessment

    def to_dict(self) -> dict:
        return asdict(self)


# System prompt for AI scoring
AI_SCORER_SYSTEM_PROMPT = """You are an expert electronics engineer evaluating circuit designs in TOKN format.

## TOKN Format Specification

TOKN (Token-Optimised KiCad Notation) is a compact format for representing electronic schematics:

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

### Field Definitions

**Components Section:**
- ref: Reference designator (R1, C1, U1, IC1, etc.)
- type: Component type or part number
- value: Component value (10k, 0.1u, 100n, etc.)
- fp: Footprint (0402, 0603, 0805, SOIC-8, etc.)
- x,y: Position in mm
- w,h: Symbol width/height in mm
- a: Rotation angle in degrees

**Pins Section:**
Define pin mappings for ICs and multi-pin components with their datasheet names.

**Nets Section:**
- name: Net name (power rails like +5V, GND, or signal names)
- pins: Comma-separated list of "REF.PIN" connections

**Wires Section:**
Physical routing paths for each net.

## Your Task

Evaluate the generated TOKN circuit against the user's prompt. Check if the circuit will actually work as intended.

You must return a JSON object with the following structure:

```json
{
  "functionality_score": <0-100>,
  "completeness_score": <0-100>,
  "correctness_score": <0-100>,
  "best_practices_score": <0-100>,
  "issues": ["issue 1", "issue 2", ...],
  "suggestions": ["suggestion 1", "suggestion 2", ...],
  "explanation": "Overall assessment of the circuit design"
}
```

## Scoring Criteria

### Functionality Score (0-100)
**Will this circuit perform the requested function?**
- Does the circuit topology match what was requested?
- Are the right ICs and components used for the task?
- Will the circuit achieve the intended purpose?
- Are critical functional connections present?

Deductions:
- -50 if completely wrong circuit type
- -30 if partially correct but missing key functionality
- -20 if functional but inefficient approach
- -10 if minor functional issues

### Completeness Score (0-100)
**Are all necessary components present?**
- Are all required ICs included?
- Are all power pins connected (VCC, VDD, GND, VSS)?
- Are decoupling capacitors present? (0.1uF ceramic per IC minimum)
- Are bulk capacitors present for power entry? (10uF+)
- Are pull-up/pull-down resistors included where needed?
- Are current limiting resistors present for LEDs?
- Are necessary passive components included?

Deductions:
- -40 if power connections are missing or incomplete
- -30 if decoupling capacitors are completely missing
- -20 if some decoupling caps present but insufficient
- -15 if bulk capacitors missing on power entry
- -10 if missing pull-up/pull-down resistors where needed
- -10 if missing current limiting resistors for LEDs
- -5 per missing required component

### Correctness Score (0-100)
**Are connections correct for the ICs used?**
- Are IC pins connected according to datasheet specifications?
- Are power pins (VCC/GND) correctly identified and connected?
- Are signal pins correctly mapped to their functions?
- Are pin numbers correct for the IC packages used?
- Are polarized components (capacitors, diodes, LEDs) oriented correctly?
- Are voltage levels compatible between connected components?
- Are current limits respected?

Deductions:
- -50 if power pins are incorrectly connected (e.g., VCC to GND)
- -30 if critical signal pins are misconnected
- -20 if pin numbering doesn't match IC package
- -15 if polarized components reversed
- -10 if voltage level mismatches exist
- -10 per incorrect pin assignment

### Best Practices Score (0-100)
**Does it follow good design practices?**
- Are decoupling caps placed close to IC power pins? (check x,y coordinates)
- Are component values appropriate?
  - Pull-ups typically 4.7k-10k
  - LED current limiting resistors calculated for ~10-20mA
  - Decoupling caps 0.1uF ceramic + bulk caps
- Are net names descriptive and consistent?
- Is the layout organized logically?
- Are bypass capacitors the right values?
- Are there any obvious design smells?

Deductions:
- -20 if decoupling caps are far from IC power pins (>20mm away)
- -15 if component values are inappropriate (e.g., 100k pull-up, 100R for LED)
- -10 if net naming is poor or confusing
- -10 if layout is disorganized
- -5 per minor best practice violation

## Important Notes

1. Be thorough but fair in your evaluation
2. Consider that some missing details might be acceptable for a schematic
3. Focus on whether the circuit will work electrically
4. Check datasheet-level correctness for common ICs
5. Provide specific, actionable feedback in issues and suggestions
6. The explanation should be a concise summary (2-3 sentences)

Return ONLY the JSON object, no additional text."""


def ai_score_circuit(
    prompt: str,
    generated_tokn: str,
    model: str = "google/gemini-2.5-flash",
    api_key: str = None
) -> AIScoreResult:
    """
    Score a generated TOKN circuit using an AI model.

    Args:
        prompt: The original user prompt
        generated_tokn: The generated TOKN circuit
        model: Model to use for scoring (default: google/gemini-2.5-flash)
        api_key: API key for OpenRouter (defaults to OPENROUTER_API_KEY env var)

    Returns:
        AIScoreResult with scores and feedback
    """
    try:
        import openai
    except ImportError:
        raise ImportError("openai package required. Run: pip install openai")

    if api_key is None:
        api_key = os.environ.get('OPENROUTER_API_KEY')

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY not found. "
            "Set it in .env.local or pass as api_key parameter. "
            "Get your key from https://openrouter.ai/keys"
        )

    client = openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    # Construct the user message
    user_message = f"""Please evaluate this TOKN circuit design.

**Original Prompt:**
{prompt}

**Generated TOKN:**
```
{generated_tokn}
```

Evaluate the circuit and return ONLY a JSON object with your assessment."""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": AI_SCORER_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.1,  # Low temperature for consistent scoring
            max_tokens=2048,
            extra_headers={
                "HTTP-Referer": "https://github.com/MichaelAyles/tokn",
                "X-Title": "TOKN AI Scorer"
            }
        )

        response_text = response.choices[0].message.content.strip()

        # Extract JSON from response (may be wrapped in ```json```)
        import re
        json_match = re.search(r'```json\s*\n(.*?)\n```', response_text, re.DOTALL)
        if json_match:
            json_text = json_match.group(1)
        else:
            # Try to find JSON object directly
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
            else:
                json_text = response_text

        # Parse the JSON response
        result = json.loads(json_text)

        # Calculate overall score (weighted average)
        overall = (
            result['functionality_score'] * 0.35 +
            result['completeness_score'] * 0.25 +
            result['correctness_score'] * 0.25 +
            result['best_practices_score'] * 0.15
        )

        return AIScoreResult(
            functionality_score=result['functionality_score'],
            completeness_score=result['completeness_score'],
            correctness_score=result['correctness_score'],
            best_practices_score=result['best_practices_score'],
            overall_score=round(overall, 2),
            issues=result.get('issues', []),
            suggestions=result.get('suggestions', []),
            explanation=result.get('explanation', '')
        )

    except json.JSONDecodeError as e:
        print(f"Error parsing AI response as JSON: {e}")
        print(f"Response was: {response_text[:500]}")
        # Return a default failure result
        return AIScoreResult(
            functionality_score=0,
            completeness_score=0,
            correctness_score=0,
            best_practices_score=0,
            overall_score=0.0,
            issues=["Failed to parse AI scorer response"],
            suggestions=[],
            explanation=f"AI scorer returned invalid JSON: {str(e)}"
        )
    except Exception as e:
        print(f"Error calling AI scorer: {e}")
        return AIScoreResult(
            functionality_score=0,
            completeness_score=0,
            correctness_score=0,
            best_practices_score=0,
            overall_score=0.0,
            issues=[f"AI scorer API error: {str(e)}"],
            suggestions=[],
            explanation=f"Failed to score circuit: {str(e)}"
        )


def ai_score_batch(
    results_jsonl_path: str,
    output_path: str,
    model: str = "google/gemini-2.5-flash",
    limit: int = None,
    api_key: str = None
) -> None:
    """
    Score a batch of results from a JSONL file.

    Args:
        results_jsonl_path: Path to benchmark results JSONL file
        output_path: Path to save AI scores JSON file
        model: Model to use for scoring
        limit: Optional limit on number of results to score
        api_key: Optional API key (defaults to env var)
    """
    # Load results
    with open(results_jsonl_path, 'r', encoding='utf-8') as f:
        results = [json.loads(line) for line in f]

    if limit:
        results = results[:limit]

    print(f"Scoring {len(results)} circuits using {model}")
    print("=" * 60)

    scored_results = []

    for i, result in enumerate(results):
        prompt = result['prompt']
        generated_tokn = result['generated_tokn']

        print(f"\n[{i+1}/{len(results)}] {prompt[:60]}...")

        if not generated_tokn or not generated_tokn.strip():
            print("  Skipping: No TOKN generated")
            ai_score = AIScoreResult(
                functionality_score=0,
                completeness_score=0,
                correctness_score=0,
                best_practices_score=0,
                overall_score=0.0,
                issues=["No TOKN was generated"],
                suggestions=[],
                explanation="Circuit generation failed"
            )
        else:
            ai_score = ai_score_circuit(prompt, generated_tokn, model, api_key)
            print(f"  Overall: {ai_score.overall_score:.1f}/100")
            print(f"  Func: {ai_score.functionality_score} | "
                  f"Complete: {ai_score.completeness_score} | "
                  f"Correct: {ai_score.correctness_score} | "
                  f"Practice: {ai_score.best_practices_score}")
            if ai_score.issues:
                print(f"  Issues: {len(ai_score.issues)}")
                for issue in ai_score.issues[:2]:  # Show first 2 issues
                    print(f"    - {issue[:80]}")

        # Combine original result with AI score
        scored_result = {
            **result,
            'ai_score': ai_score.to_dict()
        }
        scored_results.append(scored_result)

    # Calculate summary statistics
    valid_scores = [r['ai_score'] for r in scored_results if r['ai_score']['overall_score'] > 0]

    summary = {
        'model': model,
        'total_scored': len(scored_results),
        'valid_scores': len(valid_scores),
        'avg_overall_score': sum(s['overall_score'] for s in valid_scores) / len(valid_scores) if valid_scores else 0,
        'avg_functionality': sum(s['functionality_score'] for s in valid_scores) / len(valid_scores) if valid_scores else 0,
        'avg_completeness': sum(s['completeness_score'] for s in valid_scores) / len(valid_scores) if valid_scores else 0,
        'avg_correctness': sum(s['correctness_score'] for s in valid_scores) / len(valid_scores) if valid_scores else 0,
        'avg_best_practices': sum(s['best_practices_score'] for s in valid_scores) / len(valid_scores) if valid_scores else 0,
        'score_distribution': {
            '90-100': len([s for s in valid_scores if s['overall_score'] >= 90]),
            '80-89': len([s for s in valid_scores if 80 <= s['overall_score'] < 90]),
            '70-79': len([s for s in valid_scores if 70 <= s['overall_score'] < 80]),
            '60-69': len([s for s in valid_scores if 60 <= s['overall_score'] < 70]),
            '50-59': len([s for s in valid_scores if 50 <= s['overall_score'] < 60]),
            '0-49': len([s for s in valid_scores if s['overall_score'] < 50]),
        }
    }

    # Save detailed results
    detailed_output = output_path.replace('.json', '_detailed.jsonl')
    with open(detailed_output, 'w', encoding='utf-8') as f:
        for r in scored_results:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

    # Save summary
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("AI SCORING SUMMARY")
    print("=" * 60)
    print(f"Model: {summary['model']}")
    print(f"Total scored: {summary['total_scored']}")
    print(f"Valid scores: {summary['valid_scores']}")
    print(f"\nAverage Scores:")
    print(f"  Overall:        {summary['avg_overall_score']:.1f}/100")
    print(f"  Functionality:  {summary['avg_functionality']:.1f}/100")
    print(f"  Completeness:   {summary['avg_completeness']:.1f}/100")
    print(f"  Correctness:    {summary['avg_correctness']:.1f}/100")
    print(f"  Best Practices: {summary['avg_best_practices']:.1f}/100")
    print(f"\nScore Distribution:")
    for range_name, count in summary['score_distribution'].items():
        pct = 100 * count / summary['valid_scores'] if summary['valid_scores'] > 0 else 0
        print(f"  {range_name}: {count:3d} ({pct:5.1f}%)")
    print(f"\nDetailed results: {detailed_output}")
    print(f"Summary saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='AI-based semantic scoring for TOKN circuits',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Score all results from a benchmark run
  python benchmark/ai_scorer.py --input benchmark/results_results.jsonl --output benchmark/ai_scores.json

  # Score first 10 results only
  python benchmark/ai_scorer.py --input benchmark/results_results.jsonl --output benchmark/ai_scores.json --limit 10

  # Use a different model
  python benchmark/ai_scorer.py --input results.jsonl --output scores.json --model anthropic/claude-sonnet-4

  # Score a single circuit
  python benchmark/ai_scorer.py --prompt "Design a 555 timer LED blinker" --tokn circuit.tokn
        """
    )

    # Batch mode arguments
    parser.add_argument('--input', help='Input JSONL file with benchmark results')
    parser.add_argument('--output', help='Output JSON file for AI scores')
    parser.add_argument('--limit', type=int, help='Limit number of results to score')

    # Single circuit mode arguments
    parser.add_argument('--prompt', help='Single prompt to evaluate')
    parser.add_argument('--tokn', help='TOKN file to evaluate')

    # Common arguments
    parser.add_argument('--model', default='google/gemini-2.5-flash',
                       help='Model to use (default: google/gemini-2.5-flash)')
    parser.add_argument('--api-key', help='OpenRouter API key (defaults to OPENROUTER_API_KEY env var)')

    args = parser.parse_args()

    # Determine mode
    if args.input and args.output:
        # Batch mode
        ai_score_batch(args.input, args.output, args.model, args.limit, args.api_key)
    elif args.prompt and args.tokn:
        # Single circuit mode
        with open(args.tokn, 'r', encoding='utf-8') as f:
            tokn_content = f.read()

        result = ai_score_circuit(args.prompt, tokn_content, args.model, args.api_key)

        print("\n" + "=" * 60)
        print("AI SCORE RESULT")
        print("=" * 60)
        print(f"Overall Score: {result.overall_score:.1f}/100")
        print(f"\nDetailed Scores:")
        print(f"  Functionality:  {result.functionality_score}/100")
        print(f"  Completeness:   {result.completeness_score}/100")
        print(f"  Correctness:    {result.correctness_score}/100")
        print(f"  Best Practices: {result.best_practices_score}/100")
        print(f"\nExplanation:")
        print(f"  {result.explanation}")
        if result.issues:
            print(f"\nIssues Found ({len(result.issues)}):")
            for issue in result.issues:
                print(f"  - {issue}")
        if result.suggestions:
            print(f"\nSuggestions ({len(result.suggestions)}):")
            for suggestion in result.suggestions:
                print(f"  - {suggestion}")
    else:
        parser.print_help()
        print("\nError: Must provide either (--input and --output) or (--prompt and --tokn)")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
