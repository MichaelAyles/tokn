# TOKN Benchmark Suite

Benchmarks for evaluating LLM performance on TOKN circuit generation.

## Overview

This suite tests a model's ability to generate valid TOKN schematics from natural language prompts. It establishes baseline metrics before fine-tuning and measures improvement after.

## Components

### `prompts.py` - Prompt Generator

Generates varied natural language prompts from the training data.

```bash
python benchmark/prompts.py
```

**Output:** `benchmark/test_prompts.jsonl`

**Prompt styles:**
- `direct_give` - "Give me a TOKN circuit for..."
- `direct_create` - "Create a {name} in TOKN format"
- `component_focused` - "Design a circuit using {components}"
- `function_focused` - "I need to {use_case}"
- `tag_based` - "Give me a {tag} circuit"

### `validate.py` - Validation Suite

Validates generated TOKN for correctness.

```bash
python benchmark/validate.py <file.tokn> [--verbose] [--roundtrip]
```

**Validation checks:**

1. **Syntax validity** - Parses as valid TOKN
2. **Semantic validity** - References exist, connections make sense
3. **Completeness** - Has decoupling caps, power/ground for ICs
4. **Round-trip** (optional) - Can decode back to KiCad

**Scoring:**
- Base score: 1.0
- -0.1 per semantic error
- -0.02 per warning
- -0.2 for roundtrip failure

### `runner.py` - Benchmark Runner

Runs prompts through a model API and collects results.

```bash
# Using Anthropic
python benchmark/runner.py --provider anthropic --model claude-sonnet-4-20250514 --limit 20

# Using OpenAI
python benchmark/runner.py --provider openai --model gpt-4o --limit 20
```

**Arguments:**
- `--prompts` - Path to prompts JSONL (default: `benchmark/test_prompts.jsonl`)
- `--output` - Output path for summary (default: `benchmark/results.json`)
- `--model` - Model name
- `--provider` - `anthropic` or `openai`
- `--limit` - Limit number of prompts (for testing)

**Output files:**
- `benchmark/results.json` - Summary statistics
- `benchmark/results_results.jsonl` - Detailed per-prompt results

## Metrics

### Per-prompt metrics
- Syntax valid (bool)
- Semantic valid (bool)
- Complete (bool)
- Validation score (0-1)
- Generation time (ms)

### Aggregate metrics
- % Syntax valid
- % Semantic valid
- % Complete
- Average validation score
- Average generation time
- Scores by prompt style

## Usage

### 1. Generate test prompts

```bash
python benchmark/prompts.py
```

### 2. Run baseline benchmark

```bash
# Test with small batch first
python benchmark/runner.py --limit 10

# Full benchmark
python benchmark/runner.py
```

### 3. Fine-tune model

(Use training data from `data/training/`)

### 4. Run post-training benchmark

```bash
python benchmark/runner.py --model <fine-tuned-model> --output benchmark/results_finetuned.json
```

### 5. Compare results

```bash
python -c "
import json
baseline = json.load(open('benchmark/results.json'))
finetuned = json.load(open('benchmark/results_finetuned.json'))
print(f'Baseline score: {baseline[\"avg_validation_score\"]:.3f}')
print(f'Fine-tuned score: {finetuned[\"avg_validation_score\"]:.3f}')
print(f'Improvement: {finetuned[\"avg_validation_score\"] - baseline[\"avg_validation_score\"]:.3f}')
"
```

## Test Prompts

200 prompts generated from high-quality (score >= 5) training data:

| Style | Count |
|-------|-------|
| direct_give | ~43 |
| direct_create | ~45 |
| component_focused | ~37 |
| function_focused | ~41 |
| tag_based | ~34 |

Each prompt includes:
- Natural language request
- Reference TOKN (ground truth)
- Metadata (subcircuit name, tags, source repo)

## System Prompt

The benchmark uses this system prompt for generation:

```
You are an expert electronics design assistant that generates TOKN format schematics.

TOKN (Token-Optimised KiCad Notation) is a compact format for representing electronic schematics.

[Format specification...]

Generate valid, complete TOKN schematics based on the user's request.
```

See `runner.py` for the full prompt.
