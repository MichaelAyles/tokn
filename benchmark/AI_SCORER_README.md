# AI Scorer for TOKN Circuits

AI-based semantic scoring system that evaluates generated TOKN circuits against their original prompts to determine if they will actually work as intended.

## Overview

The AI scorer goes beyond syntax validation to assess:
- Will the circuit actually function as requested?
- Are all necessary components present?
- Are connections correct for the ICs used?
- Does it follow electronics design best practices?

## Integration

The AI scorer is integrated into the benchmark runner by default:

```bash
# With AI scoring (default)
python benchmark/runner.py -e 5 -m 5 -H 5

# Without AI scoring (faster)
python benchmark/runner.py -e 5 -m 5 -H 5 --no-ai
```

AI scoring uses **Gemini 2.5 Flash via OpenRouter** regardless of which model is used for generation. This provides consistent scoring across different generation models.

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
- Pull-up/pull-down resistors where needed

### 3. Correctness Score (25% weight)
**Are connections correct for the ICs used?**
- IC pins connected per datasheet specs
- Power pins correctly identified
- Pin numbers match IC packages
- Voltage levels compatible

### 4. Best Practices Score (15% weight)
**Does it follow good design practices?**
- Decoupling caps close to IC power pins
- Appropriate component values
- Descriptive net naming
- Logical layout organization

### Overall Score
Weighted average: `0.35*func + 0.25*complete + 0.25*correct + 0.15*practice`

## Standalone Usage

Score a single circuit directly:

```bash
python benchmark/ai_scorer.py \
  --prompt "Design a 555 timer LED blinker" \
  --tokn examples/circuit.tokn
```

## Output

Results are included in the benchmark output:

```json
{
  "ai_functionality_score": 80,
  "ai_completeness_score": 70,
  "ai_correctness_score": 60,
  "ai_best_practices_score": 60,
  "ai_overall_score": 69.5,
  "ai_issues": [
    "Missing decoupling capacitor on IC1",
    "LED current limiting resistor too large"
  ],
  "ai_suggestions": [
    "Add 0.1uF ceramic cap between VCC and GND",
    "Replace R1 with 330R for proper LED current"
  ],
  "ai_explanation": "Circuit is functional but missing critical decoupling."
}
```

## Partial Response Handling

The scorer includes robust handling for truncated AI responses. If the JSON is cut off mid-way through verbose issues/suggestions arrays, it extracts numeric scores via regex:

```python
# Even if response truncates here:
{"functionality_score": 80, "completeness_score": 70, "issues": ["Missing dec...

# Scores are still extracted successfully
```

## Requirements

- `openai` Python package
- `OPENROUTER_API_KEY` environment variable

```bash
pip install openai python-dotenv
```

## Cost

Using Gemini 2.5 Flash via OpenRouter:
- ~$0.10 per 1M input tokens
- ~$0.0003 per circuit evaluation
- Scoring 100 circuits: ~$0.03

## What Gets Checked

### Power Integrity
- All IC power pins (VCC/VDD/GND/VSS) connected
- Decoupling capacitors present and placed correctly
- Power rail net names consistent

### Component Correctness
- Right ICs for the requested function
- Component values appropriate
- Polarized components oriented correctly

### Pin Connectivity
- Pin connections match datasheet specifications
- Pin numbers correct for package type
- Signal pins mapped to proper functions

### Design Quality
- Layout organized logically
- Net names descriptive
- Reference designators sequential
