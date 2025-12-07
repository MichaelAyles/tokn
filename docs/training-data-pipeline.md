# TOKN Training Data Pipeline

## Overview

This document describes the pipeline for generating LLM training data from open-source KiCad schematics. The goal is to train a model to generate valid TOKN circuit descriptions from natural language prompts.

## Pipeline Status

**Completed:** Data collection, classification, TOKN encoding, database storage

**Next:** Training data formatting, prompt variation, benchmark suite

## Data Sources

### Scraped Repositories

- **Source:** GitHub repositories containing `.kicad_sch` files
- **Database:** `data/kicad_repos.db` (SQLite)
- **Raw files:** `data/repos/` (gitignored)

### Repository Statistics

| Metric | Count |
|--------|-------|
| Total repositories | 287 |
| Total schematic files | 4,586 |
| Files with TOKN encoding | 3,123 |
| Encoding failures | 32 (UTF-8 issues) |

### Notable Projects in Dataset

| Stars | Repository | Description |
|-------|------------|-------------|
| 6,865 | foostan/crkbd | Corne split keyboard |
| 6,299 | ClemensElflein/OpenMower | Robotic mower upgrade |
| 3,031 | opulo-inc/lumenpnp | Pick and place machine |
| 1,261 | skot/bitaxe | Bitcoin ASIC miner |
| 1,171 | EEVengers/ThunderScope | Open source oscilloscope |
| 1,000 | mjbots/moteus | Brushless servo controller |

## Database Schema

### `files` table (relevant columns)

| Column | Description |
|--------|-------------|
| `id` | Primary key |
| `file_name` | Schematic filename |
| `file_path` | Path within repository |
| `local_path` | Local path to raw file |
| `tokn` | **TOKN v1 encoded schematic** |
| `flattened_data` | Legacy descriptive text format |
| `classification_score` | Quality score 0-10 |
| `classification_data` | JSON with subcircuit analysis |
| `component_count` | Number of components |

### `repositories` table

| Column | Description |
|--------|-------------|
| `full_name` | owner/repo format |
| `url` | GitHub URL |
| `license` | License name |
| `stars` | Star count |
| `description` | Repo description |

## Classification Data

Each schematic was analyzed by an LLM to identify reusable subcircuits. The `classification_data` JSON contains:

```json
{
  "score": 8.5,
  "hasUsefulSubcircuits": true,
  "subcircuits": [
    {
      "name": "ESP32-S3 Mini Power Supply and Reset Circuitry",
      "description": "This block centers around the ESP32-S3-MINI-1U module...",
      "components": "ESP32-S3-MINI-1U (U1), C101, C102, C105, R101, SW102",
      "useCase": "Any design incorporating the ESP32-S3-MINI module...",
      "notes": "The decoupling values (22uF, 100nF, 1uF) are typical...",
      "tags": ["wifi-module", "power", "decoupling", "esp32-s3", "reset-circuit"]
    }
  ]
}
```

### Classification Statistics

| Metric | Value |
|--------|-------|
| Files with subcircuits | 3,155 |
| Total subcircuits identified | 10,088 |
| Average subcircuits per file | 3.2 |
| Average classification score | 5.90 |
| Classification cost | ~$0.70 |

### Score Distribution

| Score | Record Count |
|-------|--------------|
| 8+ | 523 |
| 7 | 3,720 |
| 6 | 2,730 |
| 5 | 1,478 |
| 4 | 400 |
| 3 | 1,072 |
| 2 | 42 |
| 1 | 20 |

### Top Subcircuit Tags

| Tag | Count |
|-----|-------|
| interface | 2,581 |
| power | 2,390 |
| digital | 1,832 |
| decoupling | 1,582 |
| analog | 1,144 |
| protection | 935 |
| voltage-regulator | 892 |
| filtering | 729 |
| connector | 598 |
| indicator | 541 |

### License Distribution

| License | Files |
|---------|-------|
| Unknown | 2,473 |
| MIT | 1,882 |
| GPL v3.0 | 1,049 |
| CC-BY-NC-SA-4.0 | 863 |
| Apache 2.0 | 590 |
| Custom | 455 |
| CC0 | 317 |
| CC-BY 4.0 | 290 |
| CERN-OHL-P v2 | 253 |

## Generated Training Data

### Output Files

Located in `data/training/`:

| File | Description |
|------|-------------|
| `training_data.jsonl` | Raw records (9,985 lines) |
| `training_conversations.jsonl` | Conversation format |
| `training_stats.json` | Statistics |

### Record Format (`training_data.jsonl`)

```json
{
  "file": {
    "id": 1261,
    "name": "Motor-MK1.kicad_sch",
    "path": "boards/Motor-MK1/Motor-MK1.kicad_sch"
  },
  "attribution": {
    "repo": "ISSUIUC/ISS-PCB",
    "url": "https://github.com/ISSUIUC/ISS-PCB",
    "license": "Unknown",
    "owner": "ISSUIUC",
    "stars": 22
  },
  "classification": {
    "score": 8.5,
    "rank": 1,
    "total": 5,
    "name": "ESP32-S3 Mini Power Supply and Reset Circuitry",
    "description": "This block centers around...",
    "components": "ESP32-S3-MINI-1U (U1), C101, C102...",
    "use_case": "Any design incorporating...",
    "notes": "The decoupling values...",
    "tags": ["wifi-module", "power", "decoupling"]
  },
  "tokn": "# TOKN v1\ntitle: MotorBoard MK1\n\ncomponents[63]..."
}
```

## Scripts

### `scripts/generate_training_data.py`

Generates training data by:
1. Reading files from database with `classification_score > 0`
2. Re-encoding raw `.kicad_sch` files to TOKN format
3. Pairing TOKN with classification metadata
4. Writing JSONL output files

Usage:
```bash
python scripts/generate_training_data.py
```

## Next Steps

### 1. Training Data Preparation

- [ ] Filter to score >= 5 (8,451 records)
- [ ] Generate varied prompt styles:
  - Direct: "give me a circuit for..."
  - Component-focused: "using a LM5117..."
  - Function-focused: "step down 24V to 5V"
- [ ] Include tag/component information in prompts
- [ ] Consider license filtering for commercial use

### 2. Benchmark Suite

Evaluate generated TOKN quality:

1. **Syntactic validity** - Parses as valid TOKN
2. **Semantic validity** - Sensible connections (no floating IC pins, power connected)
3. **Component appropriateness** - Relevant parts for the request
4. **Completeness** - Decoupling caps, pull-ups where needed
5. **Round-trip test** - Decodes to valid KiCad schematic

### 3. Fine-tuning

- Format: OpenAI/Anthropic conversation JSONL
- System prompt defining TOKN format
- User prompts with varied natural language
- Assistant responses with TOKN output

## Sample Queries

### Get high-quality power circuits:
```sql
SELECT f.file_name, f.tokn, f.classification_data, r.full_name
FROM files f
JOIN repositories r ON f.repo_id = r.id
WHERE f.classification_score >= 7
  AND f.classification_data LIKE '%power%'
  AND f.tokn IS NOT NULL
LIMIT 10;
```

### Get circuits by tag:
```sql
SELECT f.file_name, f.classification_score, r.full_name
FROM files f
JOIN repositories r ON f.repo_id = r.id
WHERE f.classification_data LIKE '%"voltage-regulator"%'
  AND f.classification_score >= 6
ORDER BY f.classification_score DESC;
```
