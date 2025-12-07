# TOKN Benchmark Suite

Comprehensive evaluation framework for measuring LLM performance at generating valid electronic circuit schematics in TOKN format.

## Overview

This suite tests a model's ability to generate valid, functional TOKN circuits from natural language prompts. It combines:
- **Static validation** — syntax, semantic, and requirement checking
- **AI semantic scoring** — evaluates if circuits would actually work

## Quick Start

```bash
# Install dependencies
pip install openai python-dotenv

# Set API keys in .env.local (project root)
OPENROUTER_API_KEY=your_openrouter_key
CEREBRAS_API_KEY=your_cerebras_key

# Run benchmark with defaults (2 easy, 2 medium, 2 hard)
python benchmark/runner.py

# Run with specific counts
python benchmark/runner.py -e 10 -m 10 -H 10

# Skip AI scoring for faster runs
python benchmark/runner.py -e 5 -m 5 -H 5 --no-ai
```

## Providers & Models

### Cerebras (Recommended for speed)

Prefix models with `cerebras/`:

```bash
python benchmark/runner.py -e 5 --model cerebras/qwen-3-235b-a22b-instruct-2507
python benchmark/runner.py -e 5 --model cerebras/llama-3.3-70b
python benchmark/runner.py -e 5 --model cerebras/llama3.1-8b
python benchmark/runner.py -e 5 --model cerebras/qwen-3-32b
python benchmark/runner.py -e 5 --model cerebras/gpt-oss-120b
python benchmark/runner.py -e 5 --model cerebras/zai-glm-4.6
```

Requires `CEREBRAS_API_KEY` environment variable.

### OpenRouter (Default)

Use standard model names:

```bash
python benchmark/runner.py -e 5 --model google/gemini-2.5-flash
python benchmark/runner.py -e 5 --model anthropic/claude-sonnet-4
python benchmark/runner.py -e 5 --model openai/gpt-4o
```

Requires `OPENROUTER_API_KEY` environment variable.

## Latest Results (December 2024)

Benchmarked on 30 prompts (10 easy, 10 medium, 10 hard) via Cerebras:

| Model | AI Score | Static Score | Syntax Valid |
|-------|----------|--------------|--------------|
| **Qwen 3 235B** | 49.6/100 | 86.7% | 100% |
| ZAI GLM 4.6 | 49.4/100 | 76.1% | 90% |
| GPT-OSS 120B | 41.8/100 | 54.5% | 63% |
| Llama 3.3 70B | 35.8/100 | 82.1% | 100% |
| Qwen 3 32B | 14.5/100 | 32.4% | 40% |
| Llama 3.1 8B | 12.6/100 | 57.1% | 80% |

### By Difficulty Level

| Model | Easy | Medium | Hard |
|-------|------|--------|------|
| Qwen 3 235B | 59.6 | 41.5 | 47.6 |
| ZAI GLM 4.6 | 57.7 | 51.1 | 39.4 |
| GPT-OSS 120B | 65.5 | 29.9 | 29.9 |
| Llama 3.3 70B | 42.5 | 39.6 | 25.3 |
| Qwen 3 32B | 7.0 | 15.7 | 20.9 |
| Llama 3.1 8B | 1.4 | 16.7 | 19.6 |

## Prompt Library

| Difficulty | Count | Description |
|------------|-------|-------------|
| Easy | 100 | Single IC circuits (regulators, op-amps, 555 timers) |
| Medium | 100 | 2-3 IC subsystems (motor drivers, sensor interfaces) |
| Hard | 50 | 4+ IC complex systems (ECUs, keyboards, USB hubs) |

### Example Prompts

**Easy:**
> Design a 5V linear regulator using LM7805 with 0.33uF input capacitor and 0.1uF output capacitor

**Medium:**
> Design a BLDC motor controller with DRV8313, MAX9918 bidirectional current sense amplifier with 10mOhm shunt

**Hard:**
> Design an engine control unit with STM32F407VGT6 processor, MCP2562 CAN transceiver, VNQ5050 quad high-side driver for injectors, BTS7008 for ignition coils, 8MHz crystal with 20pF load caps

## Scoring System

### Static Validation (validate.py)

| Check | Weight | Description |
|-------|--------|-------------|
| Requirement matching | 50% | Required ICs and components present |
| Semantic correctness | 30% | Valid connections, power pins connected |
| Completeness | 20% | Decoupling caps, power/ground nets |

### AI Scoring (ai_scorer.py)

| Score | Weight | Description |
|-------|--------|-------------|
| Functionality | 35% | Will the circuit perform the requested function? |
| Completeness | 25% | All necessary components present? |
| Correctness | 25% | IC pins connected per datasheet? |
| Best Practices | 15% | Appropriate values, good layout? |

AI scoring uses Gemini 2.5 Flash via OpenRouter by default.

## Output Structure

Results are saved to timestamped directories:

```
benchmark/output/YYMMDD_HHMMSS_results/
  summary.json          # Overall benchmark summary
  all_results.jsonl     # All results as JSONL
  000_easy/             # Individual result folders
    prompt.txt          # The prompt
    output.tokn         # Generated TOKN
    result.json         # Full result with scores
  001_medium/
  002_hard/
  ...
```

## CLI Reference

```
python benchmark/runner.py [options]

Options:
  -e, --easy N       Number of easy prompts (default: 2, max: 100)
  -m, --medium N     Number of medium prompts (default: 2, max: 100)
  -H, --hard N       Number of hard prompts (default: 2, max: 50)
  --model MODEL      Model to use (default: google/gemini-2.5-flash)
  --no-ai            Skip AI scoring (faster)
  --prompts FILE     Custom prompts file (overrides -e/-m/-H)
```

## Files

| File | Description |
|------|-------------|
| `runner.py` | Main benchmark runner with multi-provider support |
| `validate.py` | Static TOKN validation suite |
| `ai_scorer.py` | AI semantic scoring system |
| `prompts_easy.py` | 100 easy prompts (single IC) |
| `prompts_medium.py` | 100 medium prompts (2-3 ICs) |
| `prompts_hard.py` | 50 hard prompts (4+ ICs, systems) |

## Documentation

- [Benchmark Suite Details](../docs/03-benchmark-suite.md) — Full documentation
- [Model Comparison](../docs/04-model-comparison-dec2024.md) — Detailed analysis
- [Fine-Tuning Dilemma](../docs/05-fine-tuning-dilemma.md) — Why bigger models win
