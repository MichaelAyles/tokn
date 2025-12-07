# TOKN Benchmark Suite

A comprehensive evaluation framework for measuring LLM performance at generating valid electronic circuit schematics in TOKN format.

## Overview

The benchmark suite tests an LLM's ability to generate valid, functional circuit designs from natural language prompts. It combines static validation (syntax and semantic checks) with AI-powered semantic scoring to evaluate whether generated circuits would actually work.

## Why This Benchmark?

Training LLMs to generate circuit schematics presents unique challenges:

1. **Structured output** - TOKN has strict syntax requirements
2. **Domain knowledge** - Correct IC pinouts, power connections, decoupling
3. **Completeness** - All power pins connected, appropriate passive components
4. **Functional correctness** - The circuit must actually work as intended

Initial benchmarking with simple prompts yielded 99% scores - far too easy. The final suite achieves ~50% baseline scores on hard prompts for untrained models, providing meaningful differentiation.

## Prompt Difficulty Tiers

### Easy (100 prompts)
Single IC circuits with basic supporting components:
- Linear regulators (LM7805, AMS1117, LM317)
- Op-amp configurations (voltage follower, inverting amp)
- Timer circuits (555 astable/monostable)
- Crystal oscillators
- LED circuits

Example:
```
Design a 5V linear regulator using LM7805 with 0.33uF input
capacitor and 0.1uF output capacitor
```

### Medium (100 prompts)
Multi-IC subsystems with 2-3 ICs and 10+ components:
- Motor drivers with H-bridges
- Display interfaces (TFT, OLED, 7-segment)
- Sensor interfaces with ADCs
- Communication interfaces (CAN, I2C level shifters)
- Audio circuits (preamps, DACs)

Example:
```
Design a BLDC motor controller with DRV8313, MAX9918 bidirectional
current sense amplifier with 10mOhm shunt, LM5008 5V buck converter
with 100uH inductor
```

### Hard (50 prompts)
Complex system-level designs with 4+ ICs across 10 categories:

| Category | Example Systems |
|----------|-----------------|
| Engine Control Units | STM32 + CAN + injector drivers |
| Computer Keyboards | ATmega32U4 + LED drivers + USB |
| USB Hubs | USB2514B + power switches + ESD |
| Flight Computers | STM32H7 + IMU + GPS + telemetry |
| BLDC Controllers | Gate drivers + current sense + encoder |
| Switch Mode Power | Multi-rail supplies with buck/boost |
| Audio Systems | DAC + amp + headphone driver |
| IoT Gateways | ESP32 + LoRa + Ethernet |
| Battery Management | BQ76940 + cell balancing + charger |
| Test Equipment | ADC + analog frontend + display |

Example:
```
Design a fixed-wing autopilot with STM32H743VIT6, ADIS16470 IMU,
MAX-M10S GPS, RFD900 telemetry connector, PCA9685 servo driver,
LIS3MDL magnetometer, MPXV7002DP airspeed sensor, SD card logging,
LM2596 5V buck with 47uH inductor
```

## Scoring System

### Static Validation (validate.py)

The static validator checks:

1. **Syntax validity** - Does it parse as valid TOKN?
2. **Semantic validity** - Are connections sensible?
   - All net references point to existing components
   - Wire nets are defined in nets section
   - IC power pins (VCC, GND) are connected
3. **Requirement matching** - Are specified components present?
4. **Completeness** - Best practices followed?
   - Decoupling capacitors present
   - Power/ground nets exist

**Score Weighting:**
- Requirement matching: 50%
- Semantic correctness: 30%
- Completeness: 20%

### AI Semantic Scoring (ai_scorer.py)

An AI model (Gemini 2.5 Flash via OpenRouter) evaluates whether the circuit would actually work:

| Score | Weight | Criteria |
|-------|--------|----------|
| Functionality | 35% | Will the circuit perform the requested function? |
| Completeness | 25% | All necessary components present? |
| Correctness | 25% | IC pins connected per datasheet? |
| Best Practices | 15% | Appropriate values, good layout? |

The AI scorer checks datasheet-level details:
- Correct pinout for specific ICs
- Appropriate component values (4.7k-10k pull-ups, etc.)
- Decoupling cap placement near IC power pins
- Voltage level compatibility

**Partial JSON Extraction:**
To handle truncated AI responses, the scorer extracts numeric scores via regex even when the full JSON is cut off mid-way through verbose issues/suggestions arrays.

## Running Benchmarks

### Basic Usage

```bash
# Default: 2 easy, 2 medium, 2 hard
python benchmark/runner.py

# Specific counts
python benchmark/runner.py -e 10 -m 5 -H 3

# All prompts from a tier
python benchmark/runner.py -e  # All 100 easy

# Skip AI scoring (faster)
python benchmark/runner.py -e 5 -m 5 -H 5 --no-ai
```

### Provider Selection

The benchmark supports multiple LLM providers:

```bash
# OpenRouter (default)
python benchmark/runner.py -e 5 --model google/gemini-2.5-flash

# Cerebras
python benchmark/runner.py -e 5 --model cerebras/llama-4-scout-17b-16e-instruct
```

**Environment Variables:**
- `OPENROUTER_API_KEY` - For OpenRouter models
- `CEREBRAS_API_KEY` - For Cerebras models

### Output Structure

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

## Baseline Results

### Gemini 2.5 Flash (30 prompts)

| Difficulty | Static Score | AI Score | Count |
|------------|-------------|----------|-------|
| Easy | 90.7% | 68.0/100 | 10 |
| Medium | 79.4% | 39.4/100 | 10 |
| Hard | 62.3% | 26.7/100 | 10 |

**Overall:** 77.5% static, 44.7/100 AI score

### Cerebras (3 prompts)

| Difficulty | Static Score | AI Score |
|------------|-------------|----------|
| Easy | 100% | 69.5/100 |
| Medium | 100% | 73.2/100 |
| Hard | 77.5% | 34.5/100 |

Note: Cerebras shows faster generation times (~1.5-5s vs ~10-16s for OpenRouter).

## Validation Details

### Requirement Matching

Each prompt specifies required ICs and component values:

```python
{
    "prompt": "Design an ECU with STM32F407VGT6...",
    "required_ics": ["STM32F407VGT6", "MCP2562", "VNQ5050"],
    "required_components": ["8MHz", "20pF", "100uF", "0.1uF"]
}
```

The validator normalizes values for matching:
- `0.1uF` matches `100nF`
- `STM32F407VGT6` matches `STM32F407` (prefix matching)
- Case-insensitive comparison

ICs are weighted 2x compared to passive components.

### Semantic Validation

Critical checks that produce **errors** (not warnings):
- IC power pins must be connected
- Nets must reference existing components
- Wires must reference defined nets

Checks that produce **warnings**:
- Single-pin nets (potential floating signal)
- Missing decoupling capacitors
- No power/ground nets defined

## System Prompt

The benchmark uses an in-context learning approach with a comprehensive system prompt including:

1. **Full TOKN specification** - Format definitions for all sections
2. **Field definitions** - Reference designators, value formats, coordinates
3. **Complete example** - MAX9926 VR Conditioner (~45 lines of valid TOKN)
4. **Design rules** - Decoupling requirements, net naming conventions

This provides the model with everything needed to generate valid TOKN without fine-tuning.

## Files

| File | Description |
|------|-------------|
| `benchmark/runner.py` | Main benchmark runner |
| `benchmark/validate.py` | Static TOKN validation |
| `benchmark/ai_scorer.py` | AI semantic scoring |
| `benchmark/prompts_easy.py` | 100 easy prompts |
| `benchmark/prompts_medium.py` | 100 medium prompts |
| `benchmark/prompts_hard.py` | 50 hard prompts |
| `benchmark/prompts_*.jsonl` | JSONL versions for loading |

## Future Work

- [ ] Add more provider integrations (Anthropic, OpenAI)
- [ ] Round-trip validation (decode to KiCad, verify opens)
- [ ] Component library coverage scoring
- [ ] Fine-tuning evaluation with trained models
- [ ] Automated regression testing
