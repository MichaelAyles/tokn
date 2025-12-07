# TOKN Model Comparison: Cerebras Inference Benchmark

**Date:** December 7, 2024
**Benchmark:** 30 prompts per model (10 easy, 10 medium, 10 hard)
**Scorer:** Google Gemini 2.5 Flash via OpenRouter

## Executive Summary

We benchmarked six models available via Cerebras Inference on their ability to generate valid electronic circuit schematics in TOKN format. The results show significant variation in performance, with **Qwen 3 235B** emerging as the top performer for circuit generation tasks.

### Key Findings

1. **Qwen 3 235B** achieved the highest overall scores (49.6/100 AI, 86.7% static)
2. **Model size doesn't always correlate with performance** - Llama 3.3 70B underperformed smaller models
3. **Syntax validity varies dramatically** - from 40% (Qwen 3 32B) to 100% (Llama 3.3 70B, Qwen 3 235B)
4. **All models struggle with hard prompts** - highlighting the challenge of complex circuit design

---

## Overall Rankings

### By AI Score (Weighted: Functionality 35%, Completeness 25%, Correctness 25%, Best Practices 15%)

| Rank | Model | AI Score | Static Score | Syntax Valid |
|------|-------|----------|--------------|--------------|
| 1 | **Qwen 3 235B** | 49.6/100 | 86.7% | 100% |
| 2 | ZAI GLM 4.6 | 49.4/100 | 76.1% | 90% |
| 3 | GPT-OSS 120B | 41.8/100 | 54.5% | 63% |
| 4 | Llama 3.3 70B | 35.8/100 | 82.1% | 100% |
| 5 | Qwen 3 32B | 14.5/100 | 32.4% | 40% |
| 6 | Llama 3.1 8B | 12.6/100 | 57.1% | 80% |

```
AI Score by Model
═══════════════════════════════════════════════════════════════════

Qwen 3 235B    ████████████████████████████████████████████████▉  49.6
ZAI GLM 4.6    ████████████████████████████████████████████████▍  49.4
GPT-OSS 120B   █████████████████████████████████████████▊         41.8
Llama 3.3 70B  ███████████████████████████████████▊               35.8
Qwen 3 32B     ██████████████▌                                    14.5
Llama 3.1 8B   ████████████▌                                      12.6

                0        20        40        60        80       100
```

---

## Detailed Breakdown by Difficulty

### Easy Prompts (Single IC circuits)

| Model | Static Score | AI Score |
|-------|-------------|----------|
| Llama 3.3 70B | 96.3% | 42.5 |
| Qwen 3 235B | 90.9% | 59.6 |
| GPT-OSS 120B | 82.8% | 65.5 |
| ZAI GLM 4.6 | 72.8% | 57.7 |
| Llama 3.1 8B | 56.9% | 1.4 |
| Qwen 3 32B | 17.3% | 7.0 |

```
Easy Prompts - AI Score
═══════════════════════════════════════════════════════════════════

GPT-OSS 120B   █████████████████████████████████████████████████████████████████▌  65.5
Qwen 3 235B    ███████████████████████████████████████████████████████████▌        59.6
ZAI GLM 4.6    █████████████████████████████████████████████████████████▋          57.7
Llama 3.3 70B  ██████████████████████████████████████████▌                         42.5
Qwen 3 32B     ███████                                                              7.0
Llama 3.1 8B   █▍                                                                   1.4
```

### Medium Prompts (2-3 IC subsystems)

| Model | Static Score | AI Score |
|-------|-------------|----------|
| Qwen 3 235B | 91.1% | 41.5 |
| ZAI GLM 4.6 | 82.5% | 51.1 |
| Llama 3.3 70B | 81.1% | 39.6 |
| Llama 3.1 8B | 77.2% | 16.7 |
| GPT-OSS 120B | 41.9% | 29.9 |
| Qwen 3 32B | 37.2% | 15.7 |

```
Medium Prompts - AI Score
═══════════════════════════════════════════════════════════════════

ZAI GLM 4.6    ███████████████████████████████████████████████████▏                51.1
Qwen 3 235B    █████████████████████████████████████████▌                          41.5
Llama 3.3 70B  ███████████████████████████████████████▌                            39.6
GPT-OSS 120B   █████████████████████████████▉                                      29.9
Llama 3.1 8B   ████████████████▋                                                   16.7
Qwen 3 32B     ███████████████▋                                                    15.7
```

### Hard Prompts (4+ IC complex systems)

| Model | Static Score | AI Score |
|-------|-------------|----------|
| Qwen 3 235B | 78.2% | 47.6 |
| ZAI GLM 4.6 | 73.2% | 39.4 |
| GPT-OSS 120B | 38.7% | 29.9 |
| Llama 3.3 70B | 68.9% | 25.3 |
| Qwen 3 32B | 42.6% | 20.9 |
| Llama 3.1 8B | 37.1% | 19.6 |

```
Hard Prompts - AI Score
═══════════════════════════════════════════════════════════════════

Qwen 3 235B    ███████████████████████████████████████████████▌                    47.6
ZAI GLM 4.6    ███████████████████████████████████████▍                            39.4
GPT-OSS 120B   █████████████████████████████▉                                      29.9
Llama 3.3 70B  █████████████████████████▎                                          25.3
Qwen 3 32B     ████████████████████▉                                               20.9
Llama 3.1 8B   ███████████████████▌                                                19.6
```

---

## Score Component Breakdown

### AI Scoring Components (Average across all difficulties)

| Model | Functionality | Completeness | Correctness | Best Practices |
|-------|--------------|--------------|-------------|----------------|
| Qwen 3 235B | 59.3 | 48.3 | 39.5 | 45.7 |
| ZAI GLM 4.6 | 58.3 | 48.7 | 40.2 | 45.2 |
| GPT-OSS 120B | 49.7 | 40.2 | 34.5 | 38.0 |
| Llama 3.3 70B | 44.3 | 37.2 | 23.8 | 33.5 |
| Llama 3.1 8B | 19.7 | 11.2 | 6.0 | 9.3 |
| Qwen 3 32B | 19.7 | 13.3 | 9.7 | 12.7 |

**Key Observation:** Correctness scores are consistently the lowest across all models, indicating that even when models produce syntactically valid TOKN with the right components, the actual pin connections and circuit topology often have errors.

---

## Validation Metrics

### Static Validation Results

| Model | Syntax Valid | Semantic Valid | Requirement Match |
|-------|-------------|----------------|-------------------|
| Qwen 3 235B | 100% (30/30) | 53% (16/30) | 95.6% |
| Llama 3.3 70B | 100% (30/30) | 37% (11/30) | 96.4% |
| ZAI GLM 4.6* | 90% (27/30) | 53% (16/30) | 84.9% |
| Llama 3.1 8B | 80% (24/30) | 30% (9/30) | 75.8% |
| GPT-OSS 120B | 63% (19/30) | 80% (24/30) | 56.2% |
| Qwen 3 32B | 40% (12/30) | 77% (23/30) | 36.5% |

*ZAI GLM 4.6 hit rate limits on 3 prompts due to restrictive quotas.

**Interesting Pattern:** High syntax validity doesn't guarantee high semantic validity. Llama 3.3 70B has perfect syntax but only 37% semantic validity - it generates well-formed TOKN that often has invalid connections.

---

## Generation Speed

All models were run via Cerebras Inference, known for extremely fast inference:

| Model | Avg Time/Prompt | Total Run Time (30 prompts) |
|-------|-----------------|----------------------------|
| GPT-OSS 120B | ~2.4s | 237s |
| Qwen 3 32B | ~3.1s | 253s |
| Llama 3.3 70B | ~1.2s | 265s |
| Llama 3.1 8B | ~1.6s | 268s |
| Qwen 3 235B | ~1.8s | 291s |
| ZAI GLM 4.6 | ~3.2s | 294s |

Note: Total run time includes AI scoring via OpenRouter (Gemini), which adds ~10-20s per prompt.

---

## Analysis

### Why Qwen 3 235B Leads

1. **Consistent syntax** - 100% valid TOKN structure
2. **Strong requirement matching** - 95.6% of required components included
3. **Best correctness scores** - Fewer pin assignment errors
4. **Maintains quality on hard prompts** - 47.6/100 vs others dropping to 20-30

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

1. **For TOKN generation, use Qwen 3 235B** - Best overall performance and consistency

2. **Model size matters, but not linearly** - The 235B Qwen outperforms smaller models, but 70B Llama underperforms expectations

3. **Syntax ≠ Semantics** - A model can produce valid TOKN structure while still making circuit design errors

4. **Hard prompts remain challenging** - No model exceeds 50/100 on complex system designs, indicating significant room for improvement through fine-tuning

5. **Cerebras is fast** - All models complete generation in 1-3 seconds, with total benchmark time dominated by AI scoring

---

## Next Steps

1. **Fine-tune on TOKN training data** - We have 10,000+ schematic examples ready
2. **Expand benchmark to other providers** - Compare against GPT-4, Claude, etc.
3. **Improve hard prompts** - Add more system-level designs to stress test
4. **Track improvements over time** - Re-run benchmarks after training

---

## Raw Data

Full results are available in the benchmark output directories:
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
