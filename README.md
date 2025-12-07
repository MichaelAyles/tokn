# TOKN

**Token-Optimised KiCad Notation** — a compact format for representing KiCad schematics, designed for LLM training and generation.

## What is TOKN?

TOKN converts KiCad schematic files (`.kicad_sch`) into a token-efficient representation, achieving **>92% token reduction** while preserving electrical connectivity, component positions, and wire geometry. It's built on [TOON](https://github.com/toon-format/spec) (Token-Oriented Object Notation).

![MAX9926 Comparison](examples/max9926-vr-conditioner/comparison.png)

### Results

| Metric | KiCad | TOKN | Reduction |
|--------|-------|------|-----------|
| File Size | 83,834 bytes | 5,077 bytes | **-93.9%** |
| Lines | 4,535 | 143 | **-96.8%** |
| Tokens | 38,678 | 3,027 | **-92.2%** |

### Goals

- **Minimise tokens** — strip UUIDs, graphics, structural noise
- **Preserve design intent** — component types, values, positions, connectivity
- **Preserve layout** — wire geometry for schematic reconstruction
- **Enable round-trip conversion** — `kicad_sch → TOKN → kicad_sch`
- **Be learnable** — consistent structure for LLM pattern learning

## Benchmark Suite

We've built a comprehensive benchmark to evaluate LLM performance at generating valid TOKN circuits. See [docs/03-benchmark-suite.md](docs/03-benchmark-suite.md) for full details.

### Latest Results (December 2024)

Benchmarked on 30 prompts (10 easy, 10 medium, 10 hard) via Cerebras Inference:

| Model | AI Score | Static Score | Syntax Valid |
|-------|----------|--------------|--------------|
| **Qwen 3 235B** | 49.6/100 | 86.7% | 100% |
| ZAI GLM 4.6 | 49.4/100 | 76.1% | 90% |
| GPT-OSS 120B | 41.8/100 | 54.5% | 63% |
| Llama 3.3 70B | 35.8/100 | 82.1% | 100% |
| Qwen 3 32B | 14.5/100 | 32.4% | 40% |
| Llama 3.1 8B | 12.6/100 | 57.1% | 80% |

**Key findings:**
- Larger models have significantly better domain knowledge (IC pinouts, circuit theory)
- Syntax validity doesn't correlate with correctness — models can produce valid TOKN that's electrically wrong
- See [docs/04-model-comparison-dec2024.md](docs/04-model-comparison-dec2024.md) for detailed analysis
- See [docs/05-fine-tuning-dilemma.md](docs/05-fine-tuning-dilemma.md) for discussion on whether fine-tuning helps

### Running Benchmarks

```bash
# Install dependencies
pip install openai python-dotenv

# Set API keys in .env.local
echo "OPENROUTER_API_KEY=your_key" >> .env.local
echo "CEREBRAS_API_KEY=your_key" >> .env.local

# Run benchmark (default: 2 easy, 2 medium, 2 hard)
python benchmark/runner.py

# Run with specific counts
python benchmark/runner.py -e 10 -m 10 -H 10

# Use different providers
python benchmark/runner.py -e 5 --model google/gemini-2.5-flash      # OpenRouter
python benchmark/runner.py -e 5 --model cerebras/qwen-3-235b-a22b-instruct-2507  # Cerebras
```

## Format

TOKN v1.2 includes four sections:

```toon
# TOKN v1
title: MAX9926 Dual VR Conditioner

components[10]{ref,type,value,fp,x,y,w,h,a}:
  C66,C,1n,,160.02,73.66,0.00,7.62,0
  IC16,MAX9926UAEE_V+,MAX9926UAEE_V+,SOP-16,129.54,88.90,38.10,17.78,0
  R75,R,10k,0603,168.91,67.31,7.62,0.00,90

pins{IC16}[16]:
  1,IN_THRS1
  2,EXT1
  3,BIAS1
  ...
  16,IN1+

nets[12]{name,pins}:
  +5VD,"C68.1,C69.1,C70.1,IC16.14"
  GND,"C68.2,C69.2,C70.2,IC16.1,IC16.3"
  DIN0-VR1-IN+,R75.2

wires[45]{net,pts}:
  +5VD,"156.21 85.09,167.64 85.09"
  +5VD,"167.64 85.09,179.07 85.09"
```

### Component Fields

| Field | Description |
|-------|-------------|
| `ref` | Reference designator (R1, C1, U1) |
| `type` | Normalised type (R, C, CP, LED, MCP2551, etc.) |
| `value` | Component value or part number |
| `fp` | Footprint shorthand (0603, SOIC-8, etc.) |
| `x,y` | Center position (mm) |
| `w,h` | Pin spread dimensions (mm) |
| `a` | Rotation angle (0, 90, 180, 270) |

### Pins Section

The `pins{REF}[N]:` section lists all pins for ICs with their datasheet names. This helps LLMs understand pin functions (including unconnected pins) and handle multi-function pins like `PC6/~{RESET}`.

## Usage

### Convert KiCad to TOKN

```bash
python src/tokn_encoder.py schematic.kicad_sch output.tokn
```

### Convert TOKN back to KiCad (experimental)

```bash
python src/tokn_decoder.py output.tokn output.kicad_sch
```

Note: The decoder is experimental. It generates valid KiCad schematics with:
- Simplified symbol representations (rectangles with pin names for ICs)
- Footprint lookup from `src/footprints.json` for common packages
- Standard dual-inline pin layout for generic ICs

See [docs/01-kicad-schematic-generation.md](docs/01-kicad-schematic-generation.md) for technical details.

### Render Comparison

```bash
python src/render.py --compare schematic.kicad_sch output.tokn comparison.png
```

### Parse TOKN

```bash
python src/tokn_parser.py output.tokn
```

## Training Data

We've collected and processed 10,000+ real-world KiCad schematics for potential LLM training:

- **3,123 files** encoded to TOKN format
- **10,088 subcircuits** identified and tagged
- High-quality examples from popular open-source projects (crkbd, OpenMower, ThunderScope, etc.)

See [docs/02-training-data-pipeline.md](docs/02-training-data-pipeline.md) for details.

## Architecture

```
                         ┌─────────────────────────────────────┐
                         │           .kicad_sch                │
                         └──────────────────┬──────────────────┘
                                            │
                         ┌──────────────────▼──────────────────┐
                         │            kicad_sch.py             │
                         │   (S-expr parser, symbol extract)   │
                         └──────────────────┬──────────────────┘
                                            │
              ┌─────────────────────────────┼─────────────────────────────┐
              │                             │                             │
              ▼                             ▼                             ▼
┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
│    connectivity.py      │  │    tokn_encoder.py      │  │      render.py          │
│  (net/pin extraction)   │  │   (TOKN generation)     │  │  (visual preview)       │
└─────────────────────────┘  └────────────┬────────────┘  └─────────────────────────┘
                                          │
                                          ▼
                         ┌─────────────────────────────────────┐
                         │              .tokn                  │
                         └──────────────────┬──────────────────┘
                                            │
              ┌─────────────────────────────┼─────────────────────────────┐
              │                             │                             │
              ▼                             ▼                             ▼
┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
│    tokn_parser.py       │  │    tokn_decoder.py      │  │      render.py          │
│   (parse to objects)    │  │  (KiCad generation)     │  │  (visual preview)       │
└─────────────────────────┘  └────────────┬────────────┘  └─────────────────────────┘
                                          │
                                          ▼
                         ┌─────────────────────────────────────┐
                         │           .kicad_sch                │
                         │          (reconstructed)            │
                         └─────────────────────────────────────┘
```

## Project Structure

```
tokn/
├── spec/
│   └── TOKN-v1.md              # Format specification (v1.2)
├── docs/
│   ├── 01-kicad-schematic-generation.md   # KiCad file format research
│   ├── 02-training-data-pipeline.md       # Training data collection
│   ├── 03-benchmark-suite.md              # Benchmark documentation
│   ├── 04-model-comparison-dec2024.md     # Model comparison results
│   └── 05-fine-tuning-dilemma.md          # Analysis on fine-tuning value
├── src/
│   ├── kicad_sch.py            # KiCad schematic parser
│   ├── connectivity.py         # Net/connectivity analyzer
│   ├── tokn_encoder.py         # KiCad → TOKN converter
│   ├── tokn_parser.py          # TOKN parser
│   ├── tokn_decoder.py         # TOKN → KiCad converter (experimental)
│   ├── footprints.json         # Footprint lookup table
│   └── render.py               # Schematic renderer
├── benchmark/
│   ├── runner.py               # Benchmark runner (multi-provider)
│   ├── validate.py             # Static TOKN validation
│   ├── ai_scorer.py            # AI semantic scoring
│   ├── prompts_easy.py         # 100 easy prompts
│   ├── prompts_medium.py       # 100 medium prompts
│   └── prompts_hard.py         # 50 hard prompts
└── examples/
    ├── mcp2551-can-transceiver/
    ├── max232-uart-rs232/
    ├── max9926-vr-conditioner/
    ├── 4-channel-current-source/
    └── tpic8101-knock-sensor/
```

## Known Issues

- **Component rotation**: Some passive components (R, C) may render with incorrect orientation in the preview. The rotation angle is stored correctly but the renderer doesn't always interpret it properly for all symbol orientations.

## Related

- [TOON Specification](https://github.com/toon-format/spec)
- [KiCad](https://www.kicad.org/)

## License

[MIT](LICENSE)
