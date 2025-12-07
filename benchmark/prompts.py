"""
Benchmark prompts for TOKN generation.

Generates specific, testable prompts from the training data.
Prompts include concrete component requirements that can be verified.
"""

import json
import random
import re
import sqlite3
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class BenchmarkPrompt:
    """A benchmark prompt with expected reference output."""
    prompt: str
    prompt_style: str
    reference_tokn: str

    # Requirements extracted from the prompt for validation
    required_components: list[str] = field(default_factory=list)  # e.g., ["EMC2101", "10k", "0.1uF"]
    required_ics: list[str] = field(default_factory=list)  # e.g., ["EMC2101", "RT9080"]

    # Metadata
    subcircuit_name: str = ""
    subcircuit_tags: list[str] = field(default_factory=list)
    subcircuit_components: str = ""
    file_id: int = 0
    file_name: str = ""
    repo: str = ""
    score: float = 0.0


def parse_components(components_str: str) -> tuple[list[str], list[str]]:
    """Parse component string to extract ICs and values.

    Input: "U7 (EMC2101), R9 (10k), C33 (0.1uF), C29 (0.1uF)"
    Output: (["EMC2101"], ["EMC2101", "10k", "0.1uF"])
    """
    ics = []
    all_parts = []

    # Find IC part numbers in parentheses after U/IC references
    ic_pattern = r'[UI]C?\d+\s*\(([^)]+)\)'
    for match in re.finditer(ic_pattern, components_str):
        part = match.group(1).strip()
        # Must look like a part number (has letters and numbers, not just text)
        if part and re.search(r'[A-Z].*\d|\d.*[A-Z]', part, re.I):
            ics.append(part)
            all_parts.append(part)

    # Find values in parentheses (resistors, caps, inductors)
    # Must be actual values like 10k, 0.1uF, 4.7nF, 100R, 2.2uH
    value_pattern = r'[RCLF]\d+\s*\(([^)]+)\)'
    for match in re.finditer(value_pattern, components_str):
        value = match.group(1).strip()
        # Must look like a component value (number + unit)
        if value and re.match(r'^[\d.]+\s*[kKmMuUnNpPrRfFhH]', value):
            all_parts.append(value)

    return ics, all_parts


def generate_specific_prompt(subcircuit: dict) -> tuple[str, str, list[str], list[str]]:
    """Generate a specific, testable prompt from subcircuit data.

    Returns: (prompt_text, style, required_ics, required_components)
    """
    name = subcircuit.get('name', '')
    description = subcircuit.get('description', '')
    components = subcircuit.get('components', '')
    use_case = subcircuit.get('useCase', '')

    ics, all_parts = parse_components(components)

    # Build a specific prompt that mentions the key components
    style = random.choice(['detailed', 'component_list', 'functional'])

    if style == 'detailed' and description:
        # Use description but add component requirements
        prompt = f"{description.split('.')[0]}."
        if ics:
            prompt += f" Use {', '.join(ics[:3])}."
        if len(all_parts) > len(ics):
            # Add some passive values
            passives = [p for p in all_parts if p not in ics][:3]
            if passives:
                prompt += f" Include {', '.join(passives)} components."

    elif style == 'component_list':
        # Direct component specification
        if ics:
            prompt = f"Design a {name} circuit using {', '.join(ics[:3])}"
        else:
            prompt = f"Design a {name} circuit"

        # Add passive requirements
        passives = [p for p in all_parts if p not in ics][:4]
        if passives:
            prompt += f" with {', '.join(passives)}"
        prompt += "."

    else:  # functional
        # Use case with component hints
        if use_case:
            prompt = f"I need to {use_case.lower().lstrip('to ').lstrip('for ')}."
        else:
            prompt = f"Create a {name}."

        if ics:
            prompt += f" Use {ics[0]}."
        if len(all_parts) > 1:
            prompt += f" Include appropriate decoupling."

    return prompt, style, ics, all_parts


def load_benchmark_prompts(
    db_path: str,
    min_score: float = 5.0,
    limit: int = 100,
    seed: int = 42
) -> list[BenchmarkPrompt]:
    """Load benchmark prompts from the database."""
    random.seed(seed)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get high-quality files with TOKN
    cursor.execute('''
        SELECT f.id, f.file_name, f.tokn, f.classification_data, f.classification_score,
               r.full_name
        FROM files f
        JOIN repositories r ON f.repo_id = r.id
        WHERE f.tokn IS NOT NULL
          AND f.classification_score >= ?
        ORDER BY f.classification_score DESC
    ''', (min_score,))

    rows = cursor.fetchall()
    conn.close()

    # Build prompts from subcircuits
    all_prompts = []

    for row in rows:
        file_id, file_name, tokn, classification_json, score, repo = row

        try:
            classification = json.loads(classification_json)
            subcircuits = classification.get('subcircuits', [])
        except:
            continue

        for sc in subcircuits:
            # Skip subcircuits without specific components
            components = sc.get('components', '')
            if not components or len(components) < 10:
                continue

            # Generate specific prompt with requirements
            prompt_text, style, req_ics, req_components = generate_specific_prompt(sc)

            # REQUIRE at least one IC - this is what makes the benchmark meaningful
            # Without a specific IC requirement, the model can generate any valid circuit
            if not req_ics:
                continue

            # Also require at least 2 total components to test
            if len(req_components) < 2:
                continue

            benchmark = BenchmarkPrompt(
                prompt=prompt_text,
                prompt_style=style,
                reference_tokn=tokn,
                required_components=req_components,
                required_ics=req_ics,
                subcircuit_name=sc.get('name', ''),
                subcircuit_tags=sc.get('tags', []),
                subcircuit_components=components,
                file_id=file_id,
                file_name=file_name,
                repo=repo,
                score=score,
            )
            all_prompts.append(benchmark)

    # Shuffle and limit
    random.shuffle(all_prompts)
    return all_prompts[:limit]


def export_prompts_jsonl(prompts: list[BenchmarkPrompt], output_path: str):
    """Export prompts to JSONL for benchmarking."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for p in prompts:
            obj = {
                'prompt': p.prompt,
                'prompt_style': p.prompt_style,
                'reference_tokn': p.reference_tokn,
                'required_components': p.required_components,
                'required_ics': p.required_ics,
                'metadata': {
                    'subcircuit_name': p.subcircuit_name,
                    'subcircuit_tags': p.subcircuit_tags,
                    'subcircuit_components': p.subcircuit_components,
                    'file_id': p.file_id,
                    'file_name': p.file_name,
                    'repo': p.repo,
                    'score': p.score,
                }
            }
            f.write(json.dumps(obj, ensure_ascii=False) + '\n')

    print(f"Exported {len(prompts)} prompts to {output_path}")


def main():
    base_dir = Path(__file__).parent.parent
    db_path = base_dir / 'data' / 'kicad_repos.db'
    output_path = base_dir / 'benchmark' / 'test_prompts.jsonl'

    print(f"Loading prompts from {db_path}")
    prompts = load_benchmark_prompts(str(db_path), min_score=5.0, limit=200)

    # Show distribution
    styles = {}
    for p in prompts:
        styles[p.prompt_style] = styles.get(p.prompt_style, 0) + 1

    print(f"\nGenerated {len(prompts)} benchmark prompts")
    print("\nPrompt style distribution:")
    for style, count in sorted(styles.items()):
        print(f"  {style}: {count}")

    # Show requirement stats
    avg_ics = sum(len(p.required_ics) for p in prompts) / len(prompts)
    avg_components = sum(len(p.required_components) for p in prompts) / len(prompts)
    print(f"\nAverage required ICs per prompt: {avg_ics:.1f}")
    print(f"Average required components per prompt: {avg_components:.1f}")

    print("\nSample prompts:")
    for p in prompts[:5]:
        print(f"\n  [{p.prompt_style}] {p.prompt}")
        print(f"    Required ICs: {p.required_ics}")
        print(f"    Required components: {p.required_components[:5]}...")

    export_prompts_jsonl(prompts, str(output_path))


if __name__ == '__main__':
    main()
