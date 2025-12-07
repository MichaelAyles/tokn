# AI Scorer for TOKN Circuits

An AI-based semantic scoring system that evaluates generated TOKN circuits against their original prompts to determine if they will actually work as intended.

## Overview

The AI scorer goes beyond syntax validation to assess:
- Will the circuit actually function as requested?
- Are all necessary components present?
- Are connections correct for the ICs used?
- Does it follow electronics design best practices?

## Scoring Categories

Each circuit receives scores in four categories (0-100):

### 1. Functionality Score (35% weight)
**Will this circuit perform the requested function?**
- Does the circuit topology match what was requested?
- Are the right ICs and components used?
- Will it achieve the intended purpose?

### 2. Completeness Score (25% weight)
**Are all necessary components present?**
- All required ICs included
- Power pins connected (VCC, GND, etc.)
- Decoupling capacitors (0.1uF per IC minimum)
- Bulk capacitors for power entry (10uF+)
- Pull-up/pull-down resistors where needed
- Current limiting resistors for LEDs

### 3. Correctness Score (25% weight)
**Are connections correct for the ICs used?**
- IC pins connected per datasheet specs
- Power pins correctly identified
- Signal pins mapped to proper functions
- Pin numbers match IC packages
- Polarized components oriented correctly
- Voltage levels compatible

### 4. Best Practices Score (15% weight)
**Does it follow good design practices?**
- Decoupling caps close to IC power pins
- Appropriate component values
  - Pull-ups: 4.7k-10k typical
  - LED current limiting: ~10-20mA
  - Decoupling: 0.1uF ceramic + bulk caps
- Descriptive, consistent net naming
- Logical layout organization

### Overall Score
Weighted average: `0.35*func + 0.25*complete + 0.25*correct + 0.15*practice`

## Installation

Requires the OpenAI Python library for OpenRouter API access:

```bash
pip install openai python-dotenv
```

Set your OpenRouter API key in `.env.local`:
```
OPENROUTER_API_KEY=your_key_here
```

Get an API key from [https://openrouter.ai/keys](https://openrouter.ai/keys)

## Usage

### Score a Batch of Benchmark Results

```bash
# Score all results
python benchmark/ai_scorer.py \
  --input benchmark/results_results.jsonl \
  --output benchmark/ai_scores.json

# Score first 10 results only
python benchmark/ai_scorer.py \
  --input benchmark/results_results.jsonl \
  --output benchmark/ai_scores.json \
  --limit 10

# Use a different model
python benchmark/ai_scorer.py \
  --input benchmark/results_results.jsonl \
  --output benchmark/ai_scores.json \
  --model anthropic/claude-sonnet-4
```

### Score a Single Circuit

```bash
python benchmark/ai_scorer.py \
  --prompt "Design a 555 timer LED blinker" \
  --tokn examples/circuit.tokn \
  --model google/gemini-2.0-flash-exp
```

## Output Format

### Detailed Results (`*_detailed.jsonl`)

Each line contains the original benchmark result plus an `ai_score` field:

```json
{
  "prompt": "Design a 555 timer circuit...",
  "generated_tokn": "# TOKN v1\n...",
  "validation": {...},
  "ai_score": {
    "functionality_score": 85,
    "completeness_score": 75,
    "correctness_score": 90,
    "best_practices_score": 70,
    "overall_score": 82.5,
    "issues": [
      "Missing decoupling capacitor on IC1 pin 8",
      "LED current limiting resistor R1 is too large (should be ~330R, not 1k)"
    ],
    "suggestions": [
      "Add 0.1uF ceramic capacitor between IC1 pin 8 (VCC) and pin 1 (GND)",
      "Replace R1 with 330R for proper LED current (~15mA at 5V)"
    ],
    "explanation": "Circuit is functional and will work as a 555 timer, but missing critical decoupling cap."
  }
}
```

### Summary Results (`*.json`)

```json
{
  "model": "google/gemini-2.0-flash-exp",
  "total_scored": 50,
  "valid_scores": 48,
  "avg_overall_score": 76.3,
  "avg_functionality": 82.1,
  "avg_completeness": 71.5,
  "avg_correctness": 78.9,
  "avg_best_practices": 68.2,
  "score_distribution": {
    "90-100": 5,
    "80-89": 12,
    "70-79": 18,
    "60-69": 9,
    "50-59": 3,
    "0-49": 1
  }
}
```

## Supported Models

Any model available on OpenRouter can be used. Popular choices:

- `google/gemini-2.0-flash-exp` (default, fast and affordable)
- `anthropic/claude-sonnet-4` (high quality)
- `openai/gpt-4o` (good balance)
- `meta-llama/llama-3.1-70b-instruct` (open source)

See [OpenRouter models](https://openrouter.ai/models) for full list.

## What the AI Checks

The AI scorer evaluates circuits with electronics expertise, checking:

### Power Integrity
- Are all IC power pins (VCC/VDD/GND/VSS) connected?
- Are decoupling capacitors present and properly placed?
- Are bulk capacitors included for power supply filtering?
- Are power rail net names consistent (+5V, +3V3, GND)?

### Component Correctness
- Are the right ICs used for the requested function?
- Are component values appropriate (resistors, capacitors)?
- Are polarized components oriented correctly?
- Are current limiting resistors sized correctly for LEDs?

### Pin Connectivity
- Do IC pin connections match datasheet specifications?
- Are pin numbers correct for the package type?
- Are signal pins connected to appropriate functions?
- Are unconnected pins handled properly?

### Design Quality
- Is the layout organized logically?
- Are net names descriptive and meaningful?
- Are component reference designators sequential?
- Does the design follow industry best practices?

## Example Evaluations

### High Score (90+)
```
Functionality: 95 - Perfect 555 astable circuit implementation
Completeness: 90 - All components present, good decoupling
Correctness:   95 - All connections match datasheet
Practices:     85 - Good layout, decoupling caps well-placed
Overall:       92.5
```

### Medium Score (70-79)
```
Functionality: 85 - Circuit will work but suboptimal timing
Completeness: 70 - Missing bulk cap, some decoupling present
Correctness:   80 - Minor pin assignment issues
Practices:     65 - Poor net naming, layout could be better
Overall:       76.5
```

### Low Score (<60)
```
Functionality: 60 - Circuit topology is questionable
Completeness: 40 - Missing critical decoupling, no bulk caps
Correctness:   50 - Several pin misconnections
Practices:     30 - Poor organization, confusing net names
Overall:       48.5
```

## Common Issues Found

The AI scorer frequently identifies:

1. **Missing decoupling capacitors** - Most common issue
2. **Incorrect resistor values** - LEDs, pull-ups, timing
3. **Unconnected power pins** - VCC or GND not connected
4. **Pin numbering errors** - Wrong package pinout used
5. **Missing bulk capacitors** - Power supply stability
6. **Poor net naming** - N1, N2 instead of descriptive names
7. **Component placement** - Decoupling caps far from ICs

## Limitations

The AI scorer:
- Cannot simulate actual circuit operation
- May not catch all edge cases in complex designs
- Depends on model knowledge of specific ICs
- Works best with common, well-documented components
- May be conservative about uncommon design patterns

## Testing

Run the unit tests to verify functionality:

```bash
python benchmark/test_ai_scorer.py
```

This tests:
- Dataclass structure and serialization
- System prompt completeness
- Weighted average calculation

## Cost Considerations

Pricing varies by model (see [OpenRouter pricing](https://openrouter.ai/models)):

- Gemini 2.0 Flash: ~$0.10 per 1M input tokens
- Claude Sonnet 4: ~$3.00 per 1M input tokens
- GPT-4o: ~$2.50 per 1M input tokens

Typical circuit evaluation: ~2000 input tokens, ~500 output tokens
- Gemini Flash: $0.0002-0.0003 per circuit
- Claude Sonnet: $0.006-0.008 per circuit

Scoring 100 circuits:
- Gemini Flash: ~$0.03
- Claude Sonnet: ~$0.70

## Integration with Benchmarks

The AI scorer integrates seamlessly with benchmark runs:

```bash
# Run benchmark
python benchmark/runner.py \
  --prompts benchmark/test_prompts.jsonl \
  --output benchmark/results.json \
  --limit 50

# Score the results
python benchmark/ai_scorer.py \
  --input benchmark/results_results.jsonl \
  --output benchmark/ai_scores.json

# Compare syntax validation vs AI scores
python -c "
import json
with open('benchmark/ai_scores_detailed.jsonl') as f:
    for line in f:
        r = json.loads(line)
        print(f'{r[\"validation_score\"]:.2f} syntax vs {r[\"ai_score\"][\"overall_score\"]:.1f} AI')
"
```

## Future Enhancements

Potential improvements:
- Integration with SPICE simulation for functional verification
- Component value optimization suggestions
- PCB layout quality scoring
- Power consumption estimation
- Cost optimization recommendations
- Manufacturability assessment
