# The Fine-Tuning Dilemma: When More Training Doesn't Mean More Knowledge

**Date:** December 7, 2024

## The Question

We have 10,000+ real-world KiCad schematics encoded in TOKN format. We have a benchmark showing that current models score between 12-50/100 on circuit generation. The obvious next step seems clear: fine-tune a model on this data and watch the scores improve.

But should we?

Our benchmark results reveal a fundamental problem that challenges the value proposition of fine-tuning for this domain. This post explores why.

---

## What the Benchmarks Actually Tell Us

Let's look at two outputs for similar tasks - a differential amplifier from Llama 3.1 8B and a voltage follower from Qwen 3 235B.

### Llama 3.1 8B: The Format-Follower

**Prompt:** "Design a differential amplifier using TL072 with 10kohm input resistors and 100kohm feedback resistors"

```
pins{U1}[8]:
  1,PIN1+
  2,PIN1-
  3,PIN4+
  4,PIN5+
  5,PIN9+
  6,PIN10+
  7,PIN13-
  8,PIN14-
```

**Static Score:** 98% (syntax valid, requirements matched)
**AI Score:** 0/100

The model produced perfectly formatted TOKN. It included the TL072 and all required resistors. But the pin definitions are completely fabricated - "PIN1+, PIN4+, PIN9+" aren't real TL072 pins. A TL072 has pins like "OUT1, IN1-, IN1+, V-, IN2+, IN2-, OUT2, V+".

The model knows **how to write TOKN** but doesn't know **what a TL072 is**.

### Qwen 3 235B: The Knowledgeable Imperfect

**Prompt:** "Design a voltage follower using TL071 op-amp"

```
pins{U1}[8]:
  1,OFFSET NULL
  2,IN-
  3,IN+
  4,V-
  5,OFFSET NULL
  6,OUTPUT
  7,V+
  8,NC
```

**Static Score:** 98%
**AI Score:** 61.5/100

This model used the **correct TL071 pinout** from memory. It knows that pin 2 is the inverting input, pin 3 is non-inverting, pin 4 is V-, etc. This is knowledge from pre-training on datasheets, electronics forums, and textbooks.

But it still made errors - it forgot to connect output to IN- (the defining characteristic of a voltage follower). It added unnecessary components. The circuit wouldn't work as drawn.

---

## The Knowledge Gap

Here's the uncomfortable truth our benchmarks reveal:

| Model | Syntax Valid | AI Correctness |
|-------|-------------|----------------|
| Llama 3.1 8B | 80% | 6.0/100 |
| Qwen 3 32B | 40% | 9.7/100 |
| Llama 3.3 70B | 100% | 23.8/100 |
| GPT-OSS 120B | 63% | 34.5/100 |
| ZAI GLM 4.6 | 90% | 40.2/100 |
| Qwen 3 235B | 100% | 39.5/100 |

**Correctness** - knowing the right pin numbers, proper connections, valid circuit topologies - tops out at 40% even for the best models. This isn't a format problem. It's a **domain knowledge problem**.

The 8B model achieved 80% syntax validity. Fine-tuning could probably push that to 95-100%. But its correctness score of 6.0/100 reflects a fundamental lack of electronics knowledge that no amount of TOKN examples will fix.

---

## What Fine-Tuning Can Actually Improve

### Things Fine-Tuning Can Fix

1. **TOKN Syntax** - Headers, section structure, field formatting
2. **Common Patterns** - Decoupling capacitor placement, power rail naming
3. **Template Matching** - If the training data has "LM7805 + 0.33uF + 0.1uF", the model learns this combo
4. **Requirement Adherence** - Including components mentioned in the prompt

### Things Fine-Tuning Cannot Fix

1. **IC Pinouts** - A TL072 has 8 pins with specific functions. This is factual knowledge.
2. **Circuit Theory** - Understanding why a voltage follower needs feedback
3. **Component Selection** - Knowing that a 4.7k pull-up is appropriate for I2C
4. **Engineering Judgment** - Choosing between circuit topologies
5. **Novel ICs** - Any IC not extensively covered in pre-training

The crux: **Fine-tuning can teach format, but not facts.**

---

## The Memorization Problem

"But wait," you might say, "if we fine-tune on 10,000 circuits with correct pinouts, won't the model learn those pinouts?"

Yes and no.

The model might memorize that specific circuit configurations. Train it on 50 examples of "STM32F407 power supply" and it might reproduce those correctly. But:

1. **We can only fine-tune small models** (8B-32B range) due to compute constraints
2. **Small models have limited capacity** for storing factual knowledge
3. **The long tail is infinite** - there are thousands of ICs we can't cover
4. **Memorization isn't generalization** - knowing STM32F407 doesn't help with STM32H743

Consider: Our training data has ~3,000 unique schematics. The electronics industry has millions of IC variants. We'd be teaching a small fraction of the knowledge needed.

---

## The Economic Calculation

Let's be honest about the numbers:

**Fine-tuning costs:**
- Compute time for training
- Iteration cycles (probably 3-5 attempts)
- Evaluation and testing
- Ongoing maintenance as base models update

**Expected improvement:**
- Syntax: 80% → 95% (achievable)
- Requirement matching: 75% → 90% (achievable)
- **Correctness: 6% → ??? (the unknown)**

If correctness only improves to 15-20%, we've spent significant resources to build something still worse than just calling Qwen 235B via API.

**The API alternative:**
- Qwen 235B scores 39.5/100 on correctness already
- Cerebras inference is fast (~2s per generation)
- No training costs, always gets base model improvements

---

## A More Honest Assessment

Let's model what a fine-tuned Llama 3.1 8B might realistically achieve:

| Metric | Before | After (Optimistic) | Qwen 235B |
|--------|--------|-------------------|-----------|
| Syntax Valid | 80% | 98% | 100% |
| Requirement Match | 75.8% | 92% | 95.6% |
| AI Correctness | 6.0 | 18.0 | 39.5 |
| **AI Overall** | **12.6** | **~28** | **49.6** |

Even with optimistic improvements, we'd achieve roughly half the performance of using a larger model. And this assumes correctness improves 3x - which may be generous for a model lacking fundamental knowledge.

---

## The Hybrid Approach

If we still want to pursue fine-tuning, the honest path forward is a hybrid system:

### Option 1: Format-Only Fine-Tuning
Fine-tune a small model purely for TOKN format compliance. Use it as a "formatter" that takes rough circuit descriptions and outputs valid TOKN structure. Accept that it won't know pinouts.

**Then:** Use RAG or tool-calling to look up actual IC pinouts from a database.

### Option 2: Verification Pipeline
Use a small fine-tuned model for fast generation, then validate with a larger model. The small model drafts, the large model checks and corrects.

**Trade-off:** You're now paying for two models instead of one.

### Option 3: Focus on Embeddings
Instead of fine-tuning for generation, create embeddings of our schematic corpus. Use semantic search to find similar circuits, then let a large model adapt them.

**Benefit:** Leverages our data without the generation burden.

---

## What We're Really Building

The honest answer to "should we fine-tune?" depends on what we're actually building:

### If Building a Research Benchmark
Don't fine-tune. Use the best available models via API. The benchmark's value is measuring capability, not creating capability.

### If Building a Product
Consider whether your product can tolerate errors. At 40% correctness, circuits need human review anyway. Is a fine-tuned model at 20% correctness materially different for your workflow?

### If Building for Offline/Edge
Fine-tuning makes sense if you need local inference and can accept lower quality. A 95% syntax-valid 8B model running locally may beat a 40% correct API model that's unavailable.

### If Cost is the Constraint
Run the numbers. At what volume does fine-tuning cost less than API calls? Remember to include training iteration costs, not just inference.

---

## Our Conclusion

We're not going to fine-tune. Here's why:

1. **The gap is too large.** Llama 3.1 8B at 12.6/100 vs Qwen 235B at 49.6/100 is a 4x difference. Fine-tuning won't close that gap.

2. **Correctness is the bottleneck.** Our data can't teach IC pinouts to a model that doesn't already know them. We'd be polishing format while the core problem remains.

3. **The economics don't work.** Cerebras gives us fast, cheap inference on capable models. Fine-tuning a worse model doesn't make sense.

4. **We'd rather invest elsewhere.** Better prompts, better evaluation, better RAG for pinout lookup - these seem more promising than fighting the knowledge gap.

---

## The Uncomfortable Truth

This analysis reveals something uncomfortable about the current state of LLM fine-tuning:

**Fine-tuning works best when you're teaching format, style, or domain-specific language patterns. It works poorly when you're trying to instill factual knowledge the base model lacks.**

For TOKN generation, we're firmly in the second category. We need a model that knows electronics - that has absorbed datasheets, application notes, and circuit theory during pre-training. That knowledge lives in the larger models.

Our 10,000 schematics are valuable - but perhaps not for fine-tuning. They're valuable for:
- Benchmarking model capabilities
- Few-shot examples in prompts
- RAG retrieval for similar circuits
- Validation of generated outputs

The path to better circuit generation probably isn't "train our own model." It's "use the best available models intelligently."

---

## Appendix: The Numbers

### Benchmark Configuration
- 30 prompts per model (10 easy, 10 medium, 10 hard)
- AI scoring via Gemini 2.5 Flash
- All models run via Cerebras Inference

### Full Results Summary

| Model | Params | Syntax | Semantic | Requirement | AI Score |
|-------|--------|--------|----------|-------------|----------|
| Qwen 3 235B | 235B | 100% | 53% | 95.6% | 49.6 |
| ZAI GLM 4.6 | ~200B? | 90% | 53% | 84.9% | 49.4 |
| GPT-OSS 120B | 120B | 63% | 80% | 56.2% | 41.8 |
| Llama 3.3 70B | 70B | 100% | 37% | 96.4% | 35.8 |
| Qwen 3 32B | 32B | 40% | 77% | 36.5% | 14.5 |
| Llama 3.1 8B | 8B | 80% | 30% | 75.8% | 12.6 |

### Key Correlations
- Model size correlates with AI score (r ≈ 0.7)
- Syntax validity does NOT correlate with correctness
- Requirement matching is achievable even at small scale
- Correctness remains the limiting factor across all sizes
