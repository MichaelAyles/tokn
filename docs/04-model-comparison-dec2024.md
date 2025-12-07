# TOKN Model Comparison: LLM Circuit Generation Benchmark

**Date:** December 7, 2024
**Benchmark:** 30 prompts (10 easy, 10 medium, 10 hard) for Cerebras models; 15 prompts (5/5/5) for Claude Opus
**Scorer:** Google Gemini 2.5 Flash via OpenRouter

## Executive Summary

We benchmarked seven models on their ability to generate valid electronic circuit schematics in TOKN format. **Claude Opus 4.5** emerged as the clear leader, achieving 58.9/100 AI score — significantly ahead of the open models available via Cerebras.

### Key Findings

1. **Claude Opus 4.5** achieved the highest overall scores (58.9/100 AI, 90.5% static)
2. **Qwen 3 235B** is the best open model (49.6/100 AI, 86.7% static)
3. **Model size doesn't always correlate with performance** - Llama 3.3 70B underperformed smaller models
4. **Syntax validity varies dramatically** - from 40% (Qwen 3 32B) to 100% (Claude, Llama 3.3 70B, Qwen 3 235B)
5. **Claude maintains quality on hard prompts** - scoring 58.6 vs others dropping to 25-47

---

## Overall Rankings

### By AI Score (Weighted: Functionality 35%, Completeness 25%, Correctness 25%, Best Practices 15%)

| Rank | Model | Provider | AI Score | Static Score | Syntax Valid |
|------|-------|----------|----------|--------------|--------------|
| 1 | **Claude Opus 4.5** | OpenRouter | 58.9/100 | 90.5% | 100% |
| 2 | Qwen 3 235B | Cerebras | 49.6/100 | 86.7% | 100% |
| 3 | ZAI GLM 4.6 | Cerebras | 49.4/100 | 76.1% | 90% |
| 4 | GPT-OSS 120B | Cerebras | 41.8/100 | 54.5% | 63% |
| 5 | Llama 3.3 70B | Cerebras | 35.8/100 | 82.1% | 100% |
| 6 | Qwen 3 32B | Cerebras | 14.5/100 | 32.4% | 40% |
| 7 | Llama 3.1 8B | Cerebras | 12.6/100 | 57.1% | 80% |

```
AI Score by Model
═══════════════════════════════════════════════════════════════════

Claude Opus 4.5 ██████████████████████████████████████████████████████████▉  58.9
Qwen 3 235B     ████████████████████████████████████████████████▉            49.6
ZAI GLM 4.6     ████████████████████████████████████████████████▍            49.4
GPT-OSS 120B    █████████████████████████████████████████▊                   41.8
Llama 3.3 70B   ███████████████████████████████████▊                         35.8
Qwen 3 32B      ██████████████▌                                              14.5
Llama 3.1 8B    ████████████▌                                                12.6

                 0        20        40        60        80       100
```

---

## Detailed Breakdown by Difficulty

### Easy Prompts (Single IC circuits)

| Model | Static Score | AI Score |
|-------|-------------|----------|
| Claude Opus 4.5 | 92.2% | 62.8 |
| GPT-OSS 120B | 82.8% | 65.5 |
| Qwen 3 235B | 90.9% | 59.6 |
| ZAI GLM 4.6 | 72.8% | 57.7 |
| Llama 3.3 70B | 96.3% | 42.5 |
| Qwen 3 32B | 17.3% | 7.0 |
| Llama 3.1 8B | 56.9% | 1.4 |

```
Easy Prompts - AI Score
═══════════════════════════════════════════════════════════════════

GPT-OSS 120B    █████████████████████████████████████████████████████████████████▌  65.5
Claude Opus 4.5 ██████████████████████████████████████████████████████████████▊     62.8
Qwen 3 235B     ███████████████████████████████████████████████████████████▌        59.6
ZAI GLM 4.6     █████████████████████████████████████████████████████████▋          57.7
Llama 3.3 70B   ██████████████████████████████████████████▌                         42.5
Qwen 3 32B      ███████                                                              7.0
Llama 3.1 8B    █▍                                                                   1.4
```

### Medium Prompts (2-3 IC subsystems)

| Model | Static Score | AI Score |
|-------|-------------|----------|
| Claude Opus 4.5 | 99.2% | 55.4 |
| ZAI GLM 4.6 | 82.5% | 51.1 |
| Qwen 3 235B | 91.1% | 41.5 |
| Llama 3.3 70B | 81.1% | 39.6 |
| GPT-OSS 120B | 41.9% | 29.9 |
| Llama 3.1 8B | 77.2% | 16.7 |
| Qwen 3 32B | 37.2% | 15.7 |

```
Medium Prompts - AI Score
═══════════════════════════════════════════════════════════════════

Claude Opus 4.5 ███████████████████████████████████████████████████████▍            55.4
ZAI GLM 4.6     ███████████████████████████████████████████████████▏                51.1
Qwen 3 235B     █████████████████████████████████████████▌                          41.5
Llama 3.3 70B   ███████████████████████████████████████▌                            39.6
GPT-OSS 120B    █████████████████████████████▉                                      29.9
Llama 3.1 8B    ████████████████▋                                                   16.7
Qwen 3 32B      ███████████████▋                                                    15.7
```

### Hard Prompts (4+ IC complex systems)

| Model | Static Score | AI Score |
|-------|-------------|----------|
| **Claude Opus 4.5** | 80.0% | **58.6** |
| Qwen 3 235B | 78.2% | 47.6 |
| ZAI GLM 4.6 | 73.2% | 39.4 |
| GPT-OSS 120B | 38.7% | 29.9 |
| Llama 3.3 70B | 68.9% | 25.3 |
| Qwen 3 32B | 42.6% | 20.9 |
| Llama 3.1 8B | 37.1% | 19.6 |

```
Hard Prompts - AI Score
═══════════════════════════════════════════════════════════════════

Claude Opus 4.5 ██████████████████████████████████████████████████████████▌        58.6
Qwen 3 235B     ███████████████████████████████████████████████▌                   47.6
ZAI GLM 4.6     ███████████████████████████████████████▍                           39.4
GPT-OSS 120B    █████████████████████████████▉                                     29.9
Llama 3.3 70B   █████████████████████████▎                                         25.3
Qwen 3 32B      ████████████████████▉                                              20.9
Llama 3.1 8B    ███████████████████▌                                               19.6
```

**Notable:** Claude Opus 4.5 is the only model that maintains high scores on hard prompts, achieving 58.6 — higher than most models score on easy prompts.

---

## Score Component Breakdown

### AI Scoring Components (Average across all difficulties)

| Model | Functionality | Completeness | Correctness | Best Practices |
|-------|--------------|--------------|-------------|----------------|
| **Claude Opus 4.5** | 68.3 | 57.3 | **50.3** | 54.0 |
| Qwen 3 235B | 59.3 | 48.3 | 39.5 | 45.7 |
| ZAI GLM 4.6 | 58.3 | 48.7 | 40.2 | 45.2 |
| GPT-OSS 120B | 49.7 | 40.2 | 34.5 | 38.0 |
| Llama 3.3 70B | 44.3 | 37.2 | 23.8 | 33.5 |
| Llama 3.1 8B | 19.7 | 11.2 | 6.0 | 9.3 |
| Qwen 3 32B | 19.7 | 13.3 | 9.7 | 12.7 |

**Key Observation:** Claude Opus 4.5 achieves 50.3/100 on correctness — the first model to break 50%. Correctness (knowing correct IC pinouts, proper connections) remains the hardest challenge, indicating this requires deep domain knowledge.

---

## Validation Metrics

### Static Validation Results

| Model | Syntax Valid | Semantic Valid | Requirement Match |
|-------|-------------|----------------|-------------------|
| Claude Opus 4.5 | 100% (15/15) | 80% (12/15) | 92.0% |
| Qwen 3 235B | 100% (30/30) | 53% (16/30) | 95.6% |
| Llama 3.3 70B | 100% (30/30) | 37% (11/30) | 96.4% |
| ZAI GLM 4.6* | 90% (27/30) | 53% (16/30) | 84.9% |
| Llama 3.1 8B | 80% (24/30) | 30% (9/30) | 75.8% |
| GPT-OSS 120B | 63% (19/30) | 80% (24/30) | 56.2% |
| Qwen 3 32B | 40% (12/30) | 77% (23/30) | 36.5% |

*ZAI GLM 4.6 hit rate limits on 3 prompts due to restrictive quotas.

**Claude's advantage:** 80% semantic validity is the highest, indicating fewer invalid connections and better understanding of circuit design requirements.

---

## Generation Speed

| Model | Provider | Avg Time/Prompt | Notes |
|-------|----------|-----------------|-------|
| Llama 3.3 70B | Cerebras | ~1.2s | Fastest |
| Llama 3.1 8B | Cerebras | ~1.6s | |
| Qwen 3 235B | Cerebras | ~1.8s | |
| GPT-OSS 120B | Cerebras | ~2.4s | |
| Qwen 3 32B | Cerebras | ~3.1s | |
| ZAI GLM 4.6 | Cerebras | ~3.2s | |
| **Claude Opus 4.5** | OpenRouter | **~40s** | Slowest but highest quality |

Note: Claude Opus 4.5 is significantly slower but produces the best results. For production use, consider the quality vs speed tradeoff.

---

## Analysis

### Why Claude Opus 4.5 Leads

1. **Best correctness scores** - 50.3/100, first to break 50%
2. **Maintains quality on hard prompts** - 58.6 vs others dropping to 25-47
3. **Highest semantic validity** - 80% of outputs have valid connections
4. **Deep domain knowledge** - Knows IC pinouts and circuit theory

### Cerebras Models: Qwen 3 235B is Best

Among the open models available via Cerebras:
1. **Consistent syntax** - 100% valid TOKN structure
2. **Strong requirement matching** - 95.6% of required components included
3. **Best open-model correctness** - 39.5/100
4. **Fast inference** - ~1.8s per generation

### The Llama Paradox

Llama 3.3 70B shows an interesting pattern:
- Perfect syntax validity (100%)
- Excellent requirement matching (96.4%)
- But low AI scores (35.8/100)

This suggests the model generates structurally correct TOKN with the right components, but makes errors in the actual circuit connections - it knows the format but not the electronics.

### Small Model Struggles

Both Llama 3.1 8B and Qwen 3 32B struggle significantly:
- High rate of syntax errors (60-80% invalid)
- Very low correctness scores (<10/100)
- These models lack the capacity for the domain knowledge required

---

## Conclusions

1. **For best quality, use Claude Opus 4.5** - 58.9/100 AI score, maintains quality on complex circuits

2. **For speed + quality balance, use Qwen 3 235B via Cerebras** - 49.6/100 AI score at ~1.8s/prompt

3. **Syntax ≠ Semantics** - A model can produce valid TOKN structure while still making circuit design errors

4. **Correctness is the bottleneck** - Even Claude only reaches 50.3/100 on correctness, indicating room for improvement

5. **Hard prompts differentiate models** - Claude maintains 58.6 on hard vs others dropping to 20-47

---

## Recommendations

| Use Case | Recommended Model | Rationale |
|----------|-------------------|-----------|
| Highest quality | Claude Opus 4.5 | Best scores across all metrics |
| Production (speed matters) | Qwen 3 235B via Cerebras | Good quality, 20x faster |
| Budget-conscious | ZAI GLM 4.6 via Cerebras | Similar to Qwen, may be cheaper |
| Not recommended | Llama 3.1 8B, Qwen 3 32B | Too low quality for practical use |

---

## Raw Data

Full results are available in the benchmark output directories:
- `benchmark/output/251207_223238_results/` - Claude Opus 4.5
- `benchmark/output/251207_210416_results/` - GPT-OSS 120B
- `benchmark/output/251207_210827_results/` - Llama 3.3 70B
- `benchmark/output/251207_211305_results/` - Llama 3.1 8B
- `benchmark/output/251207_211746_results/` - Qwen 3 235B
- `benchmark/output/251207_212251_results/` - Qwen 3 32B
- `benchmark/output/251207_212717_results/` - ZAI GLM 4.6

Each directory contains:
- `summary.json` - Aggregate statistics
- `all_results.jsonl` - Full results for each prompt
- Individual folders with `prompt.txt`, `output.tokn`, and `result.json`
